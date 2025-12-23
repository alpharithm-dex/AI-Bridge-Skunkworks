#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diagnostic Evaluation Script for Rule-Based Bias Detection System
Evaluates detection accuracy and rewrite quality against ground truth.
"""

import json
import sys
import io
from typing import Dict, List, Any
from difflib import SequenceMatcher

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rule_based_detector import analyze, ProgressBar, show_stage_progress

# =============================================================================
# EVALUATION METRICS
# =============================================================================

def text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def word_overlap(text1: str, text2: str) -> float:
    """Calculate word overlap ratio between two texts."""
    if not text1 or not text2:
        return 0.0
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)  # Jaccard similarity


def has_gender_reduction(original: str, rewritten: str, reference: str) -> bool:
    """Check if rewrite reduces gendered language toward reference."""
    # Simple heuristic: check if key gendered words are removed/neutralized
    gender_markers = [
        'mosadi', 'monna', 'mosetsana', 'mosimane', 'basadi', 'banna',
        'umama', 'ubaba', 'umfazi', 'indoda', 'intombazane', 'umfana',
        'abesifazane', 'abesilisa', 'amantombazane', 'amakhwenkwe'
    ]
    
    original_markers = sum(1 for m in gender_markers if m in original.lower())
    rewritten_markers = sum(1 for m in gender_markers if m in rewritten.lower())
    
    # Good if markers reduced or neutralized
    return rewritten_markers <= original_markers


# =============================================================================
# EVALUATION RUNNER
# =============================================================================

def load_ground_truth(path: str = "ground_truth.json") -> List[Dict]:
    """Load ground truth data."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for key, value in data.items():
        items.append({
            "id": value.get("id", key),
            "language": value.get("language", "tn"),
            "biased_text": value.get("biased_text", ""),
            "bias_free_text": value.get("bias_free_text", ""),
            "bias_category": value.get("bias_category", "Unknown"),
            "translation_en": value.get("translation_en", ""),
            "bias_free_translation_en": value.get("bias_free_translation_en", "")
        })
    
    return items


def evaluate_single(item: Dict) -> Dict:
    """Evaluate system on a single item."""
    biased_text = item["biased_text"]
    reference_text = item["bias_free_text"]
    language = "zu" if item["language"] == "zu" else "tn"
    
    # Run detection
    result = analyze(biased_text, language, show_progress=False)
    
    # Calculate metrics
    predicted_rewrite = result["suggested_rewrite"]
    
    metrics = {
        "id": item["id"],
        "language": item["language"],
        "category": item["bias_category"],
        "original": biased_text,
        "reference": reference_text,
        "predicted": predicted_rewrite,
        "detected_bias": result["detected_bias"],
        "num_rules_triggered": len(result["explanations"]),
        "rules_triggered": [e["rule_triggered"] for e in result["explanations"]],
        
        # Similarity metrics
        "rewrite_similarity": text_similarity(predicted_rewrite, reference_text),
        "word_overlap": word_overlap(predicted_rewrite, reference_text),
        "gender_reduced": has_gender_reduction(biased_text, predicted_rewrite, reference_text),
        
        # Did we change the input at all?
        "text_modified": predicted_rewrite.lower() != biased_text.lower(),
    }
    
    return metrics


def run_evaluation(ground_truth_path: str = "ground_truth.json") -> Dict:
    """Run full evaluation and return results."""
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC EVALUATION: Rule-Based Bias Detection System")
    print("=" * 70)
    
    # Load data
    print("\n[1] Loading ground truth data...")
    items = load_ground_truth(ground_truth_path)
    print(f"    Loaded {len(items)} items")
    
    # Count by language
    tn_count = sum(1 for i in items if i["language"] == "tn")
    zu_count = sum(1 for i in items if i["language"] == "zu")
    print(f"    Setswana (tn): {tn_count}")
    print(f"    isiZulu (zu):  {zu_count}")
    
    # Count by category
    categories = {}
    for item in items:
        cat = item["bias_category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n    Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"      - {cat}: {count}")
    
    # Evaluate
    print("\n[2] Running evaluation...")
    progress = ProgressBar(len(items), "Evaluating")
    
    results = []
    for item in items:
        result = evaluate_single(item)
        results.append(result)
        progress.update()
    
    # Calculate aggregate metrics
    print("\n[3] Calculating metrics...")
    
    total = len(results)
    detected = sum(1 for r in results if r["detected_bias"])
    modified = sum(1 for r in results if r["text_modified"])
    gender_reduced = sum(1 for r in results if r["gender_reduced"])
    
    avg_similarity = sum(r["rewrite_similarity"] for r in results) / total
    avg_word_overlap = sum(r["word_overlap"] for r in results) / total
    
    # Rules triggered breakdown
    rule_counts = {}
    for r in results:
        for rule in r["rules_triggered"]:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    # Category-level metrics
    category_metrics = {}
    for cat in categories.keys():
        cat_items = [r for r in results if r["category"] == cat]
        if cat_items:
            category_metrics[cat] = {
                "count": len(cat_items),
                "detected": sum(1 for r in cat_items if r["detected_bias"]),
                "detection_rate": sum(1 for r in cat_items if r["detected_bias"]) / len(cat_items),
                "avg_similarity": sum(r["rewrite_similarity"] for r in cat_items) / len(cat_items)
            }
    
    # Compile summary
    summary = {
        "total_items": total,
        "detection_rate": detected / total,
        "modification_rate": modified / total,
        "gender_reduction_rate": gender_reduced / total,
        "avg_rewrite_similarity": avg_similarity,
        "avg_word_overlap": avg_word_overlap,
        "rules_triggered": rule_counts,
        "category_metrics": category_metrics,
        "by_language": {
            "setswana": {
                "total": tn_count,
                "detected": sum(1 for r in results if r["language"] == "tn" and r["detected_bias"])
            },
            "isizulu": {
                "total": zu_count,
                "detected": sum(1 for r in results if r["language"] == "zu" and r["detected_bias"])
            }
        }
    }
    
    return {"summary": summary, "results": results}


def print_report(eval_results: Dict):
    """Print formatted evaluation report."""
    summary = eval_results["summary"]
    results = eval_results["results"]
    
    print("\n" + "=" * 70)
    print("EVALUATION REPORT")
    print("=" * 70)
    
    # Overall metrics
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                        OVERALL METRICS                              │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    print(f"│  Total Items Evaluated:        {summary['total_items']:>5}                              │")
    print(f"│  Bias Detection Rate:          {summary['detection_rate']*100:>5.1f}%                             │")
    print(f"│  Text Modification Rate:       {summary['modification_rate']*100:>5.1f}%                             │")
    print(f"│  Gender Reduction Rate:        {summary['gender_reduction_rate']*100:>5.1f}%                             │")
    print(f"│  Avg Rewrite Similarity:       {summary['avg_rewrite_similarity']*100:>5.1f}%                             │")
    print(f"│  Avg Word Overlap (Jaccard):   {summary['avg_word_overlap']*100:>5.1f}%                             │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # By language
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                         BY LANGUAGE                                 │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    for lang, data in summary["by_language"].items():
        rate = (data["detected"] / data["total"] * 100) if data["total"] > 0 else 0
        print(f"│  {lang.capitalize():12} Total: {data['total']:>3}  Detected: {data['detected']:>3}  Rate: {rate:>5.1f}%       │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # Rules triggered
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                       RULES TRIGGERED                               │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    for rule, count in sorted(summary["rules_triggered"].items(), key=lambda x: -x[1]):
        print(f"│  {rule:40} {count:>5} times                │")
    if not summary["rules_triggered"]:
        print("│  (No rules triggered)                                               │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # By category
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                        BY CATEGORY                                  │")
    print("├─────────────────────────────────────────────────────────────────────┤")
    for cat, metrics in sorted(summary["category_metrics"].items(), key=lambda x: -x[1]["count"]):
        rate = metrics["detection_rate"] * 100
        sim = metrics["avg_similarity"] * 100
        print(f"│  {cat[:35]:35}                                  │")
        print(f"│    Count: {metrics['count']:>3}  Detection: {rate:>5.1f}%  Similarity: {sim:>5.1f}%        │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # Sample results
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                    SAMPLE RESULTS (First 5)                         │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    for i, r in enumerate(results[:5], 1):
        print(f"\n  [{i}] {r['id']} ({r['language'].upper()})")
        print(f"      Category: {r['category']}")
        print(f"      Original:  \"{r['original'][:60]}{'...' if len(r['original']) > 60 else ''}\"")
        print(f"      Reference: \"{r['reference'][:60]}{'...' if len(r['reference']) > 60 else ''}\"")
        print(f"      Predicted: \"{r['predicted'][:60]}{'...' if len(r['predicted']) > 60 else ''}\"")
        print(f"      Detected: {r['detected_bias']}  |  Similarity: {r['rewrite_similarity']*100:.1f}%  |  Rules: {r['num_rules_triggered']}")
    
    # Failure analysis
    print("\n┌─────────────────────────────────────────────────────────────────────┐")
    print("│                      FAILURE ANALYSIS                               │")
    print("└─────────────────────────────────────────────────────────────────────┘")
    
    # Items where no bias was detected
    missed = [r for r in results if not r["detected_bias"]]
    print(f"\n  Items where bias was NOT detected: {len(missed)}/{len(results)}")
    
    if missed:
        print("\n  Sample missed items:")
        for r in missed[:3]:
            print(f"    • [{r['id']}] \"{r['original'][:50]}...\"")
            print(f"      Category: {r['category']}")
    
    # Low similarity rewrites  
    low_sim = [r for r in results if r["detected_bias"] and r["rewrite_similarity"] < 0.3]
    print(f"\n  Low similarity rewrites (<30%): {len(low_sim)}")
    
    if low_sim:
        print("\n  Sample low-similarity rewrites:")
        for r in low_sim[:3]:
            print(f"    • [{r['id']}] Similarity: {r['rewrite_similarity']*100:.1f}%")
            print(f"      Original:  \"{r['original'][:40]}...\"")
            print(f"      Reference: \"{r['reference'][:40]}...\"")
            print(f"      Predicted: \"{r['predicted'][:40]}...\"")


def save_results(eval_results: Dict, output_path: str = "diagnostic_eval_results.json"):
    """Save evaluation results to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(eval_results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Results saved to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate Rule-Based Bias Detection")
    parser.add_argument("--input", "-i", default="ground_truth.json", help="Ground truth file")
    parser.add_argument("--output", "-o", default="diagnostic_eval_results.json", help="Output file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Run evaluation
    eval_results = run_evaluation(args.input)
    
    # Print report
    if not args.quiet:
        print_report(eval_results)
    
    # Save results
    save_results(eval_results, args.output)
    
    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70 + "\n")
