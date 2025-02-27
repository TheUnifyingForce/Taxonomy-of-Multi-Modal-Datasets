import json
from difflib import SequenceMatcher
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

class ImprovedDatatypeSimilarityAnalyzer:
    def __init__(self, similarity_threshold: float = 0.85):
        # Load configuration
        with open('5_3_3_pattern_similarity_config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.similarity_threshold = similarity_threshold
        
        # Build prefix and suffix lookup tables
        self.prefix_category_map = self._build_pattern_category_map(self.config['prefix_patterns'])
        self.suffix_category_map = self._build_pattern_category_map(self.config['suffix_patterns'])
        
        # High frequency patterns
        self.high_freq_prefixes = self.config['high_frequency_patterns']['prefixes']
        self.high_freq_suffixes = self.config['high_frequency_patterns']['suffixes']
    
    def _build_pattern_category_map(self, patterns: Dict) -> Dict[str, Tuple[str, str]]:
        """Build mapping from patterns to categories"""
        pattern_map = {}
        for category_type, categories in patterns.items():
            for category, terms in categories.items():
                for term in terms:
                    pattern_map[term] = (category_type, category)
        return pattern_map
    
    def normalize_type(self, dtype: str) -> str:
        """Normalize data type name"""
        return dtype.lower().replace('-', '_').replace(' ', '_')
    
    def get_string_similarity(self, a: str, b: str) -> float:
        """Calculate the similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def split_compound_type(self, dtype: str) -> List[str]:
        """Decompose a compound data type name while maintaining order"""
        return self.normalize_type(dtype).split('_')
    
    def get_pattern_categories(self, term: str, is_prefix: bool = True) -> Optional[Tuple[str, str]]:
        """Get category information for a pattern"""
        pattern_map = self.prefix_category_map if is_prefix else self.suffix_category_map
        return pattern_map.get(term)
    
    def should_group_types(self, type1: str, type2: str) -> bool:
        """Determine if two types should be grouped"""
        parts1 = self.split_compound_type(type1)
        parts2 = self.split_compound_type(type2)
        
        # 1. Check prefix patterns
        prefix1 = parts1[0] if parts1 else None
        prefix2 = parts2[0] if parts2 else None
        
        if prefix1 and prefix2:
            # Check high frequency prefixes
            if prefix1 in self.high_freq_prefixes and prefix2 in self.high_freq_prefixes:
                if prefix1 == prefix2:
                    return True
            
            # Check prefix categories
            prefix1_cat = self.get_pattern_categories(prefix1, True)
            prefix2_cat = self.get_pattern_categories(prefix2, True)
            if prefix1_cat and prefix2_cat and prefix1_cat == prefix2_cat:
                return True
        
        # 2. Check suffix patterns
        suffix1 = parts1[-1] if parts1 else None
        suffix2 = parts2[-1] if parts2 else None
        
        if suffix1 and suffix2:
            # Check high frequency suffixes
            if suffix1 in self.high_freq_suffixes and suffix2 in self.high_freq_suffixes:
                if suffix1 == suffix2:
                    return True
            
            # Check suffix categories
            suffix1_cat = self.get_pattern_categories(suffix1, False)
            suffix2_cat = self.get_pattern_categories(suffix2, False)
            if suffix1_cat and suffix2_cat and suffix1_cat == suffix2_cat:
                # If suffix categories are the same, check the similarity of the middle parts
                middle1 = parts1[1:-1] if len(parts1) > 2 else parts1
                middle2 = parts2[1:-1] if len(parts2) > 2 else parts2
                if set(middle1).intersection(set(middle2)):
                    return True
        
        # 3. As a fallback, check the similarity of the entire string
        if self.get_string_similarity(type1, type2) > self.similarity_threshold:
            return True
        
        return False
    
    def find_similar_groups(self, data_list: List[List]) -> Dict[str, List[Tuple[str, int]]]:
        """Find similar data type groups"""
        similar_groups = defaultdict(list)
        processed = set()
        
        # Convert list data to dictionary format
        counts_dict = {item[0]: item[1] for item in data_list}
        
        # Sort data types by frequency
        sorted_types = sorted(counts_dict.items(), key=lambda x: x[1], reverse=True)
        
        for type1, count1 in sorted_types:
            if type1 in processed:
                continue
            
            current_group = [(type1, count1)]
            processed.add(type1)
            
            for type2, count2 in sorted_types:
                if type2 in processed:
                    continue
                
                if self.should_group_types(type1, type2):
                    current_group.append((type2, count2))
                    processed.add(type2)
            
            if len(current_group) > 1:
                key = current_group[0][0]
                similar_groups[key] = current_group
        
        return similar_groups

    def analyze_and_generate_statistics(self, similar_groups: Dict[str, List[Tuple[str, int]]]) -> Dict:
        """Generate statistical analysis results"""
        stats = {
            "overall_statistics": {
                "total_groups": len(similar_groups),
                "total_types": sum(len(group) for group in similar_groups.values()),
                "total_frequency": sum(
                    sum(count for _, count in group)
                    for group in similar_groups.values()
                )
            },
            "matching_statistics": {
                "prefix_exact_match": defaultdict(int),
                "prefix_category_match": defaultdict(lambda: {
                    "group_count": 0,
                    "type_count": 0,
                    "total_frequency": 0,
                    "matched_patterns": set(),
                    "unmatched_patterns": set()
                }),
                "suffix_exact_match": defaultdict(int),
                "suffix_category_match": defaultdict(lambda: {
                    "group_count": 0,
                    "type_count": 0,
                    "total_frequency": 0,
                    "matched_patterns": set(),
                    "unmatched_patterns": set()
                }),
                "similarity_match": {
                    "group_count": 0,
                    "type_count": 0,
                    "total_frequency": 0
                }
            }
        }
        
        # Analyze matching situation for each group
        for key, group in similar_groups.items():
            group_freq = sum(count for _, count in group)
            parts = self.split_compound_type(key)
            prefix = parts[0] if parts else None
            suffix = parts[-1] if parts else None
            
            # Record matching type
            match_type = self._determine_match_type(key, group)
            
            # Update statistics based on matching type
            if match_type.startswith("prefix_exact"):
                stats["matching_statistics"]["prefix_exact_match"][prefix] += group_freq
                
            elif match_type.startswith("prefix_category"):
                prefix_cat = self.get_pattern_categories(prefix, True)
                if prefix_cat:
                    category = f"{prefix_cat[0]}_{prefix_cat[1]}"
                    cat_stats = stats["matching_statistics"]["prefix_category_match"][category]
                    cat_stats["group_count"] += 1
                    cat_stats["type_count"] += len(group)
                    cat_stats["total_frequency"] += group_freq
                    cat_stats["matched_patterns"].add(prefix)
                    
            elif match_type.startswith("suffix_exact"):
                stats["matching_statistics"]["suffix_exact_match"][suffix] += group_freq
                
            elif match_type.startswith("suffix_category"):
                suffix_cat = self.get_pattern_categories(suffix, False)
                if suffix_cat:
                    category = f"{suffix_cat[0]}_{suffix_cat[1]}"
                    cat_stats = stats["matching_statistics"]["suffix_category_match"][category]
                    cat_stats["group_count"] += 1
                    cat_stats["type_count"] += len(group)
                    cat_stats["total_frequency"] += group_freq
                    cat_stats["matched_patterns"].add(suffix)
                    
            elif match_type == "similarity":
                stats["matching_statistics"]["similarity_match"]["group_count"] += 1
                stats["matching_statistics"]["similarity_match"]["type_count"] += len(group)
                stats["matching_statistics"]["similarity_match"]["total_frequency"] += group_freq
        
        # Add unmatched patterns
        self._add_unmatched_patterns(stats)
        
        # Convert sets to lists for JSON serialization
        self._convert_sets_to_lists(stats)
        
        return stats

    def _determine_match_type(self, key: str, group: List[Tuple[str, int]]) -> str:
        """Determine the matching type for a group"""
        # Get the second element (if exists) for comparison
        second_type = group[1][0] if len(group) > 1 else None
        if not second_type:
            return "unknown"
        
        parts1 = self.split_compound_type(key)
        parts2 = self.split_compound_type(second_type)
        
        prefix1 = parts1[0] if parts1 else None
        prefix2 = parts2[0] if parts2 else None
        
        # Check prefix matches
        if prefix1 and prefix2:
            if (prefix1 in self.high_freq_prefixes and 
                prefix2 in self.high_freq_prefixes and 
                prefix1 == prefix2):
                return "prefix_exact"
            
            prefix1_cat = self.get_pattern_categories(prefix1, True)
            prefix2_cat = self.get_pattern_categories(prefix2, True)
            if prefix1_cat and prefix2_cat and prefix1_cat == prefix2_cat:
                return "prefix_category"
        
        # Check suffix matches
        suffix1 = parts1[-1] if parts1 else None
        suffix2 = parts2[-1] if parts2 else None
        
        if suffix1 and suffix2:
            if (suffix1 in self.high_freq_suffixes and 
                suffix2 in self.high_freq_suffixes and 
                suffix1 == suffix2):
                return "suffix_exact"
            
            suffix1_cat = self.get_pattern_categories(suffix1, False)
            suffix2_cat = self.get_pattern_categories(suffix2, False)
            if suffix1_cat and suffix2_cat and suffix1_cat == suffix2_cat:
                return "suffix_category"
        
        # If none of the above matches, it's similarity match
        return "similarity"

    def _add_unmatched_patterns(self, stats: Dict) -> None:
        """Add unmatched patterns"""
        # Add unmatched prefix patterns
        for category_type, categories in self.config['prefix_patterns'].items():
            for category, patterns in categories.items():
                cat_key = f"{category_type}_{category}"
                if cat_key in stats["matching_statistics"]["prefix_category_match"]:
                    current_matched = stats["matching_statistics"]["prefix_category_match"][cat_key]["matched_patterns"]
                    stats["matching_statistics"]["prefix_category_match"][cat_key]["unmatched_patterns"].update(
                        set(patterns) - current_matched
                    )
        
        # Add unmatched suffix patterns
        for category_type, categories in self.config['suffix_patterns'].items():
            for category, patterns in categories.items():
                cat_key = f"{category_type}_{category}"
                if cat_key in stats["matching_statistics"]["suffix_category_match"]:
                    current_matched = stats["matching_statistics"]["suffix_category_match"][cat_key]["matched_patterns"]
                    stats["matching_statistics"]["suffix_category_match"][cat_key]["unmatched_patterns"].update(
                        set(patterns) - current_matched
                    )

    def _convert_sets_to_lists(self, stats: Dict) -> None:
        """Convert sets in statistics to lists for JSON serialization"""
        for cat_stats in stats["matching_statistics"]["prefix_category_match"].values():
            cat_stats["matched_patterns"] = sorted(cat_stats["matched_patterns"])
            cat_stats["unmatched_patterns"] = sorted(cat_stats["unmatched_patterns"])
        
        for cat_stats in stats["matching_statistics"]["suffix_category_match"].values():
            cat_stats["matched_patterns"] = sorted(cat_stats["matched_patterns"])
            cat_stats["unmatched_patterns"] = sorted(cat_stats["unmatched_patterns"])

def main():
    # Load data
    with open('data_types_counts.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    # Create analyzer instance
    analyzer = ImprovedDatatypeSimilarityAnalyzer()
    
    # Analyze data
    similar_groups = analyzer.find_similar_groups(data_list)
    
    # Generate statistics
    statistics = analyzer.analyze_and_generate_statistics(similar_groups)
    
    # Organize results
    analysis_results = {
        "statistics": statistics,
        "groups": {}
    }
    
    # Sort groups by total frequency
    sorted_groups = []
    for key, group in similar_groups.items():
        total_freq = sum(count for _, count in group)
        sorted_groups.append((key, group, total_freq))
    
    sorted_groups.sort(key=lambda x: x[2], reverse=True)
    
    # Restructure group data
    for key, group, _ in sorted_groups:
        analysis_results["groups"][key] = {
            "total_frequency": sum(count for _, count in group),
            "types": [
                {"name": dtype, "frequency": count}
                for dtype, count in sorted(group, key=lambda x: x[1], reverse=True)
            ]
        }
    
    # Save JSON results
    with open('improved_similarity_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    report = ["Data Type Similarity Analysis Report", "=" * 50, "\n"]
    
    # Add overall statistics
    stats = statistics["overall_statistics"]
    report.append("Overall Statistics")
    report.append("-" * 30)
    report.append(f"Total Groups: {stats['total_groups']}")
    report.append(f"Total Types: {stats['total_types']}")
    report.append(f"Total Frequency: {stats['total_frequency']}\n")
    
    # Add matching statistics
    report.append("Matching Statistics")
    report.append("-" * 30)
    
    # Prefix exact matches
    report.append("\nPrefix Exact Matches:")
    for prefix, freq in sorted(statistics["matching_statistics"]["prefix_exact_match"].items(), 
                             key=lambda x: x[1], reverse=True):
        report.append(f"  {prefix}: {freq}")
    
    # Prefix category matches
    report.append("\nPrefix Category Matches:")
    for category, cat_stats in sorted(statistics["matching_statistics"]["prefix_category_match"].items()):
        if cat_stats["group_count"] > 0:
            report.append(f"\n{category}:")
            report.append(f"  Groups: {cat_stats['group_count']}")
            report.append(f"  Types: {cat_stats['type_count']}")
            report.append(f"  Total Frequency: {cat_stats['total_frequency']}")
            report.append(f"  Matched Patterns: {', '.join(cat_stats['matched_patterns'])}")
            if cat_stats["unmatched_patterns"]:
                report.append(f"  Unmatched Patterns: {', '.join(cat_stats['unmatched_patterns'])}")
    
    # Suffix exact matches
    report.append("\nSuffix Exact Matches:")
    for suffix, freq in sorted(statistics["matching_statistics"]["suffix_exact_match"].items(), 
                             key=lambda x: x[1], reverse=True):
        report.append(f"  {suffix}: {freq}")
    
    # Suffix category matches
    report.append("\nSuffix Category Matches:")
    for category, cat_stats in sorted(statistics["matching_statistics"]["suffix_category_match"].items()):
        if cat_stats["group_count"] > 0:
            report.append(f"\n{category}:")
            report.append(f"  Groups: {cat_stats['group_count']}")
            report.append(f"  Types: {cat_stats['type_count']}")
            report.append(f"  Total Frequency: {cat_stats['total_frequency']}")
            report.append(f"  Matched Patterns: {', '.join(cat_stats['matched_patterns'])}")
            if cat_stats["unmatched_patterns"]:
                report.append(f"  Unmatched Patterns: {', '.join(cat_stats['unmatched_patterns'])}")
    
    # Similarity match statistics
    report.append("\nSimilarity Matches:")
    sim_stats = statistics["matching_statistics"]["similarity_match"]
    report.append(f"  Groups: {sim_stats['group_count']}")
    report.append(f"  Types: {sim_stats['type_count']}")
    report.append(f"  Total Frequency: {sim_stats['total_frequency']}")
    
    # Add matching type distribution statistics
    report.append("\nMatching Type Distribution")
    report.append("-" * 30)
    
    # Calculate total frequency for each matching type
    total_prefix_exact = sum(statistics["matching_statistics"]["prefix_exact_match"].values())
    total_prefix_category = sum(
        cat_stats["total_frequency"] 
        for cat_stats in statistics["matching_statistics"]["prefix_category_match"].values()
    )
    total_suffix_exact = sum(statistics["matching_statistics"]["suffix_exact_match"].values())
    total_suffix_category = sum(
        cat_stats["total_frequency"] 
        for cat_stats in statistics["matching_statistics"]["suffix_category_match"].values()
    )
    total_similarity = statistics["matching_statistics"]["similarity_match"]["total_frequency"]
    
    # Calculate total frequency
    grand_total = total_prefix_exact + total_prefix_category + total_suffix_exact + \
                 total_suffix_category + total_similarity
    
    # Add distribution statistics
    if grand_total > 0:
        report.append(f"\nPrefix Exact Matches: {total_prefix_exact} ({(total_prefix_exact/grand_total)*100:.2f}%)")
        report.append(f"Prefix Category Matches: {total_prefix_category} ({(total_prefix_category/grand_total)*100:.2f}%)")
        report.append(f"Suffix Exact Matches: {total_suffix_exact} ({(total_suffix_exact/grand_total)*100:.2f}%)")
        report.append(f"Suffix Category Matches: {total_suffix_category} ({(total_suffix_category/grand_total)*100:.2f}%)")
        report.append(f"Similarity Matches: {total_similarity} ({(total_similarity/grand_total)*100:.2f}%)")
    
    # Add high frequency pattern statistics
    report.append("\nHigh Frequency Pattern Statistics")
    report.append("-" * 30)
    
    # High frequency prefix match statistics
    report.append("\nMost Common Prefix Match Patterns:")
    prefix_matches = statistics["matching_statistics"]["prefix_exact_match"]
    for prefix, freq in sorted(prefix_matches.items(), key=lambda x: x[1], reverse=True)[:10]:
        report.append(f"  {prefix}: {freq}")
    
    # High frequency suffix match statistics
    report.append("\nMost Common Suffix Match Patterns:")
    suffix_matches = statistics["matching_statistics"]["suffix_exact_match"]
    for suffix, freq in sorted(suffix_matches.items(), key=lambda x: x[1], reverse=True)[:10]:
        report.append(f"  {suffix}: {freq}")
    
    # Save report
    with open('improved_similarity_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

if __name__ == "__main__":
    main() 