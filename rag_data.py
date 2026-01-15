"""
RAG (Retrieval-Augmented Generation) Data for Bias Correction
Contains ground truth examples, occupation terms, and bias detection lexicons

This file loads the full ground truth from ground_truth.json
"""

import json

def load_ground_truth(json_path="ground_truth.json"):
    """Load ground truth data from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to list format
        examples = []
        for key, value in data.items():
            examples.append({
                "language": value.get("language", "tn"),
                "bias_category": value.get("bias_category", "Unknown"),
                "biased_text": value.get("biased_text", ""),
                "bias_free_text": value.get("bias_free_text", ""),
                "id": value.get("id", key),
                "domain": value.get("domain", ""),
                "meta": value.get("meta", {})
            })
        
        return examples
    except FileNotFoundError:
        print(f"Warning: {json_path} not found. Using hardcoded examples.")
        return FALLBACK_DATA

# Fallback data if JSON file not found
FALLBACK_DATA = [
    {
        "language": "tn",
        "bias_category": "Occupational & Role Stereotyping",
        "biased_text": "Monna thotse o a nama",
        "bias_free_text": "Motho mongwe le mongwe ke thotse o a anama",
        "id": "fallback-1",
        "domain": "educational"
    }
]

# Load ground truth from JSON file
GROUND_TRUTH_DATA = load_ground_truth()

# --- Custom Lexicons for Bias Detection ---

# Occupational terms in Setswana and Zulu
OCCUPATIONAL_TERMS = {
    "traditional_male": [
        "motshameki", "motlhankedi", "motsekarabo",  # driver, guard, carpenter
        "mothapi", "motlhagisi", "motlhobi",  # builder, mechanic, miner
        "unjiniyela", "umshayeli", "umakhi", "umphathi", "usosayensi", # Zulu: engineer, driver, builder, manager, scientist
        "umshushisi", "ummeli", "ijaji", "iphoyisa" # Zulu: prosecutor, lawyer, judge, police
    ],
    "traditional_female": [
        "modiredibala", "morutišana", "morutisi",  # nurse, nurse (formal), teacher
        "mooki", "moapei", "motlhokomedi", # nurse, cook, caregiver
        "unesi", "uthisha", "umhlengikazi", "umama wekhaya" # Zulu: nurse, teacher, nurse, housewife
    ],
    "gender_neutral": [
        "sekwena", "matlhale", "serutiši",  # computer, intelligence, assistant
        "ngaka", "molaodi", "modiri", # doctor, director, worker
        "udokotela", "umqondisi", "umsebenzi" # Zulu: doctor, director, worker
    ]
}

# Gendered terms
GENDERED_TERMS = {
    "male_identifiers": [
        "monna", "ngwana", "botona", "mosemane", "rre", "ntate", "malome", "rra", # Setswana
        "indoda", "umfana", "ubaba", "umlisa", "abesilisa", "amakhwenkwe", "abafana", "umkhwenyana", "bhuti", "malume" # Zulu
    ],
    "female_identifiers": [
        "mosadi", "mosetsana", "botshadi", "mma", "tate", "mme", "rakgadi", # Setswana
        "umfazi", "intombazane", "umama", "insizwa", "abesifazane", "amantombazane", "amankazana", "umuntu wesifazane", "sisi", "anti", "ugogo" # Zulu
    ],
    "neutral_replacements": [
        "motho", "ngwana", "batlhokwa", "umuntu", "abantu", "ilunga"
    ]
}

# Pejorative terms (from CSV analysis)
PEJORATIVE_TERMS = {
    "setswana": ["isiwula", "mbumbulu", "ohlwempu", "segafi", "sematla", "setlaela", "ngaletseng"],
    "isizulu": [
        "isiwula", "isigebengu", "mbumbulu", "ohlwempu", "ubunuku", "isishimane", "isidididi",
        "ukuqoqoza", "ongenamqondo", "ongemthetho", "isithunzi", "ubudedengu", "ubuthakathaka"
    ]
}

# Pronominalization terms (Cultural names/idioms)
PRONOMINALIZATION_TERMS = {
    "wealth_related": ["khumoetsile", "khumo", "humo"],
    "leadership_related": ["kgosietsile", "kgosi", "morena"],
    "marriage_related": ["lobola", "magadi", "bogadi", "lerapo"]
}

# Common biased phrases and patterns
BIAS_PATTERNS = {
    "occupational_stereotyping": [
        r"\b(mosadi|monna)\s+\w+\s+(wa|yo)\s+\w+",  # gendered occupational roles
        r"\b(monna|mosadi)\s+\w+\s+\w+",  # gender + role patterns
        r"\b(indoda|umfazi)\s+\w+", # Zulu gender + role
    ],
    "capability_assumptions": [
        r"\b(kgona|go kgona)\s+\w+",  # assumptions about ability
        r"\b(ba kgona|ha ba kgone)",  # gendered capability statements
        r"\b(akakwazi|uyakwazi)\s+\w+", # Zulu capability
    ],
    "honorific_asymmetry": [
        r"\b(rra|mma)-[a-zA-Z]+", # Compound titles like Rra-Ngaka
        r"\b(u-?mnumzane|u-?nkosikazi)\s+[a-zA-Z]+" # Zulu titles
    ]
}

# Bias categories mapping (updated for all categories in ground truth)
BIAS_CATEGORIES = {
    "Occupational & Role Stereotyping": {
        "keywords": [
            # Setswana occupational and role terms
            "motshameki", "morutišana", "motlhankedi", "thotse", "selepe", "motho", "manamagadi",
            "mma seapei", "mosala gae", "poo", "lesaka", "dinke", "mabogo",
            # Zulu occupational and academic terms
            "ubunjiniyela", "ifisiksi", "ezobuciko", "isayensi", "ikhompyutha", 
            "ezemidlalo", "ezomnotho", "ukufunda", "bangcono", "akufanele",
            # Common phrases
            "monna", "mosadi", "amakhwenkwe", "abesilisa", "abesifazane", "amantombazane"
        ],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Occupational & Role Stereotyping"]
    },
    "Gender": {
        "keywords": ["mosetsana", "mosimane", "intombazane", "umfana"],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Gender"]
    },
    "Gendered Wording": {
        "keywords": ["segametsi", "mme", "mmagwana", "motsadi", "ga a nyala mosadi", "owesifazane", "owesilisa"],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Gendered Wording"]
    },
    "Stereotypical Pronominalization": {
        "keywords": ["khumoetsile", "kgosietsile", "lerapo", "lobola", "lerapo", "magadi"],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Stereotypical Pronominalization"]
    },
    "Honorific & Title Asymmetry": {
        "keywords": ["rra-", "mma-", "u-mnumzane", "u-nkosikazi"],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Honorific & Title Asymmetry"]
    },
    "Semantic Derogation": {
        "keywords": ["isiwula", "isigebengu", "mbumbulu", "ohlwempu", "ubunuku"],
        "examples": [ex for ex in GROUND_TRUTH_DATA if ex["bias_category"] == "Semantic Derogation"]
    }
}

def retrieve_examples(category, k=2):
    """
    Retrieves 'k' examples from ground truth for a specific category.
    This is the "Retrieval" part of RAG.
    """
    examples = []
    
    # Try to get examples from the specific category
    for entry in GROUND_TRUTH_DATA:
        if entry.get('bias_category') == category:
            examples.append({
                "biased": entry['biased_text'],
                "corrected": entry['bias_free_text']
            })
            if len(examples) >= k:
                break
    
    # Fallback: get any examples if category doesn't match
    if not examples:
        for entry in GROUND_TRUTH_DATA[:k]:
            examples.append({
                "biased": entry['biased_text'],
                "corrected": entry['bias_free_text']
            })
    
    return examples

def get_category_from_text(text):
    """
    Attempts to identify the bias category from the input text
    """
    text_lower = text.lower()
    
    # Check keywords for each category
    for category, data in BIAS_CATEGORIES.items():
        for keyword in data["keywords"]:
            if keyword in text_lower:
                return category
    
    # Default category
    return "General Bias"

