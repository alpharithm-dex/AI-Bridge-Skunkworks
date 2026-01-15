import pandas as pd
import re
from collections import Counter
import json

def analyze_csv(file_path, language):
    print(f"Analyzing {language} dataset: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

    # Extract common terms in biased text
    biased_texts = df['IsiZulu' if language == 'isizulu' else 'IsiZulu'].tolist() # The column name seems to be IsiZulu in both based on previous view_file, but let's check
    # Wait, the previous view_file of zulu_bias_dataset_final_clean.csv showed "IsiZulu,English,bias_type,discipline"
    # The setswana file likely has a similar structure or maybe "Setswana" column.
    # Let's handle column names dynamically or check first.
    
    # Actually, let's just read the first few lines to be sure about column names in the script if we can, 
    # but for now I'll assume standard names or try to detect them.
    
    text_col = 'IsiZulu' if 'IsiZulu' in df.columns else 'Setswana'
    if text_col not in df.columns:
        # Fallback to first column
        text_col = df.columns[0]
    
    print(f"Using text column: {text_col}")
    
    all_text = " ".join(df[text_col].astype(str).tolist()).lower()
    words = re.findall(r'\b\w+\b', all_text)
    common_words = Counter(words).most_common(50)
    
    print(f"Top 50 words in {language}:")
    print(common_words)
    
    # Extract potential bias patterns based on bias_type
    bias_types = df['bias_type'].unique()
    patterns = {}
    
    for b_type in bias_types:
        subset = df[df['bias_type'] == b_type]
        subset_text = " ".join(subset[text_col].astype(str).tolist()).lower()
        subset_words = Counter(re.findall(r'\b\w+\b', subset_text)).most_common(20)
        patterns[b_type] = subset_words
        
    return patterns

def main():
    zulu_patterns = analyze_csv('zulu_bias_dataset_final_clean.csv', 'isizulu')
    setswana_patterns = analyze_csv('setswana_bias_dataset_final.csv', 'setswana')
    
    results = {
        "isizulu": zulu_patterns,
        "setswana": setswana_patterns
    }
    
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("Analysis complete. Results saved to analysis_results.json")

if __name__ == "__main__":
    main()
