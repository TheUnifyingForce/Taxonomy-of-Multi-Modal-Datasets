import json
from collections import Counter, defaultdict
from typing import Dict, List
import numpy as np

class DatasetQualityAnalyzer:
    def __init__(self, data_path: str):
        """初始化分析器"""
        self.data = self._load_data(data_path)
        
    def _load_data(self, data_path: str) -> Dict:
        """加载数据"""
        results = {}
        with open(data_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # 跳过空行
                if not line.strip():
                    continue
                    
                try:
                    # 解析JSONL行
                    item = json.loads(line)
                    
                    # 提取message中的JSON字符串并清理
                    message = item.get('message', '')
                    if not message:
                        print(f"Line {line_num}: Empty message")
                        continue
                        
                    json_str = message.strip('```json').strip('```').strip()
                    
                    # 解析JSON内容
                    content = json.loads(json_str)
                    
                    results[item['custom_id']] = content
                    
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: JSON解析错误 - {e}")
                except Exception as e:
                    print(f"Line {line_num}: 处理错误 - {type(e).__name__}: {e}")
                    continue
                    
        if not results:
            raise ValueError("没有加载到有效数据")
            
        return results

    def analyze_modality_distribution(self) -> Dict:
        """分析模态分布"""
        modality_counts = Counter()
        for content in self.data.values():
            for modality in content['modalities']:
                modality_counts[modality['title']] += 1
                
        total = sum(modality_counts.values())
        distribution = {k: f"{(v/total)*100:.1f}%" for k, v in modality_counts.items()}
        
        return {
            'distribution': distribution,
            'total_samples': total,
            'unique_modalities': len(modality_counts)
        }

    def analyze_data_types(self) -> Dict:
        """分析数据类型统计"""
        type_stats = defaultdict(list)
        type_examples = defaultdict(set)
        
        for content in self.data.values():
            for modality in content['modalities']:
                # 统计每个模态的数据类型数量
                type_count = len(modality['data_types'])
                type_stats[modality['title']].append(type_count)
                
                # 收集数据类型示例
                for dtype in modality['data_types']:
                    type_examples[modality['title']].add(dtype['title'])

        results = {}
        for modality, counts in type_stats.items():
            results[modality] = {
                'avg_types_per_task': np.mean(counts),
                'max_types': max(counts),
                'min_types': min(counts),
                'unique_types': list(type_examples[modality])
            }
            
        return results

    def analyze_explanation_stats(self) -> Dict:
        """分析解释文本的统计特征"""
        explanation_stats = defaultdict(list)
        
        for content in self.data.values():
            for modality in content['modalities']:
                # 计算解释的词数
                word_count = len(modality['explanation'].split())
                explanation_stats[modality['title']].append(word_count)

        results = {}
        for modality, lengths in explanation_stats.items():
            results[modality] = {
                'avg_words': np.mean(lengths),
                'min_words': min(lengths),
                'max_words': max(lengths),
                'total_explanations': len(lengths)
            }
            
        return results

    def generate_report(self) -> Dict:
        """生成完整分析报告"""
        return {
            'modality_distribution': self.analyze_modality_distribution(),
            'data_types': self.analyze_data_types(),
            'explanation_stats': self.analyze_explanation_stats()
        }

def print_report(report: Dict):
    """打印格式化的报告"""
    print("\n=== 数据集质量分析报告 ===\n")
    
    # 1. 模态分布
    dist = report['modality_distribution']
    print("1. 模态分布统计:")
    print(f"总样本数: {dist['total_samples']}")
    print(f"唯一模态数: {dist['unique_modalities']}")
    print("分布情况:")
    for modality, percentage in dist['distribution'].items():
        print(f"  - {modality}: {percentage}")
    
    # 2. 数据类型统计
    print("\n2. 数据类型统计:")
    for modality, stats in report['data_types'].items():
        print(f"\n{modality}:")
        print(f"  平均类型数: {stats['avg_types_per_task']:.1f}")
        print(f"  最大/最小类型数: {stats['max_types']}/{stats['min_types']}")
        print(f"  唯一数据类型: {', '.join(stats['unique_types'])}")
    
    # 3. 解释文本统计
    print("\n3. 解释文本统计:")
    for modality, stats in report['explanation_stats'].items():
        print(f"\n{modality}:")
        print(f"  样本数: {stats['total_explanations']}")
        print(f"  平均词数: {stats['avg_words']:.1f}")
        print(f"  最短/最长词数: {stats['min_words']}/{stats['max_words']}")

def save_modality_distribution(report: Dict, output_path: str = "modality_distribution.json"):
    """保存模态分布分析结果"""
    formatted_data = {
        "distribution": report['modality_distribution']['distribution'],
        "total_samples": report['modality_distribution']['total_samples'],
        "unique_modalities": report['modality_distribution']['unique_modalities']
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"\n模态分布报告已保存至: {output_path}")

def save_data_types(report: Dict, output_path: str = "data_types.json"):
    """保存数据类型统计结果"""
    formatted_data = {
        modality: {
            'avg_types_per_task': f"{stats['avg_types_per_task']:.1f}",
            'max_types': stats['max_types'],
            'min_types': stats['min_types'],
            'unique_types': stats['unique_types']
        }
        for modality, stats in report['data_types'].items()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"数据类型统计已保存至: {output_path}")

def save_explanation_stats(report: Dict, output_path: str = "explanation_stats.json"):
    """保存解释文本统计结果"""
    formatted_data = {
        modality: {
            'avg_words': f"{stats['avg_words']:.1f}",
            'min_words': stats['min_words'],
            'max_words': stats['max_words'],
            'total_explanations': stats['total_explanations']
        }
        for modality, stats in report['explanation_stats'].items()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"解释文本统计已保存至: {output_path}")

def analyze_datatype_counts(report: Dict, output_path: str = "datatype_counts.json"):
    """统计数据类型数量"""
    # 收集所有独特的数据类型
    all_datatypes = set()
    counts_by_modality = {}
    
    # 统计每个模态的数据类型数量
    for modality, stats in report['data_types'].items():
        unique_types = set(stats['unique_types'])
        all_datatypes.update(unique_types)
        counts_by_modality[modality] = len(unique_types)
    
    # 准备输出数据
    formatted_data = {
        "total_unique_datatypes": len(all_datatypes),
        "counts_by_modality": counts_by_modality
    }
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"\n数据类型数量统计已保存至: {output_path}")
    
    # 打印统计结果
    print("\n=== 数据类型数量统计 ===")
    print(f"总计独特数据类型数: {len(all_datatypes)}")
    print("\n各模态数据类型数量:")
    for modality, count in counts_by_modality.items():
        print(f"  {modality}: {count}")

def save_unique_modalities(report: Dict, output_path: str = "unique_modalities.json"):
    """保存唯一模态列表"""
    unique_modalities = list(report['modality_distribution']['distribution'].keys())
    
    formatted_data = {
        "unique_modalities": unique_modalities,
        "count": len(unique_modalities)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"\n唯一模态列表已保存至: {output_path}")

if __name__ == "__main__":
    # 初始化分析器
    analyzer = DatasetQualityAnalyzer("result_2_messages.jsonl")
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 打印报告
    print_report(report)
    
    # 保存各维度分析结果
    save_modality_distribution(report)
    save_data_types(report)
    save_explanation_stats(report)
    
    # 统计数据类型数量
    analyze_datatype_counts(report)
    
    # 保存唯一模态列表
    save_unique_modalities(report)
