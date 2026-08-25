from bottle import route, run, request
import sqlite3

@route('/')
def home():
    # URLについている検索条件を受け取る(まだ何も選ばれていなければ空)
    raw_list = request.query.getall('smoking')
    smoking_list = [s.encode('latin-1').decode('utf-8') for s in raw_list]
    morning = request.query.morning
    night = request.query.night

    # 検索条件を組み立てる
    conditions = []
    params = []

    if smoking_list:
        placeholders = ', '.join(['?'] * len(smoking_list))
        conditions.append(f"smoking IN ({placeholders})")
        params.extend(smoking_list)
        
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
    cur.execute(sql, params)
    cafes = cur.fetchall()
    conn.close()

    # 検索フォームのHTML
    html = f"""
        <h1>喫茶店マップサイト準備中</h1>
        <form method="get">
            <label><input type="checkbox" name="smoking" value="禁煙" {"checked" if "禁煙" in smoking_list else ""}> 禁煙</label>
            <label><input type="checkbox" name="smoking" value="分煙" {"checked" if "分煙" in smoking_list else ""}> 分煙</label>
            <label><input type="checkbox" name="smoking" value="全席喫煙可" {"checked" if "全席喫煙可" in smoking_list else ""}> 全席喫煙可</label>
            <br>
            <label><input type="checkbox" name="morning" value="yes" {"checked" if morning == "yes" else ""}> モーニングあり</label>
            <label><input type="checkbox" name="night" value="yes" {"checked" if night == "yes" else ""}> 夜営業あり(18時以降)</label>
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
