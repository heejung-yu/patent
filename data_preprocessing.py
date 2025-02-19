import pandas as pd
from tqdm import tqdm
from typing import List
import os, re
from functions import *
import logging

def read_main_claim_file(data_path: str)-> pd.DataFrame:
    def delete_col(df: pd.DataFrame, col:str='Unnamed: 0')-> pd.DataFrame:
        try:
            df = df.drop(columns=[col])
            return df
        except:
            return df
        
    for filename in tqdm(os.listdir(data_path)):
        if "claim" in filename:
            claim_df = read_csv(os.path.join(data_path, filename))
        else:
            main_df = read_csv(os.path.join(data_path, filename))
    
    claim_df = delete_col(claim_df); main_df = delete_col(main_df)
    
    return claim_df, main_df

def calculate_cpc_statistics(main_df: pd.DataFrame):
    cpc_dict = {}
    errorData = []

    for _, data in tqdm(main_df.iterrows(), total=len(main_df)):
        try:
            cpc_str = data['listCPC']  # None값인 경우도 있음
            cpc_str = cpc_str.replace("[", ""); cpc_str = cpc_str.replace("]", "")
        except AttributeError:
            continue
        except Exception as e:
            errorData.append([data['applicationNumber'], e])

        cpc_list = [cpc.strip() for cpc in cpc_str.split(",")]
        split_cpc_list = [cpc[:4] for cpc in cpc_list]

        
        # for cpc in set(split_cpc_list):
        #     if cpc[0] == 'G':
        #         if cpc not in cpc_dict: cpc_dict[cpc] = 1
        #         else: cpc_dict[cpc]+=1


target_patent_number = []
errorData = []

for _, data in tqdm(main_df.iterrows(), total=len(main_df)):
    try:
        cpc_str = data['listCPC']  # None값인 경우도 있음
        cpc_str = cpc_str.replace("[", ""); cpc_str = cpc_str.replace("]", "")
    except AttributeError:
        continue
    except Exception as e:
        errorData.append([data['applicationNumber'], e])

    cpc_list = [cpc.strip() for cpc in cpc_str.split(",")]
    split_cpc_list = [cpc[:4] for cpc in cpc_list]

    for cpc in set(split_cpc_list):
        if cpc[:4] == "G16Y":
            patentNumber = data['applicationNumber']
            target_patent_number.append(patentNumber)
            break
        

claim_df = claim_df[claim_df['applicationNumber'].isin(target_patent_number)]
claim_df = claim_df.reset_index(drop=True)  
claim_df.head()


# 불용어 제거
def delete_word(text: str)->str:
    delete_word = ["삭제", "<P INDENT='14' ALIGN='JUSTIFIED'>", "</P>", "\n"]
    for delete in delete_word:
        text = text.replace(delete, "", -1).strip()
    return text

claim_df['claim'] = claim_df['claim'].apply(lambda data: delete_word(data))
claim_df

#TODO: functions.py의 delete_claim_number 함수로 교체
def text_replace(text:str)->str:
    new_text = re.sub(r"(\d)\. ", " ", text, count=1)
    new_text = re.sub(r"(\d)\. ", "\n", new_text)
    return new_text.strip()

claim_df['claim'] = claim_df['claim'].apply(lambda data: text_replace(data))
claim_df

claim_df2 = claim_df.copy()
claim_df2 = claim_df2.assign(sentence=claim_df2['claim'].str.split("\n")).explode("sentence").reset_index(drop=True) # 청구항 문장 단위로 분리
claim_df2 = claim_df2[claim_df2['sentence'].apply(lambda data: True if len(data)>1 else False)]  # 공백 제거
claim_df2 = claim_df2.assign(len_sen=claim_df2['sentence'].apply(lambda data: len(data)))
claim_df2 = claim_df2.drop(columns=['claim'])
claim_df2

#TODO: functions.py 수정

model_path = "../KIPI-KorPatELECTRA/KorPatELECTRA/PT"
tokenizer = ElectraTokenizer.from_pretrained(model_path)
def tokenizing(sen: str)-> str:
    tokens = tokenizer.tokenize(sen)
    tokens = ["[CLS]"] + tokens + ["[SEP]"]

    return ", ".join(token for token in tokens)
    
target_df['tokens'] = target_df['sentence'].apply(lambda data: tokenizing(data))
target_df

if __name__ == "__main__":
    setup_logging()
    logging.INFO("--------------특허 데이터 전처리-----------------")
    
    save_path = "../data/target"
    data_path = "../data/kipris_ami"
    
    claim_df, main_df = read_main_claim_file(data_path)