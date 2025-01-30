import pandas as pd
from tqdm import tqdm
import json
from typing import List
import os
import pymysql
from functions import setup_logging, get_env_var
import logging

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
    logging.INFO("--------------ami서버에서 특허 데이터 데이터프레임으로 저장-----------------")
    try:
        connection = create_connection()
        save_path = "./data/kipris_ami"
        tables = {'Main_patent': "kipris_main_patent.csv",
            'MainClaim_patent': "kipris_claim_patent.csv"}  # table명: 저장할 파일 이름
        run(connection, save_path, tables)
    finally:
        connection.close()