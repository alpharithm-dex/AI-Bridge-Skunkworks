
# -*- coding: utf-8 -*-

"""
Ithute CLI Tool
Command-line interface for the Bias Detection & Rewriting System.
"""

import argparse
import json
import sys
import os
import time
from typing import List, Dict, Any

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rewriter import correct_bias
from rule_based_detector import ProgressBar

def process_single_item(text: str, language: str = None) -> Dict[str, Any]:
    """Process a single text item."""
    return correct_bias(text, language)

def process_batch(items: List[Dict[str, Any]], output_file: str = None):
    """Process a batch of items with a progress bar."""
    results = []
    total = len(items)
    pb = ProgressBar(total, "Processing Batch")
    
    for item in items:
        text = item.get("text")
        if not text:
            pb.update()
            continue
            
        # Handle 'lang' or 'language' keys
        lang = item.get("lang") or item.get("language")
        result = process_single_item(text, lang)
        
        # Merge result with original item data
        output_item = item.copy()
        output_item.update(result)
        results.append(output_item)
        
        pb.update()
        # Small delay to make progress bar visible for small batches
        time.sleep(0.05)
        
    pb.complete()
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to {output_file}")
        except Exception as e:
            print(f"\nError saving output: {e}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description="Ithute AI Bridge - Bias Detection & Rewriting CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Rewrite Command
    rewrite_parser = subparsers.add_parser("rewrite", help="Rewrite text to remove bias")
    group = rewrite_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Single text string to rewrite")
    group.add_argument("--json", help="JSON string input (e.g. '{\"text\": \"...\", \"lang\": \"tn\"}')")
    group.add_argument("--file", help="Path to JSON input file (list of objects with 'text' field)")
    
    rewrite_parser.add_argument("--output", help="Path to output file (for batch processing)")
    
    args = parser.parse_args()
    
    if args.command == "rewrite":
        if args.text:
            # Single text mode
            result = process_single_item(args.text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.json:
            # JSON string mode
            try:
                data = json.loads(args.json)
                text = data.get("text")
                if not text:
                    print("Error: JSON must contain 'text' field.")
                    sys.exit(1)
                
                # Handle 'lang' or 'language' keys
                lang = data.get("lang") or data.get("language")
                result = process_single_item(text, lang)
                
                # Merge with input data to preserve ID etc
                output = data.copy()
                output.update(result)
                print(json.dumps(output, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("Error: Invalid JSON string.")
                sys.exit(1)
                
        elif args.file:
            # File batch mode
            if not os.path.exists(args.file):
                print(f"Error: File not found: {args.file}")
                sys.exit(1)
                
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    process_batch(data, args.output)
                elif isinstance(data, dict):
                    # Single object in file
                    text = data.get("text")
                    if text:
                        lang = data.get("lang") or data.get("language")
                        result = process_single_item(text, lang)
                        output = data.copy()
                        output.update(result)
                        print(json.dumps(output, indent=2, ensure_ascii=False))
                    else:
                        print("Error: JSON object must contain 'text' field.")
                else:
                    print("Error: JSON file must contain a list or an object.")
                    
            except json.JSONDecodeError:
                print("Error: Invalid JSON file.")
                sys.exit(1)
            except Exception as e:
                print(f"Error processing file: {e}")
                sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
