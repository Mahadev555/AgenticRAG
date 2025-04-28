import pandas as pd
import json
import os
from typing import List, Dict, Any
import tiktoken

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def chunk_dataframe(df: pd.DataFrame, max_tokens: int = 500) -> List[Dict[str, Any]]:
    """Split dataframe into chunks that fit within token limit."""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        row_json = json.dumps(row_dict)
        row_tokens = count_tokens(row_json)
        
        if current_tokens + row_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        
        current_chunk.append(row_dict)
        current_tokens += row_tokens
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def parse_csv(file_path: str, max_tokens: int = 500) -> List[Dict[str, Any]]:
    """Parse CSV file and return chunks of data within token limit."""
    df = pd.read_csv(file_path)
    return chunk_dataframe(df, max_tokens)

def parse_excel(file_path: str, max_tokens: int = 500) -> List[Dict[str, Any]]:
    """Parse Excel file and return chunks of data within token limit."""
    df = pd.read_excel(file_path)
    return chunk_dataframe(df, max_tokens)

def process_tabular_files(data_folder: str = "../../data"):
    """Process all CSV and Excel files in the data folder."""
    for file_name in os.listdir(data_folder):
        file_path = os.path.join(data_folder, file_name)
        
        if not os.path.isfile(file_path):
            continue
            
        file_ext = os.path.splitext(file_name)[1].lower()
        
        try:
            if file_ext == '.csv':
                chunks = parse_csv(file_path)
            elif file_ext in ['.xls', '.xlsx']:
                chunks = parse_excel(file_path)
            else:
                continue
                
            # Save chunks as JSON files
            for i, chunk in enumerate(chunks):
                output_path = f"{file_path}_chunk_{i}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(chunk, f, indent=2)
                    
            print(f"Successfully processed: {file_name}")
            
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")

if __name__ == "__main__":
    process_tabular_files() 