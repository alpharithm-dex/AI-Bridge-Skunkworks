# Evaluation Protocol v0.1

**Version:** 0.1  
**Date:** October 30, 2025  
**Status:** Draft for Gates Foundation Review

---

## 1. Overview

This document specifies the evaluation protocol for gender bias detection and correction systems in low-resource African languages.

**Objective**: Establish a standardized, reproducible evaluation framework that can be shared across teams and allows for fair comparison of approaches.

---

## 2. Data Versions

### 2.1 Ground Truth Dataset
- **File**: `ground_truth.json`
- **Version**: 1.0 (October 30, 2025)
- **Total examples**: 30
- **Languages**: Setswana (tn): 26, Zulu (zu): 4
- **Bias categories**: 4 (Occupational & Role, Gendered Wording, Pronominalization, Gender)

### 2.2 Data Splits (Current)
- **All data for evaluation**: Single set (no train/test split yet)
- **Rationale**: Small dataset size; currently used for end-to-end evaluation
- **Future**: Will create train/validation/test splits when dataset expands

### 2.3 Held-Out Data
- **Current**: None
- **Planned**: Maintain expert-curated held-out set for final evaluation

---

## 3. Evaluation Setup

### 3.1 Detection Evaluation

**Goal**: Measure how well the system identifies gender bias in text.

**Input**: Biased text from ground truth  
**Output**: Binary prediction (bias/no bias) + category label

**Metrics**:
1. **Precision**: TP / (TP + FP)
2. **Recall**: TP / (TP + FN)
3. **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
4. **Macro-F1**: Average F1 across all categories

**Assumption**: All examples in ground truth contain bias (TP = true positives when system correctly detects bias)

### 3.2 Correction Evaluation

**Goal**: Measure quality of bias-free rewriting.

**Input**: Biased text + system output  
**Output**: Quality scores

**Metrics**:
1. **Exact Match Rate**: Exact match with ground truth
2. **Bias Removal Rate**: Percentage of corrections free of gendered terms
3. **Word-Level Similarity**: (Planned) Jaccard, BLEU
4. **Semantic Similarity**: (Planned) Embedding-based cosine similarity
5. **Grammatical Correctness**: Human evaluation
6. **Meaning Preservation**: Human evaluation

### 3.3 Language-Specific Evaluation

**Report metrics separately for**:
- Setswana (tn)
- Zulu (zu)
- Overall (combined)

---

## 4. Evaluation Scripts

### 4.1 Automated Evaluation

**Files**:
- `evaluate.py`: Core evaluation metrics
- `batch_evaluate.py`: Batch processing on ground truth

**Usage**:
```bash
python batch_evaluate.py
```

**Outputs**:
- Console report
- `evaluation_results.json`: Detailed results

### 4.2 Metrics Definitions

```python
# Detection Metrics
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 × (Precision × Recall) / (Precision + Recall)

# By Category
# For each bias category, compute P, R, F1 independently

# Overall Metrics
Macro-F1 = mean(F1_per_category)
```

### 4.3 Baseline Comparisons

**To be implemented**:
1. **Random baseline**: Random predictions
2. **Public model baseline**: Pre-trained models (if available)
3. **Rule-only baseline**: Lexicons without LLM
4. **LLM-only baseline**: No RAG examples

---

## 5. Experimental Setup

### 5.1 Software Environment

**Requirements**:
```txt
Python >= 3.6
requests >= 2.31.0
spacy >= 3.7.0 (optional)
```

**Configuration**:
- Ollama server: `http://localhost:11434`
- Model: `gemma2:2b`
- Temperature: 0.2 (for corrections)

### 5.2 Reproducibility

**Randomness**: Minimal (deterministic patterns, fixed LLM parameters)

**Versioning**: All scripts in GitHub with commit hashes

**Documentation**: Each run logs:
- Git commit hash
- Python version
- System configuration
- Date/time

### 5.3 Running Evaluation

**Step 1**: Start Ollama server
```bash
ollama serve
```

**Step 2**: Pull model
```bash
ollama pull gemma2:2b
```

**Step 3**: Run evaluation
```bash
python batch_evaluate.py
```

**Step 4**: Review results
```bash
cat evaluation_results.json
```

---

## 6. Results Reporting

### 6.1 Required Format

**Detection Metrics Table**:

| Category | Precision | Recall | F1 | TP | FP | FN |
|----------|-----------|--------|----|----|----|----|
| Occupational & Role | X.XXX | X.XXX | X.XXX | X | X | X |
| Gendered Wording | X.XXX | X.XXX | X.XXX | X | X | X |
| Pronominalization | X.XXX | X.XXX | X.XXX | X | X | X |
| Gender | X.XXX | X.XXX | X.XXX | X | X | X |
| **Overall** | **X.XXX** | **X.XXX** | **X.XXX** | **X** | **X** | **X** |
| **Macro-F1** | - | - | **X.XXX** | - | - | - |

**By Language**:

| Language | Overall F1 | Macro-F1 | Examples |
|----------|------------|----------|----------|
| Setswana (tn) | X.XXX | X.XXX | 26 |
| Zulu (zu) | X.XXX | X.XXX | 4 |
| **Combined** | **X.XXX** | **X.XXX** | **30** |

**Correction Metrics** (if available):

| Metric | Value |
|--------|-------|
| Total Corrections | X |
| Exact Match Rate | X.XXX |
| Bias Removal Rate | X.XXX |

### 6.2 Failure Cases

**Required**: Report 3 failure cases per evaluation

**Format**:
```markdown
### Failure Case 1

- **Input**: [Biased text]
- **Expected**: [Bias category]
- **Detected**: [Predicted category]
- **Corrected**: [Output]
- **Ground Truth**: [Expected correction]
- **Diagnosis**: [Why it failed]
- **Fix**: [Planned improvement]
```

---

## 7. Evaluation Schedule

### 7.1 Weekly Evaluations

**Day**: Every Monday  
**Required Actions**:
1. Run `batch_evaluate.py`
2. Generate metrics tables
3. Identify 3 failure cases
4. Document in Weekly Metrics Log
5. Update Approach Card with learnings

### 7.2 Weekly Metrics Log

**Format**: `WEEKLY_METRICS_LOG.md`

```markdown
# Weekly Metrics Log - Week [Date]

## Summary
- Overall F1: X.XXX
- Macro-F1: X.XXX
- Changes from last week: +X.XXX

## By Language
### Setswana
- Overall F1: X.XXX
- Key improvements: [List]

### Zulu
- Overall F1: X.XXX
- Key improvements: [List]

## Failure Cases (Top 3)
1. [Description]
2. [Description]
3. [Description]

## Action Items
- [ ] Action 1
- [ ] Action 2

## Notes
[Any observations]
```

---

## 8. Quality Assurance

### 8.1 Validation Checks

Before submitting results:
- [ ] All 30 examples evaluated
- [ ] Metrics computed correctly
- [ ] Failure cases documented
- [ ] Results reproducible (another team can run same)

### 8.2 Human Evaluation

**Planned for future iterations**:
- Corrected sentences reviewed by linguists
- Grammatical correctness rating (1-5)
- Meaning preservation rating (1-5)
- Bias removal confirmation

**Protocol**: To be developed

---

## 9. Ablation Studies

**Components to test**:

| Component | Baseline | Variant | Expected Impact |
|-----------|----------|---------|-----------------|
| Lexicons | Full | Reduced | ↓ Precision |
| Patterns | All | None | ↓ Recall |
| spaCy | Enabled | Disabled | ± Minor |
| RAG k | 2 | 1 or 0 | ↓ Correction quality |
| LLM Temp | 0.2 | 0.7 | ↓ Consistency |

**Method**: Run evaluation with each component disabled/modified

---

## 10. Troubleshooting

### 10.1 Common Issues

**Ollama connection failed**:
- Check server running: `ollama list`
- Start server: `ollama serve`

**Import errors**:
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

**Missing ground truth**:
- Verify `ground_truth.json` exists
- Check file path in scripts

### 10.2 Contact

**Technical Issues**: [GitHub Issues]  
**Protocol Questions**: [Contact Lead]

---

## 11. Future Enhancements

### 11.1 Planned Additions
- Human evaluation protocol
- Cross-validation setup
- Synthetic data generation
- Additional languages
- Fine-grained category expansion

### 11.2 Feedback Integration
- Incorporate Gates Foundation feedback
- Add evaluation dimensions as needed
- Refine metrics based on expert input

---

## 12. References

- Datasheet: `DATASET_DATASHEET.md`
- Approach: `APPROACH_CARD.md`
- Evaluation Script: `evaluate.py`
- Weekly Log: `WEEKLY_METRICS_LOG.md`

---

**Document Status**: Draft v0.1 for Review (October 30, 2025)

**Next Version**: Incorporate feedback, add baselines, expand protocol

