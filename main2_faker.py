import json
import pandas as pd
from pathlib import Path
import sys
import random
import traceback
from data_generators import replace_and_label, TAGS, DATAGEN
from faker import Faker

fake = Faker(locale='ru_RU')

def load_dataset(file_path: str) -> list:
    """
    Загружает датасет из разных форматов в единый формат [{'message': 'текст'}, ...]
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    ext = file_path.suffix.lower()
    
    try:
        if ext == '.csv':
            return _load_from_csv(file_path)
        elif ext == '.json':
            return _load_from_json(file_path)
        elif ext in ['.jsonl', '.jl']:
            return _load_from_jsonl(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {ext}. Поддерживаемые форматы: .csv, .json, .jsonl")
            
    except Exception as e:
        raise ValueError(f"Ошибка при загрузке файла {file_path}: {str(e)}")

def _load_from_csv(file_path: Path) -> list:
    """Загружает данные из CSV файла"""
    # Пробуем разные кодировки для поддержки русского языка
    encodings = ['utf-8', 'cp1251', 'utf-8-sig']
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            if not df.empty:
                break
        except UnicodeDecodeError:
            continue
    else:
        df = pd.read_csv(file_path)
    
    # Ищем колонку с сообщениями
    message_col = None
    for col in ['message', 'text', 'content', 'sentence', 'utterance']:
        if col in df.columns:
            message_col = col
            break
    
    if message_col is None:
        message_col = df.columns[0]
    
    # Обрабатываем сообщения
    result = []
    for text in df[message_col].dropna():
        if isinstance(text, str) and text.strip():
            result.append({"message": text.strip()})
    
    return result

def _load_from_json(file_path: Path) -> list:
    """Загружает данные из JSON файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return _process_json_list(data)
    elif isinstance(data, dict):
        if 'data' in data and isinstance(data['data'], list):
            return _process_json_list(data['data'])
        elif 'items' in data and isinstance(data['items'], list):
            return _process_json_list(data['items'])
        elif 'messages' in data and isinstance(data['messages'], list):
            return _process_json_list(data['messages'])
        else:
            for key, value in data.items():
                if isinstance(value, list):
                    return _process_json_list(value)
    
    raise ValueError("Неподдерживаемая структура JSON файла")

def _load_from_jsonl(file_path: Path) -> list:
    """Загружает данные из JSONL файла"""
    result = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                item = json.loads(line)
                if isinstance(item, dict) and 'message' in item:
                    text = item['message']
                    if isinstance(text, str) and text.strip():
                        result.append({"message": text.strip()})
                else:
                    for key in ['text', 'content', 'sentence', 'utterance', 'message']:
                        if key in item and isinstance(item[key], str) and item[key].strip():
                            result.append({"message": item[key].strip()})
                            break
            
            except json.JSONDecodeError:
                continue
    
    return result

def _process_json_list(data_list: list) -> list:
    """Обрабатывает список из JSON данных"""
    result = []
    
    for item in data_list:
        if not isinstance(item, dict):
            continue
        
        message_value = None
        
        # Сначала проверяем стандартные имена полей
        for field in ['message', 'text', 'content', 'sentence', 'utterance']:
            if field in item and isinstance(item[field], str) and item[field].strip():
                message_value = item[field].strip()
                break
        
        # Если не нашли, берем первое строковое поле
        if message_value is None:
            for key, value in item.items():
                if isinstance(value, str) and value.strip():
                    message_value = value.strip()
                    break
        
        if message_value:
            result.append({"message": message_value})
    
    return result

def save_dataset(data: list, output_path: str, output_format: str) -> None:
    """
    Сохраняет датасет в указанном формате
    """
    output_path = Path(output_path)
    output_format = output_format.lower()
    
    # Проверяем, содержит ли датасет разметку (entities)
    has_entities = any('entities' in item for item in data)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    elif output_format == 'csv':
        if has_entities:
            print("⚠️  Внимание: CSV формат не поддерживает вложенные структуры. Сущности будут сохранены как строки.")
            # Создаем DataFrame с колонками text и entities
            df = pd.DataFrame([
                {
                    'text': item['text'],
                    'entities': json.dumps(item['entities'], ensure_ascii=False)
                } for item in data
            ])
        else:
            df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    elif output_format in ['jsonl', 'jl']:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    else:
        raise ValueError(f"Неподдерживаемый формат сохранения: {output_format}. Поддерживаемые форматы: json, csv, jsonl")

def display_preview(data: list, title: str, num_items: int = 3) -> None:
    """Отображает превью датасета"""
    print(f"\n{title}:")
    print("-" * 50)
    
    # Определяем тип данных
    is_labeled = any('entities' in item for item in data)
    
    if is_labeled:
        # Показываем размеченные данные
        for i, item in enumerate(data[:num_items], 1):
            print(f"{i}. Текст: {item['text']}")
            print("   Сущности:")
            for entity in item.get('entities', []):
                entity_text = item['text'][entity[0]:entity[1]]
                print(f"     - {entity[2]}: '{entity_text}' [{entity[0]}:{entity[1]}]")
    else:
        # Показываем неразмеченные данные
        for i, item in enumerate(data[:num_items], 1):
            print(f"{i}. {item['message']}")
    
    if len(data) > num_items:
        print(f"... и еще {len(data) - num_items} записей")
    print("-" * 50)

def process_dataset_with_faker(input_data):
    """
    Обрабатывает весь датасет с помощью фейкера
    
    Args:
        input_data (list): Список словарей в формате [{'message': 'текст с тегами'}, ...]
    
    Returns:
        list: Список словарей в формате spaCy [{'text': '...', 'entities': [...]}, ...]
    """
    processed_data = []
    total_entities = 0
    
    print("\n🔄 Генерация реальных данных с помощью фейкера...")
    print("-" * 60)
    
    for i, item in enumerate(input_data, 1):
        if i % 100 == 0:
            print(f"Обработано {i} сообщений...")
        
        try:
            # Применяем фейкер к каждому сообщению
            result = replace_and_label(item['message'])
            processed_data.append(result)
            total_entities += len(result['entities'])
        except Exception as e:
            print(f"⚠️  Ошибка при обработке сообщения {i}: {str(e)}")
            print(f"   Текст: {item['message']}")
    
    print(f"✅ Обработка завершена! Всего обработано {len(input_data)} сообщений")
    print(f"📊 Сгенерировано {total_entities} сущностей")
    
    return processed_data

def count_tags_in_dataset(data):
    """
    Считает количество сущностей каждого типа в датасете
    
    Args:
        data (list): Датасет в формате [{'text': '...', 'entities': [...]}, ...]
    
    Returns:
        dict: Словарь с количеством каждой сущности
    """
    tag_counts = {}
    
    for item in data:
        for entity in item['entities']:
            tag = entity[2]  # entity[2] - это тип сущности
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return tag_counts

def main():
    """Основная функция для интерактивной работы с датасетом"""
    print("🚀 Конвертер датасетов и генератор размеченных данных")
    print("=" * 70)
    
    # Выбор режима работы
    print("\n🔧 Выберите режим работы:")
    print("   1. Обычный режим: конвертация форматов (csv/json/jsonl)")
    print("   2. Режим с фейкером: генерация размеченных данных для NER")
    
    while True:
        mode = input("\n🔢 Введите номер режима (1/2): ").strip()
        if mode in ['1', '2']:
            break
        print("❌ Неверный выбор. Пожалуйста, введите 1 или 2.")
    
    # Запрашиваем путь к файлу
    input_file = input("📁 Введите путь к исходному файлу (csv/json/jsonl): ").strip()
    
    if mode == '1':
        # Обычный режим конвертации
        print("\n💾 Поддерживаемые форматы для сохранения:")
        print("   - json  : Структурированный JSON")
        print("   - csv   : Табличный формат CSV")
        print("   - jsonl : JSON Lines (по одной записи на строку)")
        
        while True:
            output_format = input("\n🔤 Введите формат для сохранения (json/csv/jsonl): ").strip().lower()
            if output_format in ['json', 'csv', 'jsonl']:
                break
            print("❌ Неверный формат. Пожалуйста, выберите из: json, csv, jsonl")
    
    else:
        # Режим с фейкером
        print("\n💡 В режиме фейкера поддерживаются форматы с поддержкой разметки:")
        print("   - json  : Структурированный JSON (рекомендуется для spaCy)")
        print("   - jsonl : JSON Lines")
        
        while True:
            output_format = input("\n🔤 Введите формат для сохранения (json/jsonl): ").strip().lower()
            if output_format in ['json', 'jsonl']:
                break
            print("❌ Неверный формат. Пожалуйста, выберите из: json, jsonl")
    
    try:
        # Загружаем датасет
        print(f"\n⏳ Загружаем датасет из {input_file}...")
        data = load_dataset(input_file)
        print(f"✅ Успешно загружено {len(data)} сообщений")
        
        # В режиме фейкера обрабатываем данные
        if mode == '2':
            print("\n✨ Переключаемся в режим генерации размеченных данных...")
            data = process_dataset_with_faker(data)
            
            # Показываем статистику по тегам
            tag_stats = count_tags_in_dataset(data)
            print(f"\n📊 Статистика по сгенерированным сущностям:")
            print("-" * 40)
            for tag, count in sorted(tag_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"{tag}: {count}")
        
        # Показываем превью данных
        preview_title = "📊 Исходные данные" if mode == '1' else "✅ Сгенерированные размеченные данные"
        display_preview(data, preview_title)
        
        # Формируем имя выходного файла
        input_path = Path(input_file)
        output_filename = f"{input_path.stem}_{'labeled' if mode == '2' else 'converted'}.{output_format}"
        
        # Сохраняем датасет
        print(f"\n💾 Сохраняем датасет в формате {output_format}...")
        save_dataset(data, output_filename, output_format)
        
        # Загружаем сохраненный файл для проверки
        print(f"\n🔍 Проверяем сохраненный файл...")
        if output_format == 'json':
            with open(output_filename, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
        elif output_format == 'csv':
            saved_df = pd.read_csv(output_filename)
            if 'text' in saved_df.columns and 'entities' in saved_df.columns:
                # Это размеченные данные в CSV
                saved_data = []
                for _, row in saved_df.iterrows():
                    try:
                        entities = json.loads(row['entities'])
                        saved_data.append({'text': row['text'], 'entities': entities})
                    except:
                        saved_data.append({'text': row['text'], 'entities': []})
            else:
                # Это обычные данные в CSV
                message_col = saved_df.columns[0]
                saved_data = [{"message": str(row[message_col]).strip()} 
                            for _, row in saved_df.iterrows() if pd.notna(row[message_col])]
        elif output_format in ['jsonl', 'jl']:
            saved_data = []
            with open(output_filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        saved_data.append(json.loads(line))
        
        # Показываем результат
        result_title = "✅ Результат после преобразования" if mode == '1' else "✅ Результат разметки"
        display_preview(saved_data, result_title)
        
        # Выводим информацию о файле
        file_size = Path(output_filename).stat().st_size / 1024  # в KB
        print(f"\n📋 Информация о сохраненном файле:")
        print(f"   📄 Имя файла: {output_filename}")
        print(f"   📍 Расположение: {Path(output_filename).resolve()}")
        print(f"   💾 Размер: {file_size:.1f} KB")
        print(f"   📊 Количество записей: {len(saved_data)}")
        
        if mode == '2':
            total_entities = sum(len(item.get('entities', [])) for item in saved_data)
            print(f"   🏷  Количество сущностей: {total_entities}")
        
        print(f"\n🎉 Готово! Файл успешно сохранен и {'готов для использования' if mode == '1' else 'готов для обучения NER модели'}!")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()