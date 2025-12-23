"""
Batch Evaluation Script
Runs bias detection and correction on all ground truth examples
Generates evaluation metrics
"""

import json
from evaluate import BiasEvaluator
from rewriter import detect_bias, correct_bias_tn
from rag_data import get_category_from_text

def run_batch_evaluation():
    """Run evaluation on all ground truth examples"""
    
    # Initialize evaluator
    evaluator = BiasEvaluator("ground_truth.json")
    
    # Load predictions
    predictions = []
    corrections = []
    
    print("Running batch evaluation on", len(evaluator.examples), "examples...")
    print("=" * 80)
    
    for ex in evaluator.examples:
        ex_id = ex.get('id', 'unknown')
        biased_text = ex.get('biased_text', '')
        language = ex.get('language', 'tn')
        true_category = ex.get('bias_category', 'Unknown')
        
        # Run detection
        bias_results = detect_bias(biased_text, language=language)
        predicted_category = get_category_from_text(biased_text)
        
        predictions.append({
            'example_id': ex_id,
            'predicted_has_bias': bias_results['has_bias'],
            'predicted_category': predicted_category,
            'true_category': true_category,
            'language': language
        })
        
        # Run correction (optional, comment out if Ollama not available)
        # Note: Correction requires Ollama server to be running
        try:
            # Skip correction for now to avoid Ollama dependency
            # Uncomment below when Ollama is available
            # corrected = correct_bias_tn(biased_text, category=predicted_category)
            # if corrected:
            #     corrections.append({
            #         'example_id': ex_id,
            #         'corrected_text': corrected,
            #         'ground_truth_corrected': ex.get('bias_free_text', ''),
            #         'biased_text': biased_text
            #     })
            pass
        except Exception as e:
            print(f"Warning: Could not correct {ex_id}: {e}")
    
    print("\nComputing metrics...")
    
    # Compute detection metrics
    detection_results = evaluator.compute_detection_metrics(predictions)
    
    # Compute correction metrics (if available)
    correction_results = None
    if corrections:
        correction_results = evaluator.compute_correction_metrics(corrections)
    
    # Generate report
    report = evaluator.generate_report(detection_results, correction_results)
    print(report)
    
    # Save detailed results
    results = {
        'detection_metrics': detection_results,
        'correction_metrics': correction_results,
        'predictions': predictions,
        'corrections': corrections
    }
    
    with open('evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\nDetailed results saved to evaluation_results.json")
    
    return results

if __name__ == "__main__":
    results = run_batch_evaluation()

