import pandas as pd
from tqdm import tqdm
import os, re
from transformers import ElectraModel, ElectraTokenizer
from dotenv import load_dotenv
import logging

load_dotenv()

# csv 파일 읽기 -------------------------------------------------------------------------------
def read_csv(path: str)-> pd.DataFrame:
    for encoding in ['utf-8', 'euc-kr', 'cp949']:
        try:
            df = pd.read_csv(path, encoding=encoding)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise Exception(f"{path}: {e}")
            
    return pd.DataFrame()
    
# "1."" -> "제 1항" ---------------------------------------------------------------------------
# 번호만 있을 뿐, 문장 내에는 문제 되지 않음. ex: 2번 청구항에서 "제 1 항에 있어서.."라고 시작함. 
# def claim_number_replace(df: pd.DataFrame, text: str)-> pd.DataFrame:
#     def text_replace(text:str)->str:
#         new_text = re.sub(r"(\d)\.", lambda match: f"제 {match.group(1)} 항.", text)
#         return new_text
#     df['문장'] = df['문장'].apply(lambda sen: text_replace(sen))

#     return df

# 청구항에서 의미없는 청구항 번호 삭제
def delete_claim_number(df: pd.DataFrame, col: str)-> pd.DataFrame:
    def text_replace(text:str)->str:
        new_text = re.sub(r"(\d)\. ", " ", text, count=1)
        new_text = re.sub(r"(\d)\. ", "\n", new_text)
        return new_text.strip()

    df[col] = df[col].apply(lambda sen: text_replace(sen))

    return df

# 문장 토크나이징 -----------------------------------------------------------------------------
def tokenizing_sentence(df:pd.DataFrame, sen_col: str, new_col: str)-> list:
    model_path = "./KIPI-KorPatELECTRA/KorPatELECTRA/PT"
    tokenizer = ElectraTokenizer.from_pretrained(model_path)
    def tokenizing(sen: str)-> str:
        tokens = tokenizer.tokenize(sen)
        tokens = ["[CLS]"] + tokens + ["[SEP]"]

        return tokens
    
    df[new_col] = df[sen_col].apply(lambda data: tokenizing(data))
    return df

# 로깅 설정 ----------------------------------------------------------------------------------------------
def setup_logging(log_file: str = "log.txt"):
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",  
        handlers=[
            logging.FileHandler(log_file),  # mode='w': 파일에 로그 저장, mode 기본은 append
            logging.StreamHandler()  # 콘솔 출력 (필요 없으면 제거 가능)
        ]
    )
    
# 환경 변수 값 가져오기 ---------------------------------------------------------------------------------
def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value:
        logging.error(f"환경 변수 {key} 없음")
        raise ValueError(f"환경 변수 {key} 없음")
    return value