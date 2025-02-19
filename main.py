import os, sys
import read_ami_kipris_data
import create_ner_data_using_gpt
import data_preprocessing

if __name__ == "__main__":
    
    read_ami_kipris_data.main()   
    
    #TODO: 차후 수정 --------------------------------
    data_preprocessing.main()  #TODO: 이 함수 수정 해야 됨
    create_ner_data_using_gpt.main()
    
    
    
    