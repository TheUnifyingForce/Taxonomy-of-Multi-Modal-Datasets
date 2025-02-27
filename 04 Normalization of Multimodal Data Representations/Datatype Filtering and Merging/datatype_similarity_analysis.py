import json
from difflib import SequenceMatcher
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class DatatypeSimilarityAnalyzer:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.common_prefixes = {'3d', '2d', '4d'}
        self.common_words = {'data', 'signal', 'information', 'sequence'}
    
    def normalize_type(self, dtype: str) -> str:
        """Normalize data type name"""
        return dtype.lower().replace('-', '_').replace(' ', '_')
    
    def get_string_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def split_compound_type(self, dtype: str) -> Set[str]:
        """Split compound data type name"""
        parts = set(self.normalize_type(dtype).split('_'))
        return {p for p in parts if p not in self.common_words}
    
    def find_similar_groups(self, data_list: List[List]) -> Dict[str, List[Tuple[str, int]]]:
        """Find groups of similar data types"""
        similar_groups = defaultdict(list)
        processed = set()
        
        # Convert list data to dictionary format
        counts_dict = {item[0]: item[1] for item in data_list}
        
        # Data types sorted by frequency
        sorted_types = sorted(counts_dict.items(), key=lambda x: x[1], reverse=True)
        
        for type1, count1 in sorted_types:
            if type1 in processed:
                continue
                
            current_group = [(type1, count1)]
            processed.add(type1)
            norm_type1 = self.normalize_type(type1)
            parts1 = self.split_compound_type(type1)
            
            for type2, count2 in sorted_types:
                if type2 in processed:
                    continue
                    
                norm_type2 = self.normalize_type(type2)
                parts2 = self.split_compound_type(type2)
                
                # Check similarity conditions
                should_group = False
                
                # 1. Direct string similarity
                if self.get_string_similarity(norm_type1, norm_type2) > self.similarity_threshold:
                    should_group = True
                
                # 2. Common keywords
                elif len(parts1.intersection(parts2)) >= min(len(parts1), len(parts2)) * 0.5:
                    should_group = True
                
                # 3. Prefix/suffix patterns
                elif any(p in self.common_prefixes for p in parts1.intersection(parts2)):
                    remaining1 = parts1 - self.common_prefixes
                    remaining2 = parts2 - self.common_prefixes
                    if remaining1.intersection(remaining2):
                        should_group = True
                
                if should_group:
                    current_group.append((type2, count2))
                    processed.add(type2)
            
            if len(current_group) > 1:
                # Use the most frequent type as group name
                key = current_group[0][0]
                similar_groups[key] = current_group
        
        return similar_groups
    
    def analyze_and_report(self, data_list: List[List]) -> Tuple[Dict[str, List[Tuple[str, int]]], str]:
        """Analyze data types and generate report"""
        similar_groups = self.find_similar_groups(data_list)
        
        # 生成报告
        report = ["Data Type Similarity Analysis Report\n" + "="*50 + "\n"]
        
        total_groups = len(similar_groups)
        total_types_in_groups = sum(len(group) for group in similar_groups.values())
        
        report.append(f"Found {total_groups} groups of similar data types, involving {total_types_in_groups} types\n")
        
        for key, group in similar_groups.items():
            total_frequency = sum(count for _, count in group)
            report.append(f"\nGroup: {key} (Total Frequency: {total_frequency})")
            report.append("-" * 40)
            for dtype, count in sorted(group, key=lambda x: x[1], reverse=True):
                report.append(f"  - {dtype}: {count}")
        
        return similar_groups, "\n".join(report)

def main():
    # Load data
    with open('data_types_counts.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    # Create analyzer instance
    analyzer = DatatypeSimilarityAnalyzer(similarity_threshold=0.85)
    
    # Analyze data
    similar_groups, report = analyzer.analyze_and_report(data_list)
    
    # Save report
    with open('datatype_similarity_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Print report
    print(report)
    
    # Save grouping results as JSON
    groups_json = {
        key: {
            "total_frequency": sum(count for _, count in group),
            "types": [{
                "name": dtype,
                "frequency": count
            } for dtype, count in sorted(group, key=lambda x: x[1], reverse=True)]
        }
        for key, group in similar_groups.items()
    }
    
    with open('datatype_similar_groups.json', 'w', encoding='utf-8') as f:
        json.dump(groups_json, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main() 