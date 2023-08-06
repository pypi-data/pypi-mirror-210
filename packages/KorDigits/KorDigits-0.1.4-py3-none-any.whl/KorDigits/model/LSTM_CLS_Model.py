import torch.nn as nn
from torch.autograd import Variable
import torch
import torch.nn.functional as F

# input shape [seq_len, batch, input_size]
class LSTM_Model(nn.Module):
    def __init__(self, num_classes, input_size, emb_dim, hidden_size, num_layers, dropout, num_filters, kernel_size):
        super(LSTM_Model, self).__init__()

        self.num_classes = num_classes
        self.num_layers = num_layers
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(input_size, emb_dim)
        self.conv1d = nn.Conv1d(emb_dim, num_filters, kernel_size=kernel_size, padding=kernel_size//2)

        self.batch_norm = nn.BatchNorm1d(num_filters)

        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
        self.rnn1 = nn.LSTM(num_filters, hidden_size//2, num_layers=1, batch_first=True, dropout=dropout, bidirectional=True)
        # self.rnn1 = nn.GRU(num_filters, hidden_size//2, num_layers=1, batch_first=True, dropout=dropout, bidirectional=True)
        # self.rnn1 = nn.GRU(hidden_size, hidden_size//2, num_layers=1, batch_first=True, dropout=dropout, bidirectional=True)
        # self.rnn2 = nn.GRU(hidden_size, hidden_size//2, num_layers=1, batch_first=True, dropout=dropout, bidirectional=True)
        self.rnn2 = nn.LSTM(hidden_size, hidden_size//2, num_layers=1, batch_first=True, dropout=dropout, bidirectional=True)
        self.fc1 = nn.Linear(hidden_size, hidden_size//2)
        self.fc2 = nn.Linear(hidden_size//2, int(num_classes))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, device):
        h = torch.zeros((self.num_layers, x.size(0), self.hidden_size // 2)).to(device)
        c = torch.zeros((self.num_layers, x.size(0), self.hidden_size // 2)).to(device)

        torch.nn.init.xavier_normal_(h)
        torch.nn.init.xavier_normal_(c)

        embed = self.dropout(self.embedding(x))
        """CNN"""
        output = embed.transpose(1, 2) # Conv1d input shape (batch_size, input_channels, sequence_length)
        output = self.conv1d(output)
        output = self.batch_norm(output)

        output = F.relu(output)
        output = self.pool(output)

        output = output.transpose(1, 2) # LSTM input shape으로 되돌림
        #
        output, (h, c) = self.rnn1(output, (h, c))

        # output, h = self.rnn1(output, h)
        output, _ = self.rnn2(output, (h, c))
        # output, _ = self.rnn2(output, h)
        # output, _ = self.rnn3(output)
        output = self.fc1(output[:,-1,:])
        output = self.fc2(output)

        log_probs = nn.LogSoftmax(dim=1)(output)
        return log_probs

def init_weights(m):
    for name, param in m.named_parameters():
        nn.init.uniform_(param.data, -0.08, 0.08)

