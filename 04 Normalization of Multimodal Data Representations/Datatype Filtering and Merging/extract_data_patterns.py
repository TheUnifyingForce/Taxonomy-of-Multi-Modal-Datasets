import json
from collections import defaultdict
import re

def analyze_patterns(data_list):
    """Analyze common patterns in data types"""
    prefixes = defaultdict(int)
    suffixes = defaultdict(int)
    
    for dtype, count in data_list:
        # Split the type name into words
        words = dtype.lower().replace('-', ' ').replace('_', ' ').split()
        
        if len(words) >= 2:
            # Record the first word as a prefix
            prefixes[words[0]] += count
            # Record the last word as a suffix
            suffixes[words[-1]] += count
    
    return dict(prefixes), dict(suffixes)

def find_dimensional_prefixes(data_list):
    """Find dimension-related prefixes"""
    pattern = r'^(\d+d|multi|high|low|cross|inter|sub|super|meta)'
    dimensional = defaultdict(int)
    
    for dtype, count in data_list:
        match = re.match(pattern, dtype.lower())
        if match:
            dimensional[match.group(1)] += count
    
    return dict(dimensional)

def find_data_type_suffixes(data_list):
    """Find data type-related suffixes"""
    common_type_suffixes = {'data', 'signal', 'sequence', 'series', 'stream', 
                           'record', 'file', 'format', 'collection', 'set', 
                           'array', 'matrix', 'tensor', 'vector', 'map'}
    type_suffixes = defaultdict(int)
    
    for dtype, count in data_list:
        words = dtype.lower().split()
        if words[-1] in common_type_suffixes:
            type_suffixes[words[-1]] += count
    
    return dict(type_suffixes)

def main():
    # Load data
    with open('data_types_counts.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    # Analyze patterns
    prefixes, suffixes = analyze_patterns(data_list)
    dimensional_prefixes = find_dimensional_prefixes(data_list)
    type_suffixes = find_data_type_suffixes(data_list)
    
    # Sort by frequency
    sorted_prefixes = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)
    sorted_suffixes = sorted(suffixes.items(), key=lambda x: x[1], reverse=True)
    sorted_dimensional = sorted(dimensional_prefixes.items(), key=lambda x: x[1], reverse=True)
    sorted_type_suffixes = sorted(type_suffixes.items(), key=lambda x: x[1], reverse=True)
    
    # Output results
    print("Common prefixes (occurrences >= 50):")
    print("-" * 40)
    for prefix, count in sorted_prefixes:
        if count >= 50:
            print(f"{prefix}: {count}")
    
    print("\nDimension-related prefixes:")
    print("-" * 40)
    for prefix, count in sorted_dimensional:
        print(f"{prefix}: {count}")
    
    print("\nCommon suffixes (occurrences >= 50):")
    print("-" * 40)
    for suffix, count in sorted_suffixes:
        if count >= 50:
            print(f"{suffix}: {count}")
    
    print("\nData type-related suffixes:")
    print("-" * 40)
    for suffix, count in sorted_type_suffixes:
        print(f"{suffix}: {count}")
    
    # Save results
    results = {
        'common_prefixes': dict(sorted_prefixes),
        'dimensional_prefixes': dict(sorted_dimensional),
        'common_suffixes': dict(sorted_suffixes),
        'type_suffixes': dict(sorted_type_suffixes)
    }
    
    with open('data_pattern_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main() 