import json
import evaluate
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import spacy

class NERTester:
    def __init__(self, model_path: str):
        """
        Инициализация тестера с загрузкой модели
        
        Args:
            model_path: путь к обученной spaCy модели
        """
        self.model = spacy.load(model_path)
        self.seqeval = evaluate.load("seqeval")
        
    def load_dataset(self, file_path: str, format_type: str = "auto") -> List[Dict[str, Any]]:
        """
        Загрузка датасета из различных форматов
        
        Args:
            file_path: путь к файлу с данными
            format_type: auto, jsonl, json, csv, parquet
            
        Returns:
            Список словарей с ключами 'text' и 'entities'
        """
        file_path = Path(file_path)
        
        if format_type == "auto":
            # Автоопределение формата по расширению
            if file_path.suffix == '.jsonl':
                format_type = 'jsonl'
            elif file_path.suffix == '.json':
                format_type = 'json'
            elif file_path.suffix == '.csv':
                format_type = 'csv'
            elif file_path.suffix == '.parquet':
                format_type = 'parquet'
            else:
                raise ValueError(f"Неизвестный формат файла: {file_path.suffix}")
        
        data = []
        
        if format_type == 'jsonl':
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
                        
        elif format_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
        elif format_type == 'csv':
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                item = {'text': row['text']}
                if 'entities' in row and pd.notna(row['entities']):
                    if isinstance(row['entities'], str):
                        item['entities'] = eval(row['entities'])
                    else:
                        item['entities'] = row['entities']
                data.append(item)
                
        elif format_type == 'parquet':
            df = pd.read_parquet(file_path)
            for _, row in df.iterrows():
                item = {'text': row['text']}
                if 'entities' in row and pd.notna(row['entities']):
                    if isinstance(row['entities'], str):
                        item['entities'] = eval(row['entities'])
                    else:
                        item['entities'] = row['entities']
                data.append(item)
        
        # Валидация данных
        validated_data = []
        for item in data:
            if 'text' in item and 'entities' in item:
                validated_data.append({
                    'text': item['text'],
                    'entities': item['entities']
                })
        
        print(f"Загружено {len(validated_data)} примеров")
        return validated_data
    
    def calculate_iou(self, span1: Tuple[int, int], span2: Tuple[int, int]) -> float:
        """
        Вычисление Intersection over Union для двух интервалов
        
        Args:
            span1: (start, end)
            span2: (start, end)
            
        Returns:
            IoU значение от 0 до 1
        """
        start1, end1 = span1
        start2, end2 = span2
        
        # Находим пересечение
        intersection_start = max(start1, start2)
        intersection_end = min(end1, end2)
        intersection = max(0, intersection_end - intersection_start)
        
        # Находим объединение
        union = (end1 - start1) + (end2 - start2) - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def evaluate_entities(self, true_entities: List[Tuple[int, int, str]], 
                        pred_entities: List[Tuple[int, int, str]], 
                        text: str) -> Dict[str, Any]:
        """
        Оценка сущностей по всем стратегиям для одного примера
        
        Args:
            true_entities: истинные сущности [(start, end, label)]
            pred_entities: предсказанные сущности [(start, end, label)]
            text: исходный текст для валидации spans
            
        Returns:
            Словарь с результатами по всем стратегиям
        """
        # Валидация spans
        valid_true_entities = []
        for start, end, label in true_entities:
            if 0 <= start <= end <= len(text):
                valid_true_entities.append((start, end, label))
        
        valid_pred_entities = []
        for start, end, label in pred_entities:
            if 0 <= start <= end <= len(text):
                valid_pred_entities.append((start, end, label))
        
        # Подсчет TN - общая длина текста минус все сущности
        total_chars = len(text)
        total_entity_chars = sum(end - start for start, end, label in valid_true_entities)
        tn_chars = total_chars - total_entity_chars
        
        results = {
            'exact': {'tp': 0, 'tn': tn_chars, 'fp': 0, 'fn': 0},
            'partial': {'tp': 0, 'tn': tn_chars, 'fp': 0, 'fn': 0},
            'type_only': {'tp': 0, 'tn': tn_chars, 'fp': 0, 'fn': 0},
            'bounds_only': {'tp': 0, 'tn': tn_chars, 'fp': 0, 'fn': 0},
            'partial_iou': {'tp': 0, 'tn': tn_chars, 'fp': 0, 'fn': 0}
        }
        
        # Матрицы для отслеживания сопоставлений
        true_matched = {i: False for i in range(len(valid_true_entities))}
        pred_matched = {i: False for i in range(len(valid_pred_entities))}
        
        # Сопоставление сущностей
        for i, (t_start, t_end, t_label) in enumerate(valid_true_entities):
            for j, (p_start, p_end, p_label) in enumerate(valid_pred_entities):
                # Точное совпадение
                if t_start == p_start and t_end == p_end and t_label == p_label:
                    results['exact']['tp'] += 1
                    true_matched[i] = True
                    pred_matched[j] = True
                
                # Частичное совпадение (любое пересечение + совпадение типа)
                intersection = max(0, min(t_end, p_end) - max(t_start, p_start))
                if intersection > 0 and t_label == p_label:
                    results['partial']['tp'] += 1
                
                # Совпадение по типу
                if t_label == p_label:
                    results['type_only']['tp'] += 1
                
                # Совпадение по границам
                if t_start == p_start and t_end == p_end:
                    results['bounds_only']['tp'] += 1
                
                # Частичное совпадение по IoU > 0.5
                iou = self.calculate_iou((t_start, t_end), (p_start, p_end))
                if iou > 0.5 and t_label == p_label:
                    results['partial_iou']['tp'] += 1
        
        # Подсчет FP и FN для каждой стратегии
        results['exact']['fn'] = sum(not matched for matched in true_matched.values())
        results['exact']['fp'] = sum(not matched for matched in pred_matched.values())
        
        # Для других стратегий FP/FN считаются по-разному
        # (упрощенная логика - в реальной реализации нужно уточнить)
        
        return results
    
    def calculate_metrics(self, tp: int, fp: int, fn: int) -> Dict[str, float]:  
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0  # без tn
    
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'accuracy': accuracy,
            'tp': tp,
            'fp': fp,
            'fn': fn
    }
    
    def evaluate(self, test_data_path: str, output_json_path: str = None, 
                format_type: str = "auto") -> Dict[str, Any]:
        """
        Полная оценка модели
        
        Args:
            test_data_path: путь к тестовым данным
            output_json_path: путь для сохранения результатов
            format_type: формат данных
            
        Returns:
            Полные результаты оценки
        """
        # Загрузка данных
        test_data = self.load_dataset(test_data_path, format_type)
        
        # Инициализация счетчиков
        strategy_results = {
            'exact': {'tp': 0,'tn':0,  'fp': 0, 'fn': 0},
            'partial': {'tp': 0,'tn':0, 'fp': 0, 'fn': 0},
            'type_only': {'tp': 0,'tn':0, 'fp': 0, 'fn': 0},
            'bounds_only': {'tp': 0,'tn':0, 'fp': 0, 'fn': 0},
            'partial_iou': {'tp': 0,'tn':0, 'fp': 0, 'fn': 0}
        }
        
        confusion_data = []
        
        print("Начинаем оценку модели...")
        
        for i, item in enumerate(test_data):
            if i % 100 == 0:
                print(f"Обработано {i}/{len(test_data)} примеров")
            
            text = item['text']
            true_entities = item['entities']
            
            # Получаем предсказания модели
            doc = self.model(text)
            pred_entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
            
            # Оценка для текущего примера
            example_results = self.evaluate_entities(true_entities, pred_entities, text)
            
            # Агрегируем результаты по стратегиям
            for strategy in strategy_results:
                for metric in ['tp', 'tn', 'fp', 'fn']:
                    strategy_results[strategy][metric] += example_results[strategy][metric]
            
            # Собираем данные для confusion matrix
            for t_start, t_end, t_label in true_entities:
                for p_start, p_end, p_label in pred_entities:
                    if t_start == p_start and t_end == p_end:
                        confusion_data.append((t_label, p_label))
                        
        total_tn_chars = 0
        total_text_chars = 0
    
        for i, item in enumerate(test_data):
            text = item['text']
            true_entities = item['entities']
        
        # Подсчет TN для этого текста
            total_text_chars += len(text)
            total_entity_chars = sum(end - start for start, end, label in true_entities)
            total_tn_chars += len(text) - total_entity_chars
        
        # Расчет финальных метрик
        final_results = {}
        
        for strategy, counts in strategy_results.items():
            final_results[strategy] = self.calculate_metrics(
                counts['tp'], counts['fp'], counts['fn']
            )
        
        # Генерация confusion matrix
        confusion_matrix = self._create_confusion_matrix(confusion_data)
        
        # Сборка полных результатов
        full_results = {
            'overall_metrics': final_results,
            'tn_stats': {
                    'total_tn_chars': total_tn_chars,
                    'total_text_chars': total_text_chars,
                    'tn_ratio': total_tn_chars / total_text_chars if total_text_chars > 0 else 0.0},
            'confusion_matrix': confusion_matrix,
            'test_info': {
                'dataset_size': len(test_data),
                'model_path': str(self.model.path if hasattr(self.model, 'path') else 'unknown'),
                'evaluation_date': pd.Timestamp.now().isoformat()}
        }
        
        # Сохранение результатов
        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(full_results, f, indent=2, ensure_ascii=False)
            print(f"Результаты сохранены в: {output_json_path}")
        
        # Вывод в консоль
        self._print_report(full_results)
        
        return full_results
    
    def _create_confusion_matrix(self, confusion_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Создание confusion matrix данных"""
        if not confusion_data:
            return {}
            
        true_labels, pred_labels = zip(*confusion_data)
        
        # Все уникальные метки
        all_labels = sorted(set(true_labels) | set(pred_labels))
        
        # Создание матрицы
        matrix = np.zeros((len(all_labels), len(all_labels)), dtype=int)
        label_to_idx = {label: idx for idx, label in enumerate(all_labels)}
        
        for true_label, pred_label in confusion_data:
            true_idx = label_to_idx[true_label]
            pred_idx = label_to_idx[pred_label]
            matrix[true_idx][pred_idx] += 1
        
        return {
            'matrix': matrix.tolist(),
            'labels': all_labels,
            'label_to_idx': label_to_idx
        }
    
    def _print_report(self, results: Dict[str, Any]):
        """Красивый вывод отчета в консоль"""
        print("\n" + "="*80)
        print("ОТЧЕТ ПО ОЦЕНКЕ NER МОДЕЛИ")
        print("="*80)
        
        overall = results['overall_metrics']
        
        for strategy, metrics in overall.items():
            print(f"\n--- {strategy.upper()} ---")
            print(f"Precision:  {metrics['precision']:.4f}")
            print(f"Recall:     {metrics['recall']:.4f}")
            print(f"F1-Score:   {metrics['f1']:.4f}")
            print(f"Accuracy: {metrics['accuracy']:.4f}")
            print(f"TP/FP/FN: {metrics['tp']}/{metrics['fp']}/{metrics['fn']}")            
            print(f"TN: {results['tn_stats']['total_tn_chars']}")
            print("\n📊 ПОЯСНЕНИЕ МЕТРИК:")
            print("TP - Правильно найденные сущности\nFP - Ложные срабатывания (найдено лишнее)\nFN - Пропущенные сущности\nTN - Символы без сущностей (не используется в расчетах)")

            if strategy.upper() == "EXACT":
                print("EXACT - строгая оценка, точное совпадение границ и типов")
            if strategy.upper() == "PARTIAL":
                print("PARTIAL - учитывает небольшие ошибки в границах")
            if strategy.upper() == "TYPE_ONLY":
                print("TYPE_ONLY - оценивает только классификацию типов")
            if strategy.upper() == "BOUNDS_ONLY":
                print(
                    "BOUNDS_ONLY - оценивает только детекцию границ")
            if strategy.upper() == "PARTIAL_IOU":
                print("Intersection-over-Union - Пересечение сущностей > 50% + совпадение типа (Пересечение) / (Объединение)")
        # Визуализация confusion matrix
        self._plot_confusion_matrix(results['confusion_matrix'])
    
    def _plot_confusion_matrix(self, confusion_data: Dict[str, Any]):
        """Визуализация confusion matrix"""
        if not confusion_data or not confusion_data.get('matrix'):
            print("\nНедостаточно данных для confusion matrix")
            return
            
        matrix = np.array(confusion_data['matrix'])
        labels = confusion_data['labels']
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()


# Пример использования
if __name__ == "__main__":
    # Инициализация тестера
    tester = NERTester("../the-coolest/models/best_model")
    
    # Запуск оценки
    results = tester.evaluate(
        test_data_path="../the-coolest/data/val_data.json",
        output_json_path="evaluation_results.json",
        format_type="json"
    )
    
#(config_path="../the-coolest/models/best_model/config.cfg",