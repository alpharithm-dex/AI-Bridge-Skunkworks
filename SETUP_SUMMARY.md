# Setup Summary

## What Was Created

### 1. Main Script: `rewriter.py`
- Full rewrite with spaCy integration for bias detection
- Custom lexicons and regex patterns for detecting gendered associations
- Automatic bias category detection
- Interactive mode: Type biased sentences and get unbiased output
- Test mode: Run sample tests
- UTF-8 encoding support for Windows

**Key Features:**
- Detects bias using custom lexicons and regex patterns
- Falls back gracefully if spaCy is not installed
- Retrieves relevant examples from RAG data
- Sends prompts to Gemma via Ollama for correction

### 2. RAG Data File: `rag_data.py`
Contains all the data for the RAG system:
- `GROUND_TRUTH_DATA`: Examples of biased and bias-free text
- `OCCUPATIONAL_TERMS`: Traditional male, female, and neutral occupational terms
- `GENDERED_TERMS`: Male, female identifiers with neutral replacements
- `BIAS_PATTERNS`: Regex patterns for detecting biased phrases
- `BIAS_CATEGORIES`: Mapping of categories to keywords and examples
- Helper functions: `retrieve_examples()` and `get_category_from_text()`

### 3. Requirements: `requirements.txt`
List of Python dependencies

### 4. Documentation: `README.md`
Complete usage instructions and feature overview

## How to Use

### Basic Setup

1. **Install dependencies** (optional - spaCy for advanced detection):
   ```bash
   pip install -r requirements.txt
   python -m spacy download xx_ent_wiki_sm
   ```

2. **Install Ollama and pull Gemma model**:
   ```bash
   ollama pull gemma2:2b
   ollama serve
   ```

3. **Run interactive mode**:
   ```bash
   python rewriter.py
   ```

4. **Run test mode**:
   ```bash
   python rewriter.py test
   ```

### Adding More Data

To expand the bias detection and correction:

1. Edit `rag_data.py` and add more:
   - Ground truth examples to `GROUND_TRUTH_DATA`
   - Occupational terms to `OCCUPATIONAL_TERMS`
   - Gendered terms to `GENDERED_TERMS`
   - Bias patterns to `BIAS_PATTERNS`
   - Categories to `BIAS_CATEGORIES`

2. The script will automatically use the new data in its bias detection

## What's Necessary for Full Functionality

✅ **Currently Implemented:**
- Bias detection with lexicons and regex (works without spaCy)
- Automatic category detection
- RAG-based example retrieval
- Gemma model integration via Ollama
- Interactive and test modes
- UTF-8 encoding support

⚠️ **Optional (for enhanced detection):**
- spaCy installation for advanced NLP-based bias detection
- spaCy multilingual model (xx_ent_wiki_sm)

🔧 **Required:**
- Ollama running with gemma2:2b model
- Python 3.6+ with requests library

## Testing Results

All 4 test samples completed successfully:
1. "Monna thotse o a nama" - Bias detected, corrected
2. "Monna selepe o a adingwana" - Bias detected, corrected
3. "Kubukeka sengathi Amantombana bangcono ku ifisiksi." - Processed
4. "Mosadi yo o tla dirisa motšhene wa go hlanka" - Bias detected, corrected

## Architecture

```
rewriter.py
├── detect_bias()           # Bias detection using lexicons/regex/spaCy
├── build_prompt()          # Build few-shot prompt with RAG examples
├── call_gemma_corrector()  # API call to Ollama
├── correct_bias_tn()       # Main orchestration function
└── run_interactive()       # Interactive mode

rag_data.py
├── GROUND_TRUTH_DATA       # Biased/corrected examples
├── OCCUPATIONAL_TERMS      # Terms by gender association
├── GENDERED_TERMS          # Gender identifiers
├── BIAS_PATTERNS           # Regex patterns
├── BIAS_CATEGORIES         # Category mapping
├── retrieve_examples()     # RAG retrieval
└── get_category_from_text() # Auto-categorization
```

## Next Steps for Enhancement

1. Add more occupational terms and biased phrase patterns
2. Include more ground truth examples (expand from current 6 to 71)
3. Fine-tune bias detection patterns based on results
4. Add support for other African languages
5. Implement evaluation metrics for correction quality

