# -*- coding: utf-8 -*-

"""
Visualization Generator for Rewriting Quality Evaluation
Creates publication-quality charts following End of year report style.
"""

import json
import sys
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Professional color palette
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'success': '#06A77D',      # Green
    'warning': '#F18F01',      # Orange
    'info': '#4ECDC4',         # Teal
    'setswana': '#5E60CE',     # Purple-blue
    'isizulu': '#F72585',      # Pink-red
    'quality': '#06A77D',      # Green
    'detection': '#2E86AB'     # Blue
}

def load_results(filepath: str) -> Dict:
    """Load evaluation results from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def chart1_quality_metrics_dashboard(data: Dict, output_path: str):
    """
    Chart 1: Rewriting Quality Metrics Dashboard
    Multi-metric bar chart showing all 4 rewriting scores by language.
    """
    summary = data['summary']
    
    metrics = ['Semantic\nSimilarity', 'Context\nPreservation', 
               'Gender\nNeutralization', 'Fluency']
    
    # Overall scores
    overall_scores = [
        summary['avg_semantic_similarity'],
        summary['avg_context_preservation'],
        summary['avg_gender_neutralization'],
        summary['avg_fluency']
    ]
    
    # By language
    setswana_scores = [
        summary['by_language']['setswana']['avg_semantic_similarity'],
        summary['by_language']['setswana']['avg_context_preservation'],
        0,  # Gender neutralization not tracked per language
        0   # Fluency not tracked per language
    ]
    
    isizulu_scores = [
        summary['by_language']['isizulu']['avg_semantic_similarity'],
        summary['by_language']['isizulu']['avg_context_preservation'],
        0,
        0
    ]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(metrics))
    width = 0.25
    
    # Plot bars
    bars1 = ax.bar(x - width, overall_scores, width, label='Overall', 
                   color=COLORS['primary'], alpha=0.9)
    bars2 = ax.bar(x, setswana_scores[:2] + [0, 0], width, label='Setswana',
                   color=COLORS['setswana'], alpha=0.9)
    bars3 = ax.bar(x + width, isizulu_scores[:2] + [0, 0], width, label='isiZulu',
                   color=COLORS['isizulu'], alpha=0.9)
    
    # Customize
    ax.set_ylabel('Score (0-100)', fontsize=12, fontweight='bold')
    ax.set_title('Rewriting Quality Metrics Dashboard', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add value labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9)
    
    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart 1 saved: {output_path}")


def chart2_similarity_distribution(data: Dict, output_path: str):
    """
    Chart 2: Similarity Distribution Histogram
    Shows distribution of semantic similarity scores.
    """
    results = data['results']
    similarities = [r['semantic_similarity'] for r in results]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histogram
    n, bins, patches = ax.hist(similarities, bins=20, color=COLORS['primary'], 
                                alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Color bins by quality level
    for i, patch in enumerate(patches):
        if bins[i] < 50:
            patch.set_facecolor(COLORS['warning'])
        elif bins[i] < 75:
            patch.set_facecolor(COLORS['info'])
        else:
            patch.set_facecolor(COLORS['success'])
    
    # Add mean line
    mean_sim = np.mean(similarities)
    ax.axvline(mean_sim, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_sim:.1f}')
    
    ax.set_xlabel('Semantic Similarity Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Semantic Similarity Scores', fontsize=14, 
                 fontweight='bold', pad=20)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart 2 saved: {output_path}")


def chart3_performance_by_bias_type(data: Dict, output_path: str):
    """
    Chart 3: Performance by Bias Type
    Grouped bar chart showing detection rate vs rewriting quality per bias type.
    """
    bias_metrics = data['summary']['by_bias_type']
    
    # Sort by count (most common first), take top 10
    sorted_types = sorted(bias_metrics.items(), key=lambda x: -x[1]['count'])[:10]
    
    bias_types = [bt[0][:30] for bt in sorted_types]  # Truncate long names
    detection_rates = [bt[1]['detection_rate'] for bt in sorted_types]
    quality_scores = [bt[1]['avg_overall_quality'] for bt in sorted_types]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = np.arange(len(bias_types))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, detection_rates, width, label='Detection Rate (%)',
                   color=COLORS['detection'], alpha=0.9)
    bars2 = ax.bar(x + width/2, quality_scores, width, label='Rewriting Quality (0-100)',
                   color=COLORS['quality'], alpha=0.9)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Performance by Bias Type (Top 10)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(bias_types, rotation=45, ha='right', fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart 3 saved: {output_path}")


def chart4_context_preservation_heatmap(data: Dict, output_path: str):
    """
    Chart 4: Context Preservation Heatmap
    2D heatmap: Language × Bias Type showing context preservation scores.
    """
    results = data['results']
    
    # Group by language and bias type
    by_lang_bias = defaultdict(lambda: defaultdict(list))
    for r in results:
        by_lang_bias[r['language']][r['bias_type']].append(r['context_preservation'])
    
    # Get top bias types
    bias_counts = defaultdict(int)
    for r in results:
        bias_counts[r['bias_type']] += 1
    top_bias_types = sorted(bias_counts.items(), key=lambda x: -x[1])[:8]
    bias_types = [bt[0][:25] for bt in top_bias_types]
    
    # Build matrix
    languages = ['tn', 'zu']
    lang_labels = ['Setswana', 'isiZulu']
    matrix = []
    
    for lang in languages:
        row = []
        for bt_full, _ in top_bias_types:
            scores = by_lang_bias[lang][bt_full]
            avg_score = np.mean(scores) if scores else 0
            row.append(avg_score)
        matrix.append(row)
    
    matrix = np.array(matrix)
    
    fig, ax = plt.subplots(figsize=(12, 4))
    
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # Set ticks
    ax.set_xticks(np.arange(len(bias_types)))
    ax.set_yticks(np.arange(len(lang_labels)))
    ax.set_xticklabels(bias_types, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(lang_labels, fontsize=11)
    
    # Add text annotations
    for i in range(len(lang_labels)):
        for j in range(len(bias_types)):
            text = ax.text(j, i, f'{matrix[i, j]:.0f}',
                          ha="center", va="center", color="black", fontsize=9,
                          fontweight='bold')
    
    ax.set_title('Context Preservation Score by Language and Bias Type', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Context Preservation Score', rotation=270, labelpad=20, fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart 4 saved: {output_path}")


def chart5_quality_scatter(data: Dict, output_path: str):
    """
    Chart 5: Quality Score Scatter Plot
    X-axis: Detection confidence (num rules triggered)
    Y-axis: Overall quality score
    Color: Bias type
    """
    results = data['results']
    
    # Get top bias types for coloring
    bias_counts = defaultdict(int)
    for r in results:
        bias_counts[r['bias_type']] += 1
    top_bias_types = [bt[0] for bt in sorted(bias_counts.items(), key=lambda x: -x[1])[:5]]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot by bias type
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['success'], 
                   COLORS['warning'], COLORS['info']]
    
    for i, bias_type in enumerate(top_bias_types):
        type_results = [r for r in results if r['bias_type'] == bias_type]
        x = [r['num_rules_triggered'] for r in type_results]
        y = [r['overall_quality'] for r in type_results]
        
        ax.scatter(x, y, c=colors_list[i], label=bias_type[:30], alpha=0.6, s=50)
    
    # Others
    other_results = [r for r in results if r['bias_type'] not in top_bias_types]
    if other_results:
        x = [r['num_rules_triggered'] for r in other_results]
        y = [r['overall_quality'] for r in other_results]
        ax.scatter(x, y, c='gray', label='Other types', alpha=0.3, s=30)
    
    ax.set_xlabel('Number of Rules Triggered (Detection Confidence)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Overall Rewriting Quality Score', fontsize=12, fontweight='bold')
    ax.set_title('Rewriting Quality vs Detection Confidence', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=9, loc='best')
    ax.grid(alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart 5 saved: {output_path}")


def generate_all_charts(results_file: str, output_dir: str = "."):
    """Generate all visualization charts."""
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATION CHARTS")
    print("=" * 80 + "\n")
    
    # Load data
    print(f"Loading results from: {results_file}")
    data = load_results(results_file)
    
    # Generate charts
    chart1_quality_metrics_dashboard(data, f"{output_dir}/chart1_quality_dashboard.png")
    chart2_similarity_distribution(data, f"{output_dir}/chart2_similarity_distribution.png")
    chart3_performance_by_bias_type(data, f"{output_dir}/chart3_performance_by_bias_type.png")
    chart4_context_preservation_heatmap(data, f"{output_dir}/chart4_context_heatmap.png")
    chart5_quality_scatter(data, f"{output_dir}/chart5_quality_scatter.png")
    
    print("\n" + "=" * 80)
    print("ALL CHARTS GENERATED SUCCESSFULLY")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate evaluation visualizations")
    parser.add_argument("--input", "-i", default="rewriting_eval_results.json",
                        help="Input JSON results file")
    parser.add_argument("--output-dir", "-o", default=".",
                        help="Output directory for charts")
    
    args = parser.parse_args()
    
    generate_all_charts(args.input, args.output_dir)
