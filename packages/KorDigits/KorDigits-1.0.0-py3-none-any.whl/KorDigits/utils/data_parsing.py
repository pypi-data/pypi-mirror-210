import os
import re
import pickle
import glob
from dataclasses import dataclass, fields
from sklearn.model_selection import train_test_split



class Numeric:
    def __init__(self, src_path: str):
        if not os.path.exists(src_path):
            print("path error")
        else:
            self.data_list = [x for x in glob.glob(src_path+"\*\*\*.txt")]

    def find_index(self, non_split_words, source):
        indexes = []
        for w in non_split_words:
            is_continue = False

            # index 찾기
            for s in range(len(source)):
                if w in source[s]:
                    indexes.append(s)

            # index 값이 전부 연속 값 인지 확인
            if len(indexes) > 2:
                for i in range(len(indexes) - 1):
                    if indexes[i + 1] - indexes[i] == 1:
                        is_continue = True
                    else:
                        is_continue = False

        return indexes, is_continue, len(indexes)

    def parse(self, data_list, write_file):
        all_data = []
        regex = "\u200b\n"
        all_string = ""
        all_word = ""
        p = re.compile(r"\[(.+)\](.+)")

        for file_path in data_list:
            with open(file_path, 'r', encoding="utf-8") as f:
                file = f.readlines()
                file = [re.sub(regex, "", x) for x in file]
                file = list(filter(None, file))

                # 입력 데이터 check
                check = [x.replace("\n", "").split(" : ")[0] for x in file]
                data = [x.replace("\n", "").replace("\t", " ").replace("  ", " ").split(" : ")[1] for x in file]
                for c in [check]:
                    assert  c[1] == 'scriptITN', f"{f} source 안맞음"
                    assert  c[2] == 'scriptTN', f"{f} target 안맞음"
                    assert  c[3] == 'scriptNumberWord', f"{f} source word 안맞음"
                for x in [data]:
                    new_source, new_target = "", ""
                    source = x[1]
                    target = x[2]
                    word = eval(x[3])   # source에서 num 단어
                    non_split_words = []

                    for w in word:
                        w = w.strip()
                        non_split_word = w.replace(" ", "")
                        non_split_words.append(non_split_word)
                        source = source.replace(w, non_split_word)
                    source = source.split(" ")

                    # []안에 있는 정답 숫자 단어
                    target_word = re.findall('\[(.*?)\]', target)

                    for t in target_word:
                        non_split_word = t.replace(" ", "")
                        target = target.replace(f"[{t}]", f"[{non_split_word}]")
                    target = target.split(" ")

                    if len(source) != len(target):
                        print("len error")
                        print(source, len(source))
                        print(target, len(target))
                        print(word)
                        print(x[1])
                        print(x[2])
                        print()
                        continue

                    # index값 찾기
                    indexes, is_continue, length = self.find_index(non_split_words, source)

                    # source에서 정답 단어
                    for i, index in enumerate(indexes):
                        # index 값이 전부 연속 일때 처리
                        if is_continue:
                            end = min(len(source), index+length)
                            start = max(0, index-length)
                            new_source = " ".join(source[start:end])
                            new_target = " ".join(target[start:end])

                            new_source = new_source.rstrip()
                            new_target = new_target.rstrip()

                            for w in non_split_words:
                                new_source = new_source.replace(w.replace(" ", ""), w)  # source 숫자 붙여 놓은 거 다시 띄어 쓰기

                            for t in target_word:
                                new_target = new_target.replace(t.replace(" ", ""), t)  # target 숫자 붙여 놓은 거 다시 띄어 쓰기

                            all_string += new_source + "\t" + new_target + "\n"
                            all_word += str(target_word) + "\n"
                            break

                        # 연속이 아니면
                        else:
                            if index > 0 and index < len(source) - 1:
                                new_source = " ".join(source[index - 1 : index + 2])
                                new_target = " ".join(target[index - 1: index + 2])
                            elif index < 1 and index < len(source) - 1:
                                new_source = " ".join(source[index:index + 2])
                                new_target = " ".join(target[index:index + 2])
                            elif index > 0 and index >= len(source) - 1:
                                new_source = " ".join(source[index-2:])
                                new_target = " ".join(target[index-2:])
                            else:
                                new_source = " ".join(source[:])
                                new_target = " ".join(target[:])

                            new_source = new_source.rstrip()
                            new_target = new_target.rstrip()

                            for w in word:
                                new_source = new_source.replace(w.replace(" ", ""), w)  # source 숫자 붙여 놓은 거 다시 띄어 쓰기

                            for t in target_word:
                                new_target = new_target.replace(t.replace(" ", ""), t)  # target 숫자 붙여 놓은 거 다시 띄어 쓰기

                            new_target_word = re.findall('\[(.*?)\]', new_target)

                            if new_target_word:
                                all_string += new_source + "\t" + new_target + "\n"
                                all_word += str(new_target_word) + "\n"
                            else:
                                pass
                                # print(x[2], word)
                                # print(x[1], indexes)
                                # print()



        with open(f"../data/{write_file}.txt", 'w', encoding='utf-8') as f:
            f.writelines(all_string)
        with open(f"../data/{write_file}_target.txt", 'w', encoding='utf-8') as f:
            f.writelines(all_word)


    def data_split(self, save_path:str):
        with open(f"{save_path}.txt", 'r', encoding='utf-8') as p:
            file = p.readlines()
            print(len(file))
            train, test = train_test_split(file, test_size=0.3, random_state=42)
            val, test = train_test_split(test, test_size=0.5, random_state=42)

        with open(f'{save_path}_target.txt', 'r', encoding='utf-8') as p:
            file = p.readlines()
            print(len(file))
            train_y, test_y = train_test_split(file, test_size=0.3, random_state=42)
            val_y, test_y = train_test_split(test_y, test_size=0.5, random_state=42)

        train_file = open('../data/special_window_train.txt', 'w', encoding='utf-8')
        val_file = open('../data/special_window_val.txt', 'w', encoding='utf-8')
        test_file = open('../data/special_window_test.txt', 'w', encoding='utf-8')

        trainy_file = open('../data/special_window_train_target.txt', 'w', encoding='utf-8')
        valy_file = open('../data/special_window_val_target.txt', 'w', encoding='utf-8')
        testy_file = open('../data/special_window_test_target.txt', 'w', encoding='utf-8')

        train_file.writelines(train)
        val_file.writelines(val)
        test_file.writelines(test)

        trainy_file.writelines(train_y)
        valy_file.writelines(val_y)
        testy_file.writelines(test_y)

        train_file.close()
        val_file.close()
        test_file.close()

        trainy_file.close()
        valy_file.close()
        testy_file.close()

if __name__ == '__main__':
    num = Numeric(src_path="../../../159.숫자가 포함된 패턴 발화 데이터/1.Training/원천데이터")
    # num.parse(num.data_list, write_file="../data/special_window_train")
    # num.data_split(save_path="../data/special_window_train")