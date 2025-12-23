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
PEJORATIVE_TERMS = {
    "setswana": ["isiwula", "mbumbulu", "ohlwempu", "segafi", "sematla", "setlaela"],
    "isizulu": [
        "isiwula", "isigebengu", "mbumbulu", "ohlwempu", "ubunuku", "isishimane", "isidididi",
        "ukuqoqoza", "ongenamqondo", "ongemthetho", "isithunzi", "ohlwempu"
    ],
}

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
        "Lexicon Matching",
        "Rule Application",
        "Rewrite Generation"
    ]
    
    if show_progress:
        show_stage_progress(stages, 0)
    
    # Step 1: Detect language
    if language is None:
        language = detect_language(text)
    elif language in ["tn", "st"]:
        language = "setswana"
    elif language in ["zu", "zulu"]:
        language = "isizulu"
    
    if show_progress:
        time.sleep(0.2)
        show_stage_progress(stages, 1)
    
    # Step 2: Preprocessing (implicit in rule functions)
    if show_progress:
        time.sleep(0.2)
        show_stage_progress(stages, 2)
    
    # Step 3: Lexicon matching (implicit in rule functions)
    if show_progress:
        time.sleep(0.2)
        show_stage_progress(stages, 3)
    
    # Step 4: Apply all rules
    all_explanations = []
    all_explanations.extend(rule_1_subject_stereotype_match(text, language))
    all_explanations.extend(rule_2_contrastive_gender_roles(text, language))
    all_explanations.extend(rule_3_unnecessary_gender_marking(text, language))
    all_explanations.extend(rule_4_generalizations(text, language))
    all_explanations.extend(rule_5_diminutives(text, language))
    all_explanations.extend(rule_6_asymmetrical_ordering(text, language))
    all_explanations.extend(rule_7_pejorative_association(text, language))
    all_explanations.extend(rule_9_named_entity_bias(text, language))
    
    # Deduplicate
    seen = set()
    unique_explanations = []
    for exp in all_explanations:
        key = (exp["span"], exp["rule_triggered"])
        if key not in seen:
            seen.add(key)
            unique_explanations.append(exp)
    
    if show_progress:
        time.sleep(0.2)
        show_stage_progress(stages, 4)
    
    # Step 5: Generate rewrite
    detected_bias = len(unique_explanations) > 0
    suggested_rewrite = generate_rewrite(text, language, unique_explanations) if detected_bias else text
    
    if show_progress:
        time.sleep(0.1)
        print("✓ Processing complete!\n")
    
    return {
        "detected_bias": detected_bias,
        "language_detected": language,
        "explanations": unique_explanations,
        "suggested_rewrite": suggested_rewrite
    }


def analyze_json(text: str, language: Optional[str] = None) -> str:
    """Convenience function that returns JSON string."""
    result = analyze(text, language)
    return json.dumps(result, ensure_ascii=False, indent=2)


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def process_batch(input_file: str, output_file: Optional[str] = None, show_progress: bool = True) -> List[Dict[str, Any]]:
    """
    Process multiple texts from a JSON file.
    
    Input JSON format:
    {
        "items": [
            {"id": "1", "text": "...", "language": "tn"},
            {"id": "2", "text": "...", "language": "zu"},
            ...
        ]
    }
    
    Returns list of results with original item data plus analysis.
    """
    print(f"\n{'=' * 60}")
    print("BATCH PROCESSING MODE")
    print(f"{'=' * 60}")
    print(f"Input file: {input_file}")
    
    # Load input
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get("items", [])
    total = len(items)
    print(f"Found {total} items to process\n")
    
    results = []
    
    if show_progress:
        progress = ProgressBar(total, "Processing")
    
    for i, item in enumerate(items):
        text = item.get("text", "")
        language = item.get("language")
        item_id = item.get("id", str(i + 1))
        
        # Analyze
        result = analyze(text, language, show_progress=False)
        
        # Combine with original item data
        output_item = {
            "id": item_id,
            "original_text": text,
            **result
        }
        results.append(output_item)
        
        if show_progress:
            progress.update()
    
    # Summary
    biased_count = sum(1 for r in results if r["detected_bias"])
    print(f"\n{'─' * 60}")
    print(f"BATCH SUMMARY:")
    print(f"  Total processed:  {total}")
    print(f"  Bias detected:    {biased_count}")
    print(f"  No bias:          {total - biased_count}")
    print(f"{'─' * 60}")
    
    # Save output
    if output_file:
        output_data = {
            "summary": {
                "total": total,
                "biased": biased_count,
                "clean": total - biased_count
            },
            "results": results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {output_file}")
    
    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        RULE-BASED BIAS DETECTION SYSTEM                          ║
║        Supports Setswana (tn) and isiZulu (zu)                   ║
╠══════════════════════════════════════════════════════════════════╣
║  USAGE:                                                          ║
║                                                                   ║
║  Single text analysis:                                           ║
║    python rule_based_detector.py "<text>"                        ║
║    python rule_based_detector.py --text "<text>"                 ║
║    python rule_based_detector.py --text "<text>" --lang tn       ║
║                                                                   ║
║  Batch processing:                                                ║
║    python rule_based_detector.py --batch input.json              ║
║    python rule_based_detector.py --batch input.json -o out.json  ║
║                                                                   ║
║  Options:                                                         ║
║    --text, -t    Text to analyze                                 ║
║    --lang, -l    Language (tn=Setswana, zu=isiZulu)              ║
║    --batch, -b   Batch input JSON file                           ║
║    --output, -o  Output file for batch results                   ║
║    --progress    Show progress bar (default: on)                 ║
║    --json        Output as JSON only                             ║
║    --help, -h    Show this help                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rule-Based Bias Detection System", add_help=False)
    parser.add_argument("text", nargs="?", help="Text to analyze")
    parser.add_argument("--text", "-t", dest="text_opt", help="Text to analyze")
    parser.add_argument("--lang", "-l", help="Language code (tn/zu)")
    parser.add_argument("--batch", "-b", help="Batch input JSON file")
    parser.add_argument("--output", "-o", help="Output file for batch results")
    parser.add_argument("--json", action="store_true", help="Output as JSON only")
    parser.add_argument("--progress", action="store_true", default=True, help="Show progress")
    parser.add_argument("--help", "-h", action="store_true", help="Show help")
    
    args = parser.parse_args()
    
    if args.help:
        print_usage()
        sys.exit(0)
    
    # Batch mode
    if args.batch:
        results = process_batch(args.batch, args.output, show_progress=True)
        if args.json and not args.output:
            print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # Single text mode
    elif args.text or args.text_opt:
        input_text = args.text or args.text_opt
        
        if args.json:
            # JSON-only output
            result = analyze(input_text, args.lang, show_progress=False)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Full output with progress
            print(f"\n{'=' * 60}")
            print("SINGLE TEXT ANALYSIS")
            print(f"{'=' * 60}")
            print(f"Input: {input_text}\n")
            
            result = analyze(input_text, args.lang, show_progress=True)
            
            print(f"\n{'─' * 60}")
            print("RESULT:")
            print(f"  Bias Detected: {result['detected_bias']}")
            print(f"  Language:      {result['language_detected']}")
            if result['explanations']:
                print(f"\n  Explanations:")
                for exp in result['explanations']:
                    print(f"    • Rule: {exp['rule_triggered']}")
                    print(f"      Span: {exp['span']}")
                    print(f"      Reason: {exp['reason']}")
            print(f"\n  Original:  {input_text}")
            print(f"  Rewritten: {result['suggested_rewrite']}")
            print(f"{'─' * 60}")
            
            print("\n📄 JSON Output:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        # Default example
        print_usage()
        print("\nRunning with default example...\n")
        input_text = "Mosetsana o apea dijo fa mosimane a bala buka."
        result = analyze(input_text, show_progress=True)
        print(f"\nInput: {input_text}")
        print(f"\nOutput:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
