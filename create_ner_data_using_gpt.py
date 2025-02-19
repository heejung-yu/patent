import os, sys
from tqdm import tqdm
from functions import *
from transformers import ElectraModel, ElectraTokenizer
import openai




def create_query(sen: str, tokens: str)-> str:
    base_query = "너는 대한민국에서 가장 유능한 특허 전문가야. 특허 전문가로서 특허 청구항 일부인 아래 문장과 토큰을 보고, 특허 도메인에서 유의미한 값을 갖는 개체명을 찾아줘. 유의미한 개체명이 없는 경우 <None>이라고 답변해줘. 출력은 설명없이 개체명만 ", "로 이어서 출력해줘."
    result_query = f'{base_query}\n문장:{sen}\n토큰:{tokens}'
    return result_query

def get_chatGpt_res(query: str)->str:
    openai.api_key = get_env_var("GPT_API_KEY")
    model = 'gpt-4o'
    messages = [{
        "role": "system",
        "content": "You are the nation's top patent expert."
    }, {
        "role": "user",
        "content": query
    }]

    response = openai.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0.1  
    )
    answer = response.choices[0].message.content

    return answer

# tokens, bio 리스트 피기
result_df = data_df.copy()

def str_to_list(data: str)->list:
    result_list = [token.strip() for token in data.split(",")]
    return result_list

result_df['tokens'] = result_df['tokens'].apply(lambda data: str_to_list(data)) # 문자열을 리스트로 변경
result_df['entity'] = result_df['entity'].apply(lambda data: str_to_list(data))

model_path = "../KIPI-KorPatELECTRA/KorPatELECTRA/PT"
tokenizer = ElectraTokenizer.from_pretrained(model_path)
def tokenizing(sen: str)-> str:
    tokens = tokenizer.tokenize(sen)
    return tokens

def tag_entity(tokens, entities):
    bio_tags = ["O"] * len(tokens) 

    for entity in entities:
        entity_tokens = tokenizing(entity)  
        entity_len = len(entity_tokens)

        for i in range(len(tokens) - entity_len + 1):
            if tokens[i:i+entity_len] == entity_tokens:  
                bio_tags[i] = "B"  
                for j in range(1, entity_len):
                    bio_tags[i + j] = "I"  
    
    return bio_tags

def bio_tagging(row):
    return tag_entity(row['tokens'], row['entity'])
    
result_df['bio'] = None
result_df['bio'] = result_df.apply(bio_tagging, axis=1)


expanded_df = result_df.explode(["tokens", "bio"]).reset_index(drop=True) # 리스트를 행으로 확장

if __name__ == "__main__":
    setup_logging()
    logging.INFO("--------------ami서버에서 특허 데이터 데이터프레임으로 저장-----------------")
    data_path = "./data/target/llm프롬포팅용데이터.csv"
    
    data_df = read_csv(data_path)
    data_df = data_df.drop(columns=['seq', 'len_sen'])
    data_df = data_df.assign(sen_idx=range(1, len(data_df) + 1)) #TODO: 나중에 데이터 분리할 때부터 idx 추가하는 걸로 변경