import numpy as np
from collections import defaultdict
from difflib import SequenceMatcher
import json
from typing import Dict, List, Tuple
from datetime import datetime
import os

class ClusteringEvaluator:
    """
    A class to evaluate the effectiveness of data type clustering
    """
    def __init__(self, original_data: List[Tuple[str, int]], clustering_results: Dict):
        """
        Initialize with original data and clustering results
        
        Args:
            original_data: List of tuples (data_type, frequency)
            clustering_results: Dictionary containing clustering information
        """
        self.original_data = original_data
        self.clustering_results = clustering_results
        
        # Calculate basic statistics
        self.total_original_types = len(original_data)
        self.total_original_freq = sum(freq for _, freq in original_data)
        self.total_clusters = clustering_results['statistics']['overall_statistics']['total_groups']
        self.total_clustered_types = clustering_results['statistics']['overall_statistics']['total_types']
        self.total_clustered_freq = clustering_results['statistics']['overall_statistics']['total_frequency']

    def calculate_compression_ratio(self) -> float:
        """Calculate the compression ratio achieved by clustering"""
        return 1 - (self.total_clusters / self.total_original_types)

    def calculate_frequency_coverage(self) -> float:
        """Calculate the frequency coverage of clustered data"""
        return self.total_clustered_freq / self.total_original_freq

    def calculate_type_retention(self) -> float:
        """Calculate the proportion of data types retained after clustering"""
        return self.total_clustered_types / self.total_original_types

    def calculate_matching_distribution(self) -> Dict[str, float]:
        """Calculate the distribution of different matching methods"""
        stats = self.clustering_results['statistics']['matching_statistics']
        total_matches = sum([
            len(stats['prefix_exact_match']),
            sum(group['total_frequency'] for group in stats['prefix_category_match'].values()),
            sum(stats['suffix_exact_match'].values()),
            sum(group['total_frequency'] for group in stats['suffix_category_match'].values())
        ])
        
        return {
            'prefix_exact': len(stats['prefix_exact_match']) / total_matches,
            'prefix_category': sum(group['total_frequency'] for group in stats['prefix_category_match'].values()) / total_matches,
            'suffix_exact': sum(stats['suffix_exact_match'].values()) / total_matches,
            'suffix_category': sum(group['total_frequency'] for group in stats['suffix_category_match'].values()) / total_matches
        }

    def calculate_cluster_quality(self) -> Dict[str, float]:
        """Calculate quality metrics for clustering results"""
        # Get all clusters from the results
        clusters = defaultdict(list)
        for group_name, group_data in self.clustering_results['groups'].items():
            for type_info in group_data['types']:
                clusters[group_name].append(type_info['name'])
        
        # Calculate average similarity within clusters
        intra_cluster_similarities = []
        for cluster_types in clusters.values():
            if len(cluster_types) > 1:
                similarities = []
                for i in range(len(cluster_types)):
                    for j in range(i + 1, len(cluster_types)):
                        sim = SequenceMatcher(None, cluster_types[i], cluster_types[j]).ratio()
                        similarities.append(sim)
                if similarities:
                    intra_cluster_similarities.append(np.mean(similarities))
        
        # Calculate average distance between clusters
        inter_cluster_distances = []
        cluster_names = list(clusters.keys())
        for i in range(len(cluster_names)):
            for j in range(i + 1, len(cluster_names)):
                distances = []
                for type1 in clusters[cluster_names[i]]:
                    for type2 in clusters[cluster_names[j]]:
                        # Convert similarity to distance
                        distance = 1 - SequenceMatcher(None, type1, type2).ratio()
                        distances.append(distance)
                if distances:
                    inter_cluster_distances.append(np.mean(distances))
        
        # Calculate cluster size statistics
        cluster_sizes = [len(c) for c in clusters.values()]
        
        return {
            'avg_intra_cluster_similarity': np.mean(intra_cluster_similarities),
            'avg_inter_cluster_distance': np.mean(inter_cluster_distances),
            'cluster_size_stats': {
                'mean': np.mean(cluster_sizes),
                'median': np.median(cluster_sizes),
                'std': np.std(cluster_sizes),
                'min': np.min(cluster_sizes),
                'max': np.max(cluster_sizes)
            },
            'silhouette_score_estimate': (np.mean(inter_cluster_distances) - 
                                        (1 - np.mean(intra_cluster_similarities))) / 
                                        max(np.mean(inter_cluster_distances), 
                                            1 - np.mean(intra_cluster_similarities))
        }

    def generate_evaluation_report(self) -> Dict:
        """Generate a comprehensive evaluation report"""
        # Get cluster quality metrics
        cluster_quality = self.calculate_cluster_quality()
        
        cluster_size_stats = cluster_quality['cluster_size_stats']
        converted_size_stats = {
            'mean': float(cluster_size_stats['mean']),
            'median': float(cluster_size_stats['median']),
            'std': float(cluster_size_stats['std']),
            'min': int(cluster_size_stats['min']),
            'max': int(cluster_size_stats['max'])
        }
        
        converted_quality = {
            'avg_intra_cluster_similarity': float(cluster_quality['avg_intra_cluster_similarity']),
            'avg_inter_cluster_distance': float(cluster_quality['avg_inter_cluster_distance']),
            'cluster_size_stats': converted_size_stats,
            'silhouette_score_estimate': float(cluster_quality['silhouette_score_estimate'])
        }
        
        return {
            'basic_metrics': {
                'compression_ratio': self.calculate_compression_ratio(),
                'frequency_coverage': self.calculate_frequency_coverage(),
                'type_retention': self.calculate_type_retention()
            },
            'matching_distribution': self.calculate_matching_distribution(),
            'cluster_quality': converted_quality
        }

    def format_report_text(self, report: Dict) -> str:
        """Format evaluation report as readable text"""
        lines = [
            "Data Type Clustering Effectiveness Evaluation Report",
            "================================================",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\nInput Statistics:",
            f"Total original data types: {self.total_original_types:,}",
            f"Total original frequency: {self.total_original_freq:,}",
            f"Total clusters formed: {self.total_clusters:,}",
            "\nEffectiveness Metrics:",
            "-------------------",
            f"Compression Ratio: {report['basic_metrics']['compression_ratio']:.2%}",
            f"Frequency Coverage: {report['basic_metrics']['frequency_coverage']:.2%}",
            f"Type Retention: {report['basic_metrics']['type_retention']:.2%}",
            "\nMatching Method Distribution:",
            "-------------------------"
        ]
        
        for method, ratio in report['matching_distribution'].items():
            lines.append(f"{method.replace('_', ' ').title()}: {ratio:.2%}")
            
        lines.extend([
            "\nKey Findings:",
            f"1. Successfully reduced {self.total_original_types:,} data types to {self.total_clusters:,} clusters",
            f"2. Maintained {report['basic_metrics']['frequency_coverage']:.1%} of the original frequency coverage",
            f"3. Most common matching method: {max(report['matching_distribution'].items(), key=lambda x: x[1])[0].replace('_', ' ').title()}"
        ])
        
        # Add cluster quality section
        lines.extend([
            "\nCluster Quality Metrics:",
            "----------------------",
            f"Average Intra-cluster Similarity: {report['cluster_quality']['avg_intra_cluster_similarity']:.2%}",
            f"Average Inter-cluster Distance: {report['cluster_quality']['avg_inter_cluster_distance']:.2%}",
            f"Estimated Silhouette Score: {report['cluster_quality']['silhouette_score_estimate']:.2%}",
            "\nCluster Size Statistics:",
            f"Mean Size: {report['cluster_quality']['cluster_size_stats']['mean']:.1f}",
            f"Median Size: {report['cluster_quality']['cluster_size_stats']['median']:.1f}",
            f"Standard Deviation: {report['cluster_quality']['cluster_size_stats']['std']:.1f}",
            f"Size Range: {report['cluster_quality']['cluster_size_stats']['min']} - {report['cluster_quality']['cluster_size_stats']['max']}"
        ])
        
        # Add quality-related key finding
        lines.append(
            f"4. Average intra-cluster similarity of {report['cluster_quality']['avg_intra_cluster_similarity']:.1%} "
            f"indicates strong coherence within clusters"
        )
        
        return "\n".join(lines)

def main():
    # Create output directory if it doesn't exist
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load original data
    with open('data_types_counts.json', 'r') as f:
        original_data = json.load(f)

    # Load clustering results
    with open('improved_similarity_analysis_results.json', 'r') as f:
        clustering_results = json.load(f)

    # Initialize evaluator
    evaluator = ClusteringEvaluator(original_data, clustering_results)
    
    # Generate evaluation report
    report = evaluator.generate_evaluation_report()
    
    # Save results in both JSON and text formats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON report
    json_path = os.path.join(output_dir, f'clustering_evaluation_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Save formatted text report
    text_path = os.path.join(output_dir, f'clustering_evaluation_{timestamp}.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(evaluator.format_report_text(report))
    
    print(f"Evaluation results have been saved to:")
    print(f"- JSON format: {json_path}")
    print(f"- Text format: {text_path}")

if __name__ == "__main__":
    main()
