from bottle import route, run, request, static_file
import sqlite3

@route('/photo/<filename>')
def serve_photo(filename):
    return static_file(filename, root='photo')

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

    sql = "SELECT name, address, rating, photo FROM cafes"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute(sql)
    cafes = cur.fetchall()
    conn.close()

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
        <h1>喫茶店検索サイト準備中</h1>
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
    </script>
    <ul>
    """
    for name, address, rating, photo in cafes:
        star_display = "★" * rating + "☆" * (5 - rating)
        if photo:
            html += f'<li><img src="/photo/{photo}" style="width:80px; height:80px; object-fit:cover; vertical-align:middle;"> {name}({star_display}) - {address}</li>'
        else:
            html += f"<li>{name}({star_display}) - {address}</li>"
    return html

run(host='localhost', port=8080, debug=True)
