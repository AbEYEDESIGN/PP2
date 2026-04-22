
import psycopg2 
import csv
from psycopg2 import OperationalError
DB_CONFIG={
    "host":"localhost",
    "database":"phonebook_db",
    "user":"postgres",
    "password":"1234"}
def get_connection():
    try:
        connection=psycopg2.connect(**DB_CONFIG)
        return connection
    except OperationalError as e:
        print(f"the error '{e}' occurred")
        return None
def creating_table():
    command=(
        """ 
        CREATE TABLE IF NOT EXISTS contacts(
        phone_number VARCHAR(20) PRIMARY KEY,
        name VARCHAR(50) NOT NULL)
    """,
    )
    try:
        with get_connection() as connection:
            with connection.cursor() as cur:
                for i in command:
                    cur.execute(i)
            print("table created successfully")
    except Exception as e:
            print(f"the error '{e}' occurred")
def add_contact():
    name=input("enter name:")
    phone=input("enter phone number:")
    try:
        with get_connection() as connection:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO contacts (name,phone_number) VALUES(%s,%s)",(name,phone))
        print("contact added successfully")
    except Exception as e:
        print(f"the error '{e}' occurred")
def insert_csv(file_path):
    try:
        with get_connection() as connection:
            with connection.cursor() as cur:
                with open(file_path,'r',encoding='utf-8') as f:
                    reader=csv.DictReader(f)
                    for row in reader:
                        cur.execute("INSERT INTO contacts (name,phone_number) VALUES(%s,%s)",(row['name'],row['phone_number']))
        print("csv file inserted successfully")
    except Exception as e:
        print(f"the error in inserting csv '{e}' occurred")
def show_contacts():
    try:
        with get_connection() as connection:
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM contacts")
                rows=cur.fetchall()
                for row in rows:
                    print(f"name: {row[0]}, phone_number:{row[1]}")
    except Exception as e:
        print(f"the error in showing conacts '{e}' occured")
def change_contact():
    changed_name=input("enter the name of contact that you want to change ")
    new_phone=input("enter the new phone number:")
    try:
        with get_connection() as connection:
            with connection.cursor() as cur:
                cur.execute("UPDATE contacts set phone_number=%s where name=%s",(new_phone,changed_name))
        print("contact changed successfully")
    except Exception as e:
        print(f"the error in changing contact '{e}' occurred")
def delete_contact():
    name=input("name of contact that you want to delete:")
    try:
        with get_connection() as connections:
            with connections.cursor() as cur:
                cur.execute("DELETE FROM contacts where name=%s",(name,))
        print("contact deleted successfully")
    except Exception as e:
        print(f"the error in deleting contact '{e}' occurred")
print("HELLO WELCOME TO THE PHONEBOOK APP")
print("we get connection and create table")
creating_table()
while True:
    print("what do you want to do?")
    print("1. add contact manually")
    print("2. insert contacts from csv file")
    print("3. exit")
    print("4. show all contacts")
    print("5. change contact")
    print("6. delete contact")
    choice=input("enter your choice:")
    if choice=="1":
        add_contact()
    elif choice=="4":
        show_contacts()
    elif choice=="5":
        change_contact()
    elif choice=="6":
        delete_contact()
    elif choice=="3":
        print("good bye!")
        break
    elif choice=="2":
        file_path=input("enter the path of csv file:")
        insert_csv(file_path)
    else:
        print("invalid choice, please try again")