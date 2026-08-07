import sqlite3
import csv

# データベースファイルを作る(なければ新規作成、あれば接続)
conn = sqlite3.connect('cafe.db')
cur = conn.cursor()

# 表(テーブル)を作る。すでにあれば一度削除してから作り直す
cur.execute('DROP TABLE IF EXISTS cafes')
cur.execute('''
    CREATE TABLE cafes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        rating INTEGER,
        smoking TEXT,
        hours TEXT,
        morning TEXT,
        night TEXT,
        closed_day TEXT,
        photo TEXT,
        memo TEXT
    )
''')

# CSVファイルを読み込んで、1行ずつデータベースに入れる
with open('cafe_list.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        # 店名が空っぽの行(未入力の行)はスキップする
        if not row['店名']:
            continue

        cur.execute('''
            INSERT INTO cafes
            (name, address, rating, smoking, hours, morning, night, closed_day, photo, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['店名'],
            row['住所'],
            row['星評価(1-5)'],
            row['喫煙区分'],
            row['営業時間'],
            row['モーニング有無'],
            row['夜営業有無'],
            row['定休日'],
            row['写真ファイル名'],
            row['メモ'],
        ))
        count += 1

conn.commit()
conn.close()

print(f'{count}件のデータをデータベースに登録しました')