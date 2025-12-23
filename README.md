# Bias Correction Model for Setswana Text

A RAG-based (Retrieval-Augmented Generation) bias correction system for Setswana text that detects gender-based bias and occupational stereotyping, then corrects it using Gemma via Ollama.

## What's New

- **Separate RAG Data File** (`rag_data.py`): All ground truth examples, lexicons, and bias patterns are now in a dedicated file that can be easily expanded
- **spaCy Integration**: Advanced NLP-based bias detection (optional, falls back to lexicons if not installed)
- **Automatic Bias Detection**: Custom lexicons and regex patterns detect gendered terms and occupational stereotyping
- **Interactive Mode**: Type biased sentences and receive unbiased corrections
- **Test Mode**: Run predefined test samples

## Features

- **Bias Detection**: Uses spaCy with custom lexicons and regex patterns to detect:
  - Gendered identifiers (monna, mosadi, etc.)
  - Occupational stereotyping
  - Gender-based language patterns

- **Automatic Category Detection**: Identifies bias categories from the text

- **RAG-based Correction**: Retrieves relevant examples from ground truth data to guide correction

- **Interactive Mode**: Type biased sentences and receive unbiased corrections

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
python -m spacy download xx_ent_wiki_sm
```

### 2. Install and Setup Ollama

Download and install Ollama from: https://ollama.ai

Pull the Gemma2 model:
```bash
ollama pull gemma2:2b
```

Start Ollama server:
```bash
ollama serve
```

## Usage

### Interactive Mode (Default)

Simply type biased sentences when prompted:

```bash
python rewriter.py
```

Example:
```
Enter biased text: Monna thotse o a nama
```

### Test Mode

Run test samples:

```bash
python rewriter.py test
```

## File Structure

- `rewriter.py` - Main script with bias detection and correction logic
- `rag_data.py` - RAG data including ground truth examples, lexicons, and bias patterns
- `requirements.txt` - Python dependencies
- `README.md` - This file

## How It Works

1. **Bias Detection**: The text is analyzed using:
   - Custom lexicons for gendered and occupational terms
   - Regex patterns for biased phrases
   - spaCy for additional linguistic analysis

2. **Category Identification**: Determines the type of bias (e.g., "Occupational & Role Stereotyping")

3. **Example Retrieval**: Retrieves relevant examples from `rag_data.py` based on the detected category

4. **Few-Shot Prompting**: Builds a prompt with examples for the Gemma model

5. **Generation**: Sends the prompt to Gemma via Ollama for bias-free rewriting

## Adding More Data

Edit `rag_data.py` to add:
- More ground truth examples in `GROUND_TRUTH_DATA`
- Additional occupational terms in `OCCUPATIONAL_TERMS`
- Gendered terms in `GENDERED_TERMS`
- Bias patterns in `BIAS_PATTERNS`

## Notes

- The system uses Gemma2:2b which is lightweight and runs on CPU
- Ensure Ollama is running before executing the script
- The bias detection works best with Setswana text but can be adapted for other languages

