#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV Dataset Evaluation Script
Runs F1 score evaluations on Zulu and Setswana bias datasets.
Computes Precision, Recall, F1 per bias type and overall.
"""

import csv
import json
import sys
import io
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rule_based_detector import analyze, ProgressBar


def load_csv_dataset(filepath: str, language: str) -> List[Dict]:
    """
    Load a CSV dataset and return list of examples.
    
    Args:
        filepath: Path to CSV file
        language: 'zu' for Zulu, 'tn' for Setswana
    
    Returns:
        List of dicts with keys: text, english, bias_type, discipline, language
    """
    examples = []
    text_col = "IsiZulu" if language == "zu" else "Setswana"
    
    # Try multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    # Skip empty rows
                    text = row.get(text_col, "").strip()
                    if not text:
                        continue
                    
                    examples.append({
                        "id": f"{language}-{i:05d}",
                        "text": text,
                        "english": row.get("English", "").strip(),
                        "bias_type": row.get("bias_type", "Unknown").strip(),
                        "discipline": row.get("discipline", "Unknown").strip(),
                        "language": language
                    })
            print(f"    (Loaded with encoding: {encoding})")
            return examples
        except UnicodeDecodeError:
            examples = []  # Reset and try next encoding
            continue
        except Exception as e:
            raise e
    
    raise ValueError(f"Could not decode file {filepath} with any supported encoding")


def evaluate_single(example: Dict) -> Dict:
    """
    Evaluate detection on a single example.
    
    Args:
        example: Dict with text, language, bias_type
    
    Returns:
        Dict with prediction results
    """
    text = example["text"]
    language = example["language"]
    
    # Run detection (no progress bar for individual items)
    result = analyze(text, language, show_progress=False)
    
    return {
        "id": example["id"],
        "text": text[:100] + "..." if len(text) > 100 else text,
        "bias_type": example["bias_type"],
        "discipline": example["discipline"],
        "language": language,
        "detected_bias": result["detected_bias"],
        "num_rules_triggered": len(result["explanations"]),
        "rules_triggered": [e["rule_triggered"] for e in result["explanations"]],
        "suggested_rewrite": result["suggested_rewrite"][:100] if result["suggested_rewrite"] else None
    }


def compute_metrics(results: List[Dict]) -> Dict:
    """
    Compute F1, Precision, Recall metrics from results.
    
    Since all examples are labeled as biased:
    - TP = detected as biased (correct)
    - FN = not detected (missed)
    - FP = 0 (no non-biased examples to falsely detect)
    
    This gives us Detection Rate = Recall = TP / (TP + FN)
    """
    total = len(results)
    detected = sum(1 for r in results if r["detected_bias"])
    missed = total - detected
    
    # Overall metrics (all examples are TP or FN)
    tp = detected
    fn = missed
    fp = 0  # No negatives in dataset
    
    precision = 1.0 if tp > 0 else 0.0  # All detections are correct
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # By bias type
    by_bias_type = defaultdict(lambda: {"tp": 0, "fn": 0})
    for r in results:
        bt = r["bias_type"]
        if r["detected_bias"]:
            by_bias_type[bt]["tp"] += 1
        else:
            by_bias_type[bt]["fn"] += 1
    
    bias_type_metrics = {}
    for bt, counts in by_bias_type.items():
        bt_tp = counts["tp"]
        bt_fn = counts["fn"]
        bt_prec = 1.0 if bt_tp > 0 else 0.0
        bt_rec = bt_tp / (bt_tp + bt_fn) if (bt_tp + bt_fn) > 0 else 0.0
        bt_f1 = 2 * (bt_prec * bt_rec) / (bt_prec + bt_rec) if (bt_prec + bt_rec) > 0 else 0.0
        
        bias_type_metrics[bt] = {
            "precision": bt_prec,
            "recall": bt_rec,
            "f1": bt_f1,
            "tp": bt_tp,
            "fn": bt_fn,
            "total": bt_tp + bt_fn
        }
    
    # Macro F1 (average across bias types)
    f1_values = [m["f1"] for m in bias_type_metrics.values()]
    macro_f1 = sum(f1_values) / len(f1_values) if f1_values else 0.0
    
    # By discipline
    by_discipline = defaultdict(lambda: {"tp": 0, "fn": 0})
    for r in results:
        disc = r["discipline"]
        if r["detected_bias"]:
            by_discipline[disc]["tp"] += 1
        else:
            by_discipline[disc]["fn"] += 1
    
    discipline_metrics = {}
    for disc, counts in by_discipline.items():
        d_tp = counts["tp"]
        d_fn = counts["fn"]
        d_rec = d_tp / (d_tp + d_fn) if (d_tp + d_fn) > 0 else 0.0
        discipline_metrics[disc] = {
            "recall": d_rec,
            "detection_rate": d_rec,
            "tp": d_tp,
            "fn": d_fn,
            "total": d_tp + d_fn
        }
    
    # Rules triggered distribution
    rule_counts = defaultdict(int)
    for r in results:
        for rule in r["rules_triggered"]:
            rule_counts[rule] += 1
    
    return {
        "total": total,
        "detected": detected,
        "missed": missed,
        "detection_rate": detected / total if total > 0 else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "macro_f1": macro_f1,
        "by_bias_type": dict(bias_type_metrics),
        "by_discipline": dict(discipline_metrics),
        "rules_triggered": dict(rule_counts)
    }


def print_report(language: str, metrics: Dict, results: List[Dict]):
    """Print formatted evaluation report."""
    lang_name = "isiZulu" if language == "zu" else "Setswana"
    
    print(f"\n{'='*80}")
    print(f"EVALUATION REPORT: {lang_name.upper()}")
    print(f"{'='*80}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Overall metrics
    print(f"\n{'─'*40}")
    print(f"OVERALL METRICS")
    print(f"{'─'*40}")
    print(f"  Total Examples:     {metrics['total']:,}")
    print(f"  Detected Bias:      {metrics['detected']:,}")
    print(f"  Missed:             {metrics['missed']:,}")
    print(f"  Detection Rate:     {metrics['detection_rate']*100:.2f}%")
    print(f"  Precision:          {metrics['precision']*100:.2f}%")
    print(f"  Recall (F1 base):   {metrics['recall']*100:.2f}%")
    print(f"  F1 Score:           {metrics['f1']*100:.2f}%")
    print(f"  Macro-F1:           {metrics['macro_f1']*100:.2f}%")
    
    # By bias type
    print(f"\n{'─'*40}")
    print(f"BY BIAS TYPE")
    print(f"{'─'*40}")
    sorted_bt = sorted(metrics['by_bias_type'].items(), key=lambda x: -x[1]['total'])
    for bt, m in sorted_bt[:15]:  # Top 15
        print(f"  {bt[:35]:35} | F1: {m['f1']*100:5.1f}% | Recall: {m['recall']*100:5.1f}% | {m['total']:5} examples")
    if len(sorted_bt) > 15:
        print(f"  ... and {len(sorted_bt) - 15} more bias types")
    
    # By discipline (top 10)
    print(f"\n{'─'*40}")
    print(f"BY DISCIPLINE (Top 10)")
    print(f"{'─'*40}")
    sorted_disc = sorted(metrics['by_discipline'].items(), key=lambda x: -x[1]['total'])
    for disc, m in sorted_disc[:10]:
        print(f"  {disc[:35]:35} | Detection: {m['detection_rate']*100:5.1f}% | {m['total']:5} examples")
    
    # Rules triggered
    print(f"\n{'─'*40}")
    print(f"RULES TRIGGERED")
    print(f"{'─'*40}")
    sorted_rules = sorted(metrics['rules_triggered'].items(), key=lambda x: -x[1])
    for rule, count in sorted_rules:
        print(f"  {rule[:40]:40} {count:6,} times")
    if not sorted_rules:
        print(f"  (No rules triggered)")
    
    # Sample missed detections
    missed = [r for r in results if not r["detected_bias"]][:5]
    if missed:
        print(f"\n{'─'*40}")
        print(f"SAMPLE MISSED DETECTIONS (First 5)")
        print(f"{'─'*40}")
        for r in missed:
            print(f"  [{r['id']}] {r['bias_type']}")
            print(f"    \"{r['text'][:70]}...\"")


def run_evaluation():
    """Run full evaluation on both datasets."""
    print("\n" + "="*80)
    print("CSV DATASET EVALUATION")
    print("F1 Score Analysis for Zulu and Setswana Bias Detection")
    print("="*80)
    
    all_results = {}
    all_metrics = {}
    
    # Define datasets
    datasets = [
        ("zu", "zulu_bias_dataset_final_clean.csv", "isiZulu"),
        ("tn", "setswana_bias_dataset_final.csv", "Setswana")
    ]
    
    for lang, filepath, lang_name in datasets:
        print(f"\n\n{'#'*80}")
        print(f"# Processing {lang_name} Dataset: {filepath}")
        print(f"{'#'*80}")
        
        # Load dataset
        print(f"\n[1] Loading dataset...")
        try:
            examples = load_csv_dataset(filepath, lang)
            print(f"    Loaded {len(examples):,} examples")
        except FileNotFoundError:
            print(f"    ERROR: File not found: {filepath}")
            continue
        except Exception as e:
            print(f"    ERROR: {e}")
            continue
        
        if not examples:
            print(f"    No examples found in {filepath}")
            continue
        
        # Count bias types
        bt_counts = defaultdict(int)
        for ex in examples:
            bt_counts[ex["bias_type"]] += 1
        print(f"    Bias types: {len(bt_counts)}")
        
        # Run evaluation
        print(f"\n[2] Running bias detection...")
        progress = ProgressBar(len(examples), "Evaluating")
        
        results = []
        for example in examples:
            result = evaluate_single(example)
            results.append(result)
            progress.update()
        
        # Compute metrics
        print(f"\n[3] Computing metrics...")
        metrics = compute_metrics(results)
        
        # Store results
        all_results[lang] = results
        all_metrics[lang] = metrics
        
        # Print report
        print_report(lang, metrics, results)
    
    # Combined summary
    print(f"\n\n{'='*80}")
    print("COMBINED SUMMARY")
    print(f"{'='*80}")
    
    combined_table = []
    for lang, lang_name in [("zu", "isiZulu"), ("tn", "Setswana")]:
        if lang in all_metrics:
            m = all_metrics[lang]
            combined_table.append({
                "language": lang_name,
                "total": m["total"],
                "detected": m["detected"],
                "detection_rate": m["detection_rate"],
                "f1": m["f1"],
                "macro_f1": m["macro_f1"]
            })
    
    print(f"\n{'Language':<15} {'Total':>10} {'Detected':>10} {'Rate':>10} {'F1':>10} {'Macro-F1':>10}")
    print("-" * 70)
    for row in combined_table:
        print(f"{row['language']:<15} {row['total']:>10,} {row['detected']:>10,} {row['detection_rate']*100:>9.1f}% {row['f1']*100:>9.1f}% {row['macro_f1']*100:>9.1f}%")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "datasets": {
            lang: {
                "metrics": all_metrics.get(lang),
                "sample_results": all_results.get(lang, [])[:20]  # First 20 for brevity
            }
            for lang in ["zu", "tn"] if lang in all_metrics
        }
    }
    
    output_file = "csv_evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✓ Full results saved to: {output_file}")
    print(f"{'='*80}\n")
    
    return all_metrics


if __name__ == "__main__":
    run_evaluation()
