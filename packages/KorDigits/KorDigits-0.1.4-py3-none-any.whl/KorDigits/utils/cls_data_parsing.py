import os
import re
import pickle
import glob
from dataclasses import dataclass, fields
from collections import Counter

import pandas as pd
from sklearn.model_selection import train_test_split
from typing import List
import torch

class Numeric:
    def __init__(self, src_path: str):
        if not os.path.exists(src_path):
            print("path error")
        else:
            self.data_list = [x for x in glob.glob(src_path+"\*\*\*.txt")]

    # 입력 데이터 체크
    def check_input(self, file, f):
        # 입력 데이터 check
        check = [x.replace("\n", "").split(" : ")[0] for x in file]
        data = [x.replace("\n", "").replace("\t", " ").replace("  ", " ").split(" : ")[1] for x in file]
        for c in [check]:
            assert c[1] == 'scriptITN', f"{f} source 안맞음"
            assert c[2] == 'scriptTN', f"{f} target 안맞음"
            assert c[3] == 'scriptNumberWord', f"{f} source word 안맞음"

        return data

    # email 형식 체크
    def check_email(self, email, is_email=False, mode="split"):
        if mode == "split":
            email_regex = re.compile(r'(\w+)\s*@\s*(\w+)\s*\.\s*(\w+)')
            matched = email_regex.search(email)
            if matched:
                is_email=True
                username = matched.group(1)
                domain = matched.group(2)
                extension = matched.group(3)
                email = email.replace(matched.group(), f"{username} @ {domain} . {extension}")
        elif mode == "combi":
            email_regex = re.compile(r'(\w+)\s* @ \s*(\w+)\s* \. \s*(\w+)')
            matched = email_regex.search(email)
            if matched:
                is_email=True
                username = matched.group(1)
                domain = matched.group(2)
                extension = matched.group(3)
                email = email.replace(matched.group(), f"{username}@{domain}.{extension}")
        return email, is_email

    def split_sentence(self, source:str, target:str, word:List, split_words) -> (List, List, List, List):
        num_pattern = re.compile(r"[0-9]+")
        notNum_index = []
        target_notNum = 0
        target_word = [] # 최종 target_word

        # source tagging matching
        for i, w in enumerate(word):
            w = w.strip()
            # 숫자 태그만 입력으로 받기
            num_matched = num_pattern.search(w)
            non_split_word = w.replace(" ", "") # 띄어쓰기 없애기(나중에 split 할 때를 위해)
            source = source.replace(w, non_split_word)

            # 숫자 아닌 태그 index 저장
            if not num_matched:
                notNum_index.append(i)
                continue
            split_words.append(w)
        source = source.split(" ")

        # []안에 있는 정답 숫자 단어
        target_words = re.findall('\[(.*?)\]', target)
        for i, t in enumerate(target_words):
            non_split_word = t.replace(" ", "")
            target = target.replace(f"[{t}]", f"[{non_split_word}]")

            # 숫자 아닌 태거 target에서 제외
            if len(notNum_index) > target_notNum:
                if target_notNum == notNum_index[target_notNum]:
                    target = target.replace(f"[{non_split_word}]", f"{non_split_word}")
                    target_notNum += 1
        target = target.split(" ")

        target_word = [word for i, word in enumerate(target_words) if i not in notNum_index]

        return source, target, target_word, split_words

    # scriptNumberWord index 찾기, 연속 확인
    def find_index(self, split_words, source):
        indexes = []
        is_continue = False
        for w in split_words:
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

    # index 제외 대괄호 삭제, source index tagging <N> 감싸기
    def remove_bracket(self, source, target, index, split_words, i):
        new_target = []
        new_source = source[:]
        n_target = split_words[i]
        # source 현재 봐야할 부분 <N> </N> 태깅
        new_source[index] = new_source[index].replace(n_target.replace(" ", ""), f'<N>{n_target}</N>')
        if '<N>' not in new_source[index]:
            new_source[index] = new_source[index].replace(new_source[index], f'<N>{new_source[index]}</N>')
        split_words = [x.replace(x, f"<N>{x}</N>") for x in split_words]

        # target에서 index제외 대괄호 지우기
        for i, word in enumerate(target):
            if i == index or '[' not in word:
                new_target.append(word)
            else:
                new_target.append(word.replace('[', '').replace(']', ''))

        return new_source, n_target, new_target, split_words

    def parse(self, data_list, write_file):
        all_data = []
        regex = "\u200b\n"
        all_string = ""
        all_word = ""
        df = pd.DataFrame(columns=['Source', 'Target', "Tagging"])
        for file_path in data_list:
            with open(file_path, 'r', encoding="utf-8") as f:
                file = f.readlines()
                file = [re.sub(regex, "", x) for x in file]
                file = list(filter(None, file))

                # 입력 데이터 체크
                data = self.check_input(file, f)

                for x in [data]:
                    new_source, new_target = "", ""
                    source = x[1]
                    target = x[2]
                    word = eval(x[3])   # source에서 num 단어
                    split_words = []

                    # email 형식 확인
                    source, is_email = self.check_email(source)

                    # source, target 띄어쓰기 단위로 split
                    # (원본 문장, 타겟 문장, source에서 num단어, 리스트)
                    # -> (splited 원본 리스트, splited 타겟 리스트, 타겟 문장의 []단어 리스트, source tagging 숫자만 들어있는 단어 리스트)
                    source, target, target_word, split_words = self.split_sentence(source=source, target=target, word=word, split_words=split_words)
                    non_split_words = [x.replace(" ", "") for x in split_words] # 띄어쓰기 없애기

                    # source, target 길이 확인
                    if len(source) != len(target):
                        print("len error")
                        print(source, len(source))
                        print(target, len(target))
                        print(word)
                        print(x[1])
                        print(x[2])
                        print()
                        continue

                    # email 형식 붙이기
                    if is_email:
                        source = " ".join(source)
                        source, _ = self.check_email(source, mode="combi")
                        source = source.split()

                    # index값 찾기
                    indexes, is_continue, length = self.find_index(non_split_words, source)

                    # source에서 정답 단어
                    for i, index in enumerate(indexes):
                        # tagger는 여러갠데 scriptNumberWord가 하나일 때 제외
                        if len(indexes) != len(split_words):
                            continue

                        # index 제외 대괄호 삭제
                        # (원본 리스트, 타겟 리스트, tagger index, tagging 리스트, 현재 index)
                        # ->(<N> 태깅된 source 리스트, source tagging 단어, 현재 index 제외 대괄호 지운 타겟 리스트, <N> 태깅된 source tagging 리스트)
                        n_sentence, n_target, remove_bracket_target, new_split_word = self.remove_bracket(source, target, index, split_words, i)

                        # index 값이 전부 연속 일때 처리
                        if is_continue:
                            end = min(len(source), index+length)
                            start = max(0, index-length)
                            new_source = " ".join(n_sentence[start:end])
                            new_target = " ".join(remove_bracket_target[start:end])

                            new_source = new_source.rstrip()
                            new_target = new_target.rstrip()


                            for w in new_split_word:
                                new_source = new_source.replace(w.replace(" ", ""), w)  # source 숫자 붙여 놓은 거 다시 띄어 쓰기

                            # for t in target_word:
                            #     new_target = new_target.replace(t.replace(" ", ""), t)  # target 숫자 붙여 놓은 거 다시 띄어 쓰기
                            target_words = re.findall('\[(.*?)\]', new_target)
                            if len(target_words) == 1:
                                df = df.append(
                                    {'Source': new_source.replace("\t", " "), 'Target': new_target.replace("\t", " "),
                                      'Tagging': str(target_words[0])}, ignore_index=True)
                            else:
                                pass

                        # 연속이 아니면
                        else:
                            if index > 0 and index < len(source) - 1:
                                new_source = " ".join(n_sentence[index - 1 : index + 2])
                                new_target = " ".join(remove_bracket_target[index - 1: index + 2])
                            elif index < 1 and index < len(source) - 1:
                                new_source = " ".join(n_sentence[index:index + 2])
                                new_target = " ".join(remove_bracket_target[index:index + 2])
                            elif index > 0 and index >= len(source) - 1:
                                new_source = " ".join(n_sentence[index-2:])
                                new_target = " ".join(remove_bracket_target[index-2:])
                            else:
                                new_source = " ".join(n_sentence[:])
                                new_target = " ".join(remove_bracket_target[:])

                            new_source = new_source.rstrip()
                            new_target = new_target.rstrip()

                            for w in new_split_word:
                                new_source = new_source.replace(w.replace(" ", ""), w)  # source 숫자 붙여 놓은 거 다시 띄어 쓰기

                            # for t in target_word:
                            #     new_target = new_target.replace(t.replace(" ", ""), t)  # target 숫자 붙여 놓은 거 다시 띄어 쓰기

                            target_words = re.findall('\[(.*?)\]', new_target)

                            if len(target_words) == 1:
                                df = df.append(
                                    {'Source': new_source.replace("\t", " "), 'Target': new_target.replace("\t", " "),
                                     'Tagging': str(target_words[0])}, ignore_index=True)
                            else:
                                pass

        df.to_csv(f"../data/{write_file}.txt", index=False, header=False, sep="\t", encoding='utf-8')
        # with open(f"../data/{write_file}.txt", 'w', encoding='utf-8') as f:
        #     f.writelines(all_string)

    def error_correct(self, file):
        df = pd.read_csv(file, encoding='utf-8', delimiter="\t")
        label_regex = r"<N>\d+.*~"
        # 아닌 부분 추출
        extract_df = df[df['source'].str.contains(label_regex) & ~df['label'].isin([10])]
        print(extract_df)
        extract_df.to_excel('../data/extract_error.xlsx', index=False, encoding='utf-8-sig')

    def concat_error_correct(self, origin_file, error_file):
        origin = pd.read_csv(origin_file, encoding='utf-8-sig', delimiter="\t")
        error = pd.read_excel(error_file)

        merged_df = pd.merge(origin, error, on='source', how='left')
        merged_df['label_x'] = merged_df['label_y'].fillna(merged_df['label_x']).astype(int)
        result_df = merged_df[['source', 'label_x', 'tagging_x']]
        result_df.columns = ['source', 'label', 'tagging']

        # print(result_df)
        result_df.to_csv("../data/correct_refine_cls_data.txt", index=False, encoding='utf-8', sep="\t")
    def _search_regex(self, trg):
        target_words = re.findall('\[(.*?)\]', str(trg))

        label0_regex = r"\w+시\w+분|\w+시간\w+분" # rank 1
        label1_regex = r"텐|일레븐|투엘브|투웰브|트웰브|트웬티|트웨니|투에니|투애니|썰틴|서틴|써틴|식스틴|투웬티|투웨니|써티|써어티|서티|써리|포티|씩스티|식스티|세븐티|에잇티|나인티" # rank 2
        label2_regex = r"일월|이월|삼월|사월|오월|유월|칠월|팔월|구월|시월|십일월|십이월"  # 월 단위 rank 3
        label3_regex = r"(이|삼|사|오|육|칠|팔|구)?십(일|이|삼|사|오|육|칠|팔|구)?|(이|삼|사|오|육|칠|팔|구)?백(일|이|삼|사|오|육|칠|팔|구)?|(이|삼|사|오|육|칠|팔|구)?벡(일|이|삼|사|오|육|칠|팔|구)?|(이|삼|사|오|육|칠|팔|구)?천(일|이|삼|사|오|육|칠|팔|구)?|(이|삼|사|오|육|칠|팔|구)?만(일|이|삼|사|오|육|칠|팔|구)?"  # 4
        label4_regex = r"제로|원|투|쓰리|포|파이브|식스|세븐|쎄븐|에잇|나인" # rank 7
        label5_regex = r"영|공|일|이|삼|사|오|육|칠|팔|구" # rank 5
        label6_regex = r"서너|예닐곱|너덧|네다섯|대엿|대여섯|일고여덟|엳아홉" # rank 10
        label7_regex = r"한|두|세|네|스무" # rank 8
        label8_regex = r"하나|둘|셋|넷|다섯|여섯|일곱|여덟|아홉|열|스물|서른|마흔|쉰|예순|일흔|여든|아흔" # rank 9

        label0_compile = re.compile(label0_regex)
        label1_compile = re.compile(label1_regex)
        label2_compile = re.compile(label2_regex)
        label3_compile = re.compile(label3_regex)
        label4_compile = re.compile(label4_regex)
        label5_compile = re.compile(label5_regex)
        label6_compile = re.compile(label6_regex)
        label7_compile = re.compile(label7_regex)
        label8_compile = re.compile(label8_regex)

        if target_words:
            label0_matched = label0_compile.search(target_words[0])
            label1_matched = label1_compile.search(target_words[0])
            label2_matched = label2_compile.search(target_words[0])
            label3_matched = label3_compile.search(target_words[0])
            label4_matched = label4_compile.search(target_words[0])
            label5_matched = label5_compile.search(target_words[0])
            label6_matched = label6_compile.search(target_words[0])
            label7_matched = label7_compile.search(target_words[0])
            label8_matched = label8_compile.search(target_words[0])

            # 예외 처리 (오전, 오후)
            if "오전" in target_words[0] or "오후" in target_words[0]:
                if label0_matched:
                    return 0
                elif label7_matched:
                    return 7
                elif label8_matched:
                    return 8
                elif label5_matched:
                    return 5
                else:
                    print(f"error [오전 오후]: {trg} -- {target_words[0]}")
                    return 11

            if label0_matched:
                return 0
            elif label1_matched:
                return 1
            elif label2_matched:
                return 2
            elif label3_matched:
                if label7_matched:
                    return 7
                elif label8_matched:
                    return 8
                return 3
            elif label4_matched:
                if label5_matched:
                    return 5
                return 4
            elif label5_matched:
                if '일곱' in target_words[0]:
                    return 8
                return 5
            elif label6_matched:
                return 6
            elif label7_matched:
                return 7
            elif label8_matched:
                return 8

            else:
                print(f"error: {trg} -- {target_words[0]}")
                return 11
        else:
            print(f"target error: {trg} -- {target_words}")
            return 11

    def convert_label(self, file:str):
        data = pd.read_csv(file, header=None, delimiter="\t", names=["src", "label", "tagging"])
        print(data.shape)

        data['label'] = data['label'].apply(self._search_regex)
        print(data[data['label'] == 11.0])
        data.drop(data[data['label'] == 11.0].index, inplace=True)
        print(data['label'].unique())
        print(data.shape)
        print(Counter(data['label']))
        data.to_csv("../data/cls_label_drop.txt", index=False, encoding='utf-8', sep="\t", header=False)
        data.to_csv("../data/cls_label_drop.csv", index=False, encoding='utf-8-sig', sep="\t")


    def data_split(self, save_path:str):

        df = pd.read_csv(f"{save_path}.txt", encoding='utf-8', delimiter="\t")
        train, test = train_test_split(df, test_size=0.2, random_state=20, stratify=df['label'])
        val, test = train_test_split(test, test_size=0.5, random_state=20, stratify=test['label'])

        print(Counter(train['label']))
        print(Counter(val['label']))
        print(Counter(test['label']))

        train.to_csv("../data/cls_refine_train.txt", header=False, sep="\t", encoding="utf-8", index=False)
        val.to_csv("../data/cls_refine_val.txt", header=False, sep="\t", encoding="utf-8", index=False)
        test.to_csv("../data/cls_refine_test.txt", header=False, sep="\t", encoding="utf-8", index=False)




if __name__ == '__main__':
    """
        1. source, target의 tagging 단어 띄어쓰기 지우고 띄어쓰기 단위로 split
        2. tagging단어 index 찾기
        3. source에서 tagging 단어 <N> 감싸기
        4. target에서 tagging 단어 제외 대괄호 지우기
        5. tagging단어 index 앞 뒤 한 어절씩 자르기
        6. tagging단어 분류
    """
    num = Numeric(src_path="../../../159.숫자가 포함된 패턴 발화 데이터/1.Training/원천데이터")
    # num.parse(num.data_list, write_file="../data/whitespace")
    # num.convert_label(file="../data/cls_token_union.txt")
    num.error_correct(file='../data/correct_refine_cls_data.txt')
    # num.concat_error_correct(origin_file="../data/correct_refine_cls_data.txt", error_file="../data/extract_error.xlsx")

    # txt = pd.read_csv("../data/correct_cls_data.csv", encoding='utf-8-sig')
    # txt.to_csv("../data/correct_cls_data.txt", index=False, encoding='utf-8', sep="\t")

    # num.data_split(save_path="../data/correct_refine_cls_data")