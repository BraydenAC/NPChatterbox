from huggingface_hub import login
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

import torch
import os
class Model:
    
    #Testing function to see if connection works
    def print_test():
        print("Model object confirmed callable!")
    
    #Calling this to retrieve and submit huggingface credentials saved in .env
    def log_into_hf():
        load_dotenv()
        token = os.getenv('HF_TOKEN')
        assert token, "Environment variable 'token' is not set"
        login(token)
    
    #Loads the tokenizer associated with the selected hf model
    def load_tokenizer(model_name: str):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token
        return tokenizer
    
    #Loads the hf model, applying lora-finetuned attention heads if passed via args
    def load_model(model_name: str, tokenizer: AutoTokenizer, model_hyperparams: dict = {}, adapter_dir: str = ""):
        model = None
        if adapter_dir == "":
            #Load the base model.
            model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                device_map="auto", 
                pad_token_id=tokenizer.eos_token_id, 
                **model_hyperparams
            )
        else:
            #Use the same conf as when finetuning?
            bitsandbytes_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )

            #Load base model, but with config for quantization
            base_model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                device_map="auto", 
                pad_token_id=tokenizer.eos_token_id, 
                quantization_config=bitsandbytes_config,
                **model_hyperparams
            )

            #Take base model, and merge adapters to it.
            model = PeftModel.from_pretrained(base_model, adapter_dir)
        model.eval()
        
        if model != None:
            return model
        else:
            raise ValueError("Model Failed to initialize correctly in load_model function!")

    def call_model(content: str, model: AutoModelForCausalLM, tokenizer: AutoTokenizer):

        # Tokenize
        inputs = tokenizer(content, return_tensors="pt").to("cuda")
        #Generate
        output = model.generate(**inputs)
        return tokenizer.decode(output[0], skip_special_tokens=True)
