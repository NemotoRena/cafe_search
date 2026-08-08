from bottle import route, run, request
import sqlite3

@route('/')
def home():
    # URLについている検索条件を受け取る(まだ何も選ばれていなければ空)
    smoking = request.query.smoking
    morning = request.query.morning
    night = request.query.night

    # 検索条件を組み立てる
    conditions = []
    params = []

    if smoking == 'nonsmoking_only':
        conditions.append("smoking = ?")
        params.append('禁煙')
        
    elif smoking == 'nonsmoking_and_separated':
        conditions.append("smoking IN (?, ?)")
        params.append('禁煙')
        params.append('分煙')
        
    elif smoking == 'smoking':
        conditions.append("smoking = ?")
        params.append('全席喫煙可')
        
    if morning == 'yes':
        conditions.append("morning = ?")
        params.append('あり')
        
    if night == 'yes':
        conditions.append("night = ?")
        params.append('あり')

    sql = "SELECT name, address, rating FROM cafes"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute(sql)
    cafes = cur.fetchall()
    conn.close()

    # 検索フォームのHTML
    html = """
    <h1>喫茶店検索サイト準備中</h1>
    <form method="get">
        <label><input type="checkbox" name="smoking" value="nonsmoking"> 禁煙・分煙のみ</label>
        <label><input type="checkbox" name="smoking" value="smoking"> 全席喫煙可のみ</label>
        <br>
        <label><input type="checkbox" name="morning" value="yes"> モーニングあり</label>
        <label><input type="checkbox" name="night" value="yes"> 夜営業あり(18時以降)</label>
        <br>
        <button type="submit">検索</button>
    </form>
    <ul>
    """
    for name, address, rating in cafes:
        html += f"<li>{name}(星{rating}) - {address}</li>"
    html += "</ul>"
    return html

run(host='localhost', port=8080, debug=True)
