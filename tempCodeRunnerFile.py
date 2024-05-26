for i in range(8):
    name = f"gleb{i}"

    cursor.execute(f'INSERT INTO users VALUES({87654321+i}, "{name}", {0})')
conn.commit()