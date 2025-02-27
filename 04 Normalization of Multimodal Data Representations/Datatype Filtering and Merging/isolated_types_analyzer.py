import json
from typing import List, Dict, Set
from collections import defaultdict

def extract_isolated_types(data_list: List[List], matched_types: Set[str]) -> Dict[str, int]:
    """Extract unmatched data types and their frequencies"""
    return {
        item[0]: item[1]
        for item in data_list 
        if item[0] not in matched_types
    }

def analyze_isolated_types(isolated_types: Dict[str, int]) -> Dict:
    """Analyze isolated data types"""
    # Define frequency ranges
    frequency_ranges = [
        (500, float('inf'), '500+'),
        (100, 499, '100-499'),
        (50, 99, '50-99'),
        (10, 49, '10-49'),
        (1, 9, '1-9')
    ]
    
    analysis = {
        "statistics": {
            "total_isolated": len(isolated_types),
            "total_frequency": sum(isolated_types.values()),
            "frequency_distribution": defaultdict(list)
        },
        "categories": {
            "special_pattern": defaultdict(dict),  # Category by frequency range special pattern
            "potential_errors": defaultdict(dict),  # Category by frequency range potential errors
            "simple_types": defaultdict(dict),     # Category by frequency range simple types
        }
    }
    
    # Analyze each type
    for dtype, freq in isolated_types.items():
        # Determine frequency range
        for min_freq, max_freq, range_label in frequency_ranges:
            if min_freq <= freq <= max_freq:
                # Category processing
                if any(char in dtype for char in ['_', '-', ' ']):
                    analysis["categories"]["special_pattern"][range_label][dtype] = freq
                elif not dtype.isalnum():
                    analysis["categories"]["potential_errors"][range_label][dtype] = freq
                else:
                    analysis["categories"]["simple_types"][range_label][dtype] = freq
                
                analysis["statistics"]["frequency_distribution"][range_label].append(dtype)
                break
    
    # Count types in each frequency range
    analysis["statistics"]["frequency_counts"] = {
        range_label: len(types)
        for range_label, types in analysis["statistics"]["frequency_distribution"].items()
    }
    
    return analysis

def generate_report(analysis: Dict) -> List[str]:
    """Generate analysis report"""
    report = ["Isolated Data Types Analysis Report", "=" * 50, "\n"]
    
    # Overall statistics
    stats = analysis["statistics"]
    report.extend([
        "Overall Statistics:",
        f"- Total isolated types: {stats['total_isolated']}",
        f"- Total frequency: {stats['total_frequency']}",
        "\nFrequency Distribution:",
    ])
    
    for range_label, count in stats["frequency_counts"].items():
        report.append(f"- {range_label}: {count} types")
    
    # Category details
    for category, freq_ranges in analysis["categories"].items():
        report.extend([
            f"\n{category}:",
            "-" * 40
        ])
        for range_label, types in freq_ranges.items():
            if types:
                report.append(f"\n{range_label} frequency range:")
                for dtype, freq in sorted(types.items(), key=lambda x: x[1], reverse=True):
                    report.append(f"  - {dtype}: {freq}")
    
    return report

def main():
    # Load original data
    with open('data_types_counts.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    # Load matched types
    with open('improved_similarity_analysis_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
        matched_types = {
            dtype["name"]
            for group in results["groups"].values()
            for dtype in group["types"]  # Removed extra nesting levels
        }
    
    # Extract and analyze isolated types
    isolated_types = extract_isolated_types(data_list, matched_types)
    analysis = analyze_isolated_types(isolated_types)
    
    # Generate report
    report = generate_report(analysis)
    
    # Save analysis results
    with open('isolated_types_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Save isolated type data
    isolated_data = {
        "total_count": len(isolated_types),
        "types": {
            dtype: freq
            for dtype, freq in sorted(isolated_types.items(), key=lambda x: x[1], reverse=True)
        }
    }
    with open('isolated_types.json', 'w', encoding='utf-8') as f:
        json.dump(isolated_data, f, indent=2, ensure_ascii=False)
    
    # Save report
    with open('isolated_types_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

if __name__ == "__main__":
    main() 