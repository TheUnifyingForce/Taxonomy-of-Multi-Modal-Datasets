import json

def load_result1(file_path):
    """加载result1数据，以数据集名称为键创建字典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 记录处理过的数据集名称，用于检查重复
            processed_names = set()
            result_dict = {}
            
            for item in data:
                name = item['name'].strip()
                if name in processed_names:
                    print(f"Warning: Duplicate dataset name found in result1: {name}")
                processed_names.add(name)
                result_dict[name] = item['tags']
                
            return result_dict
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file - {file_path}")
        return {}
    except Exception as e:
        print(f"Error loading result1: {e}")
        return {}

def load_result2(file_path):
    """加载result2数据，以数据集名称为键创建字典"""
    result2_data = {}
    error_count = 0
    processed_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    dataset_name = data['input']['dataset_name'].strip()
                    
                    if dataset_name in result2_data:
                        print(f"Warning: Duplicate dataset name in result2: {dataset_name}")
                    
                    result2_data[dataset_name] = {
                        'custom_id': data['custom_id'],
                        'description': data['input']['dataset_description'],
                        'output': data['output']
                    }
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error processing line {line_num} in result2: {e}")
                    continue
                    
        print(f"Result2 processing summary:")
        print(f"Successfully processed: {processed_count} entries")
        print(f"Errors encountered: {error_count} entries")
        
        return result2_data
        
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return {}

def combine_results(result1_path, result2_path, output_path):
    # 加载两个数据源
    print("Loading result1...")
    result1_data = load_result1(result1_path)
    print(f"Loaded {len(result1_data)} entries from result1")
    
    print("\nLoading result2...")
    result2_data = load_result2(result2_path)
    print(f"Loaded {len(result2_data)} entries from result2")
    
    # 匹配和合并数据
    print("\nCombining results...")
    combined_data = []
    matched_count = 0
    unmatched_datasets = []
    
    # 遍历result1中的每个数据集
    for dataset_name in result1_data:
        combined_entry = {
            "dataset_info": {
                "name": dataset_name,
                "description": result2_data.get(dataset_name, {}).get('description', '')
            },
            "result_1_output": result1_data[dataset_name],
            "result_2_output": result2_data.get(dataset_name, {}).get('output', None)
        }
        
        if dataset_name in result2_data:
            matched_count += 1
        else:
            unmatched_datasets.append(dataset_name)
        
        combined_data.append(combined_entry)
    
    # 检查result2中是否有未在result1中出现的数据集
    extra_datasets = set(result2_data.keys()) - set(result1_data.keys())
    if extra_datasets:
        print(f"\nFound {len(extra_datasets)} datasets in result2 that are not in result1:")
        for name in sorted(extra_datasets):
            print(f"- {name}")
    
    # 按数据集名称排序
    combined_data.sort(key=lambda x: x['dataset_info']['name'])
    
    # 写入结果
    print("\nWriting combined results...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully wrote combined results to {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")
    
    # 打印详细的统计信息
    print(f"\nDetailed Statistics:")
    print(f"Total datasets in result1: {len(result1_data)}")
    print(f"Total datasets in result2: {len(result2_data)}")
    print(f"Successfully matched datasets: {matched_count}")
    print(f"Unmatched datasets: {len(unmatched_datasets)}")
    
    if unmatched_datasets:
        print("\nUnmatched datasets from result1:")
        for i, name in enumerate(sorted(unmatched_datasets), 1):
            print(f"{i}. {name}")

if __name__ == "__main__":
    combine_results(
        'results_1.json',           # result1文件路径
        'combined_results_2.jsonl', # result2文件路径
        'final_combined_results.json'  # 输出文件路径
    ) 