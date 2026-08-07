from bottle import route, run
import sqlite3

@route('/')
def home():
    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute('SELECT name, address, rating FROM cafes')
    cafes = cur.fetchall()
    conn.close()

    html = "<h1>喫茶店検索サイト準備中</h1><ul>"
    for name, address, rating in cafes:
        html += f"<li>{name}(星{rating}) - {address}</li>"
    html += "</ul>"
    return html

run(host='localhost', port=8080, debug=True)
