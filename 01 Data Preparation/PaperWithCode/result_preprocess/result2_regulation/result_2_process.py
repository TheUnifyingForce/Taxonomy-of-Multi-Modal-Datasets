import json
import re

def process_files(input_file, output_file, result_file):
    # 存储输入和输出的字典
    input_data = {}
    output_data = {}
    
    # 读取输出文件（result_2.jsonl）
    print("Processing output file...")
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                custom_id = data['custom_id']
                # 直接获取content内容，不进行JSON解析
                content = data['response']['body']['choices'][0]['message']['content']
                output_data[custom_id] = content
            except Exception as e:
                print(f"Error processing output line for {custom_id}: {e}")
                continue
    
    print(f"Processed {len(output_data)} output records")
    
    # 读取输入文件
    print("\nProcessing input file...")
    error_count = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                custom_id = data['custom_id']
                messages = data['body']['messages']
                for msg in messages:
                    if msg['role'] == 'user':
                        content = msg['content']
                        # 使用正则表达式提取数据集名称和描述，即使描述为空也进行提取
                        name_match = re.search(r"'dataset_name': '([^']*)'", content)
                        desc_match = re.search(r"'dataset description': '([^']*)'", content)
                        
                        dataset_info = {
                            'dataset_name': name_match.group(1).strip() if name_match else '',
                            'dataset_description': desc_match.group(1).strip() if desc_match else ''
                        }
                        input_data[custom_id] = dataset_info
                        break  # 找到user消息后就退出循环
            except Exception as e:
                error_count += 1
                print(f"Error processing input line {error_count}: {e}")
                continue
    
    print(f"Processed {len(input_data)} input records")
    print(f"Total input processing errors: {error_count}")
    
    # 按custom_id排序并写入结果文件
    print("\nWriting combined results...")
    written_count = 0
    with open(result_file, 'w', encoding='utf-8') as f:
        for custom_id in sorted(input_data.keys(), key=lambda x: int(x.split('-')[1])):
            if custom_id in output_data:
                result = {
                    'custom_id': custom_id,
                    'input': input_data[custom_id],
                    'output': output_data[custom_id]
                }
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                written_count += 1
    
    print(f"\nTotal matched records written: {written_count}")
    print(f"Missing input records: {10680 - len(input_data)}")
    print(f"Missing output records: {10680 - len(output_data)}")

if __name__ == "__main__":
    process_files(
        'paperwithcode_prompt_v1.jsonl',  # 输入文件
        'result_2.jsonl',        # 输出文件
        'combined_results_2.jsonl' # 结果文件
    )

