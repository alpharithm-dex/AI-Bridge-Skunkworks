# -*- coding: utf-8 -*-

"""
Rewriting Quality Evaluation Script
Comprehensive evaluation of bias detection and rewriting quality using CSV datasets.
Focus on rewriting metrics: similarity, context preservation, and fluency.
"""

import csv
import json
import sys
import io
import random
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rewriter import correct_bias
from rule_based_detector import ProgressBar

# =============================================================================
# ENHANCED REWRITING QUALITY METRICS
# =============================================================================

def semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts (0-100).
    Combines character-level and word-level similarity.
    """
    if not text1 or not text2:
        return 0.0
    
    # Character-level similarity (SequenceMatcher)
    char_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    # Word-level similarity (Jaccard)
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if words1 and words2:
        intersection = words1 & words2
        union = words1 | words2
        word_sim = len(intersection) / len(union)
    else:
        word_sim = 0.0
    
    # Weighted combination (60% character, 40% word)
    combined = (char_sim * 0.6) + (word_sim * 0.4)
    return combined * 100


def context_preservation_score(original: str, rewritten: str) -> float:
    """
    Measure how well the rewrite preserves the original context (0-100).
    Considers word retention, structure, and meaning preservation.
    """
    if not original or not rewritten:
        return 0.0
    
    orig_words = original.lower().split()
    rewrite_words = rewritten.lower().split()
    
    if not orig_words:
        return 0.0
    
    # Define gendered terms to exclude from retention calculation
    gendered_terms = {
        'mosadi', 'monna', 'mosetsana', 'mosimane', 'basadi', 'banna',
        'umama', 'ubaba', 'umfazi', 'indoda', 'intombazane', 'umfana',
        'abesifazane', 'abesilisa', 'amantombazane', 'amakhwenkwe',
        'ngwanyana', 'moshemane', 'bomma', 'borra'
    }
    
    # Content words (non-gendered) retention
    orig_content = [w for w in orig_words if w not in gendered_terms]
    rewrite_content = [w for w in rewrite_words if w not in gendered_terms]
    
    if orig_content:
        retained = sum(1 for w in orig_content if w in rewrite_content)
        retention_rate = retained / len(orig_content)
    else:
        retention_rate = 1.0  # If all words were gendered, perfect score
    
    # Length preservation (penalize drastic changes)
    len_ratio = min(len(rewrite_words), len(orig_words)) / max(len(rewrite_words), len(orig_words))
    
    # Structure preservation (word order similarity)
    # Use longest common subsequence approximation
    structure_sim = SequenceMatcher(None, orig_words, rewrite_words).ratio()
    
    # Weighted combination
    score = (retention_rate * 0.5) + (len_ratio * 0.2) + (structure_sim * 0.3)
    return score * 100


def gender_neutralization_score(original: str, rewritten: str) -> float:
    """
    Measure effectiveness of gender neutralization (0-100).
    Higher score = more effective removal of gendered language.
    """
    gendered_terms = [
        'mosadi', 'monna', 'mosetsana', 'mosimane', 'basadi', 'banna',
        'umama', 'ubaba', 'umfazi', 'indoda', 'intombazane', 'umfana',
        'abesifazane', 'abesilisa', 'amantombazane', 'amakhwenkwe',
        'ngwanyana', 'moshemane', 'bomma', 'borra'
    ]
    
    orig_lower = original.lower()
    rewrite_lower = rewritten.lower()
    
    # Count gendered terms in original and rewrite
    orig_count = sum(1 for term in gendered_terms if term in orig_lower)
    rewrite_count = sum(1 for term in gendered_terms if term in rewrite_lower)
    
    if orig_count == 0:
        # No gendered terms to neutralize
        return 100.0
    
    # Reduction rate
    reduction = (orig_count - rewrite_count) / orig_count
    return max(0, reduction * 100)


def fluency_score(original: str, rewritten: str) -> float:
    """
    Measure fluency and naturalness of the rewrite (0-100).
    Considers length appropriateness and basic structural integrity.
    """
    if not original or not rewritten:
        return 0.0
    
    orig_words = original.split()
    rewrite_words = rewritten.split()
    
    # Length appropriateness (rewrites shouldn't be drastically different in length)
    len_ratio = min(len(rewrite_words), len(orig_words)) / max(len(rewrite_words), len(orig_words))
    
    # Penalize very short rewrites (likely incomplete)
    if len(rewrite_words) < 3:
        length_penalty = 0.5
    else:
        length_penalty = 1.0
    
    # Basic structural integrity (has some common words)
    common_words = set(original.lower().split()) & set(rewritten.lower().split())
    structure_score = min(1.0, len(common_words) / max(1, len(orig_words) * 0.3))
    
    # Weighted combination
    score = (len_ratio * 0.4) + (structure_score * 0.6)
    return score * length_penalty * 100


def overall_rewriting_quality(original: str, rewritten: str) -> Dict[str, float]:
    """
    Calculate all rewriting quality metrics and overall score.
    Returns dict with individual metrics and weighted overall score.
    """
    semantic = semantic_similarity(original, rewritten)
    context = context_preservation_score(original, rewritten)
    gender = gender_neutralization_score(original, rewritten)
    fluency = fluency_score(original, rewritten)
    
    # Weighted overall score (as per implementation plan)
    overall = (semantic * 0.40) + (context * 0.30) + (gender * 0.20) + (fluency * 0.10)
    
    return {
        "semantic_similarity": round(semantic, 2),
        "context_preservation": round(context, 2),
        "gender_neutralization": round(gender, 2),
        "fluency": round(fluency, 2),
        "overall_quality": round(overall, 2)
    }


# =============================================================================
# DATA LOADING
# =============================================================================

def load_csv_dataset(filepath: str, language: str, sample_size: int = None) -> List[Dict]:
    """
    Load CSV dataset and optionally sample.
    
    Args:
        filepath: Path to CSV file
        language: 'tn' for Setswana, 'zu' for isiZulu
        sample_size: If specified, stratified sample by bias_type
    
    Returns:
        List of dicts with text, english, bias_type, discipline, language
    """
    items = []
    
    # Try UTF-8 first, fallback to latin-1
    encodings = ['utf-8', 'latin-1', 'cp1252']
    reader = None
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle different column names
                    text_col = 'Setswana' if language == 'tn' else 'IsiZulu'
                    
                    items.append({
                        "text": row.get(text_col, ""),
                        "english": row.get("English", ""),
                        "bias_type": row.get("bias_type", "Unknown"),
                        "discipline": row.get("discipline", "Unknown"),
                        "language": language
                    })
            break  # Success, exit loop
        except UnicodeDecodeError:
            items = []  # Reset and try next encoding
            continue
        except Exception as e:
            print(f"Error reading {filepath} with {encoding}: {e}")
            items = []
            continue
    
    if not items:
        raise ValueError(f"Could not read {filepath} with any encoding")
    
    # Stratified sampling if requested
    if sample_size and sample_size < len(items):
        # Group by bias_type
        by_type = defaultdict(list)
        for item in items:
            by_type[item["bias_type"]].append(item)
        
        # Sample proportionally from each type
        sampled = []
        for bias_type, type_items in by_type.items():
            proportion = len(type_items) / len(items)
            type_sample_size = max(1, int(sample_size * proportion))
            sampled.extend(random.sample(type_items, min(type_sample_size, len(type_items))))
        
        # If we're under sample_size, randomly add more
        if len(sampled) < sample_size:
            remaining = [item for item in items if item not in sampled]
            sampled.extend(random.sample(remaining, min(sample_size - len(sampled), len(remaining))))
        
        return sampled[:sample_size]
    
    return items


# =============================================================================
# EVALUATION
# =============================================================================

def evaluate_single(item: Dict) -> Dict:
    """
    Evaluate a single item for detection and rewriting quality.
    """
    text = item["text"]
    language = item["language"]
    
    # Run bias correction
    result = correct_bias(text, language)
    
    # Extract results
    has_bias = result.get("has_bias", False)
    rewrite = result.get("rewrite", text)
    explanations = result.get("explanations", [])
    
    # Calculate rewriting quality metrics
    quality_metrics = overall_rewriting_quality(text, rewrite)
    
    # Compile evaluation result
    eval_result = {
        "text": text,
        "english": item["english"],
        "bias_type": item["bias_type"],
        "discipline": item["discipline"],
        "language": item["language"],
        "detected_bias": has_bias,
        "num_rules_triggered": len(explanations),
        "rules_triggered": [e.get("rule_triggered", "") for e in explanations],
        "rewrite": rewrite,
        "text_modified": rewrite.lower() != text.lower(),
        **quality_metrics
    }
    
    return eval_result


def run_evaluation(setswana_path: str, zulu_path: str, sample_size: int = 250) -> Dict:
    """
    Run full evaluation on both datasets.
    """
    print("\n" + "=" * 80)
    print("REWRITING QUALITY EVALUATION - Ithute AI Bridge")
    print("=" * 80)
    
    # Load datasets
    print(f"\n[1] Loading datasets (sample size: {sample_size if sample_size else 'FULL'})...")
    
    setswana_items = load_csv_dataset(setswana_path, "tn", sample_size)
    zulu_items = load_csv_dataset(zulu_path, "zu", sample_size)
    
    all_items = setswana_items + zulu_items
    
    print(f"    Setswana: {len(setswana_items)} items")
    print(f"    isiZulu:  {len(zulu_items)} items")
    print(f"    Total:    {len(all_items)} items")
    
    # Show bias type distribution
    bias_types = defaultdict(int)
    for item in all_items:
        bias_types[item["bias_type"]] += 1
    
    print(f"\n    Bias Types ({len(bias_types)}):")
    for bias_type, count in sorted(bias_types.items(), key=lambda x: -x[1])[:10]:
        print(f"      - {bias_type}: {count}")
    if len(bias_types) > 10:
        print(f"      ... and {len(bias_types) - 10} more")
    
    # Run evaluation
    print("\n[2] Running evaluation...")
    progress = ProgressBar(len(all_items), "Evaluating")
    
    results = []
    for item in all_items:
        result = evaluate_single(item)
        results.append(result)
        progress.update()
    
    progress.complete()
    
    # Calculate aggregate metrics
    print("\n[3] Calculating aggregate metrics...")
    
    total = len(results)
    detected = sum(1 for r in results if r["detected_bias"])
    modified = sum(1 for r in results if r["text_modified"])
    
    # Overall metrics
    avg_semantic = sum(r["semantic_similarity"] for r in results) / total
    avg_context = sum(r["context_preservation"] for r in results) / total
    avg_gender = sum(r["gender_neutralization"] for r in results) / total
    avg_fluency = sum(r["fluency"] for r in results) / total
    avg_overall = sum(r["overall_quality"] for r in results) / total
    
    # By language
    tn_results = [r for r in results if r["language"] == "tn"]
    zu_results = [r for r in results if r["language"] == "zu"]
    
    # By bias type
    by_bias_type = defaultdict(list)
    for r in results:
        by_bias_type[r["bias_type"]].append(r)
    
    bias_type_metrics = {}
    for bias_type, type_results in by_bias_type.items():
        bias_type_metrics[bias_type] = {
            "count": len(type_results),
            "detection_rate": sum(1 for r in type_results if r["detected_bias"]) / len(type_results) * 100,
            "avg_overall_quality": sum(r["overall_quality"] for r in type_results) / len(type_results),
            "avg_semantic_similarity": sum(r["semantic_similarity"] for r in type_results) / len(type_results),
            "avg_context_preservation": sum(r["context_preservation"] for r in type_results) / len(type_results)
        }
    
    # By discipline
    by_discipline = defaultdict(list)
    for r in results:
        by_discipline[r["discipline"]].append(r)
    
    discipline_metrics = {}
    for discipline, disc_results in by_discipline.items():
        discipline_metrics[discipline] = {
            "count": len(disc_results),
            "detection_rate": sum(1 for r in disc_results if r["detected_bias"]) / len(disc_results) * 100,
            "avg_overall_quality": sum(r["overall_quality"] for r in disc_results) / len(disc_results)
        }
    
    # Compile summary
    summary = {
        "total_items": total,
        "detection_rate": detected / total * 100,
        "modification_rate": modified / total * 100,
        
        # Rewriting quality metrics
        "avg_semantic_similarity": round(avg_semantic, 2),
        "avg_context_preservation": round(avg_context, 2),
        "avg_gender_neutralization": round(avg_gender, 2),
        "avg_fluency": round(avg_fluency, 2),
        "avg_overall_quality": round(avg_overall, 2),
        
        # By language
        "by_language": {
            "setswana": {
                "count": len(tn_results),
                "detection_rate": sum(1 for r in tn_results if r["detected_bias"]) / len(tn_results) * 100 if tn_results else 0,
                "avg_overall_quality": sum(r["overall_quality"] for r in tn_results) / len(tn_results) if tn_results else 0,
                "avg_semantic_similarity": sum(r["semantic_similarity"] for r in tn_results) / len(tn_results) if tn_results else 0,
                "avg_context_preservation": sum(r["context_preservation"] for r in tn_results) / len(tn_results) if tn_results else 0
            },
            "isizulu": {
                "count": len(zu_results),
                "detection_rate": sum(1 for r in zu_results if r["detected_bias"]) / len(zu_results) * 100 if zu_results else 0,
                "avg_overall_quality": sum(r["overall_quality"] for r in zu_results) / len(zu_results) if zu_results else 0,
                "avg_semantic_similarity": sum(r["semantic_similarity"] for r in zu_results) / len(zu_results) if zu_results else 0,
                "avg_context_preservation": sum(r["context_preservation"] for r in zu_results) / len(zu_results) if zu_results else 0
            }
        },
        
        # By bias type
        "by_bias_type": bias_type_metrics,
        
        # By discipline
        "by_discipline": discipline_metrics
    }
    
    return {
        "summary": summary,
        "results": results,
        "metadata": {
            "setswana_path": setswana_path,
            "zulu_path": zulu_path,
            "sample_size": sample_size,
            "total_evaluated": total
        }
    }


# =============================================================================
# REPORTING
# =============================================================================

def print_summary_report(eval_data: Dict):
    """Print concise summary report."""
    summary = eval_data["summary"]
    
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    print("\n┌────────────────────────────────────────────────────────────────────────────┐")
    print("│                        OVERALL PERFORMANCE                                 │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    print(f"│  Total Items:              {summary['total_items']:>6}                                        │")
    print(f"│  Detection Rate:           {summary['detection_rate']:>6.2f}%                                      │")
    print(f"│  Modification Rate:        {summary['modification_rate']:>6.2f}%                                      │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    print("│                    REWRITING QUALITY METRICS                               │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    print(f"│  Overall Quality Score:    {summary['avg_overall_quality']:>6.2f}/100                                   │")
    print(f"│  ├─ Semantic Similarity:   {summary['avg_semantic_similarity']:>6.2f}/100  (weight: 40%)                  │")
    print(f"│  ├─ Context Preservation:  {summary['avg_context_preservation']:>6.2f}/100  (weight: 30%)                  │")
    print(f"│  ├─ Gender Neutralization: {summary['avg_gender_neutralization']:>6.2f}/100  (weight: 20%)                  │")
    print(f"│  └─ Fluency:               {summary['avg_fluency']:>6.2f}/100  (weight: 10%)                  │")
    print("└────────────────────────────────────────────────────────────────────────────┘")
    
    print("\n┌────────────────────────────────────────────────────────────────────────────┐")
    print("│                        BY LANGUAGE                                         │")
    print("├────────────────────────────────────────────────────────────────────────────┤")
    for lang_name, lang_data in summary["by_language"].items():
        print(f"│  {lang_name.upper():10}                                                          │")
        print(f"│    Items: {lang_data['count']:>4}  |  Detection: {lang_data['detection_rate']:>5.1f}%  |  Quality: {lang_data['avg_overall_quality']:>5.1f}/100   │")
    print("└────────────────────────────────────────────────────────────────────────────┘")
    
    print("\n✓ Evaluation complete!")


def save_results(eval_data: Dict, output_path: str):
    """Save evaluation results to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Results saved to: {output_path}")


def save_results_csv(eval_data: Dict, output_path: str):
    """Save evaluation results to CSV for analysis."""
    results = eval_data["results"]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            "text", "english", "bias_type", "discipline", "language",
            "detected_bias", "num_rules_triggered", "rewrite", "text_modified",
            "semantic_similarity", "context_preservation", "gender_neutralization",
            "fluency", "overall_quality"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            row = {k: r.get(k, "") for k in fieldnames}
            # Convert lists to strings
            if isinstance(row.get("rules_triggered"), list):
                row["rules_triggered"] = "; ".join(row["rules_triggered"])
            writer.writerow(row)
    
    print(f"✓ CSV results saved to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rewriting Quality Evaluation")
    parser.add_argument("--setswana", "-s", default="setswana_bias_dataset_final.csv",
                        help="Path to Setswana CSV dataset")
    parser.add_argument("--zulu", "-z", default="zulu_bias_dataset_final_clean.csv",
                        help="Path to isiZulu CSV dataset")
    parser.add_argument("--sample", type=int, default=250,
                        help="Sample size per language (default: 250, use 0 for full dataset)")
    parser.add_argument("--output", "-o", default="rewriting_eval_results.json",
                        help="Output JSON file")
    parser.add_argument("--csv", default="rewriting_eval_results.csv",
                        help="Output CSV file")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Run evaluation
    sample_size = None if args.sample == 0 else args.sample
    eval_data = run_evaluation(args.setswana, args.zulu, sample_size)
    
    # Print summary
    print_summary_report(eval_data)
    
    # Save results
    save_results(eval_data, args.output)
    save_results_csv(eval_data, args.csv)
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80 + "\n")
