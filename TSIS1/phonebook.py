import json
import csv
import os
from connect import connect


# --- функции из practice 8 (вызывают процедуры/функции бд) ---

def upsert_contact(name, phone):
    # upsert = update если есть, insert если нет — процедура из practice 8
    conn = connect()
    cur = conn.cursor()
    cur.execute("call upsert_user(%s, %s)", (name, phone))
    conn.commit()
    conn.close()
    print(f"контакт '{name}' сохранён")


def delete_contact(val):
    # удаляет по имени ИЛИ по телефону — процедура из practice 8
    conn = connect()
    cur = conn.cursor()
    cur.execute("call delete_user(%s)", (val,))
    conn.commit()
    conn.close()
    print(f"контакт '{val}' удалён")


def search_p8(pattern):
    # поиск по имени или телефону — функция из practice 8
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from search_phonebook(%s)", (pattern,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("ничего не найдено")
    for r in rows:
        print(f"  имя: {r[0]}, телефон: {r[1]}")


def show_page(limit, offset):
    # пагинация — функция get_phonebook из practice 8
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from get_phonebook(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    conn.close()
    for r in rows:
        print(f"  {r}")


def insert_many():
    # массовая вставка — процедура insert_many из practice 8
    n = int(input("сколько контактов: "))
    names, phones = [], []
    for i in range(n):
        names.append(input(f"  имя {i+1}: "))
        phones.append(input(f"  телефон {i+1}: "))
    conn = connect()
    cur = conn.cursor()
    cur.execute("call insert_many(%s, %s)", (names, phones))
    conn.commit()
    conn.close()
    print(f"добавлено {n} контактов")


def add_phone(contact_name, phone, phone_type):
    # вызываем процедуру add_phone из бд
    conn = connect()
    cur = conn.cursor()
    cur.execute("call add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
    conn.commit()
    conn.close()
    print(f"телефон {phone} ({phone_type}) добавлен к '{contact_name}'")


def move_to_group(contact_name, group_name):
    # процедура сама создаст группу если её нет
    conn = connect()
    cur = conn.cursor()
    cur.execute("call move_to_group(%s, %s)", (contact_name, group_name))
    conn.commit()
    conn.close()
    print(f"'{contact_name}' перемещён в группу '{group_name}'")


def search_contacts(query):
    # функция ищет по имени, email и всем телефонам
    conn = connect()
    cur = conn.cursor()
    cur.execute("select * from search_contacts(%s)", (query,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("ничего не найдено")
        return

    print(f"\n{'id':<5} {'имя':<20} {'email':<25} {'birthday':<12} {'группа'}")
    print("-" * 70)
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<20} {str(r[2] or '—'):<25} {str(r[3] or '—'):<12} {r[4] or '—'}")


def filter_by_group(group_name):
    # join с таблицей groups чтобы найти контакты по названию группы
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select pb.id, pb.name, pb.email, pb.birthday
        from phonebook pb
        join groups g on pb.group_id = g.id
        where g.name ilike %s
        order by pb.name
    """, (group_name,))
    rows = cur.fetchall()
    conn.close()

    print(f"\nконтакты в группе '{group_name}':")
    for r in rows:
        print(f"  [{r[0]}] {r[1]}, email: {r[2]}, birthday: {r[3]}")


def search_by_email(query):
    # ilike + %% = поиск без учёта регистра, % с двух сторон = частичное совпадение
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select id, name, email from phonebook
        where email ilike %s order by name
    """, (f"%{query}%",))
    rows = cur.fetchall()
    conn.close()

    print(f"\nрезультаты поиска по email '{query}':")
    for r in rows:
        print(f"  [{r[0]}] {r[1]}, {r[2]}")


def show_sorted(sort_by="name"):
    # не передаём sort_by напрямую в sql — берём из словаря, чтобы избежать sql-инъекций
    allowed = {"name": "pb.name", "birthday": "pb.birthday", "date": "pb.id"}
    col = allowed.get(sort_by, "pb.name")

    conn = connect()
    cur = conn.cursor()
    cur.execute(f"""
        select pb.id, pb.name, pb.email, pb.birthday, g.name
        from phonebook pb
        left join groups g on pb.group_id = g.id
        order by {col}
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"\n{'id':<5} {'имя':<20} {'email':<25} {'birthday':<12} {'группа'}")
    print("-" * 70)
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<20} {str(r[2] or '—'):<25} {str(r[3] or '—'):<12} {r[4] or '—'}")


def paginated_browse():
    # листаем контакты страницами, используем get_phonebook из practice 8
    page_size = 5
    offset = 0

    while True:
        conn = connect()
        cur = conn.cursor()
        cur.execute("select * from get_phonebook(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
        conn.close()

        if not rows and offset == 0:
            print("база пуста")
            return

        print(f"\n--- страница (offset={offset}) ---")
        for r in rows:
            print(f"  {r}")

        if len(rows) < page_size:
            print("[конец списка]")
            cmd = input("prev / quit: ").strip().lower()
        else:
            cmd = input("next / prev / quit: ").strip().lower()

        if cmd == "next" and len(rows) == page_size:
            offset += page_size
        elif cmd == "prev" and offset > 0:
            offset -= page_size
        elif cmd == "quit":
            break


def export_to_json(filename="contacts_export.json"):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select pb.id, pb.name, pb.email, pb.birthday::text, g.name
        from phonebook pb
        left join groups g on pb.group_id = g.id
    """)
    contacts = cur.fetchall()

    result = []
    for c in contacts:
        cur.execute("select phone, type from phones where contact_id = %s", (c[0],))
        phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]
        result.append({
            "name": c[1], "email": c[2], "birthday": c[3],
            "group": c[4], "phones": phones
        })

    conn.close()

    # ensure_ascii=False — чтобы кириллица не превращалась в \u0410
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"экспортировано {len(result)} контактов в '{filename}'")


def import_from_json(filename="contacts_export.json"):
    if not os.path.exists(filename):
        print(f"файл '{filename}' не найден")
        return

    with open(filename, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    conn = connect()
    cur = conn.cursor()

    for c in contacts:
        name = c.get("name")
        cur.execute("select id from phonebook where name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            # дубликат — спрашиваем пользователя
            choice = input(f"'{name}' уже есть. перезаписать? (y/n): ").strip().lower()
            if choice != "y":
                print(f"  пропускаем '{name}'")
                continue
            cur.execute("update phonebook set email=%s, birthday=%s where name=%s",
                        (c.get("email"), c.get("birthday"), name))
            cur.execute("delete from phones where contact_id = %s", (existing[0],))
            contact_id = existing[0]
        else:
            # ищем или создаём группу
            group_id = None
            if c.get("group"):
                cur.execute("select id from groups where name = %s", (c["group"],))
                g = cur.fetchone()
                if g:
                    group_id = g[0]
                else:
                    cur.execute("insert into groups (name) values (%s) returning id", (c["group"],))
                    group_id = cur.fetchone()[0]

            cur.execute("""
                insert into phonebook (name, email, birthday, group_id)
                values (%s, %s, %s, %s) returning id
            """, (name, c.get("email"), c.get("birthday"), group_id))
            contact_id = cur.fetchone()[0]

        for ph in c.get("phones", []):
            cur.execute("insert into phones (contact_id, phone, type) values (%s, %s, %s)",
                        (contact_id, ph["phone"], ph["type"]))
        print(f"  импортирован: {name}")

    conn.commit()
    conn.close()
    print("импорт завершён")


def import_from_csv(filename):
    # csv должен содержать колонки: name, phone, phone_type, email, birthday, group
    conn = connect()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name       = row.get("name", "").strip()
            phone      = row.get("phone", "").strip()
            phone_type = row.get("phone_type", "mobile").strip()
            email      = row.get("email", "").strip() or None
            birthday   = row.get("birthday", "").strip() or None
            group_name = row.get("group", "").strip() or None

            group_id = None
            if group_name:
                cur.execute("select id from groups where name = %s", (group_name,))
                g = cur.fetchone()
                if g:
                    group_id = g[0]
                else:
                    cur.execute("insert into groups (name) values (%s) returning id", (group_name,))
                    group_id = cur.fetchone()[0]

            # используем upsert из practice 8
            cur.execute("call upsert_user(%s, %s)", (name, phone))
            cur.execute("update phonebook set email=%s, birthday=%s, group_id=%s where name=%s",
                        (email, birthday, group_id, name))

            cur.execute("select id from phonebook where name=%s", (name,))
            pb = cur.fetchone()
            if pb and phone:
                cur.execute("""
                    insert into phones (contact_id, phone, type) values (%s, %s, %s)
                    on conflict do nothing
                """, (pb[0], phone, phone_type))

    conn.commit()
    conn.close()
    print("csv импорт завершён")


def main():
    while True:
        print("\n========== phonebook tsis 1 ==========")
        print("--- из practice 8 ---")
        print("1.  добавить / обновить контакт (upsert)")
        print("2.  удалить контакт (по имени или телефону)")
        print("3.  поиск по имени или телефону")
        print("4.  показать страницу (пагинация)")
        print("5.  массовая вставка")
        print("--- новое в tsis 1 ---")
        print("6.  добавить телефон к контакту")
        print("7.  переместить контакт в группу")
        print("8.  поиск по имени / email / всем телефонам")
        print("9.  фильтр по группе")
        print("10. поиск по email")
        print("11. показать всё с сортировкой")
        print("12. листать страницами (навигация)")
        print("13. экспорт в json")
        print("14. импорт из json")
        print("15. импорт из csv")
        print("0.  выход")
        print("---------------------------------------")

        choice = input("выбор: ").strip()

        if choice == "1":
            upsert_contact(input("имя: "), input("телефон: "))
        elif choice == "2":
            delete_contact(input("имя или телефон: "))
        elif choice == "3":
            search_p8(input("запрос: "))
        elif choice == "4":
            limit  = int(input("сколько показать: "))
            offset = int(input("сдвиг (0 = с начала): "))
            show_page(limit, offset)
        elif choice == "5":
            insert_many()
        elif choice == "6":
            add_phone(input("имя контакта: "), input("номер: "), input("тип (home/work/mobile): "))
        elif choice == "7":
            move_to_group(input("имя контакта: "), input("группа: "))
        elif choice == "8":
            search_contacts(input("запрос: "))
        elif choice == "9":
            filter_by_group(input("группа (Family/Work/Friend/Other): "))
        elif choice == "10":
            search_by_email(input("часть email: "))
        elif choice == "11":
            show_sorted(input("сортировка (name/birthday/date): ").strip().lower())
        elif choice == "12":
            paginated_browse()
        elif choice == "13":
            export_to_json(input("имя файла (enter = contacts_export.json): ").strip() or "contacts_export.json")
        elif choice == "14":
            import_from_json(input("имя файла (enter = contacts_export.json): ").strip() or "contacts_export.json")
        elif choice == "15":
            import_from_csv(input("путь к csv: ").strip())
        elif choice == "0":
            print("выход")
            break
        else:
            print("неверный выбор")


if __name__ == "__main__":
    main()
