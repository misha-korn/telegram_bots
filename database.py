import sqlite3

conn = sqlite3.connect('inline_menu_bot_db.sqlite3')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                id INT PRIMARY KEY,
                                name TEXT);''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS payments(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INT,
                                sum INT,
                                FOREIGN KEY(user_id) REFERENCES users(id));''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS abonements(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INT,
                                pay_id INT,
                                FOREIGN KEY(user_id) REFERENCES users(id),
                                FOREIGN KEY(pay_id) REFERENCES payments(id));''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS  lessons(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                date_lessons DATE);''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS lessons_info(
                                ab_id INT,
                                les_id INT,
                                PRIMARY KEY (ab_id, les_id),
                                FOREIGN KEY(ab_id) REFERENCES abonement(id),
                                FOREIGN KEY(les_id) REFERENCES lessons(id))''')
conn.commit()

# cursor.execute(f'INSERT INTO users VALUES(12421, "Misha")')
# cursor.execute(f'INSERT INTO users VALUES(123, "Vova")')
# cursor.execute(f'INSERT INTO payments VALUES(Null, 12421, 3000)')
# cursor.execute(f'INSERT INTO payments VALUES(Null, 12421, 6000)')
# cursor.execute(f'INSERT INTO payments VALUES(Null, 123, 6000)')
# cursor.execute(f'INSERT INTO abonements VALUES(Null, 12421, 1)')
# cursor.execute(f'INSERT INTO abonements VALUES(Null, 12421, 2)')
# cursor.execute(f'INSERT INTO abonements VALUES(Null, 123, 3)')
# cursor.execute(f'INSERT INTO lessons VALUES(Null, "2024-04-03")')
# cursor.execute(f'INSERT INTO lessons VALUES(Null, "2024-04-20")')
# conn.commit()


# cursor.execute(f'INSERT INTO users VALUES(120, "Egor")')
# conn.commit()
# print(cursor.execute('SELECT * FROM payments WHERE sum = 6000 AND user_id = 12421').fetchall())



print(cursor.execute(f'''SELECT abonements.id
                        FROM users JOIN payments 
                        ON users.id=payments.user_id 
                        JOIN abonements 
                        ON users.id=abonements.user_id AND payments.id=abonements.pay_id
                        WHERE payments.sum = 6000''').fetchall())

'''SELECT users.id FROM users 
JOIN payments добавляем таблицу payments к users 
ON users.id=payments.user_id как объединяем записи
WHERE payments.sum = 6000'''
