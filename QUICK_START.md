# Quick Start Guide

## What You Have Now

Your bias correction system is ready to use! Here's what's in place:

### Files Created/Modified:
- ✅ `rewriter.py` - Main script (completely rewritten)
- ✅ `rag_data.py` - RAG data file (new)
- ✅ `requirements.txt` - Dependencies list
- ✅ `README.md` - Full documentation
- ✅ `SETUP_SUMMARY.md` - Detailed setup info

## Running the System

### Option 1: Interactive Mode (Recommended)
```bash
python rewriter.py
```
Then type biased sentences when prompted.

Example:
```
Enter biased text: Monna thotse o a nama
```

### Option 2: Test Mode
```bash
python rewriter.py test
```
Runs 4 test samples automatically.

## Adding More Data

Edit `rag_data.py` to add:

1. **More Examples**:
```python
GROUND_TRUTH_DATA.append({
    "language": "tn",
    "bias_category": "Your Category",
    "biased_text": "Your biased sentence",
    "bias_free_text": "Your corrected sentence"
})
```

2. **More Occupational Terms**:
```python
OCCUPATIONAL_TERMS["traditional_male"].append("new_term")
OCCUPATIONAL_TERMS["traditional_female"].append("new_term")
```

3. **More Gendered Terms**:
```python
GENDERED_TERMS["male_identifiers"].append("new_term")
GENDERED_TERMS["female_identifiers"].append("new_term")
```

## How It Works

1. **Detect**: Finds biased language using lexicons and patterns
2. **Categorize**: Identifies the type of bias
3. **Retrieve**: Gets relevant examples from your data (RAG)
4. **Generate**: Uses Gemma to rewrite with bias-free output

## What's Necessary

**Required:**
- Python 3.6+
- `requests` library
- Ollama running with `gemma2:2b` model

**Optional (for better detection):**
- `spacy` library
- `xx_ent_wiki_sm` spaCy model

The system works without spaCy using just lexicons and regex patterns!

## Troubleshooting

**"Connection refused to Ollama"**
→ Start Ollama: `ollama serve`

**"Module not found: requests"**
→ Install: `pip install requests`

**"Unicode errors on Windows"**
→ Already fixed! The script handles UTF-8 encoding automatically.

## Next Steps

1. Add more examples to `rag_data.py`
2. Customize bias detection patterns
3. Test with your own biased sentences
4. Expand to other languages if needed

---

**You're all set!** Just run `python rewriter.py` and start correcting bias!

