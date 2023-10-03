import os
import json

# Путь к папке libraries
library_path = 'libraries'
output_file_path = 'merged_datas.json'
# Создать пустой словарь для объединенных данных
merged_data = {
    "TimeManager": {
        "event_templates": {}
    }
}

# Проход по всем файлам в папке
for filename in os.listdir(library_path):
    if filename.endswith(".json"):
        file_path = os.path.join(library_path, filename)

        # Открыть JSON-файл и загрузить данные
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверить, соответствует ли структура данным в файле
        if "TimeManager" in data and "event_templates" in data["TimeManager"]:
            event_templates = data["TimeManager"]["event_templates"]

            # Объединить данные из текущего файла в общий словарь
            for event_name, event_data in event_templates.items():
                merged_data["TimeManager"]["event_templates"][event_name] = event_data

# Теперь merged_data содержит объединенные данные из всех JSON-файлов
# Можете использовать merged_data как ваши данные
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(merged_data, output_file, ensure_ascii=False, indent=4)

print(f'Данные сохранены в {output_file_path}')