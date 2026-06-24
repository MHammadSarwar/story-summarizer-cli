#it is a python based cli tool where we will provide the path of the story and will get its summary
#flow is like we sent the story in the form of string to a llm from hfhub using inference client 
#for live inference, before that first we need to read the text file, then we name the file where we
#want our summary to be stored as stem_summary.suffix, after that we have to write the response 
#generated from llm to a file 



from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from pathlib import Path
import os
import sys
from huggingface_hub.utils import HfHubHTTPError
import argparse
from db import save_summary,init_db,get_history
from datetime import datetime





load_dotenv()
model=InferenceClient(provider="featherless-ai")


def get_response(content,max_words):
    if not isinstance(content,str):
        print("Error: Input content must be a string.Try again with some valid string.")
        return None
    
    messages=[{"role":"user","content":f"""Write the summary of the given content with no 
               more than {max_words} words and the each new sentence should start with a 
               new line\n""" + content}]
    try:
        response=model.chat_completion(
            model="google/gemma-2-2b-it",
            messages=messages,
            max_tokens=int(max_words * 1.3 )   
        )
        
        if response and getattr(response,'choices',None):
            summary=response.choices[0].message.content
            return summary
        else:
            print("Error: Received an empty Payload from LLM provider. Check your LLM Service")
            return None
        
    except HfHubHTTPError as E:
        print(f"API HTTP Error occured (Error code: {E.response.status_code})")
        return None

    except (IndexError,TypeError,AttributeError) as E:
        print("Error occured while parsing the LLM response, most probably the LLM response to your query was empty")
        print("Parse Error:",E)
        return None

def read_textfile(filepath):
    try:
        with open(filepath, 'r') as f:
            content=f.read()
            # print(content)
            return content
    
    except FileNotFoundError as E:
        print("An Error occured while execution, there's no such file")
        print("ERROR:", E)
        sys.exit(1)
        
                
def response_name(filepath):
    path=Path(filepath)
    summary_path=path.with_name(path.stem + "_summary" + path.suffix)
    return summary_path

               
def write_response(summary,summary_path):
    try:
        with open(summary_path,'w',encoding="utf-8") as file:
            file.write(summary)
            
    except PermissionError:
        print("Error: You donot have permission to write to this location")
        sys.exit(1)
        
    except IsADirectoryError:
        print("Path you have specified is a directory not a file")
        sys.exit(1)
        
if __name__ == "__main__": 
    # filepath=r"C:\Users\Dell\Desktop\Code\MyCode\story.txt"  
    parser=argparse.ArgumentParser(description="A simple CLI based tool for summarizing the given text")
    parser.add_argument("filepath",nargs="?",default=None,help="Path of the file that you want summary of")
    parser.add_argument("--max-words",default=200,type=int,
                        help="Maximum number of words in summary to prevent it from getting unnecessarily long")
    parser.add_argument("--history",action="store_true",help="display history of the application")
    args=parser.parse_args()
    conn=init_db()
      
      
    if args.history:
        if args.filepath:
            print("You cannot get history and the summary simulatenously, try passing only the filepath "
                  "Usage: python first_summarizer.py <filepath> "
                  "For Now just displaying the history")
            
        print("History of entries from database")
        rows=get_history(conn)
        for (entry_id, filepath, summary, max_words, created_at) in rows:
            print(f"[{entry_id}] {created_at} | {filepath} | {summary[:50]}...")
    
    else:  
        
        max_words=args.max_words
        filepath=args.filepath
        
        if filepath is None:
            print("Please provide a filepath to summarize. Usage: python first_summarizer.py <filepath>")
            sys.exit(1)
            
        content=read_textfile(filepath)
        summary=get_response(content,max_words)
        
        now=datetime.now()
        timestamp_current=now.strftime("%d-%m-%Y, %I:%M:%S %p")
        
        if summary is None:
            print("Failed to get summary. Exiting...")
            sys.exit(1)
            
        summary_path=response_name(filepath)
        write_response(summary,summary_path)
        
        
        save_summary(conn,filepath,summary,max_words,timestamp_current)
    