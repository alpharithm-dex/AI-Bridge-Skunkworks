# 🎯 Demo Guide - Bias Correction System

## Quick Start for Today's Demo

### Prerequisites
1. **Start Ollama Server** (Required for actual corrections):
   ```bash
   ollama serve
   ```

2. **Ensure Gemma2 model is available**:
   ```bash
   ollama pull gemma2:2b
   ```

---

## Running the Demo

### Option 1: Interactive Mode (Recommended for Live Demo)
```bash
py -3.13 demo.py
```

**What happens:**
- You can type any biased text
- System shows all 5 steps in real-time
- Perfect for audience interaction
- Type `quit` to exit

**Example interaction:**
```
💬 Enter text to analyze: Monna thotse o a nama
```

**For Zulu text, prefix with `zu:`:**
```
💬 Enter text to analyze: zu: Kubukeka sengathi Amantombana bangcono ku ifisiksi.
```

---

### Option 2: Quick Demo (Pre-loaded Examples)
```bash
py -3.13 demo.py quick
```

**What happens:**
- Runs through 3 predefined examples automatically
- Shows complete process for each
- Great for uninterrupted presentation
- Press Enter between examples

**Examples included:**
1. "Monna thotse o a nama" (Setswana)
2. "Mosadi yo o tla dirisa motšhene wa go hlanka" (Setswana)
3. "Kubukeka sengathi Amantombana bangcono ku ifisiksi." (Zulu)

---

### Option 3: Single Test
```bash
py -3.13 demo.py test "Your text here"
```

**Example:**
```bash
py -3.13 demo.py test "Monna selepe o a adingwana"
```

---

## What the Demo Shows

### 📍 STEP 1: BIAS DETECTION
- Scans for gendered identifiers (monna, mosadi, etc.)
- Checks for occupational stereotyping
- Applies regex pattern matching
- Optional NLP analysis with spaCy
- **Output:** Bias score, detected terms, detailed findings

### 📍 STEP 2: CATEGORY CLASSIFICATION
- Automatically identifies bias type
- **Categories:**
  - Gender
  - Occupational & Role Stereotyping
  - Gendered Wording
  - Stereotypical Pronominalization

### 📍 STEP 3: RAG (Retrieval-Augmented Generation)
- Retrieves similar examples from ground truth dataset (37 examples)
- Shows the actual examples used
- **Languages:** Setswana (26 examples), Zulu (11 examples)

### 📍 STEP 4: PROMPT CONSTRUCTION
- Builds few-shot prompt with retrieved examples
- Shows prompt length and preview
- Demonstrates how we guide the LLM

### 📍 STEP 5: LLM GENERATION
- Sends to Gemma2:2b via Ollama
- Temperature: 0.2 (low for factual corrections)
- Shows generation status

### 📋 FINAL RESULTS
- Side-by-side comparison (Original vs Corrected)
- Summary statistics
- Category and bias score

---

## Demo Tips for Presentation

### 1. **Start with Quick Demo**
```bash
py -3.13 demo.py quick
```
- Shows the system working end-to-end
- No typing required
- Professional and smooth

### 2. **Then Switch to Interactive**
```bash
py -3.13 demo.py
```
- Let audience suggest biased sentences
- Shows real-time processing
- More engaging

### 3. **Highlight Key Points**
- ✅ **Perfect Precision:** 1.000 (no false positives)
- ✅ **F1 Score:** 0.787 (strong performance)
- ✅ **Multi-language:** Setswana & Zulu
- ✅ **Interpretable:** Every step is visible and auditable
- ✅ **Low-resource:** Works with minimal data

---

## Sample Biased Sentences for Demo

### Setswana Examples
1. `Monna thotse o a nama` - Male hunting stereotype
2. `Mosadi yo o tla dirisa motšhene wa go hlanka` - Female domestic work
3. `Monna selepe o a adingwana` - Male strength stereotype
4. `Basadi ba a apaya` - Women cooking stereotype

### Zulu Examples
1. `Kubukeka sengathi Amantombana bangcono ku ifisiksi.` - Girls better at physics
2. `Amakhwenkwe kufanele afunde kuphela ezobuciko bokwakha.` - Boys in construction

---

## Troubleshooting

### "Could not connect to Ollama server"
**Solution:**
```bash
# In a separate terminal:
ollama serve
```

### "Module not found: requests"
**Solution:**
```bash
pip install requests
```

### "Module not found: spacy"
**Note:** spaCy is optional. The system works without it using lexicons and regex.

**To install (optional):**
```bash
pip install spacy
python -m spacy download xx_ent_wiki_sm
```

---

## Performance Metrics to Mention

| Metric | Value | Status |
|--------|-------|--------|
| **Overall F1** | 0.787 | 🟢 Strong |
| **Precision** | 1.000 | 🟢 Perfect |
| **Recall** | 0.649 | 🟡 Good |
| **Macro-F1** | 0.414 | 🟡 Improving |

### By Category
- **Gender:** F1 = 1.000 ✅ Perfect
- **Occupational & Role:** F1 = 0.735 ✅ Good
- **Gendered Wording:** F1 = 0.333 ⚠️ Needs work
- **Pronominalization:** F1 = 0.000 🔴 Critical gap

---

## Key Messages for Audience

1. **Interpretable AI:** Every decision is visible and auditable
2. **Low-resource friendly:** Works with just 37 examples
3. **Scalable:** Easy to add new languages via lexicons
4. **Production-ready:** FastAPI backend for real-world deployment
5. **Continuous improvement:** Weekly evaluation and metrics tracking

---

## After the Demo

### Next Steps to Mention
1. Expand ground truth dataset
2. Improve pronominalization detection
3. Add more African languages
4. Human evaluation of corrections
5. Deploy to production API

---

## Quick Command Reference

```bash
# Start Ollama (required)
ollama serve

# Interactive demo
py -3.13 demo.py

# Quick demo (auto)
py -3.13 demo.py quick

# Single test
py -3.13 demo.py test "Your text"

# Original rewriter (for comparison)
py -3.13 rewriter.py

# Run evaluation
py -3.13 evaluate.py
```

---

**Good luck with your demo! 🚀**
