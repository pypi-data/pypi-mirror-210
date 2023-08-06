import random
import warnings
import pkg_resources

import os
import pandas as pd
import re
import json

from KorDigits.utils.KoCharELECTRA.tokenization_kocharelectra import KoCharElectraTokenizer
from KorDigits.model.LSTM_CLS_Model import LSTM_Model
import torch

warnings.filterwarnings("ignore")
from datetime import datetime
class Label2Num:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        hidden_size = 512  # 512
        embed_size = 512  #
        dropout = 0.3
        num_layers = 2
        num_classes = 10
        self.tokenizer = KoCharElectraTokenizer.from_pretrained("monologg/kocharelectra-base-discriminator")
        special_tokens_dict = {'additional_special_tokens': ['<N>', '</N>']}
        self.tokenizer.add_special_tokens(special_tokens_dict)
        src_vocab_size = len(self.tokenizer.get_vocab())
        self.model = LSTM_Model(num_classes, src_vocab_size, embed_size, hidden_size, num_layers, dropout, num_filters=32,
                           kernel_size=5)

        model_path = pkg_resources.resource_filename("KorDigits", "results/save_model/lstm_kt_model.pt")
        self.model.load_state_dict(torch.load(model_path))

        dict_path = pkg_resources.resource_filename("KorDigits", "utils/word_dict.json")
        dict_file = json.load(open(dict_path, 'r', encoding='utf-8'))

        self.kor1 = dict_file['kor1_dict'] # label 7
        self.kor2 = dict_file['kor2_dict'] # label 8
        self.native_unit_dict1 = dict_file['native_unit_dict1'] # label 7 십의 자리
        self.native_unit_dict2 = dict_file['native_unit_dict2'] # label 8 십의 자리
        self.hanzi = dict_file['hanzi'] # 한자어
        self.unit_dict = dict_file['unit_dict'] # 십이상의 자리
        self.eng = dict_file['eng'] # 영어
        self.cats = ['빌리언', '밀리언', '싸우전드']
        self.month_dict = dict_file['month_dict'] # 월 단위
        self.wave_dict = dict_file['wave_dict']

    def _preprocess(self, sentence):
        # 정규표현식을 이용해 숫자를 추출하는 패턴
        if sentence.endswith("."):
            sentence = sentence[:-1]
        number_pattern = r"\d+"
        is_num = False
        self.start, self.end = [], []
        if re.search(number_pattern, sentence):
            is_num = True
            result = []
            num_pattern = r'\b\S*\d+\S*\b'
            words = re.findall(num_pattern, sentence)
            sentence = re.sub(r"\d+", "NUM", sentence)
            split_sentence = sentence.split()
            for i, word in enumerate(words):
                for j in range(len(split_sentence)):
                    tmp = split_sentence[:]
                    if 'NUM' in split_sentence[j]:
                        tmp[j] = word.strip()
                        start = max(0, j - 2)
                        end = min(len(split_sentence), j+3)
                        self.start.append(start)
                        self.end.append(end)
                        result.append(" ".join(tmp[start:end]))
                        split_sentence[j] = "NuM" + str(i)
                        break
            # 결과 반환
            return result, is_num

        # 문장에 숫자가 없으면 문장 반환
        else:
            return sentence, is_num

    def generate(self, sentence):
        # 전처리
        sentence_list, is_num = self._preprocess(sentence)
        self.sentence_list = sentence_list
        self.model.eval()
        self.labels = []
        pattern = r"NuM(\d+)"
        previous_pred = []
        # 문장에 숫자가 포함되어 있을 경우
        if is_num:
            for i in range(len(self.sentence_list)):
                # 이전 NuM 채우기
                nums = re.findall(pattern, self.sentence_list[i])
                for j in nums:
                    j = int(j)
                    self.sentence_list[i] = self.sentence_list[i].replace(f"NuM{j}", previous_pred[j])
                with torch.no_grad():
                    tokenized_sentence = self.tokenizer.encode(self.sentence_list[i], add_special_tokens=True, max_length=128,
                                                          padding='max_length', truncation=True)
                    input_tensor = torch.LongTensor(tokenized_sentence).to(self.device)
                    model = self.model.to(self.device)
                    output = model(input_tensor.unsqueeze(0), self.device)
                    label = torch.argmax(output, dim=1).detach().cpu().numpy()[0]
                    self.labels.append(label)
                match = re.search(r'\b\S*\d+\S*\b', self.sentence_list[i])
                tagging = ""
                if match:
                    tagging = match.group().strip()
                    tag = tagging.replace("%","퍼센트")
                    pred = self._generate_pred(label, tag)
                    previous_pred.append(pred)
                    sentence = sentence.replace(tagging, pred, 1)

        return sentence

    def _generate_pred(self, label, tagging):
        if label == 0:
            pred = self._label_0(tagging)
        elif label == 1:
            pred = self._label_1(tagging)
        elif label == 2:
            pred = self._label_2(tagging)
        elif label == 3:
            pred = self._label_3(tagging)
        elif label == 4:
            pred = self._label_4(tagging)
        elif label == 5:
            pred = self._label_5(tagging)
        elif label == 6:
            pred = self._label_6(tagging)
        elif label == 7:
            pred = self._label_7(tagging)
        elif label == 8:
            pred = self._label_8(tagging)
        elif label == 9:
            pred = self._label_9(tagging)
        else:
            return tagging

        return pred

    def number_to_han(self, num):
        if num == '0':
            return self.hanzi[num]
        elif num == '00':
            return '공공'

        digits = []
        i = len(list(num)) - 1
        is_zero = True
        for digit in str(num):
            if digit != '0':
                is_zero = False
                unit = self.unit_dict[str(i)]
                if i in [1, 5, 9] and digit == '1':
                    digits.append(self.unit_dict[str(i)])
                else:
                    digits.append(self.hanzi[digit] + unit)
            else:
                if not is_zero and i in [4, 5, 6]:
                    digits.append(self.unit_dict[str(4)])
                elif not is_zero and i in [8, 9, 10]:
                    digits.append(self.unit_dict[str(8)])

                is_zero = True
            i = i - 1

        result = ''.join(digits)
        start = result[0:2]
        start = start.replace('일만', '만')
        result = start + result[2:]
        result = result.replace('일십', '십').replace('일백', '백').replace('일천', '천')
        return result

    def number_to_kor(self, num):
        if num == 0:
            return self.hanzi[str(num)]

        digits = []
        one = ""
        is_zero = True
        for i, digit in enumerate(num[::-1]):
            if i == 0:
                digits.append(self.kor1[digit])
                one = digit
            elif i == 1:
                if digit == '2' and one == '0':
                    digits.append(self.native_unit_dict1[digit])
                elif digit != "0":
                    digits.append(self.native_unit_dict2[digit])
            else:
                if digit != '0':
                    is_zero = False
                    unit = self.unit_dict[str(i)]
                    if i in [1, 5, 9] and digit == '1':
                        digits.append(self.unit_dict[str(i)])
                    else:
                        digits.append(self.hanzi[digit] + unit)
                else:
                    if not is_zero and i in [4, 5, 6]:
                        digits.append(self.unit_dict[str(4)])
                    elif not is_zero and i in [8, 9, 10]:
                        digits.append(self.unit_dict[str(8)])
                    is_zero = True


        result = ''.join(digits[::-1])
        start = result[0:2]
        start = start.replace('일만', '만')
        result = start + result[2:]
        result = result.replace('일십', '십').replace('일백', '백').replace('일천', '천')
        return result

    def number_to_kor2(self, num):
        if num == 0:
            return self.hanzi[str(num)]

        digits = []
        is_zero = True
        for i, digit in enumerate(num[::-1]):
            if i == 0:
                digits.append(self.kor2[digit])
            elif i == 1:
                digits.append(self.native_unit_dict2[digit])
            else:
                if digit != '0':
                    is_zero = False
                    unit = self.unit_dict[str(i)]
                    if i in [1, 5, 9] and digit == '1':
                        digits.append(self.unit_dict[str(i)])
                    else:
                        if digit != "0":
                            digits.append(self.hanzi[digit] + unit)
                else:
                    if not is_zero and i in [4, 5, 6]:
                        digits.append(self.unit_dict[str(4)])
                    elif not is_zero and i in [8, 9, 10]:
                        digits.append(self.unit_dict[str(8)])
                    is_zero = True

        result = ''.join(digits[::-1])
        start = result[0:2]
        start = start.replace('일만', '만')
        result = start + result[2:]
        result = result.replace('일십', '십').replace('일백', '백').replace('일천', '천')
        return result

    # !/usr/bin/env python3
    # -*- coding: utf-8 -*-
    # File: num2words/en.py
    #
    # Author: Saeed Rasooli <saeed.gnu@gmail.com>    (ilius)
    #
    # This library is free software; you can redistribute it and/or
    # modify it under the terms of the GNU Lesser General Public
    # License as published by the Free Software Foundation; either
    # version 2.1 of the License, or (at your option) any later version.
    #
    # This library is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    # Lesser General Public License for more details.

    ######################### ENG #######################

    def convert_hundred(self, n):
        n = str(n)
        if len(n) < 2:
            n = '0' + n
        if n[0] == '1' or n[1] == '0':
            return self.eng[n]
        else:
            if int(n) < 10:
                return self.eng['0' + n[1]]
            else:
                return self.eng[n[0] + '0'] + self.eng['0' + n[1]]

    def convert_thousand(self, n):
        assert n < 1000
        if n < 10:
            return self.eng['0' + str(n)]
        if n < 100:
            return self.convert_hundred(n)
        n = str(n)
        if n[1:] == '00':
            return f"{self.eng['0' + n[0]]}헌드레드"
        return f"{self.eng['0' + n[0]]}헌드레드{self.convert_hundred(int(n[1:]))}"

    def convert_eng(self, n):
        n = str(n)
        n = n.zfill(12)
        s = []
        for (i, cat) in enumerate(self.cats):
            start, end = i * 3, (i + 1) * 3
            if int(n[start:end]) > 0:
                s.append(self.convert_thousand(int(n[start:end])) + cat)
        if int(n[-3:]) >= 0:
            s.append(self.convert_thousand(int(n[-3:])))
        if s:
            return "".join(s)

    ############################################
    def _label_0(self, tagging):
        # 몇시 몇분 -> '시' 12이하는 한자어, 13이상은 고유어, '분' 한자어
        # 몇시간 몇분 -> '시간' 고유어, '분' 한자어
        # 9:00 처리
        output = tagging[:]
        minute_regex = r"(\d+)분|(\d+)여분"
        second_regex = r"\d+초"
        if ":" in tagging:
            output = output.replace(":", '시 ')
            output = output.strip() + "분"

        if '시간' in output:
            hour_regex = r"(\d+)시간"

            if re.search(hour_regex, output):
                hours = re.findall(r"\d+", output)
                for hour in hours:
                    if hour == '0':
                        hour_string = '영'
                    else:
                        hour_string = self.number_to_kor(hour)
                    output = output.replace(hour, hour_string, 1)

        elif '시' in output or "씨" in output:
            hour_regex = r"(\d+)시|(\d+)씨"
            if re.search(hour_regex, output):
                hours = re.findall(r"\d+", output)
                for hour in hours:
                    # 12시 이하
                    if int(hour) <= 12:
                        if hour == '0':
                            hour_string = '영'
                        else:
                            hour_string = self.number_to_kor(hour)
                    # 12시 이상
                    else:
                        hour_string = self.number_to_han(hour)
                    output = output.replace(hour, hour_string, 1)

        # 분 처리
        if re.search(minute_regex, output):
            minutes = re.findall(r"\d+", output)
            for minute in minutes:
                # '분' 십의 자리 숫자
                if minute == '0':
                    minute_string = "영"
                else:
                    minute_string = self.number_to_han(minute)
                output = output.replace(minute, minute_string, 1)

        # 초 처리
        if re.search(second_regex, output):
            seconds = re.findall(r"\d+", output)
            for second in seconds:
                if second == '00':
                    second_string = "영"
                else:
                    second_string = self.number_to_han(second)
                output = output.replace(second, second_string, 1)

        # 처리 안된 부분
        if re.search(r"\d+", output):
            nums = re.findall(r"\d+", output)
            for n in nums:
                num_words = self.number_to_han(n)
                output = output.replace(n, num_words)

        output = output.replace("~", "에서 ")

        return output

    def _label_1(self, tagging):
        regex = "\d+"
        num = re.findall(regex, tagging)
        output = tagging[:]
        for n in num:
            num_words = self.convert_eng(n)
            output = output.replace(n, num_words, 1)

        output = output.replace("+", '플러스')

        return output

    def _label_2(self, tagging):
        year_regex = "\d+년"
        month_regex = "\d+월"
        day_regex = "\d+일"
        wave_regex = r"\d+~\d+\D*"
        output = tagging[:]

        # ~ 앞뒤 글자
        # wave_match = re.search(wave_regex, output)
        # if wave_match:
        #     start, end, char = re.findall(r"(\d+)~(\d+)(\D+)", wave_match.group())[0]
        #     output = output.replace("~", char.strip()+"에서 ")
        output = output.replace("~", "에서 ")
        year = re.search(year_regex, output).group()[:-1] if re.search(year_regex, output) else None
        month = re.findall(month_regex, output) if re.search(month_regex, output) else None
        day = re.search(day_regex, output).group()[:-1] if re.search(day_regex, output) else None

        if year:
            num_words = self.number_to_han(year)
            output = output.replace(year, num_words, 1)
        if month:
            for m in month:
                _m = str(int(m[:-1]))
                try:
                    num_words = self.month_dict[_m]
                    output = output.replace(m[:-1], num_words, 1)
                except:
                    num_words = self.number_to_han(_m)
                    output = output.replace(m[:-1], num_words, 1)
        if day:
            num_words = self.number_to_han(day)
            output = output.replace(day, num_words, 1)

        # 나머지
        comma_regex = r"\d+"
        comma_match = re.search(comma_regex, output)
        if comma_match:
            comma_list = re.findall(comma_regex, output)
            for c in comma_list:
                num_words = self.number_to_han(c)
                output = output.replace(c, num_words, 1)
        output = output.replace(",", "")

        if year is None and month is None and day is None:
            output = self._label_3(output)

        return output

    def _label_3(self, tagging):
        tagging = tagging.replace(",", "").replace("∼", "~")
        regex = r"\d+"
        division_regex = r"^\d+/\d+[ㄱ-ㅣ가-힣]*$"
        wave_regex = r"\d+~\d+\D*"
        hyphen_regex = r"\d+-\d+\D"
        vs_regex = r"\d+대\d+"
        is_vs = False
        output = tagging[:]

        # / -> 몇분의 몇
        if re.search(division_regex, output):
            num_regex = r"(\d+)/(\d+)"
            output = re.sub(num_regex, r"\2/\1", output)
            output = output.replace("/", "분의 ")

        # 하이폰 처리
        if re.search(hyphen_regex, output):
            output = output.replace("-", "에서 ")

        # 소수점
        if "." in output:
            point_regex = r"\d+\.\d+"
            point_match = re.search(point_regex, output)
            if point_match:
                decimal_part = point_match.group()
                decimal = decimal_part.split(".")[-1]
                under_point = decimal[:]
                for d in decimal:
                    if d == "0":
                        num_words = "영"
                    else:
                        num_words = self.number_to_han(d)
                    under_point = under_point.replace(d, num_words, 1)
                output = output.replace("." + decimal, "." + under_point, 1)

        if re.search(vs_regex, output):
            is_vs = True

        num = re.findall(regex, tagging)
        for n in num:
            if is_vs and n == '0':
                num_words = '영'
            else:
                num_words = self.number_to_han(n)
            output = output.replace(n, num_words, 1)

        output = output.replace(".", "점", 1).replace("~", "에서 ").replace("-", " ").replace(":", "대")
        return output

    def _label_4(self, tagging):
        regex = "\d+"
        num = re.findall(regex, tagging)
        output = tagging[:]
        for n in num:
            for i in list(n):
                num_words = self.convert_eng(i)
                output = output.replace(i, num_words, 1)

        output = output.replace("+", '플러스')

        return output

    def _label_5(self, tagging):
        regex = r"\d"
        division_regex = r"^\d+/\d+[ㄱ-ㅣ가-힣]*$"
        output = tagging[:]
        hyphen_regex = r"\d+-\d+\D"
        vs_regex = r"\d+대\d+"
        is_vs = False
        # 소수점 처리
        if '.' in tagging:
            output = output.replace("0", "영")

        # / -> 몇분의 몇
        if re.search(division_regex, output):
            if '분기' in output:
                output = output.replace("/", "")
            else:
                num_regex = r"(\d+)/(\d+)"
                output = re.sub(num_regex, r"\2/\1", output)
                output = output.replace("/", "분의 ")

        # 하이폰 처리
        if re.search(hyphen_regex, output):
            output = output.replace("-", "에서 ")

        # 몇대몇 처리
        if re.search(vs_regex, output):
            is_vs = True

        num = re.findall(regex, output)
        if len(num) == 1 and num[0] == '0':
            output = output.replace(num[0], '영', 1)
        else:
            for n in num:
                if is_vs and n == '0':
                    num_words = '영'
                else:
                    num_words = self.hanzi[n]
                output = output.replace(n, num_words, 1)

        output = output.replace(".", '점', 1).replace("~", "에서 ").replace("+", "플러스").replace("-", " ").replace(":", "대")
        return output

    def _label_6(self, tagging):
        regex = r"\d+[~|∼]\d+"

        if not re.search(regex, tagging):
            return self._label_8(tagging)
        num = re.search(regex, tagging).group()
        output = tagging[:].replace("∼", "~")

        # 십의 자리 이상의 숫자가 들어오면
        start, end = num.split("~")
        if len(list(start)) > 1:
            start_ones = int(start[-1])
            start_tens = int(start) - start_ones
            end_ones = int(end[-1])

            tens = self.number_to_kor(str(start_tens))

            ones = str(start_ones) + "~" + str(end_ones)
            ones = self.wave_dict[ones]

            result = tens + ones
            output = output.replace(num, result)
            return output
        else:
            try:
                num_words = self.wave_dict[num]
                output = output.replace(num, num_words)
            except:
                output = self._label_7(tagging)

        return output

    def _label_7(self, tagging):
        tagging = tagging.replace(",", "").replace("∼", "~")
        regex = r"\d+"
        wave_regex = r"\d+~\d+\D*"
        hyphen_regex = r"\d+-\d+\D"
        output = tagging[:]

        # ~처리
        wave_match = re.search(wave_regex, output)
        if wave_match:
            start, end, char = re.findall(r"(\d+)~(\d+)(\D+)", wave_match.group())[0]

            # 한->하나, 두->둘, 세->셋, 네->넷
            for s, e in zip(start, end):
                num_words = self.number_to_kor2(s)
                output = output.replace(s, num_words)

            output = output.replace("~", "에서 ")

        # -처리
        if re.search(hyphen_regex, output):
            output = output.replace("-", "에서 ")

        num = re.findall(regex, output)
        for n in num:
            if n == '0':
                output = output.replace(n, '영', 1)
            else:
                num_words = self.number_to_kor(n)
                output = output.replace(n, num_words, 1)

        output = output.replace("~", "에서 ").replace("-", " ")

        return output

    def _label_8(self, tagging):
        tagging = tagging.replace(",", "").replace("∼", "~")
        regex = r"\d+"
        wave_regex = r"\d+~\d+\D*"
        hyphen_regex = r"\d+\d+\D"
        output = tagging[:]

        # # ~ 앞뒤 숫자의 차이가 1인지 확인
        # wave_match = re.search(wave_regex, tagging)
        # if wave_match:
        #     start, end, char = re.findall(r"(\d+)~(\d+)(\D+)", wave_match.group())[0]
        #     char = self.remove_josa(char)
        #     output = output.replace("~", char.strip()+"에서 ")

        # -처리
        if re.search(hyphen_regex, output):
            output = output.replace("-", "에서 ")

        num = re.findall(regex, output)
        for n in num:
            if n == '0':
                output = output.replace(n, '영', 1)
            else:
                num_words = self.number_to_kor2(n)
                output = output.replace(n, num_words, 1)

        output = output.replace("~", "에서 ").replace("-", " ")

        return output

    def _label_9(self, tagging):
        regex = r"\d+\.\d+"
        score_regex = r"\d+.*-.*\d+|\d+.*:.*\d+"
        output = tagging[:]

        if re.search(regex, output):
            num = re.search(regex, output).group()

            # 할푼리
            decimal_part = num.split(".")
            baseball = ['할', '푼', '리']

            if decimal_part[0] == '0':
                output = output.replace("0.", "")
                decimal = list(decimal_part[1])
                for i in range(len(decimal)):
                    num_i = self.number_to_han(decimal[i])
                    if int(decimal[i]) > 0:
                        result = num_i + baseball[i]
                        output = output.replace(decimal[i], result, 1)
                    else:
                        output = output.replace(decimal[i], "")

            # 날짜
            else:
                num = num.replace(".", "", 1)
                output = output.replace(".", "", 1)

                for n in num:
                    num_words = self.number_to_han(n)
                    output = output.replace(n, num_words, 1)
        elif re.search(score_regex, output):
            regex = r"\d+"
            num_list = re.findall(regex, output)
            for n in num_list:
                if n == "0":
                    num_word = "영"
                else:
                    num_word = self.number_to_han(str(n))
                output = output.replace(str(n), num_word)
            output = output.replace(":", "대").replace("-", "대")
        else:
            return self._label_5(output)

        return output


if __name__ == '__main__':
    # data = pd.read_csv("C:/Users/admin/Desktop/IPA/data/159.숫자가 포함된 패턴 발화 데이터/utils/num_test.txt", delimiter="\t", header=None, names=['source', 'target'])
    label2num = Label2Num()
    print(label2num.generate("12월 30일"))
    # start_time = datetime.now()
    # correct, total = 0, 0
    # for i in range(len(data)):
    #     sentence = data['source'][i]
    #     if re.search(r'[A-Za-z]+|~|-|%', sentence):
    #         continue
    #     output = label2num.generate(sentence).replace(" ", "")
    #     target = data['target'][i].replace(" ", "")
    #
    #     total += 1
    #     if output == target:
    #         correct += 1
    #
    #     # else:
    #     #     print(output)
    #     #     print(target)
    #     #     break
    # time_elapsed = datetime.now() - start_time
    # print(correct/total*100, total)
    # print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    # num_data_points = len(data)
    # random_indices = random.sample(range(num_data_points), 100)
    #
    # df = pd.DataFrame()
    # sentence, outputs = [], []
    # for i in random_indices:
    #     if i < num_data_points:
    #         output = label2num.generate(data.iloc[i, 0])
    #
    #         sentence.append(data.iloc[i, 0])
    #         outputs.append(output)
    #
    # df['source'] = sentence
    # df['output'] = outputs
    #
    # df.to_excel("results/test.xlsx", index=False, encoding='utf-8-sig')

