import os, sys
import read_ami_kipris_data
import create_ner_data_using_gpt
import data_preprocessing

if __name__ == "__main__":
    
    read_ami_kipris_data.main()   
    
    #TODO: 코드 수정이 필요함--------------------------------
    data_preprocessing.main()  
    create_ner_data_using_gpt.main()
    
    
    
    