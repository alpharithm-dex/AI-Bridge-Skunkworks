"""
Evaluation Module for Bias Detection and Correction
Computes Precision, Recall, F1, and other metrics
"""

import json
from typing import List, Dict, Tuple
from collections import defaultdict

class BiasEvaluator:
    """
    Evaluates bias detection and correction performance
    """
    
    def __init__(self, ground_truth_path="ground_truth.json"):
        """Initialize evaluator with ground truth data"""
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            self.gt_data = json.load(f)
        
        # Convert to list
        self.examples = [val for val in self.gt_data.values()]
        
    def compute_detection_metrics(self, predictions: List[Dict]) -> Dict:
        """
        Compute detection metrics (TP, FP, FN, Precision, Recall, F1)
        
        Args:
            predictions: List of dicts with keys: 'example_id', 'predicted_has_bias', 'predicted_category'
        
        Returns:
            Dictionary with metrics per category and overall
        """
        # Count by category
        tp_by_category = defaultdict(int)
        fp_by_category = defaultdict(int)
        fn_by_category = defaultdict(int)
        
        # Create mapping of example_id to ground truth
        gt_by_id = {ex['id']: ex for ex in self.examples}
        
        # Overall counts
        tp_total = 0
        fp_total = 0
        fn_total = 0
        
        for pred in predictions:
            ex_id = pred.get('example_id')
            pred_has_bias = pred.get('predicted_has_bias', False)
            pred_category = pred.get('predicted_category', 'Unknown')
            
            if ex_id not in gt_by_id:
                continue
                
            gt = gt_by_id[ex_id]
            gt_has_bias = True  # All examples in ground truth are biased
            gt_category = gt.get('bias_category', 'Unknown')
            
            # Classification metrics
            if pred_has_bias and gt_has_bias:
                tp_total += 1
                if pred_category == gt_category:
                    tp_by_category[gt_category] += 1
                else:
                    fp_by_category[pred_category] += 1
                    fn_by_category[gt_category] += 1
            elif pred_has_bias and not gt_has_bias:
                fp_total += 1
                fp_by_category[pred_category] += 1
            elif not pred_has_bias and gt_has_bias:
                fn_total += 1
                fn_by_category[gt_category] += 1
        
        # Compute metrics
        results = {}
        
        # Overall metrics
        precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
        recall = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results['overall'] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'tp': tp_total,
            'fp': fp_total,
            'fn': fn_total
        }
        
        # Per-category metrics
        results['by_category'] = {}
        all_categories = set(tp_by_category.keys()) | set(fp_by_category.keys()) | set(fn_by_category.keys())
        
        for cat in all_categories:
            tp = tp_by_category[cat]
            fp = fp_by_category[cat]
            fn = fn_by_category[cat]
            
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_cat = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
            
            results['by_category'][cat] = {
                'precision': prec,
                'recall': rec,
                'f1': f1_cat,
                'tp': tp,
                'fp': fp,
                'fn': fn
            }
        
        # Macro-F1 (average F1 across categories)
        category_f1s = [results['by_category'][cat]['f1'] for cat in results['by_category']]
        results['macro_f1'] = sum(category_f1s) / len(category_f1s) if category_f1s else 0
        
        return results
    
    def compute_token_f1(self, prediction: str, reference: str) -> float:
        """
        Compute F1 score based on token overlap
        """
        pred_tokens = prediction.lower().split()
        ref_tokens = reference.lower().split()
        
        if not pred_tokens or not ref_tokens:
            return 0.0
            
        common = 0
        ref_counts = defaultdict(int)
        for t in ref_tokens:
            ref_counts[t] += 1
            
        pred_counts = defaultdict(int)
        for t in pred_tokens:
            pred_counts[t] += 1
            
        for t in pred_counts:
            common += min(pred_counts[t], ref_counts[t])
            
        precision = common / len(pred_tokens)
        recall = common / len(ref_tokens)
        
        if precision + recall == 0:
            return 0.0
            
        return 2 * (precision * recall) / (precision + recall)

    def compute_similarity(self, prediction: str, reference: str) -> float:
        """
        Compute semantic similarity using SequenceMatcher ratio
        """
        import difflib
        return difflib.SequenceMatcher(None, prediction, reference).ratio()

    def compute_correction_metrics(self, corrections: List[Dict]) -> Dict:
        """
        Compute correction quality metrics including F1 and Similarity
        
        Args:
            corrections: List of dicts with keys: 'example_id', 'corrected_text', 'ground_truth_corrected'
        
        Returns:
            Dictionary with correction metrics
        """
        exact_matches = 0
        partial_matches = 0
        total = 0
        
        # Additional metrics
        bias_removed_count = 0
        total_f1 = 0
        total_similarity = 0
        
        for corr in corrections:
            ex_id = corr.get('example_id')
            corrected = corr.get('corrected_text', '').strip()
            
            # Find corresponding ground truth
            gt_ex = next((ex for ex in self.examples if ex.get('id') == ex_id), None)
            if not gt_ex:
                continue
            
            gt_corrected = gt_ex.get('bias_free_text', '').strip()
            total += 1
            
            # Exact match
            if corrected.lower() == gt_corrected.lower():
                exact_matches += 1
            
            # Bias removed (post-hoc check if no gendered terms in corrected)
            # This is simplified - would need proper detection
            gendered_terms = ['monna', 'mosadi', 'mosimane', 'mosetsana']
            if not any(term in corrected.lower() for term in gendered_terms):
                bias_removed_count += 1
                
            # Compute new metrics
            total_f1 += self.compute_token_f1(corrected, gt_corrected)
            total_similarity += self.compute_similarity(corrected, gt_corrected)
        
        results = {
            'total': total,
            'exact_match_rate': exact_matches / total if total > 0 else 0,
            'bias_removal_rate': bias_removed_count / total if total > 0 else 0,
            'average_token_f1': total_f1 / total if total > 0 else 0,
            'average_similarity': total_similarity / total if total > 0 else 0,
            'exact_matches': exact_matches
        }
        
        return results
    
    def compute_metrics_by_language(self, metrics: Dict, lang: str) -> Dict:
        """
        Extract metrics for a specific language
        
        Args:
            metrics: Full metrics dictionary
            lang: Language code (e.g., 'tn', 'zu')
        
        Returns:
            Filtered metrics for the language
        """
        # Filter examples by language
        lang_examples = [ex for ex in self.examples if ex.get('language') == lang]
        
        if not lang_examples:
            return {'error': f'No examples found for language: {lang}'}
        
        # Count by category for this language
        categories = {}
        for ex in lang_examples:
            cat = ex.get('bias_category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        result = {
            'language': lang,
            'total_examples': len(lang_examples),
            'categories': categories,
            'category_counts': categories
        }
        
        return result
    
    def generate_report(self, detection_results: Dict, correction_results: Dict = None) -> str:
        """
        Generate a formatted evaluation report
        """
        report = []
        report.append("=" * 80)
        report.append("EVALUATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall detection metrics
        report.append("DETECTION METRICS (Overall)")
        report.append("-" * 80)
        overall = detection_results.get('overall', {})
        report.append(f"Precision: {overall.get('precision', 0):.3f}")
        report.append(f"Recall:    {overall.get('recall', 0):.3f}")
        report.append(f"F1-Score:  {overall.get('f1', 0):.3f}")
        report.append(f"Macro-F1:  {detection_results.get('macro_f1', 0):.3f}")
        report.append("")
        
        # Per-category metrics
        report.append("DETECTION METRICS (By Category)")
        report.append("-" * 80)
        by_cat = detection_results.get('by_category', {})
        for cat, metrics in by_cat.items():
            report.append(f"\n{cat}:")
            report.append(f"  Precision: {metrics.get('precision', 0):.3f}")
            report.append(f"  Recall:    {metrics.get('recall', 0):.3f}")
            report.append(f"  F1-Score:  {metrics.get('f1', 0):.3f}")
            report.append(f"  TP: {metrics.get('tp', 0)}, FP: {metrics.get('fp', 0)}, FN: {metrics.get('fn', 0)}")
        
        report.append("")
        
        # Correction metrics
        if correction_results:
            report.append("CORRECTION METRICS")
            report.append("-" * 80)
            report.append(f"Total Corrections:        {correction_results.get('total', 0)}")
            report.append(f"Exact Match Rate:         {correction_results.get('exact_match_rate', 0):.3f}")
            report.append(f"Bias Removal Rate:        {correction_results.get('bias_removal_rate', 0):.3f}")
            report.append(f"Avg Token F1:             {correction_results.get('average_token_f1', 0):.3f}")
            report.append(f"Avg Semantic Similarity:  {correction_results.get('average_similarity', 0):.3f}")
            report.append("")
        
        # Dataset statistics
        report.append("DATASET STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Examples: {len(self.examples)}")
        
        # By language
        lang_counts = defaultdict(int)
        for ex in self.examples:
            lang_counts[ex.get('language', 'unknown')] += 1
        
        report.append("\nBy Language:")
        for lang, count in lang_counts.items():
            report.append(f"  {lang}: {count}")
        
        # By category
        cat_counts = defaultdict(int)
        for ex in self.examples:
            cat_counts[ex.get('bias_category', 'Unknown')] += 1
        
        report.append("\nBy Bias Category:")
        for cat, count in cat_counts.items():
            report.append(f"  {cat}: {count}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test the evaluator
    evaluator = BiasEvaluator()
    print("Evaluator initialized with", len(evaluator.examples), "examples")
    print("\nDataset summary:")
    
    lang_counts = defaultdict(int)
    cat_counts = defaultdict(int)
    for ex in evaluator.examples:
        lang_counts[ex.get('language', 'unknown')] += 1
        cat_counts[ex.get('bias_category', 'Unknown')] += 1
    
    print("\nBy Language:")
    for lang, count in lang_counts.items():
        print(f"  {lang}: {count}")
    
    print("\nBy Category:")
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count}")

