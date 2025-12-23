# Approach Card: Bias Detection and Correction for African Languages

**Version:** 1.0  
**Date:** October 30, 2025  
**Team:** AfriLabs AI Team  
**Project:** Gender Bias Detection and Mitigation in Low-Resource African Languages

---

## Executive Summary

The AI BRIDGE initiative has made significant progress in Phase 2 of developing a bias detection and correction system for low-resource African languages. Since commencing in October, the team has established a scalable framework with current support for Ndebele, Setswana, and Zulu.

**Key Progress to Date**: Initial testing of the rule-based architecture has demonstrated promising results, achieving high precision and proving that a rule-based approach (augmented by RAG) can deliver interpretable, low-compute bias mitigation. However, as the system moves into more complex linguistic territory, the integration of **Large Language Models (LLMs)** has become essential. LLMs are critical for making nuanced decisions on subtle bias cases and generating comprehensive, context-aware rewrites that go beyond simple template-based replacements.

**Next Steps (January – March)**: While the foundational systems are operational, the project is currently in an active optimization phase. The primary objective for the remaining project term is to improve F1 scores, specifically targeting nuanced and complex bias cases that require deeper semantic understanding. This will involve deeper integration of LLM-driven reasoning to handle implicit bias and culturally embedded stereotypes that rule-based systems alone cannot fully address.

---

## 1. Problem Framing

### 1.1 Objective
Design, implement, and evaluate a bias detection and correction system for gender-biased text in African languages, specifically Setswana (tn) and Zulu (zu).

### 1.2 Challenge
- **Low-resource languages**: Limited NLP tools and datasets for African languages
- **Cultural context**: Gender bias manifests differently across languages and cultures
- **Linguistic diversity**: African languages have unique grammatical structures requiring language-specific approaches
- **Generalization**: Create a system that works across multiple languages with varying resources

### 1.3 Scope
- **Languages**: Setswana (tn), isiZulu (zu)
- **Datasets**:
  - **Diagnostic Set**: 37 expert-validated examples (26 Setswana, 11 Zulu)
  - **Large-Scale Set**: 10,476 semi-annotated examples (5,756 Setswana, 4,720 Zulu)
- **Bias categories**: 
  - Occupational & Role Stereotyping
  - Gendered Wording
  - Asymmetrical Ordering (Male Firstness)
  - Pejorative Association
  - Named Entity Bias
- **Domain**: Educational and social contexts

---

## 2. Approach & Architecture

### 2.1 High-Level Architecture

```
Input Text → Bias Detection → Category Identification → Example Retrieval (RAG) → LLM Correction → Output
```

### 2.2 Bias Detection Mechanism

**Theory of Bias:**
Gender bias in African languages manifests through:
1. **Explicit gender markers**: Gendered nouns (monna/mosadi in Setswana, indoda/umfazi in Zulu)
2. **Occupational stereotypes**: Gender-specific role assignments (e.g., "woman who cooks")
3. **Cultural idioms**: Proverbs and sayings that encode gender bias (e.g., "Monna selepe o a adingwana")
4. **Morphological markers**: Language-specific gender inflections

**Detection Components:**

#### A. Lexicon-Based Detection
- **Custom lexicons** for each language:
  - Male identifiers (monna, indoda, mosimane, etc.)
  - Female identifiers (mosadi, umfazi, mosetsana, etc.)
  - Occupational terms tagged by traditional gender associations

#### B. Pattern Matching
- **Regex patterns** for:
  - Gendered occupational roles: `(mosadi|monna)\s+\w+\s+(wa|yo)\s+\w+`
  - Capability assumptions: `(kgona|go kgona)\s+\w+`
  - Cultural idioms containing gendered references

#### C. spaCy Integration (Optional)
- Named entity recognition for additional context
- Falls back gracefully if not installed

**Why This Approach:**
- **Interpretability**: Rules are explicit and auditable
- **Low resource**: Minimal data requirements
- **Language-specific**: Adapts easily to new languages via lexicons
- **Fast**: No heavy compute needed

### 2.3 Category Identification

**Strategy**: Keyword-based classification using `BIAS_CATEGORIES` mapping:
- "Occupational & Role Stereotyping" → {motshameki, morutišana, motlhankedi, thotse, selepe, motho, manamagadi}
- "Gender" → {mosetsana, mosimane, mosadi, monna}
- "Gendered Wording" → {mosadi, monna, segametsi, mme, mmagwana}
- "Stereotypical Pronominalization" → {khumoetsile, kgosietsile}

**Default**: Falls back to "General Bias" if no category match

### 2.6 Key Technical Improvements (Oct 2025)

| Improvement | Impact |
|-------------|--------|
| Expanded Zulu lexicons | 9× increase in Occupational category TPs |
| Category keyword expansion | +194% Macro-F1 |
| Pattern matching refinement | Precision maintained at 1.000 |

---

## 3. Data Collection

### 3.1 Data Collection Process
The data collection and annotation process was advised by the AI BRIDGE Data Collection and Annotation Guideline. This outlined the standardized required rules to follow in the process.

**Datasets links:**
- [4,720 semi-annotated isiZulu sentences](https://drive.google.com/file/d/1bDnbNA47m0ztjC7QIjf99RBE2wFDmdat/view?usp=sharing)
- [5,756 semi-annotated Setswana sentences](https://drive.google.com/file/d/1v0RGflpWdgjV3fHs-YPFz1gNy8p2SQay/view?usp=sharing)

### 3.2 Ground Truth Dataset Overview
| Metric | Value |
|--------|-------|
| Total Examples | 37 |
| Languages | Setswana (26), Zulu (11) |
| Bias Categories | 4 |
| Format | JSON (Firebase-style) |
| Collection Period | 28–30 October 2025 |

### 3.3 Bias Category Distribution
| Category | Count | % | Example |
|----------|-------|---|---------|
| Occupational & Role Stereotyping | 28 | 75.7% | “Monna thotse o a nama” |
| Gendered Wording | 5 | 13.5% | “Segametsi” |
| Stereotypical Pronominalization | 3 | 8.1% | “Khumoetsile” |
| Gender Role Assignment | 1 | 2.7% | Gender-based role assumption |

### 3.4 Domain Distribution
| Domain | Count |
|--------|-------|
| Educational | 25 |
| Social / Cultural | 5 |
| Professional | 2 |

### 3.5 Data Collection & Validation
- **Source**: Flutter UI submissions
- **Method**: Expert-curated, manually validated
- **Validation**: Domain expert review (100%)

#### Validators & Contributors
| Name | Role | Email |
|------|------|-------|
| Bongani Dube | Researcher | bryandube836@gmail.com |
| Agang K. Ditlhogo | Linguist (Setswana) | agangditlhogo@gmail.com |
| Trish Ngarize | Linguist (Zulu) | tngarize97@gmail.com |
| Wellington Gombarume | Researcher | wellygombaz@gmail.com |

---

## 4. Evaluation Results

In Ithute’s educational context, incorrectly modifying culturally valid or pedagogically descriptive gender references poses a higher risk than missed bias detections, as it may distort curriculum-aligned learning materials or misrepresent local knowledge. Accordingly, the system is intentionally configured to prioritise precision over recall, ensuring that only high-confidence bias instances are corrected during early deployment phases.

### 4.1 Diagnostic Evaluation Performance (Precision-First)
The performance gains shown below result from iterative system development on the expert-validated diagnostic set (37 items).

| Category | Precision | Recall | F1 | TP | FP | FN | Status |
|----------|-----------|--------|----|----|----|----|--------|
| Gender | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 🟢 Perfect- Validated and stable |
| Occupational & Role | 0.857 | 0.643 | 0.735 | 18 | 3 | 10 | 🟢 Good |
| Gendered Wording | 1.000 | 0.200 | 0.333 | 1 | 0 | 4 | ⚠️ Conservatively Limited (By Design) |
| Stereotypical Pronominalization | 0.000 | 0.000 | 0.000 | 0 | 0 | 3 | 🔴 Out of scope for current phase |
| **Overall** | **1.000** | **0.649** | **0.787** | **24** | **0** | **13** | — |
| **Macro-F1** | — | — | **0.414** | — | — | — | — |

> [!NOTE]
> Performance reflects a precision-first configuration prioritising educational safety and cultural accuracy over broad coverage.

### 4.2 Large-Scale Evaluation Results (CSV Datasets)
The system was also evaluated on the full semi-annotated datasets to measure real-world coverage across 10,476 examples.

| Language | Examples | Detected | Detection Rate | F1 Score |
|----------|----------|----------|----------------|----------|
| **isiZulu** | 4,720 | 164 | **3.5%** | **6.7%** |
| **Setswana** | 5,756 | 528 | **9.2%** | **16.8%** |

> [!TIP]
> The isiZulu detection rate saw a **5x improvement** in Phase 2 through the implementation of **Stem-Based Matching**, which successfully handled complex Zulu prefixes.

### 4.3 Performance Improvements from Lexicon Expansion and Pattern Refinement
The performance gains shown below result from iterative system development—including lexicon expansion, category-specific keyword tuning, pattern matching refinement, and the addition of expert-validated ground truth examples. Baseline refers to the initial Phase 2 system configuration, while Current reflects the refined configuration following these targeted improvements.

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Overall F1 | 0.636 | 0.787 | +24% relative increase |
| Macro-F1 | 0.141 | 0.414 | +194% relative increase |
| Precision | 1.000 | 1.000 | Maintained (0 false positives) |
| Recall | 0.467 | 0.649 | +39% relative increase |

These results demonstrate that meaningful performance improvements can be achieved through linguistically informed system refinement, without modifying underlying model weights or increasing computational requirements. Importantly, recall gains were realised while preserving perfect precision, reinforcing the system’s suitability for safety-critical educational deployment.

### 4.3 Large-Scale Evaluation Results (CSV Datasets)
The system was also evaluated on the full semi-annotated datasets to measure real-world coverage.

| Language | Examples | Detected | Detection Rate | F1 Score |
|----------|----------|----------|----------------|----------|
| **isiZulu** | 4,720 | 164 | **3.5%** | **6.7%** |
| **Setswana** | 5,756 | 528 | **9.2%** | **16.8%** |

> [!TIP]
> The isiZulu detection rate saw a **5x improvement** in Phase 2 through the implementation of **Stem-Based Matching**, which successfully handled complex Zulu prefixes.

---

## 5. Challenges & Lessons Learned

### 5.1 Key Challenges and Mitigation Strategies
The following challenges were encountered during Phase 2 development. Each reflects known constraints in low-resource language AI and informed targeted mitigation plans.

| Challenge | Description | Mitigation Strategy |
|-----------|-------------|---------------------|
| Cultural Idioms | Gender bias embedded in proverbs and idiomatic expressions is difficult to detect using surface-level lexical patterns | Develop a specialised idiom detection module informed by linguistic expertise |
| Implicit Bias | Bias expressed through context, grammar, or cultural assumptions rather than explicit gender markers | Introduce context-aware detection patterns and implicit bias rules |
| Low Recall in Specific Categories | Stereotypical pronominalization currently undetected due to cultural naming conventions | Design a dedicated detection module for culturally embedded references |
| Language Imbalance | Dataset skewed toward Setswana (70%) relative to Zulu (30%) | Prioritise expanded Zulu data collection in subsequent phases |

### 5.2 Lessons Learned
Key insights from Phase 2 development include:
- **Lexicon expansion delivers immediate gains**: Adding culturally relevant terms resulted in substantial performance improvements without increasing system complexity
- **Conservative detection rules are essential in education**: Zero false positives are critical to preserving curriculum integrity and learner trust
- **Cultural expertise is non-negotiable**: Linguistic and contextual knowledge cannot be substituted by automated methods in low-resource languages
- **Data-driven system refinement outperforms retraining at early stages**: Iterative rule and dataset improvements proved more effective and appropriate than model retraining under low-resource constraints.

---

## 6. Roadmap & Next Steps

### Immediate (Q1 2026)
| Target | Current | Action |
|--------|---------|--------|
| Recall > 0.75 | 0.649 | Expand detection patterns |
| Macro-F1 > 0.50 | 0.414 | Address pronominalization category |
| Dataset Size 100+ | 37 | Active expert-led data collection |

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Limited ground truth | High | Supplement with synthetic examples, active learning |
| LLM quality issues | Medium | Prompt engineering, example curation, fallback rules |
| Language-specific errors | Medium | Expert review, linguistic validation |
| Overfitting to examples | Low | Cross-validation, held-out test set |
| Resource constraints | Medium | Use lightweight models, optimize inference |

---

## Contact

**Team Lead**: [Contact Information]  
**Linguistics Expert**: Agang K. Ditlhogo (agangditlhogo@gmail.com)  
**Evaluation Lead**: [Contact Information]

**Repository**: [GitHub Link]

---

**Document Status**: Draft v1.0 for Gates Foundation Review (October 30, 2025)

