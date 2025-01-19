import pandas as pd
from tqdm import tqdm
import os, re
from transformers import ElectraModel, ElectraTokenizer


# csv 파일 읽기 -------------------------------------------------------------------------------
def read_csv(path: str)-> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(e)
        df = pd.DataFrame()
    return df

# "1."" -> "제 1항" ---------------------------------------------------------------------------
# 번호만 있을 뿐, 문장 내에는 문제 되지 않음. ex: 2번 청구항에서 "제 1 항에 있어서.."라고 시작함. 
# def claim_number_replace(df: pd.DataFrame, text: str)-> pd.DataFrame:
#     def text_replace(text:str)->str:
#         new_text = re.sub(r"(\d)\.", lambda match: f"제 {match.group(1)} 항.", text)
#         return new_text
#     df['문장'] = df['문장'].apply(lambda sen: text_replace(sen))

#     return df

# 청구항에서 의미없는 청구항 번호 삭제
def delete_claim_number(df: pd.DataFrame, text: str)-> pd.DataFrame:
    def text_replace(text:str)->str:
        new_text = re.sub(r"(\d)\. ", "", text)
        return new_text.rstrip()

    df['문장'] = df['문장'].apply(lambda sen: text_replace(sen))

    return df

# 문장 토크나이징 -----------------------------------------------------------------------------
def tokenizing_sentence(df:pd.DataFrame, sen: str)-> list:
    model_path = "./KIPI-KorPatELECTRA/KorPatELECTRA/PT"
    tokenizer = ElectraTokenizer.from_pretrained(model_path)
    def tokenizing(sen: str)-> str:
        tokens = tokenizer.tokenize(sen)
        tokens = ["[CLS]"] + tokens + ["[SEP]"]

        return tokens
    
    df['토큰'] = df['문장'].apply(lambda data: tokenizing(data))
    return df