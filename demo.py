#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Demo Script for Rule-Based Bias Correction System
Shows step-by-step process with detailed visualization
No LLM dependency - purely rule-based detection and rewriting
"""

import sys
import io
import time
import json

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rule_based_detector import (
    analyze,
    detect_language,
    find_gendered_subject,
    find_stereotyped_actions,
    GENDERED_NOUNS,
    STEREOTYPED_ACTIONS,
    NEUTRAL_TERMS
)

# --- Configuration ---
DEMO_DELAY = 0.5  # Seconds between steps for dramatic effect

# --- Helper Functions ---
def print_header(text, char="="):
    """Print a formatted header"""
    width = 70
    print("\n" + char * width)
    print(f"{text.center(width)}")
    print(char * width + "\n")

def print_step(step_num, title, delay=True):
    """Print a step header"""
    print(f"\n{'─' * 70}")
    print(f"📍 STEP {step_num}: {title}")
    print(f"{'─' * 70}")
    if delay:
        time.sleep(DEMO_DELAY)

def print_substep(text, icon="  →"):
    """Print a substep with icon"""
    print(f"{icon} {text}")

def print_result(label, value, color="green"):
    """Print a result with formatting"""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    color_code = colors.get(color, colors["reset"])
    reset = colors["reset"]
    print(f"  {label}: {color_code}{value}{reset}")

def demo_correction(biased_text, language=None):
    """
    Enhanced demo mode with step-by-step visualization
    Uses rule-based detection and rewriting (no LLM)
    """
    print_header("🎯 RULE-BASED BIAS CORRECTION DEMONSTRATION", "=")
    
    print_result("Input Text", f'"{biased_text}"', "blue")
    time.sleep(DEMO_DELAY)
    
    # STEP 1: Language Detection
    print_step(1, "LANGUAGE DETECTION")
    detected_lang = detect_language(biased_text) if language is None else language
    lang_display = "Setswana" if detected_lang == "setswana" else "isiZulu"
    print_result("Detected Language", lang_display, "green")
    time.sleep(DEMO_DELAY)
    
    # STEP 2: Preprocessing & Lexicon Matching
    print_step(2, "PREPROCESSING & LEXICON MATCHING")
    
    print_substep("Scanning for gendered subjects...")
    subjects = find_gendered_subject(biased_text, detected_lang)
    if subjects:
        for subj in subjects:
            gender_icon = "♂" if subj["gender"] == "male" else "♀"
            print_substep(f"{gender_icon} Found: '{subj['word']}' ({subj['gender']}) - {subj['meaning']}", "    •")
    else:
        print_substep("No gendered subjects found", "    ○")
    
    print_substep("Scanning for stereotyped actions...")
    actions = find_stereotyped_actions(biased_text, detected_lang)
    if actions:
        for action in actions:
            category_icon = "🏠" if action["category"] == "domestic" else "📚" if action["category"] == "academic_leadership" else "🔧"
            print_substep(f"{category_icon} Found: '{action['phrase']}' ({action['category']})", "    •")
    else:
        print_substep("No stereotyped actions found", "    ○")
    
    time.sleep(DEMO_DELAY)
    
    # STEP 3: Rule Application
    print_step(3, "APPLYING DETECTION RULES")
    print_substep("Rule 1: Subject-Stereotype Match")
    print_substep("Rule 2: Contrastive Gender Roles")
    print_substep("Rule 3: Unnecessary Gender Marking")
    print_substep("Rule 4: Generalizations")
    print_substep("Rule 5: Diminutives/Infantilizing")
    time.sleep(DEMO_DELAY)
    
    # STEP 4: Full Analysis
    print_step(4, "ANALYSIS & REWRITING")
    result = analyze(biased_text, language)
    
    if result["detected_bias"]:
        print_result("Status", "✓ BIAS DETECTED", "yellow")
        print(f"\n  📋 Triggered Rules:")
        for exp in result["explanations"]:
            print_substep(f"Rule: {exp['rule_triggered']}", "    ⚠")
            print_substep(f"Span: \"{exp['span']}\"", "      ")
            print_substep(f"Reason: {exp['reason']}", "      ")
    else:
        print_result("Status", "No bias patterns detected", "green")
    
    time.sleep(DEMO_DELAY)
    
    # STEP 5: Rewrite Generation
    print_step(5, "REWRITE GENERATION (Rule-Based)")
    print_substep("Applying appropriate rewrite template...")
    if result["detected_bias"]:
        rules = [e["rule_triggered"] for e in result["explanations"]]
        if "Contrastive Gender Roles" in rules or "Subject–Stereotype Match" in rules:
            print_substep("Template A: Inclusive Reframing", "    →")
        elif "Unnecessary Gender Marking" in rules:
            print_substep("Template C: Remove Gender Marking", "    →")
        elif "Generalization" in rules:
            print_substep("Template E: Everyone Pronoun", "    →")
        else:
            print_substep("Template B: Neutral Replacement", "    →")
    else:
        print_substep("No rewrite needed", "    ○")
    
    time.sleep(DEMO_DELAY)
    
    # FINAL RESULTS
    print_header("📋 FINAL RESULTS", "=")
    
    print(f"  {'Original (Biased):':<20} \"{biased_text}\"")
    print(f"  {'Corrected:':<20} \"{result['suggested_rewrite']}\"")
    print(f"\n  {'Language:':<20} {lang_display}")
    print(f"  {'Bias Detected:':<20} {result['detected_bias']}")
    print(f"  {'Rules Triggered:':<20} {len(result['explanations'])}")
    
    print("\n" + "=" * 70)
    print("\n  📄 JSON Output:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "=" * 70 + "\n")
    
    return result

def run_demo_mode():
    """Interactive demo mode"""
    print_header("🚀 RULE-BASED BIAS CORRECTION - DEMO MODE", "=")
    print("  This mode shows the complete step-by-step process")
    print("  of detecting and correcting bias in Setswana/isiZulu text.\n")
    print("  ⚡ No LLM required - purely rule-based!\n")
    print("  Commands:")
    print("    • Enter text to analyze")
    print("    • Type 'zu:' before text for Zulu (e.g., 'zu: your text')")
    print("    • Type 'quit' or 'exit' to stop\n")
    print("=" * 70)
    
    while True:
        print("\n")
        user_input = input("💬 Enter text to analyze: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print_header("👋 Demo Complete - Thank you!", "=")
            break
        
        if not user_input:
            print("  ⚠ Please enter some text.\n")
            continue
        
        # Check for language prefix
        language = None
        if user_input.lower().startswith("zu:"):
            language = "isizulu"
            user_input = user_input[3:].strip()
        elif user_input.lower().startswith("tn:"):
            language = "setswana"
            user_input = user_input[3:].strip()
        
        # Run the demo
        demo_correction(user_input, language)

def run_quick_demo():
    """Run a quick demo with predefined examples"""
    print_header("🎬 QUICK DEMO - Predefined Examples", "=")
    
    examples = [
        ("Mosetsana o apea dijo fa mosimane a bala buka.", None),
        ("Monna o a nama fa mosadi a pheha.", None),
        ("zu: Intombazane ipheka kanti umfana ufunda.", "isizulu"),
    ]
    
    for i, (text, lang) in enumerate(examples, 1):
        print(f"\n\n{'#' * 70}")
        print(f"  DEMO EXAMPLE {i}/{len(examples)}")
        print(f"{'#' * 70}\n")
        time.sleep(1)
        
        demo_correction(text, lang)
        
        if i < len(examples):
            input("\n  Press Enter to continue to next example...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            # Quick demo with predefined examples
            run_quick_demo()
        elif sys.argv[1] == "test":
            # Single test
            test_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Mosetsana o apea dijo fa mosimane a bala buka."
            demo_correction(test_text)
        else:
            print("Usage:")
            print("  python demo.py           # Interactive demo mode")
            print("  python demo.py quick     # Quick demo with predefined examples")
            print("  python demo.py test <text>  # Test single sentence")
    else:
        # Interactive mode
        run_demo_mode()
