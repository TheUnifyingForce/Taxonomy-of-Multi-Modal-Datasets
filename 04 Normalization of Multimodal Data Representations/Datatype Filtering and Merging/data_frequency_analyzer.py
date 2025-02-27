import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import PercentFormatter

# Set style parameters
plt.style.use('default')  
sns.set_theme(style="whitegrid")  
plt.rcParams['pdf.fonttype'] = 42  
plt.rcParams['font.family'] = 'Arial'

def load_data(filepath):
    """Load and parse data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    frequencies = [item[1] for item in data]
    type_names = [item[0] for item in data]
    return frequencies, type_names

def create_frequency_analysis_plot(frequencies, save_path):
    """Create comprehensive frequency analysis plot"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    for ax in [ax1, ax2]:
        ax.spines['top'].set_color('black')
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_color('black')
        ax.spines['right'].set_color('black')
        ax.tick_params(colors='black')
    
    # Left plot: Frequency distribution
    sns.histplot(data=frequencies, ax=ax1, bins=50)  
    ax1.set_title('Frequency Distribution')
    ax1.set_xlabel('Frequency')
    ax1.set_ylabel('Count')
    
    # Right plot: Cumulative percentage curve
    sorted_freq = sorted(frequencies, reverse=True)
    cumsum = np.cumsum(sorted_freq)
    cumsum_percent = cumsum / cumsum[-1] * 100
    
    ax2.plot(range(1, len(frequencies) + 1), cumsum_percent, 'b-', linewidth=2)
    ax2.set_title('Cumulative Frequency Distribution')
    ax2.set_xlabel('Number of Data Types')
    ax2.set_ylabel('Cumulative Percentage')
    ax2.yaxis.set_major_formatter(PercentFormatter())
    ax2.grid(True, alpha=0.3, color='black', linestyle=':')
    
    # Add 80% reference line
    eighty_percent_idx = np.where(cumsum_percent >= 80)[0][0]
    ax2.axhline(y=80, color='r', linestyle='--', alpha=0.5)
    ax2.axvline(x=eighty_percent_idx, color='r', linestyle='--', alpha=0.5)
    ax2.text(eighty_percent_idx + 5, 82, 
             f'{eighty_percent_idx} types ({eighty_percent_idx/len(frequencies):.1%})\ncover 80% of occurrences',
             verticalalignment='bottom')
    
    # Add other milestone lines
    milestones = [25, 50, 75, 90, 95]
    colors = ['g', 'y', 'c', 'm', 'k']
    for milestone, color in zip(milestones, colors):
        idx = np.where(cumsum_percent >= milestone)[0][0]
        ax2.axhline(y=milestone, color=color, linestyle=':', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, format='pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    return eighty_percent_idx, cumsum_percent

def create_analysis_report(frequencies, type_names, eighty_percent_idx, cumsum_percent, output_file):
    """Generate detailed analysis report"""
    total_types = len(frequencies)
    total_frequency = int(sum(frequencies)) 
    
    # Sort data by frequency
    sorted_data = sorted(zip(type_names, frequencies), key=lambda x: x[1], reverse=True)
    
    # Create distribution data for JSON
    distribution_data = {
        "summary": {
            "total_types": int(total_types),  
            "total_occurrences": total_frequency,
            "mean_frequency": float(np.mean(frequencies)),
            "median_frequency": float(np.median(frequencies)),
            "std_deviation": float(np.std(frequencies)),
            "min_frequency": int(float(min(frequencies))), 
            "max_frequency": int(float(max(frequencies))), 
            "types_for_80_percent": int(eighty_percent_idx)
        },
        "cumulative_milestones": [],
        "type_distribution": []
    }
    
    # Add cumulative milestone data
    percentiles = [25, 50, 75, 80, 90, 95, 99, 100]
    for p in percentiles:
        idx = np.where(cumsum_percent >= p)[0][0]
        distribution_data["cumulative_milestones"].append({
            "percentile": int(p), 
            "types_count": int(idx + 1), 
            "types_percentage": float((idx+1)/total_types*100)
        })
    
    # Add type distribution data
    for i, (dtype, freq) in enumerate(sorted_data, 1):
        distribution_data["type_distribution"].append({
            "rank": i,
            "type": str(dtype),  
            "frequency": int(float(freq)), 
            "percentage": float((freq / total_frequency) * 100),
            "cumulative_percentage": float(cumsum_percent[i-1])
        })
    
    # Save distribution data as JSON
    with open('frequency_distribution.json', 'w', encoding='utf-8') as json_file:
        json.dump(distribution_data, json_file, indent=4)

    # Write text report as before
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write summary statistics
        f.write("Data Type Frequency Analysis Report\n")
        f.write("=================================\n\n")
        
        f.write("Summary Statistics:\n")
        f.write("-----------------\n")
        f.write(f"Total unique data types: {total_types}\n")
        f.write(f"Total occurrences: {total_frequency}\n")
        f.write(f"Mean frequency: {np.mean(frequencies):.2f}\n")
        f.write(f"Median frequency: {np.median(frequencies):.2f}\n")
        f.write(f"Standard deviation: {np.std(frequencies):.2f}\n")
        f.write(f"Range: {min(frequencies)} to {max(frequencies)}\n")
        f.write(f"Number of types covering 80% of occurrences: {eighty_percent_idx}\n\n")
        
        # Write distribution information
        f.write("Cumulative Distribution Milestones:\n")
        f.write("--------------------------------\n")
        percentiles = [25, 50, 75, 80, 90, 95, 99, 100]
        for p in percentiles:
            idx = np.where(cumsum_percent >= p)[0][0]
            f.write(f"{p}% of occurrences covered by top {idx+1} types ({((idx+1)/total_types)*100:.1f}% of all types)\n")
        f.write("\n")
        
        # Write complete frequency distribution
        f.write("Complete Data Type Distribution:\n")
        f.write("-----------------------------\n")
        f.write("Rank. Data Type: Frequency (Percentage of Total)\n\n")
        
        for i, (dtype, freq) in enumerate(sorted_data, 1):
            percentage = (freq / total_frequency) * 100
            cumulative_percentage = cumsum_percent[i-1]
            f.write(f"{i}. {dtype}: {freq} ({percentage:.2f}%) [Cumulative: {cumulative_percentage:.2f}%]\n")

def main():
    try:
        # Load data
        frequencies, type_names = load_data('data_types_counts.json')
        
        # Create visualization
        eighty_percent_idx, cumsum_percent = create_frequency_analysis_plot(
            frequencies,
            'data_type_frequency_analysis.pdf'
        )
        
        # Generate report
        create_analysis_report(
            frequencies,
            type_names,
            eighty_percent_idx,
            cumsum_percent,
            'data_frequency_analysis.txt'
        )
        print("Analysis completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 