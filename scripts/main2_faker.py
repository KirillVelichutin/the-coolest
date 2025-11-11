import json
import os
from data_generators import replace_and_label

def load_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_dataset(data, output_path, output_format):
    output_format = output_format.lower()
    
    if output_format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    elif output_format in ['jsonl', 'jl']:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

def process_with_faker(data):
    processed_data = []
    for item in data:
        result = replace_and_label(item['message'])
        processed_data.append(result)
    return processed_data

def count_tags(data):
    tags = []
    for item in data:
        for entity in item['entities']:
            tags.append(entity[2])
    
    tag_data = {}
    for tag in set(tags):
        tag_data[tag] = tags.count(tag)
    
    return tag_data

def main():
    print("Faker Data Generator")
    print("=" * 30)
    
    convert_needed = input("\nТребуется ли преобразовать формат датасета? (yes/no): ").strip().lower()
    
    if convert_needed == 'yes':
        input_file = input("Путь к исходному файлу: ").strip()
        output_format = input("Желаемый формат (json/jsonl): ").strip().lower()
        
        data = load_dataset(input_file)
        base_name = os.path.splitext(input_file)[0]
        output_path = f"{base_name}_converted.{output_format}"
        
        print(f"\nКонвертируем {input_file} в {output_format}...")
        save_dataset(data, output_path, output_format)
        print(f"Успешно сохранено в: {output_path}")
        
        dataset_file = output_path
    else:
        dataset_file = input("Путь к файлу с шаблонами: ").strip()
    
    print(f"\nГенерируем размеченные данные из {dataset_file}...")
    template_data = load_dataset(dataset_file)
    processed_data = process_with_faker(template_data)
    
    output_file = input("Имя файла для сохранения размеченных данных: ").strip()
    output_format = input("Формат сохранения (json/jsonl): ").strip().lower()
    
    print(f"\nСохраняем размеченные данные в {output_file}...")
    save_dataset(processed_data, output_file, output_format)
    
    print("\nСтатистика по сущностям:")
    stats = count_tags(processed_data)
    for tag, count in stats.items():
        print(f"{tag}: {count}")
    
    print(f"\nГотово! Файл сохранен: {output_file}")

if __name__ == '__main__':
    main()