import csv

# Создаём тестовые данные
data = [
    {"name": "Иван Петров", "phone_number": "+7 (495) 123-45-67"},
    {"name": "Мария Смирнова", "phone_number": "8-912-345-67-89"},
    {"name": "Петр Сидоров", "phone_number": "+375 29 111-22-33"},
    # добавьте сколько хотите строк
]

# Записываем в CSV
with open('contacts.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'phone_number'])
    writer.writeheader()
    writer.writerows(data)

print("Файл contacts.csv успешно создан!")