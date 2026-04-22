from connect import connect


def add(name, phone):
    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL upsert_user(%s, %s)", (name, phone))
    conn.commit()

    conn.close()



def search(pattern):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))
    rows = cur.fetchall()

    for r in rows:
        print(r)

    conn.close()



def show(limit, offset):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_phonebook(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    for r in rows:
        print(r)

    conn.close()


def delete(val):
    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s)", (val,))
    conn.commit()

    conn.close()



def insert_many(names, phones):
    conn = connect()
    cur = conn.cursor()

    cur.execute("CALL insert_many(%s, %s)", (names, phones))
    conn.commit()

    conn.close()


if __name__ == "__main__":
    while True:
        print("1.Добавить / Обновить")
        print("2. Найти")
        print("3. Показать,пагинация")
        print("4. Удалить")
        print("5. Массовая вставка")
        

        choice = input("Выбор: ")

        if choice == "1":
            name = input("Имя: ")
            phone = input("Телефон: ")
            add(name, phone)

        elif choice == "2":
            pattern = input("Введите для поиска: ")
            search(pattern)

        elif choice == "3":
            limit = int(input("Сколько показать: "))
            offset = int(input("Сдвиг: "))
            show(limit, offset)

        elif choice == "4":
            val = input("Имя или телефон: ")
            delete(val)

        elif choice == "5":
            n = int(input("Сколько записей: "))
            names = []
            phones = []

            for i in range(n):
                names.append(input(f"Имя {i+1}: "))
                phones.append(input(f"Телефон {i+1}: "))

            insert_many(names, phones)

       
        