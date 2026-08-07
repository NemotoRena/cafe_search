from bottle import route, run, request, static_file
import sqlite3

@route('/photo/<filename>')
def serve_photo(filename):
    return static_file(filename, root='photo')

@route('/cafe/<cafe_id>')
def cafe_detail(cafe_id):
    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute("SELECT name, address, rating, smoking, hours, morning, night, closed_day, photo, memo FROM cafes WHERE id = ?", (cafe_id,))
    cafe = cur.fetchone()
    conn.close()

    if not cafe:
        return "お店が見つかりませんでした"

    name, address, rating, smoking, hours, morning, night, closed_day, photo, memo = cafe
    star_display = "★" * rating + "☆" * (5 - rating)
    photo_html = f'<img src="/photo/{photo}" style="width:100%; max-width:400px; border-radius:8px;">' if photo else ""

    return f"""
    <style>
        body {{ font-family: sans-serif; background-color: #FAF6F0; color: #4A3B2C; max-width: 800px; margin: 0 auto; padding: 20px; }}
        a {{ color: #6B4A2E; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        h1 {{ color: #6B4A2E; border-bottom: 3px solid #C9A876; padding-bottom: 8px; margin-top: 16px; }}
        .info-box {{ background-color: #FFFFFF; padding: 20px; border-radius: 8px; margin-top: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .info-box p {{ margin: 10px 0; }}
        .label {{ color: #8A7460; font-weight: bold; display: inline-block; width: 100px; }}
    </style>
    <a href="/">一覧に戻る</a>
    <h1>{name}</h1>
    {photo_html}
    <div class="info-box">
        <p><span class="label">評価</span>{star_display}</p>
        <p><span class="label">住所</span>{address}</p>
        <p><span class="label">喫煙区分</span>{smoking}</p>
        <p><span class="label">営業時間</span>{hours}</p>
        <p><span class="label">モーニング</span>{morning}</p>
        <p><span class="label">夜営業</span>{night}</p>
        <p><span class="label">定休日</span>{closed_day}</p>
        <p><span class="label">メモ</span>{memo}</p>
    </div>
    """

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
        conditions.append("smoking = '禁煙'")
    elif smoking == 'nonsmoking_and_separated':
        conditions.append("smoking IN ('禁煙', '分煙')")
    elif smoking == 'smoking':
        conditions.append("smoking = '全席喫煙可'")

    if morning == 'yes':
        conditions.append("morning = 'あり'")

    if night == 'yes':
        conditions.append("night = 'あり'")

    sql = "SELECT id, name, address, rating, photo FROM cafes"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect('cafe.db') # ① データベースファイルに接続する
    cur = conn.cursor() # ② 操作するための「道具(カーソル)」を用意する
    cur.execute(sql) # ③ 用意しておいたSQL文を実行する
    cafes = cur.fetchall() # ④ 実行結果(該当する店のデータ)を全部受け取る
    conn.close() # ⑤ 用が済んだので、データベースとの接続を切る

    # JavaScriptにピンの情報を渡すための準備
    """import json
    pins = [
        {"name": name, "address": address, "rating": rating, "lat": lat, "lng": lng}
        for name, address, rating in cafes
        if lat is not None and lng is not None
    ]
    pins_json = json.dumps(pins, ensure_ascii=False)
    """

    

    # 検索フォームのHTML
    html = f"""
    <style>
    body {{ font-family: sans-serif; background-color: #FAF6F0; color: #4A3B2C; max-width: 800px; margin: 0 auto; padding: 20px; }}
    h1 {{ color: #6B4A2E; border-bottom: 3px solid #C9A876; padding-bottom: 8px; }}
    form {{ background-color: #FFFFFF; padding: 16px; border-radius: 8px; margin-bottom: 20px; }}
    label {{ margin-right: 12px; }}
    button {{ background-color: #6B4A2E; color: #FFFFFF; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; margin-top: 8px; }}
    button:hover {{ background-color: #4A3B2C; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ background-color: #FFFFFF; margin-bottom: 12px; padding: 12px; border-radius: 8px; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    li img {{ border-radius: 6px; margin-right: 12px; }}
    </style>

    <h1>喫茶店検索サイト</h1>

    <!--
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    -->
    <form method="get">
        <label><input type="radio" name="smoking" value="nonsmoking_only" onclick="toggleRadio(this)" {"checked" if smoking == "nonsmoking_only" else ""}> 禁煙のみ</label>
        <label><input type="radio" name="smoking" value="nonsmoking_and_separated" onclick="toggleRadio(this)" {"checked" if smoking == "nonsmoking_and_separated" else ""}> 禁煙+分煙(禁煙席あり)</label>
        <label><input type="radio" name="smoking" value="smoking" onclick="toggleRadio(this)" {"checked" if smoking == "smoking" else ""}> 全席喫煙可</label>
        <br>
        <label><input type="checkbox" name="morning" value="yes" {"checked" if morning == "yes" else ""}> モーニングあり</label>
        <label><input type="checkbox" name="night" value="yes" {"checked" if night == "yes" else ""}> 夜営業あり(18時以降)</label>
        <br>
        <button type="submit">検索</button>
    </form>
    <!--<div id="map" style="height: 400px; width: 100%;"></div>-->
    <!-- 検索ボタンをクリックで解除するためJavaScriptを使用 -->
    <script>
    function toggleRadio(radio) {{
        if (radio.dataset.wasChecked === "true") {{
            radio.checked = false;
            radio.dataset.wasChecked = "false";
        }} else {{
            document.querySelectorAll('input[name="' + radio.name + '"]').forEach(r => r.dataset.wasChecked = "false");
            radio.dataset.wasChecked = "true";
        }}
    }}
    /*var map = L.map('map').setView([35.681236, 139.767125], 12);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);
    var pins = [];
    pins.forEach(function(p) {{
        L.marker([p.lat, p.lng]).addTo(map)
            .bindPopup(p.name + "(星" + p.rating + ")<br>" + p.address);
    }}); */

    </script>
    <ul>
    """

    for id, name, address, rating, photo in cafes:
        star_display = "★" * rating + "☆" * (5 - rating)
        if photo:
            html += f'<li><a href="/cafe/{id}" style="text-decoration:none; color:inherit; display:flex; align-items:center;"><img src="/photo/{photo}" style="width:80px; height:80px; object-fit:cover; vertical-align:middle;"> {name}({star_display}) - {address}</a></li>'
        else:
            html += f'<li><a href="/cafe/{id}" style="text-decoration:none; color:inherit;">{name}({star_display}) - {address}</a></li>'
    
    return html

run(host='localhost', port=8080, debug=True)
