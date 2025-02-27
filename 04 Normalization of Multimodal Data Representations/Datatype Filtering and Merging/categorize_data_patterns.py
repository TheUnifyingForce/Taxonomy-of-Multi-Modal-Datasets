import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def analyze_high_frequency_patterns(patterns: Dict[str, Dict[str, int]], 
                                  threshold: int = 100) -> Dict[str, int]:
    """Analyze high-frequency patterns (frequency >= threshold)"""
    return {k: v for k, v in patterns.items() if v >= threshold}

def suggest_categories(prefixes: Dict[str, int]) -> Dict[str, List[str]]:
    """Suggest categories based on prefix data"""
    # Basic category definitions 
    categories = {
        'visual': ['image', 'visual', 'rgb', 'depth', 'scene', 'face', 'video', 'camera', 'object'],
        'audio': ['audio', 'speech', 'sound', 'acoustic', 'voice'],
        'text': ['text', 'sentence', 'word', 'document', 'language'],
        'medical': ['medical', 'clinical', 'patient', 'health'],
        'dimensional': ['2d', '3d', '4d', 'multi'],
        'data': ['dataset', 'data', 'annotated', 'synthetic'],
        'sensor': ['rgb', 'lidar', 'radar', 'thermal', 'imu', 'gps']
    }
    
    # Convert category values to set for calculation, but return as list
    categories_sets = {k: set(v) for k, v in categories.items()}
    high_freq = {k for k, v in prefixes.items() if v >= 100}
    uncategorized = high_freq - set.union(*categories_sets.values())
    
    if uncategorized:
        categories['high_frequency_others'] = list(uncategorized)  # Convert to list
    
    return categories  

def analyze_patterns_for_similarity(patterns: Dict[str, Dict[str, int]]) -> Dict:
    """Analyze patterns for similarity matching"""
    
    # 1. Extract high-frequency patterns (frequency >= 100)
    high_freq_patterns = {
        'prefixes': {k: v for k, v in patterns['common_prefixes'].items() if v >= 100},
        'suffixes': {k: v for k, v in patterns['common_suffixes'].items() if v >= 100}
    }
    
    # 2. Prefix categories
    prefix_categories = {
        'modality': {  # Data modality
            'visual': ['image', 'visual', 'rgb', 'depth', 'scene', 'face', 'video', 'camera'],
            'audio': ['speech', 'audio', 'sound', 'voice', 'acoustic'],
            'text': ['text', 'sentence', 'word', 'document', 'language'],
            'sensor': ['rgb', 'lidar', 'radar', 'thermal', 'imu', 'gps']
        },
        'attributes': {  # Data attributes
            'dimensional': ['2d', '3d', '4d', 'multi'],
            'quality': ['high', 'low', 'raw', 'clean', 'noisy'],
            'processing': ['annotated', 'synthetic', 'processed', 'labeled']
        },
        'domain': {  # Domain specific
            'medical': ['medical', 'clinical', 'patient', 'health'],
            'scientific': ['scientific', 'research', 'experimental'],
            'social': ['social', 'user', 'human', 'personal']
        }
    }
    
    # 3. Suffix categories
    suffix_categories = {
        'content': {  # Content type
            'visual': ['image', 'video', 'photo', 'frame', 'scene'],
            'text': ['description', 'text', 'sentence', 'document', 'article'],
            'audio': ['audio', 'speech', 'sound', 'recording']
        },
        'annotation': {  # Annotation type
            'label': ['annotation', 'label', 'tag', 'mark'],
            'description': ['description', 'caption', 'summary'],
            'metadata': ['metadata', 'information', 'attribute']
        },
        'data_structure': {  # Data structure
            'sequence': ['sequence', 'series', 'stream', 'trajectory'],
            'collection': ['set', 'collection', 'array', 'matrix', 'vector'],
            'graph': ['graph', 'network', 'tree']
        },
        'data_format': {  # Data format
            'file': ['file', 'format', 'record', 'document'],
            'signal': ['signal', 'data', 'feature'],
            'mask': ['mask', 'segmentation', 'map']
        }
    }
    
    # 4. Validate and update categories
    validated_patterns = {
        'prefixes': {},
        'suffixes': {},
        'high_frequency': high_freq_patterns
    }
    
    # Validate prefix categories
    for category_type, categories in prefix_categories.items():
        validated_patterns['prefixes'][category_type] = {}
        for category, terms in categories.items():
            valid_terms = {
                term: patterns['common_prefixes'].get(term, 0)
                for term in terms
                if patterns['common_prefixes'].get(term, 0) >= 10
            }
            if valid_terms:
                validated_patterns['prefixes'][category_type][category] = valid_terms
    
    # Validate suffix categories
    for category_type, categories in suffix_categories.items():
        validated_patterns['suffixes'][category_type] = {}
        for category, terms in categories.items():
            valid_terms = {
                term: patterns['common_suffixes'].get(term, 0)
                for term in terms
                if patterns['common_suffixes'].get(term, 0) >= 10
            }
            if valid_terms:
                validated_patterns['suffixes'][category_type][category] = valid_terms
    
    return validated_patterns

def generate_similarity_config(validated_patterns: Dict) -> Dict:
    """Generate configuration for similarity analyzer"""
    return {
        'prefix_patterns': {
            category_type: {
                category: list(terms.keys())
                for category, terms in categories.items()
            }
            for category_type, categories in validated_patterns['prefixes'].items()
        },
        'suffix_patterns': {
            category_type: {
                category: list(terms.keys())
                for category, terms in categories.items()
            }
            for category_type, categories in validated_patterns['suffixes'].items()
        }
    }

def main():
    # Load pattern analysis results
    with open('pattern_analysis.json', 'r', encoding='utf-8') as f:
        patterns = json.load(f)
    
    # Analyze patterns
    validated_patterns = analyze_patterns_for_similarity(patterns)
    
    # Generate configuration
    similarity_config = generate_similarity_config(validated_patterns)
    
    # Save analysis report
    report = ["Data Type Pattern Analysis Report", "=" * 50, "\n"]
    
    # 1. Add high-frequency pattern statistics
    report.append("1. High-Frequency Pattern Analysis (frequency >= 100)")
    report.append("-" * 30)
    
    report.append("\nHigh-frequency prefixes:")
    for prefix, count in sorted(validated_patterns['high_frequency']['prefixes'].items(), 
                              key=lambda x: x[1], reverse=True):
        report.append(f"  - {prefix}: {count}")
    
    report.append("\nHigh-frequency suffixes:")
    for suffix, count in sorted(validated_patterns['high_frequency']['suffixes'].items(), 
                              key=lambda x: x[1], reverse=True):
        report.append(f"  - {suffix}: {count}")
    
    # 2. Add validated pattern statistics
    report.append("\n\n2. Categorized Pattern Analysis")
    report.append("-" * 30)
    for pattern_type, categories in validated_patterns.items():
        if pattern_type != 'high_frequency':  # Skip already reported high-frequency patterns
            report.append(f"\n{pattern_type.upper()} Analysis")
            report.append("-" * 20)
            for category_type, category_dict in categories.items():
                report.append(f"\n{category_type}:")
                for category, terms in category_dict.items():
                    report.append(f"\n  {category}:")
                    for term, freq in sorted(terms.items(), key=lambda x: x[1], reverse=True):
                        report.append(f"    - {term}: {freq}")
    
    # Save report
    with open('pattern_categories_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # Save configuration (including high-frequency patterns)
    similarity_config['high_frequency_patterns'] = validated_patterns['high_frequency']
    with open('pattern_similarity_config.json', 'w', encoding='utf-8') as f:
        json.dump(similarity_config, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main() 