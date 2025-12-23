#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rule-Based Bias Rewriter
Interactive and programmatic interface for bias detection and correction
No LLM dependency - purely rule-based
"""

import sys
import io
import json

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rule_based_detector import (
    analyze,
    analyze_json,
    detect_language,
    find_gendered_subject,
    find_stereotyped_actions,
)


def correct_bias(text, language=None):
    """
    Main function to detect and correct bias in text.
    
    Args:
        text: Input text to analyze
        language: Optional language code ('tn'/'setswana' or 'zu'/'isizulu')
    
    Returns:
        Dict with detected_bias, explanations, and suggested_rewrite
    """
    print(f"=" * 60)
    print(f"--- RULE-BASED BIAS CORRECTION ---")
    print(f"=" * 60)
    print(f"\nInput text: {text}")
    
    # Normalize language code
    if language in ["tn", "st"]:
        language = "setswana"
    elif language in ["zu", "zulu"]:
        language = "isizulu"
    
    # Step 1: Detect language if not provided
    if language is None:
        language = detect_language(text)
    print(f"\n[Step 1] Language: {language}")
    
    # Step 2: Find gendered subjects
    print(f"\n[Step 2] Scanning for gendered subjects...")
    subjects = find_gendered_subject(text, language)
    if subjects:
        for s in subjects:
            print(f"  --> Found: '{s['word']}' ({s['gender']})")
    else:
        print("  --> No gendered subjects found")
    
    # Step 3: Find stereotyped actions
    print(f"\n[Step 3] Scanning for stereotyped actions...")
    actions = find_stereotyped_actions(text, language)
    if actions:
        for a in actions:
            print(f"  --> Found: '{a['phrase']}' ({a['category']})")
    else:
        print("  --> No stereotyped actions found")
    
    # Step 4: Run full analysis
    print(f"\n[Step 4] Applying detection rules...")
    result = analyze(text, language)
    
    if result["detected_bias"]:
        print(f"\n[✓] Bias detected!")
        for exp in result["explanations"]:
            print(f"  --> Rule: {exp['rule_triggered']}")
            print(f"      Reason: {exp['reason']}")
    else:
        print(f"\n[○] No bias patterns detected")
    
    # Step 5: Show result
    print(f"\n[Step 5] Generating rewrite...")
    print(f"\n" + "-" * 60)
    print(f"RESULT:")
    print(f"  Original:  {text}")
    print(f"  Corrected: {result['suggested_rewrite']}")
    print("-" * 60)
    
    return result


def run_interactive():
    """
    Interactive mode: type a sentence and get bias-free output
    """
    print("\n" + "=" * 60)
    print("RULE-BASED BIAS CORRECTION - Interactive Mode")
    print("=" * 60)
    print("\nType a Setswana or isiZulu sentence and receive a bias-free correction.")
    print("Prefix with 'zu:' for isiZulu, 'tn:' for Setswana (auto-detected by default)")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        user_input = input("Enter text: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nExiting... Goodbye!")
            break
        
        if not user_input:
            print("Please enter some text.\n")
            continue
        
        # Check for language prefix
        language = None
        if user_input.lower().startswith("zu:"):
            language = "isizulu"
            user_input = user_input[3:].strip()
        elif user_input.lower().startswith("tn:"):
            language = "setswana"
            user_input = user_input[3:].strip()
        
        # Process the text
        result = correct_bias(user_input, language)
        
        # Print JSON output
        print("\n📄 JSON Output:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n")


if __name__ == "__main__":
    import sys
    
    # Check if running in test mode or interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test samples
        print("\n" + "=" * 60)
        print("RUNNING TEST SAMPLES")
        print("=" * 60)
        
        test_samples = [
            ("Mosetsana o apea dijo fa mosimane a bala buka.", None),
            ("Monna o a nama fa mosadi a pheha.", None),
            ("Umfana ufunda incwadi.", "isizulu"),
            ("Intombazane ipheka.", "isizulu"),
        ]
        
        for i, (text, lang) in enumerate(test_samples, 1):
            print(f"\n\nTest {i}/{len(test_samples)}")
            result = correct_bias(text, lang)
            print(f"\n{'='*60}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "json":
        # JSON output mode
        if len(sys.argv) > 2:
            text = " ".join(sys.argv[2:])
            result = analyze(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Usage: python rewriter.py json <text>")
    
    else:
        # Run in interactive mode
        run_interactive()