import pandas as pd
from tqdm import tqdm
import json
from typing import List
from dotenv import load_dotenv
import os
import pymysql
import logging

# 로깅 설정 ----------------------------------------------------------------------------------------------
def setup_logging(log_file: str = "read_ami_kipris_data_log.txt"):
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",  
        handlers=[
            logging.FileHandler(log_file, mode='w'),  # 파일에 로그 저장, mode 기본은 append
            logging.StreamHandler()  # 콘솔 출력 (필요 없으면 제거 가능)
        ]
    )

# mysql 서버 connection 생성 ----------------------------------------------------------------------------------
def create_connection()-> pymysql.connections.Connection:
    try:
        return pymysql.connect(
                host=get_env_var('IP_170'),  
                user=get_env_var('USER_170'),          
                port=int(get_env_var('PORT_170')),
                database=get_env_var('DATABASE_170'),
                password=get_env_var('PASSWORD_170')
            )
    except Exception as e:
        logging.ERROR(f"mysql 서버 connection 에러, {e}")
        raise ConnectionError(f"mysql 서버 connection 에러, {e}")

# 환경 변수 값 가져오기 ---------------------------------------------------------------------------------
def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value:
        logging.ERROR(f"환경 변수 {key} 없음")
        raise ValueError(f"환경 변수 {key} 없음")
    return value

# mysql 서버에 쿼리 날리기 -----------------------------------------------------------------------------
def select_query(table_name: str, connection: pymysql.connections.Connection)-> pd.DataFrame:
    query = f""" 
        SELECT *
        FROM {table_name};
    """
    
    try: 
        data_df = pd.read_sql(query, con=connection)
        return data_df
    except Exception as e:
        logging.ERROR(f"select 쿼리 에러, {e}")
        return pd.DataFrame()

# 데이터 저장 ------------------------------------------------------------------------------------------
def save_data(data: pd.DataFrame, file_path: str, filename: str):
    try:
        os.makedirs(file_path, exist_ok=True)
        data.to_csv(os.path.join(file_path, filename))
    except Exception as e:
        logging.ERROR(f"{filename} 저장 에러, {e}")
    
# ----------------------------------------------------------------------------------------------------
def run(connection: pymysql.connections.Connection, save_path: str, tables: dict):
    for table, filename in tables.items():
        logging.INFO(f"{table} 읽기 시작")
        df = select_query(table, connection)
        if df.empty:
            continue
        
        logging.INFO(f"{table} 건수: ", len(df))
        logging.INFO(f"{table} 저장 시작")
        save_data(df, save_path, filename)

# main -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    setup_logging()
    
    try:
        connection = create_connection()
        save_path = "./data/kipris_ami"
        tables = {'Main_patent': "kipris_main_patent.csv",
            'MainClaim_patent': "kipris_claim_patent.csv"} 
        run(connection, save_path, tables)
    finally:
        connection.close()