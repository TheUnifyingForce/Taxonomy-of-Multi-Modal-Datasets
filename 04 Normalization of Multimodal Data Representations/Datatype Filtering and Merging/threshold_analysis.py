import json
import importlib
from datatype_similarity_analysis import DatatypeSimilarityAnalyzer
from collections import defaultdict
import matplotlib.pyplot as plt

def analyze_threshold_impact(data_list, thresholds):
    """Analyze the impact of different thresholds"""
    results = []
    
    for threshold in thresholds:
        analyzer = DatatypeSimilarityAnalyzer(similarity_threshold=threshold)
        similar_groups, _ = analyzer.analyze_and_report(data_list)
        
        # Calculate statistics
        total_groups = len(similar_groups)
        total_types_in_groups = sum(len(group) for group in similar_groups.values())
        avg_group_size = total_types_in_groups / total_groups if total_groups > 0 else 0
        
        # Calculate group size distribution
        group_sizes = [len(group) for group in similar_groups.values()]
        max_group_size = max(group_sizes) if group_sizes else 0
        
        results.append({
            'threshold': threshold,
            'total_groups': total_groups,
            'total_types_in_groups': total_types_in_groups,
            'avg_group_size': avg_group_size,
            'max_group_size': max_group_size
        })
    
    return results

def plot_threshold_analysis(results):
    """Plot threshold analysis charts"""
    plt.figure(figsize=(15, 10))
    
    # Create subplots
    plt.subplot(2, 2, 1)
    plt.plot([r['threshold'] for r in results], 
            [r['total_groups'] for r in results], 
            marker='o')
    plt.title('Number of Groups vs Threshold')
    plt.xlabel('Similarity Threshold')
    plt.ylabel('Number of Groups')
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot([r['threshold'] for r in results], 
            [r['total_types_in_groups'] for r in results], 
            marker='o')
    plt.title('Total Types in Groups vs Threshold')
    plt.xlabel('Similarity Threshold')
    plt.ylabel('Total Types in Groups')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot([r['threshold'] for r in results], 
            [r['avg_group_size'] for r in results], 
            marker='o')
    plt.title('Average Group Size vs Threshold')
    plt.xlabel('Similarity Threshold')
    plt.ylabel('Average Group Size')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    plt.plot([r['threshold'] for r in results], 
            [r['max_group_size'] for r in results], 
            marker='o')
    plt.title('Maximum Group Size vs Threshold')
    plt.xlabel('Similarity Threshold')
    plt.ylabel('Maximum Group Size')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('threshold_analysis.pdf', format='pdf')
    plt.close()

def main():
    # Load data
    with open('data_types_counts.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    # Analyze different thresholds
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    results = analyze_threshold_impact(data_list, thresholds)
    
    # Plot analysis charts
    plot_threshold_analysis(results)
    
    # Print detailed results
    print("Threshold Analysis Results:")
    print("=" * 80)
    print(f"{'Threshold':^10} {'Groups':^10} {'Total Types':^12} {'Avg Size':^12} {'Max Size':^12}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['threshold']:^10.2f} {r['total_groups']:^10d} "
              f"{r['total_types_in_groups']:^12d} {r['avg_group_size']:^12.2f} "
              f"{r['max_group_size']:^12d}")
    
    # Save results
    with open('threshold_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main() 