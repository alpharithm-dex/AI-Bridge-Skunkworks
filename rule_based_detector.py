#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rule-Based Bias Detection and Rewriting System
Supports Setswana (tn) and isiZulu (zu)

No LLM dependency - purely lexicon and rule-based.
Includes progress bar and batch processing support.
"""

import re
import json
import sys
import time
from typing import Dict, List, Tuple, Optional, Any
import rag_data  # Import the centralized data module

# =============================================================================
# PROGRESS BAR UTILITY
# =============================================================================

class ProgressBar:
    """Simple progress bar for terminal display."""
    
    def __init__(self, total: int, description: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
    
    def update(self, step: int = 1):
        """Update progress by step amount."""
        self.current += step
        self._display()
    
    def set(self, value: int):
        """Set progress to specific value."""
        self.current = value
        self._display()
    
    def _display(self):
        """Display the progress bar."""
        if self.total == 0:
            percent = 100
        else:
            percent = min(100, (self.current / self.total) * 100)
        
        filled = int(self.width * percent / 100)
        bar = "█" * filled + "░" * (self.width - filled)
        
        elapsed = time.time() - self.start_time
        
        status = f"\r{self.description}: [{bar}] {percent:5.1f}% ({self.current}/{self.total}) {elapsed:.1f}s"
        sys.stdout.write(status)
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line when complete
    
    def complete(self):
        """Mark as complete."""
        self.current = self.total
        self._display()


def show_stage_progress(stages: List[str], current_stage: int):
    """Show progress through processing stages."""
    total = len(stages)
    print(f"\n{'─' * 60}")
    for i, stage in enumerate(stages):
        if i < current_stage:
            icon = "✓"
            color = "\033[92m"  # Green
        elif i == current_stage:
            icon = "▶"
            color = "\033[93m"  # Yellow
        else:
            icon = "○"
            color = "\033[90m"  # Gray
        reset = "\033[0m"
        print(f"  {color}{icon} Stage {i+1}/{total}: {stage}{reset}")
    print(f"{'─' * 60}\n")


# =============================================================================
# SECTION 1: LEXICONS
# =============================================================================

# A. Gendered nouns & pronouns (M/F coded)
# Merging local definitions with rag_data
GENDERED_NOUNS = {
    "setswana": {
        "male": {
            "monna": "man",
            "mosimane": "boy",
            "rra": "father/sir",
            "ntate": "father",
            "banna": "men",
            "basimane": "boys",
            "morwa": "son",
            "malome": "uncle",
        },
        "female": {
            "mosadi": "woman",
            "mosetsana": "girl",
            "mma": "mother/madam",
            "basadi": "women",
            "basetsana": "girls",
            "morwadi": "daughter",
            "rakgadi": "aunt",
        }
    },
    "isizulu": {
        "male": {
            "ubaba": "father",
            "umfana": "boy",
            "indoda": "man",
            "wesilisa": "male",
            "owesilisa": "a male",
            "umkhwenyana": "groom/son-in-law",
            "abafana": "boys",
            "amadoda": "men",
            "umfowethu": "brother",
            "bhuti": "brother",
            "malume": "uncle",
        },
        "female": {
            "umama": "mother",
            "intombazane": "girl",
            "umfazi": "woman",
            "wesifazane": "female",
            "owesifazane": "a female",
            "ugogo": "grandmother",
            "amantombazane": "girls",
            "abesifazane": "women",
            "udadewethu": "sister",
            "sisi": "sister",
            "anti": "aunt",
        }
    }
}

# B. Titles (including compound forms)
TITLES = {
    "setswana": {
        "male": ["rra", "rre", "ntate", "rra-ngaka", "rra-porofesa", "rra-moporesidente", "rra-ceo", "maestro"],
        "female": ["mma", "mme", "mma-ngaka", "mma-porofesa", "miss", "mme-moporesidente"],
    },
    "isizulu": {
        "male": ["mnumzane", "baba", "u-rra", "u-ngaka", "u-porofesa"],
        "female": ["nkosikazi", "nkosazana", "mama", "u-mma"],
    }
}

# B. Gender-neutral human terms
NEUTRAL_TERMS = {
    "setswana": {
        "singular": "motho",
        "plural": "batho",
        "everyone": "motho mongwe le mongwe",
    },
    "isizulu": {
        "singular": "umuntu",
        "plural": "abantu",
        "everyone": "wonke umuntu",
    }
}

# C. Stereotyped roles/verbs/phrases
STEREOTYPED_ACTIONS = {
    "domestic": {
        "setswana": ["apea dijo", "apea", "pheha", "hlatswa dijana", "phepafatsa ntlo", "tlhatswa diaparo"],
        "isizulu": ["pheka", "hlabela", "geza izitsha", "hlanza indlu", "washa izingubo"],
    },
    "academic_leadership": {
        "setswana": ["bala buka", "bala", "ruta", "kaela", "etelela pele", "laola"],
        "isizulu": ["funda", "funda incwadi", "fundisa", "hola", "qondisa", "phatha"],
    },
    "physical_labor": {
        "setswana": ["aga ntlo", "lema", "tlhaba", "tshwara dipitse"],
        "isizulu": ["akha indlu", "lima", "hlaba", "gada izinkomo"],
    }
}

# D. Occupations commonly gender-coded
# Merging with rag_data.OCCUPATIONAL_TERMS
OCCUPATIONS = {
    "setswana": {
        "neutral": {
            "ngaka": "doctor",
            "morutabana": "teacher",
            "moithuti": "student",
            "morekisi": "seller",
            "modiri": "worker",
            "molaodi": "leader",
            "mooki": "nurse",
            "moenjineri": "engineer",
            "moapei": "chef/cook",
            "lesole": "soldier",
        },
        "gendered_forms": {
            "mosadi-ngaka": "ngaka",
            "monna-ngaka": "ngaka",
            "mosadi mooki": "mooki",
            "monna mooki": "mooki",
        }
    },
    "isizulu": {
        "neutral": {
            "udokotela": "doctor",
            "uthisha": "teacher",
            "umfundi": "student",
            "unogada": "security guard",
            "umsebenzi": "worker",
            "umholi": "leader",
            "unesi": "nurse",
            "unjiniyela": "engineer",
            "ushef": "chef",
            "isosha": "soldier",
            "umhloli": "inspector/prospector",
            "ummeli": "lawyer",
            "umshushisi": "prosecutor",
            "ijaji": "judge",
            "intatheli": "journalist",
            "umbhali": "writer/author",
            "umqondisi": "director",
            "umqeqeshi": "coach",
            "ukaputeni": "captain",
        },
        "gendered_forms": {
            "umama udokotela": "udokotela",
            "ubaba udokotela": "udokotela",
            "umama unesi": "unesi",
            "ubaba unesi": "unesi",
            "wesifazane umhlengikazi": "umhlengikazi",
            "wesilisa umshushisi": "umshushisi",
        }
    }
}

# E. Pejorative Terms
# Merging with rag_data.PEJORATIVE_TERMS
PEJORATIVE_TERMS = rag_data.PEJORATIVE_TERMS

# E. Stereotyped adjectives
STEREOTYPED_ADJECTIVES = {
    "feminine_stereotypes": {
        "setswana": ["bonolo", "pelotelele", "bokoa", "maitseo"],
        "isizulu": ["mnene", "nothile", "buthaka", "nomusa"],
    },
    "masculine_stereotypes": {
        "setswana": ["thata", "bogale", "nonofo", "pelokgale"],
        "isizulu": ["qinile", "namandla", "nesibindi", "nobudoda"],
    }
}

# Generalization markers
GENERALIZATION_MARKERS = {
    "setswana": ["ka metlha", "ka gale", "ga go na", "ga ba kgone", "ka tlhago", "fela", "tsotlhe"],
    "isizulu": ["njalo", "ngaso sonke isikhathi", "abakwazi", "ngokwemvelo", "kuphela", "bonke"],
}

# Contrastive conjunctions (for Rule 2)
CONTRASTIVE_CONJUNCTIONS = {
    "setswana": ["fa", "le fa", "mme", "fela"],
    "isizulu": ["uma", "kanti", "kodwa", "ngesikhathi"],
}

# Infantilizing/diminutive patterns
INFANTILIZING_PATTERNS = {
    "setswana": [
        r"basetsana\s+ba\s+bagolo",
        r"mosetsana\s+yo\s+mogolo",
    ],
    "isizulu": [
        r"amantombazane\s+amadala",
        r"intombazane\s+endala",
    ],
}

# =============================================================================
# SECTION 2: PREPROCESSING
# =============================================================================

PREFIXES = {
    "setswana": {
        "noun_class": ["mo-", "ba-", "le-", "ma-", "se-", "di-", "n-", "bo-"],
        "verb": ["o-", "ba-", "a-", "e-", "ke-", "re-", "lo-"],
    },
    "isizulu": {
        "noun_class": ["um-", "aba-", "u-", "o-", "isi-", "izi-", "in-", "izin-", "ama-"],
        "verb": ["u-", "ba-", "a-", "i-", "ngi-", "si-", "ni-"],
    }
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into words."""
    tokens = re.findall(r'\b\w+\b|[.,!?;:]', text)
    return tokens


def identify_prefix(token: str, language: str) -> Tuple[Optional[str], str]:
    """Identify noun-class or verb prefix in a token."""
    token_lower = token.lower()
    prefixes = PREFIXES.get(language, {})
    
    # Combined list of all prefixes, sorted by length descending to match longest first
    all_prefixes = (
        prefixes.get("noun_class", []) + 
        prefixes.get("verb", []) + 
        ["ne-", "na-", "ku-", "kwa-", "wa-", "la-", "lo-", "le-"] # Common Zulu/Setswana conjunctions/prepositions
    )
    
    for prefix in sorted(all_prefixes, key=len, reverse=True):
        prefix_clean = prefix.rstrip('-')
        if token_lower.startswith(prefix_clean):
            # Ensure we don't strip the entire word
            if len(token_lower) > len(prefix_clean):
                return prefix_clean, token_lower[len(prefix_clean):]
    
    return None, token_lower


def stem(token: str, language: str) -> Tuple[str, str]:
    """Reduce word to stem for matching."""
    prefix, remainder = identify_prefix(token, language)
    return remainder, token


def detect_language(text: str) -> str:
    """Auto-detect whether text is Setswana or isiZulu."""
    text_lower = text.lower()
    
    setswana_markers = ["ke", "ba", "o a", "ga", "le", "ka", "mo", "wa", "fa", "kgotsa", "gore", "fela"]
    zulu_markers = ["ngi", "u", "ba", "uma", "ukuthi", "futhi", "kodwa", "noma", "yini", "kanjani"]
    
    setswana_score = sum(1 for m in setswana_markers if f" {m} " in f" {text_lower} " or text_lower.startswith(m + " "))
    zulu_score = sum(1 for m in zulu_markers if f" {m} " in f" {text_lower} " or text_lower.startswith(m + " "))
    
    for word in GENDERED_NOUNS["setswana"]["male"].keys():
        if word in text_lower:
            setswana_score += 2
    for word in GENDERED_NOUNS["setswana"]["female"].keys():
        if word in text_lower:
            setswana_score += 2
    for word in GENDERED_NOUNS["isizulu"]["male"].keys():
        if word in text_lower:
            zulu_score += 2
    for word in GENDERED_NOUNS["isizulu"]["female"].keys():
        if word in text_lower:
            zulu_score += 2
    
    return "isizulu" if zulu_score > setswana_score else "setswana"


def find_gendered_subject(text: str, language: str) -> List[Dict[str, Any]]:
    """Find gendered subjects and titles in the text using stem-based matching."""
    text_lower = text.lower()
    tokens = tokenize(text_lower)
    subjects = []
    lang_nouns = GENDERED_NOUNS.get(language, {})
    lang_titles = TITLES.get(language, {})
    
    # Pre-calculate stems for nouns and titles
    noun_stems = {}
    for gender in ["male", "female"]:
        for word, meaning in lang_nouns.get(gender, {}).items():
            s, _ = stem(word, language)
            noun_stems[s] = {"word": word, "gender": gender, "meaning": meaning}
            
    title_stems = {}
    for gender in ["male", "female"]:
        for title in lang_titles.get(gender, []):
            s, _ = stem(title, language)
            title_stems[s] = {"word": title, "gender": gender}

    # Match tokens against stems
    current_pos = 0
    for token in tokens:
        pos = text_lower.find(token, current_pos)
        current_pos = pos + len(token)
        
        s, _ = stem(token, language)
        
        if s in noun_stems:
            subjects.append({
                "word": token,
                "gender": noun_stems[s]["gender"],
                "position": pos,
                "original": text[pos:pos+len(token)],
                "meaning": noun_stems[s]["meaning"],
                "type": "noun"
            })
        elif s in title_stems:
            subjects.append({
                "word": token,
                "gender": title_stems[s]["gender"],
                "position": pos,
                "original": text[pos:pos+len(token)],
                "meaning": title_stems[s]["word"],
                "type": "title"
            })
    
    return sorted(subjects, key=lambda x: x["position"])


def find_stereotyped_actions(text: str, language: str) -> List[Dict[str, Any]]:
    """Find stereotyped actions/verbs in the text."""
    text_lower = text.lower()
    actions = []
    
    for category, lang_actions in STEREOTYPED_ACTIONS.items():
        for phrase in lang_actions.get(language, []):
            pattern = r'\b' + re.escape(phrase) + r'\b'
            for match in re.finditer(pattern, text_lower):
                actions.append({
                    "phrase": phrase,
                    "category": category,
                    "position": match.start(),
                })
    
    return sorted(actions, key=lambda x: x["position"])


# =============================================================================
# SECTION 3: DETECTION RULES
# =============================================================================

def rule_1_subject_stereotype_match(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 1: Subject-Stereotype Match"""
    explanations = []
    subjects = find_gendered_subject(text, language)
    actions = find_stereotyped_actions(text, language)
    
    for subject in subjects:
        for action in actions:
            if action["position"] > subject["position"]:
                is_domestic = action["category"] == "domestic"
                is_academic = action["category"] == "academic_leadership"
                
                reason = None
                if subject["gender"] == "female" and is_domestic:
                    reason = "Female subject assigned domestic work."
                elif subject["gender"] == "male" and is_academic:
                    reason = "Male subject assigned intellectual/leadership work."
                
                if reason:
                    explanations.append({
                        "span": f"{subject['original']} ... {action['phrase']}",
                        "rule_triggered": "Subject–Stereotype Match",
                        "reason": reason
                    })
    
    return explanations


def rule_2_contrastive_gender_roles(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 2: Contrastive Gender Roles"""
    explanations = []
    text_lower = text.lower()
    
    conjunctions = CONTRASTIVE_CONJUNCTIONS.get(language, [])
    subjects = find_gendered_subject(text, language)
    actions = find_stereotyped_actions(text, language)
    
    male_subjects = [s for s in subjects if s["gender"] == "male"]
    female_subjects = [s for s in subjects if s["gender"] == "female"]
    
    if male_subjects and female_subjects and len(actions) >= 2:
        for conj in conjunctions:
            if f" {conj} " in f" {text_lower} ":
                female_actions = []
                male_actions = []
                
                for action in actions:
                    closest_subject = None
                    closest_dist = float('inf')
                    for s in subjects:
                        dist = action["position"] - s["position"]
                        if 0 < dist < closest_dist:
                            closest_dist = dist
                            closest_subject = s
                    
                    if closest_subject:
                        if closest_subject["gender"] == "female":
                            female_actions.append(action)
                        else:
                            male_actions.append(action)
                
                female_domestic = any(a["category"] == "domestic" for a in female_actions)
                male_academic = any(a["category"] == "academic_leadership" for a in male_actions)
                
                if female_domestic and male_academic:
                    explanations.append({
                        "span": f"{female_subjects[0]['original']} ... {conj} ... {male_subjects[0]['original']}",
                        "rule_triggered": "Contrastive Gender Roles",
                        "reason": "Female subject assigned domestic work while male subject assigned academic/leadership work."
                    })
                    break
    
    return explanations


def rule_3_unnecessary_gender_marking(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 3: Unnecessary Gender Marking"""
    explanations = []
    text_lower = text.lower()
    
    occupations = OCCUPATIONS.get(language, {})
    gendered_forms = occupations.get("gendered_forms", {})
    
    for gendered, neutral in gendered_forms.items():
        if gendered in text_lower:
            explanations.append({
                "span": gendered,
                "rule_triggered": "Unnecessary Gender Marking",
                "reason": f"Occupation '{gendered}' unnecessarily marked with gender. Use neutral form '{neutral}' instead."
            })
    
    return explanations


def rule_4_generalizations(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 4: Generalizations"""
    explanations = []
    text_lower = text.lower()
    
    subjects = find_gendered_subject(text, language)
    markers = GENERALIZATION_MARKERS.get(language, [])
    
    for subject in subjects:
        for marker in markers:
            pattern = rf'\b{re.escape(subject["word"])}\b.*\b{re.escape(marker)}\b|\b{re.escape(marker)}\b.*\b{re.escape(subject["word"])}\b'
            if re.search(pattern, text_lower):
                explanations.append({
                    "span": f"{subject['original']} ... {marker}",
                    "rule_triggered": "Generalization",
                    "reason": f"Making generalized claim about {subject['gender']}s using '{marker}'."
                })
    
    return explanations


def rule_5_diminutives(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 5: Diminutives or Infantilizing Terms"""
    explanations = []
    text_lower = text.lower()
    patterns = INFANTILIZING_PATTERNS.get(language, [])
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            explanations.append({
                "span": match.group(),
                "rule_triggered": "Diminutive/Infantilizing",
                "reason": "Using child-coded terms for adults."
            })
    
    return explanations


def rule_6_asymmetrical_ordering(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 6: Asymmetrical Ordering (Male Firstness)"""
    explanations = []
    text_lower = text.lower()
    subjects = find_gendered_subject(text, language)
    
    # Look for patterns like "male and female" or "male, female"
    for i in range(len(subjects) - 1):
        s1 = subjects[i]
        s2 = subjects[i+1]
        
        if s1["gender"] == "male" and s2["gender"] == "female":
            # Check if they are close (within 15 chars)
            if s2["position"] - (s1["position"] + len(s1["word"])) < 15:
                explanations.append({
                    "span": f"{s1['original']} ... {s2['original']}",
                    "rule_triggered": "Asymmetrical Ordering (Male Firstness)",
                    "reason": "Male term consistently placed before female term."
                })
    
    return explanations


def rule_7_pejorative_association(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 7: Pejorative Association (Stem-based)"""
    explanations = []
    text_lower = text.lower()
    tokens = tokenize(text_lower)
    subjects = find_gendered_subject(text, language)
    pejorative_list = PEJORATIVE_TERMS.get(language, [])
    
    # Pre-calculate pejorative stems
    pej_stems = {}
    for p in pejorative_list:
        s, _ = stem(p, language)
        pej_stems[s] = p

    # Find pejoratives in tokens
    found_pejoratives = []
    current_pos = 0
    for token in tokens:
        pos = text_lower.find(token, current_pos)
        current_pos = pos + len(token)
        s, _ = stem(token, language)
        if s in pej_stems:
            found_pejoratives.append({"word": token, "stem": s, "pos": pos})

    for subject in subjects:
        for pej in found_pejoratives:
            # Check if pejorative is near the subject (within 40 chars)
            if abs(subject["position"] - pej["pos"]) < 40:
                explanations.append({
                    "span": text[min(subject["position"], pej["pos"]):max(subject["position"]+len(subject["word"]), pej["pos"]+len(pej["word"]))],
                    "rule_triggered": "Pejorative Association",
                    "reason": f"Gendered subject '{subject['word']}' associated with pejorative term '{pej['word']}'."
                })
    
    return explanations


def rule_8_translation_bias(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 8: Translation Bias (Gendered pronouns for neutral terms)"""
    # This rule requires the English translation, which isn't always available in 'analyze'
    # For now, we'll skip it or implement it if we can pass the translation
    return []


def rule_9_named_entity_bias(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 9: Named Entity Bias"""
    explanations = []
    text_lower = text.lower()
    
    # Common names associated with stereotypes in the dataset
    biased_names = {
        "thandi": "female",
        "lerato": "female",
        "palesa": "female",
        "thabo": "male",
        "mpho": "male",
        "kabelo": "male"
    }
    
    for name, gender in biased_names.items():
        if name in text_lower:
            # Check if associated with a stereotyped action
            lang_actions = STEREOTYPED_ACTIONS.get(language, {}).get(gender, {})
            for action in lang_actions:
                if action in text_lower:
                    explanations.append({
                        "span": f"{name} ... {action}",
                        "rule_triggered": "Named Entity Bias",
                        "reason": f"Name '{name}' associated with gendered stereotype '{action}'."
                    })
    
    return explanations

def rule_10_stereotypical_pronominalization(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 10: Stereotypical Pronominalization (New)"""
    explanations = []
    text_lower = text.lower()
    
    # Use terms from rag_data
    terms = rag_data.PRONOMINALIZATION_TERMS
    
    for category, words in terms.items():
        for word in words:
            if word in text_lower:
                explanations.append({
                    "span": word,
                    "rule_triggered": "Stereotypical Pronominalization",
                    "reason": f"Use of culturally loaded term '{word}' associated with {category.replace('_', ' ')}."
                })
                
    return explanations

def rule_11_implicit_bias(text: str, language: str) -> List[Dict[str, Any]]:
    """Rule 11: Implicit Bias (New)"""
    explanations = []
    text_lower = text.lower()
    
    patterns = rag_data.BIAS_PATTERNS.get("capability_assumptions", [])
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            explanations.append({
                "span": match.group(),
                "rule_triggered": "Implicit Bias",
                "reason": "Implicit assumption about capability detected."
            })
            
    return explanations


# =============================================================================
# SECTION 4: REWRITE TEMPLATES
# =============================================================================

def template_a_inclusive_reframe(text: str, language: str, female_subject: str, male_subject: str, 
                                  verb1: str, verb2: str) -> str:
    """Template A: Inclusive Reframing"""
    if language == "setswana":
        return f"{female_subject.capitalize()} le {male_subject} ba ka {verb1} kgotsa ba {verb2}."
    else:
        return f"{female_subject.capitalize()} no {male_subject} bangakwazi ukwenza u{verb1} noma u{verb2}."


def template_b_neutral_replacement(text: str, language: str) -> str:
    """Template B: Neutral-term Replacement"""
    result = text
    lang_nouns = GENDERED_NOUNS.get(language, {})
    neutral = NEUTRAL_TERMS.get(language, {})
    all_gendered = {**lang_nouns.get("male", {}), **lang_nouns.get("female", {})}
    
    for gendered, meaning in all_gendered.items():
        pattern = r'\b' + re.escape(gendered) + r'\b'
        result = re.sub(pattern, neutral["singular"], result, flags=re.IGNORECASE)
    
    return result


def template_c_remove_gender_marking(text: str, language: str) -> str:
    """Template C: Remove Gender Marking from Occupations"""
    result = text
    occupations = OCCUPATIONS.get(language, {})
    gendered_forms = occupations.get("gendered_forms", {})
    
    for gendered, neutral in gendered_forms.items():
        pattern = r'\b' + re.escape(gendered) + r'\b'
        result = re.sub(pattern, neutral, result, flags=re.IGNORECASE)
    
    return result


def template_d_pluralization(text: str, language: str) -> str:
    """Template D: Pluralization for Neutral Pronouns"""
    result = text
    if language == "setswana":
        result = re.sub(r'\bo\s+a\s+', 'ba a ', result)
        result = re.sub(r'\bo\s+', 'ba ', result)
    else:
        result = re.sub(r'\bu\s+', 'ba ', result)
    return result


def template_e_everyone_pronoun(text: str, language: str) -> str:
    """Template E: Both-Gender or Neutral Pronouns"""
    result = text
    neutral = NEUTRAL_TERMS.get(language, {})
    lang_nouns = GENDERED_NOUNS.get(language, {})
    all_gendered = list(lang_nouns.get("male", {}).keys()) + list(lang_nouns.get("female", {}).keys())
    
    for gendered in all_gendered:
        pattern = r'\b' + re.escape(gendered) + r'\b'
        if re.search(pattern, result, flags=re.IGNORECASE):
            result = re.sub(pattern, neutral["everyone"], result, flags=re.IGNORECASE)
            break
    
    return result


# =============================================================================
# SECTION 5: REWRITER
# =============================================================================

def generate_rewrite(text: str, language: str, explanations: List[Dict[str, Any]]) -> str:
    """Generate a rewritten version based on detected biases."""
    if not explanations:
        return text
    
    rewritten = text
    rules_triggered = [e["rule_triggered"] for e in explanations]
    
    subjects = find_gendered_subject(text, language)
    actions = find_stereotyped_actions(text, language)
    
    male_subjects = [s for s in subjects if s["gender"] == "male"]
    female_subjects = [s for s in subjects if s["gender"] == "female"]
    
    if "Contrastive Gender Roles" in rules_triggered or "Subject–Stereotype Match" in rules_triggered:
        if male_subjects and female_subjects and len(actions) >= 2:
            female_subj = female_subjects[0]["original"]
            male_subj = male_subjects[0]["original"]
            action_phrases = [a["phrase"] for a in actions]
            if len(action_phrases) >= 2:
                rewritten = template_a_inclusive_reframe(
                    text, language, female_subj, male_subj,
                    action_phrases[0], action_phrases[1]
                )
        else:
            rewritten = template_b_neutral_replacement(text, language)
    elif "Unnecessary Gender Marking" in rules_triggered:
        rewritten = template_c_remove_gender_marking(text, language)
    elif "Generalization" in rules_triggered:
        rewritten = template_e_everyone_pronoun(text, language)
    elif "Diminutive/Infantilizing" in rules_triggered:
        rewritten = template_b_neutral_replacement(text, language)
    elif "Asymmetrical Ordering (Male Firstness)" in rules_triggered:
        # Simple swap for asymmetrical ordering
        if len(male_subjects) >= 1 and len(female_subjects) >= 1:
            m_subj = male_subjects[0]
            f_subj = female_subjects[0]
            if m_subj["position"] < f_subj["position"]:
                # This is a very basic swap, might need more logic for complex sentences
                rewritten = text.replace(m_subj["original"], "TEMP_M").replace(f_subj["original"], m_subj["original"]).replace("TEMP_M", f_subj["original"])
    elif "Pejorative Association" in rules_triggered:
        rewritten = template_b_neutral_replacement(text, language)
        # Also remove pejorative terms
        pejoratives = PEJORATIVE_TERMS.get(language, [])
        for p in pejoratives:
            rewritten = re.sub(r'\b' + re.escape(p) + r'\b', '', rewritten, flags=re.IGNORECASE).strip()
    elif "Named Entity Bias" in rules_triggered:
        # For named entity bias, we try to use a neutral description or just keep the name but neutralize the context
        rewritten = template_b_neutral_replacement(text, language)
    elif "Stereotypical Pronominalization" in rules_triggered:
        # Try to retrieve a better example using RAG
        examples = rag_data.retrieve_examples("Stereotypical Pronominalization", k=1)
        if examples:
            # This is a bit of a hack, but we can't really "rewrite" cultural idioms without an LLM
            # So we return the text with a note, or try to apply a generic neutral template
            # For now, let's use template_b
            rewritten = template_b_neutral_replacement(text, language)
    else:
        rewritten = template_b_neutral_replacement(text, language)
    
    return rewritten


# =============================================================================
# SECTION 6: MAIN PIPELINE
# =============================================================================

def analyze(text: str, language: Optional[str] = None, show_progress: bool = False) -> Dict[str, Any]:
    """
    Main analysis function with optional progress display.
    """
    stages = [
        "Language Detection",
        "Preprocessing & Tokenization", 
        "Subject & Action Scanning",
        "Rule Application",
        "Rewrite Generation"
    ]
    
    if show_progress:
        show_stage_progress(stages, 0)
        
    # Stage 1: Language Detection
    if not language:
        language = detect_language(text)
    
    if show_progress:
        show_stage_progress(stages, 1)
        
    # Stage 2: Preprocessing
    # (Implicitly done in find functions)
    
    if show_progress:
        show_stage_progress(stages, 2)
        
    # Stage 3: Scanning
    subjects = find_gendered_subject(text, language)
    actions = find_stereotyped_actions(text, language)
    
    if show_progress:
        show_stage_progress(stages, 3)
        
    # Stage 4: Rule Application
    explanations = []
    
    rules = [
        rule_1_subject_stereotype_match,
        rule_2_contrastive_gender_roles,
        rule_3_unnecessary_gender_marking,
        rule_4_generalizations,
        rule_5_diminutives,
        rule_6_asymmetrical_ordering,
        rule_7_pejorative_association,
        rule_8_translation_bias,
        rule_9_named_entity_bias,
        rule_10_stereotypical_pronominalization, # New
        rule_11_implicit_bias # New
    ]
    
    if show_progress:
        pb = ProgressBar(len(rules), "Applying Rules")
    
    for i, rule in enumerate(rules):
        try:
            result = rule(text, language)
            if result:
                explanations.extend(result)
        except Exception as e:
            # Fail gracefully on individual rules
            pass
        if show_progress:
            pb.update()
            time.sleep(0.05) # Visual delay
            
    if show_progress:
        pb.complete()
        show_stage_progress(stages, 4)
        
    # Stage 5: Rewrite
    rewrite = generate_rewrite(text, language, explanations)
    
    return {
        "text": text,
        "language": language,
        "has_bias": len(explanations) > 0,
        "explanations": explanations,
        "rewrite": rewrite
    }


def batch_analyze(texts: List[str]) -> List[Dict[str, Any]]:
    """Analyze a batch of texts."""
    results = []
    pb = ProgressBar(len(texts), "Batch Processing")
    
    for text in texts:
        results.append(analyze(text))
        pb.update()
        
    pb.complete()
    return results


if __name__ == "__main__":
    # Simple CLI test
    if len(sys.argv) > 1:
        text_input = sys.argv[1]
        print(json.dumps(analyze(text_input, show_progress=True), indent=2))
    else:
        print("Usage: python rule_based_detector.py 'Your text here'")
