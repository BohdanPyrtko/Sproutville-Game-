import csv
import json

def load_csv(filename):
    """Завантаження CSV у вигляді списку словників"""
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено.")
        return []

def load_json(filename):
    """Завантаження JSON"""
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено.")
        return {}

def sort_list(items, key):
    """Сортування списку словників за полем key"""
    try:
        return sorted(items, key=lambda x: x.get(key))
    except Exception as e:
        print(f"Помилка при сортуванні: {e}")
        return items

def search_list(items, name):
    """Пошук елементу за назвою (регістр не враховується)"""
    name = name.lower()
    for item in items:
        if item.get('name', '').lower() == name:
            return item
    return None
