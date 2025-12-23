# Dataset Datasheet: Ground Truth for Gender Bias Detection

**Version:** 1.0  
**Date:** October 30, 2025  
**Dataset Name:** African Language Gender Bias Ground Truth  
**File:** `ground_truth.json`

---

## 1. Dataset Details

### 1.1 Basic Information
- **Total Examples**: 37 (expanded from initial 30)
- **Languages**: 2 (Setswana: 26, Zulu: 11)
- **Bias Categories**: 4
- **Format**: JSON (Firebase-style structure)
- **Encoding**: UTF-8

### 1.2 Composition by Language

| Language | Code | Count | Percentage |
|----------|------|-------|------------|
| Setswana | tn   | 26    | 70.3%      |
| Zulu     | zu   | 11    | 29.7%      |

### 1.3 Composition by Bias Category

| Category | Count | Percentage |
|----------|-------|------------|
| Occupational & Role Stereotyping | 28 | 75.7% |
| Gendered Wording | 5 | 13.5% |
| Stereotypical Pronominalization | 3 | 8.1% |
| Gender | 1 | 2.7% |

### 1.4 Domain Distribution

| Domain | Count | Examples |
|--------|-------|----------|
| Educational | 25 | Reading passages, textbook content |
| Social | 5 | Social contexts, cultural sayings |
| Professional | 2 | Professional domain examples |

### 1.5 Sub-Domain Distribution

| Sub-Domain | Count |
|------------|-------|
| reading_passage | 26 |
| textbook_content | 2 |
| main biases | 1 |
| [other] | 1 |

---

## 2. Data Collection

### 2.1 Motivation
To create a representative ground truth dataset for evaluating gender bias detection and correction systems in low-resource African languages.

### 2.2 Collection Process
1. **Source**: Flutter UI submissions from linguistic experts
2. **Method**: Expert-curated examples with validation
3. **Timeline**: October 28-30, 2025
4. **Validation**: Each example validated by domain experts

### 2.3 Curators & Validators

**Validators:**
- **Bongani Dube** (bryandube836@gmail.com) - Researcher
- **Agang K. Ditlhogo** (agangditlhogo@gmail.com) - Researcher/Linguist
- **Trish Ngarize** (tngarize97@gmail.com) - Linguist
- **Wellington Gombarume** (wellygombaz@gmail.com) - Researcher

**Roles:**
- Researchers: Bias identification and categorization
- Linguists: Language quality and cultural appropriateness
- Subject Matter Experts: Domain-specific validation

### 2.4 Curation Criteria
- **Biased text**: Contains explicit or implicit gender bias
- **Bias-free text**: Neutral, inclusive alternative
- **Preserves meaning**: Corrected version maintains original semantic content
- **Grammatically correct**: Both biased and corrected versions are valid
- **Culturally appropriate**: Examples reflect real-world usage

---

## 3. Data Characteristics

### 3.1 Text Properties
- **Average length**: Biased text ~5-20 words
- **Script**: Latin alphabet with diacritics
- **Complexity**: Varies from simple words to complex proverbs

### 3.2 Bias Manifestations

**Occupational & Role Stereotyping (21 examples):**
- Gender-specific role assignments
- Assumptions about capability based on gender
- Traditional gender roles in professions

Examples:
- "Monna thotse o a nama" (A man is like a seed that spreads) → "Motho mongwe le mongwe ke thotse o a anama"
- "Mosadi, tshwene o jewa mabogo" (A woman is a monkey, work with hands) → Generalized to all people

**Gendered Wording (5 examples):**
- Gendered terms used to refer to people
- Cultural constructs associated with gender

Examples:
- "Segametsi" (water fetcher, usually woman) → "Mosadi" (woman)
- "Mmagwana" (mother) → "Motsadi" (parent)

**Stereotypical Pronominalization (3 examples):**
- Names/titles that encode gender stereotypes
- Examples: "Khumoetsile" (source of wealth through lobola) → "Lobola"

**Gender (1 example):**
- Explicit gender-based role differentiation
- Example: Girl cooks, boy reads → Both can do either

### 3.3 Cultural Context
Many examples reflect:
- Traditional gender roles in African societies
- Cultural proverbs with embedded gender bias
- Educational contexts where bias may be perpetuated
- Professional domains with gender stereotypes

---

## 4. Provenance & Processing

### 4.1 Data Sources
- **Primary**: Flutter UI submission form
- **Format**: Firebase Realtime Database
- **Export date**: October 30, 2025

### 4.2 Data Processing
1. Exported from Firebase as JSON
2. Minimal cleaning (maintained original text)
3. Structured as dictionary with Firebase keys
4. Converted to list format for processing

### 4.3 Quality Control
- **Validator checks**: Each example reviewed by expert
- **Validation flags**: `meta.validated: true` for all examples
- **Timestamps**: Creation and validation dates recorded
- **Source tracking**: Flutter UI source documented

---

## 5. Ethics & Biases

### 5.1 Potential Biases in Dataset
- **Language imbalance**: 87% Setswana, 13% Zulu
- **Category imbalance**: 70% Occupational & Role Stereotyping
- **Geographic bias**: Predominantly Botswana (Setswana), some South Africa (Zulu)
- **Gender perspective**: May not cover all gender identities
- **Cultural specificity**: Examples reflect specific cultural contexts

### 5.2 Ethical Considerations
- **Consent**: All examples publicly submitted/validated
- **Privacy**: No personally identifiable information
- **Sensitive content**: Cultural proverbs may be offensive if taken out of context
- **Intended use**: Bias detection and correction (positive use)

### 5.3 Limitations
- **Small size**: 30 examples limits statistical power
- **Coverage gaps**: 
  - Not all bias manifestations covered
  - Limited to educational and social domains
  - Few examples per category (especially "Gender": 1)
- **Language coverage**: Only 2 of many African languages
- **No negative examples**: All examples contain bias (no clean text)

---

## 6. Maintenance & Versioning

### 6.1 Updates
- **Current version**: 1.0 (October 30, 2025)
- **Future versions**: Planned expansions:
  - More examples per category (target: 100+ total)
  - Additional languages (Xhosa, Swahili, etc.)
  - Synthetic examples to balance categories
  - Negative examples (bias-free text)

### 6.2 Data Splits
**Current**: Single dataset for evaluation  
**Recommended splits** (when expanded):
- Training: 70% (if creating supervised models)
- Validation: 15%
- Test: 15%
- **Hold-out set**: Maintain expert-curated test set

### 6.3 Change Log
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-30 | Initial dataset of 30 examples |

---

## 7. Licenses & Attribution

### 7.1 License
**To be determined** - Consult with Gates Foundation and AfriLabs

### 7.2 Attribution
All validators and contributors must be credited in publications and documentation.

### 7.3 Terms of Use
- **Research use**: Permitted
- **Commercial use**: To be determined
- **Redistribution**: To be determined
- **Modifications**: Permitted with attribution

---

## 8. Recommended Uses

### 8.1 Primary Use Case
Evaluation of gender bias detection and correction systems for African languages.

### 8.2 Appropriate Uses
- Benchmarking bias detection algorithms
- Training few-shot LLM prompts
- Developing lexicon-based detection rules
- Evaluation of correction quality
- Research on low-resource NLP

### 8.3 Inappropriate Uses
- Not for training production systems (too small)
- Not for measuring absolute bias rates in society
- Not representative of all African languages or cultures
- Should not be used without cultural context

---

## 9. Dataset Structure

### 9.1 JSON Format
```json
{
  "firebase_key": {
    "bias_category": "string",
    "bias_free_text": "string",
    "bias_free_translation_en": "string",
    "bias_subtype": ["array"],
    "biased_text": "string",
    "created_at": "ISO timestamp",
    "domain": "string",
    "id": "string",
    "language": "tn" | "zu",
    "meta": {...},
    "region": "string",
    "sub_domain": "string",
    "translation_en": "string"
  }
}
```

### 9.2 Key Fields
- **biased_text**: Original text containing bias
- **bias_free_text**: Corrected, bias-free alternative
- **bias_category**: Type of bias detected
- **language**: ISO 639-2 code for language
- **id**: Unique identifier (e.g., "tn-edu-0292")
- **meta.validated**: Boolean validation flag

---

## 10. Contact & Support

**Dataset Curator**: AfriLabs Team  
**Email**: [Contact]  
**Repository**: [GitHub Link]  
**Issues**: Report via GitHub Issues

**Questions about specific examples**: Contact the validator listed in `meta` field.

---

**Document Status**: Draft v1.0 for Gates Foundation Review (October 30, 2025)

