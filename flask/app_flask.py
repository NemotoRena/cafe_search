from flask import Flask, request, send_from_directory, redirect
import sqlite3
import html
import os

#XSS対策としてHTMLの特殊文字を無害化する関数を設定
def safe(v):
    return html.escape(v) if v else ""

app = Flask(__name__)

PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'photo')

#写真ファイルの表示
@app.route('/photo/<filename>')
def serve_photo(filename):
    return send_from_directory(PHOTO_DIR, filename)

#詳細ページの表示
@app.route('/cafe/<cafe_id>')
def cafe_detail(cafe_id):
    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    #SQLインジェクション対策のためプレースホルダ（?）を使用
    cur.execute("SELECT name, address, rating, smoking, hours, morning, night, closed_day, photo, memo FROM cafes WHERE id = ?", (cafe_id,))
    cafe = cur.fetchone()
    conn.close()

    if not cafe:
        return "お店が見つかりませんでした"

    name, address, rating, smoking, hours, morning, night, closed_day, photo, memo = cafe
    name = safe(name)
    address = safe(address)
    smoking = safe(smoking)
    hours = safe(hours)
    morning = safe(morning)
    night = safe(night)
    closed_day = safe(closed_day)
    memo = safe(memo)
    star_display = "★" * rating + "☆" * (5 - rating)
    photo_html = f'<img src="/photo/{safe(photo)}" style="width:400px; height:400px; object-fit:cover; border-radius:8px;">' if photo else ""

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
    <a href="/cafe/{cafe_id}/edit"><button style="background-color:#6B4A2E; color:white; border:none; padding:8px 16px; border-radius:4px; margin-top:16px; cursor:pointer;">この店を編集する</button></a>
    <form method="post" action="/cafe/{cafe_id}/remove" onsubmit="return confirm('本当に削除しますか?')">
    <button type="submit" style="background-color:#A32D2D; color:white; border:none; padding:8px 16px; border-radius:4px; margin-top:16px; cursor:pointer;">この店を削除する</button>
</form>
    """
    
#削除処理の実行
@app.route('/cafe/<cafe_id>/remove', methods=['POST'])
def remove_cafe(cafe_id):
    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM cafes WHERE id = ?", (cafe_id,))
    conn.commit()
    conn.close()
    return redirect('/')

#更新画面の表示
@app.route('/cafe/<cafe_id>/edit')
def edit_cafe_form(cafe_id):
    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute("SELECT name, address, rating, smoking, hours, morning, night, closed_day, photo, memo FROM cafes WHERE id = ?", (cafe_id,))
    cafe = cur.fetchone()
    conn.close()

    if not cafe:
        return "お店が見つかりませんでした"

    name, address, rating, smoking, hours, morning, night, closed_day, photo, memo = cafe
    name = safe(name)
    address = safe(address)
    hours = safe(hours)
    closed_day = safe(closed_day)
    photo = safe(photo)
    memo = safe(memo)
    rating = safe(str(rating))

    return f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta charset="UTF-8">
    <title>編集</title>
    </head>
    <body>
    <h1>{name} を編集</h1>
    <form method="post" action="/cafe/{cafe_id}/update">
        <p>店名<br><input type="text" name="name" value="{name}" style="width:300px;"></p>
        <p>住所<br><input type="text" name="address" value="{address}" style="width:300px;"></p>
        <p>星評価<br><input type="number" name="rating" value="{rating}" min="1" max="5"></p>
        <p>喫煙区分<br>
        <select name="smoking">
            <option value="禁煙" {"selected" if smoking == "禁煙" else ""}>禁煙</option>
            <option value="分煙" {"selected" if smoking == "分煙" else ""}>分煙</option>
            <option value="全席喫煙可" {"selected" if smoking == "全席喫煙可" else ""}>全席喫煙可</option>
        </select>
        </p>
        <p>営業時間<br><input type="text" name="hours" value="{hours}" style="width:300px;"></p>
        <p>モーニング<br>
        <select name="morning">
            <option value="あり" {"selected" if morning == "あり" else ""}>あり</option>
            <option value="なし" {"selected" if morning == "なし" else ""}>なし</option>
        </select>
        </p>
        <p>夜営業<br>
        <select name="night">
            <option value="あり" {"selected" if night == "あり" else ""}>あり</option>
            <option value="なし" {"selected" if night == "なし" else ""}>なし</option>
        </select>
        </p>
        <p>定休日<br><input type="text" name="closed_day" value="{closed_day}" style="width:300px;"></p>
        <p>写真ファイル名<br><input type="text" name="photo" value="{photo}" style="width:300px;"></p>
        <p>メモ<br><textarea name="memo" style="width:300px;">{memo}</textarea></p>
        <button type="submit">保存する</button>
    </form>
    <a href="/cafe/{cafe_id}">キャンセルして戻る</a>
    </body>
    </html>
    """

#更新処理の実行
@app.route('/cafe/<cafe_id>/update', methods=['POST'])
def update_cafe(cafe_id):
    name = request.form.get('name')
    address = request.form.get('address')
    rating = request.form.get('rating')
    smoking = request.form.get('smoking')
    hours = request.form.get('hours')
    morning = request.form.get('morning')
    night = request.form.get('night')
    closed_day = request.form.get('closed_day')
    photo = request.form.get('photo')
    memo = request.form.get('memo')

    conn = sqlite3.connect('cafe.db')
    cur = conn.cursor()
    cur.execute('''
        UPDATE cafes
        SET name = ?, address = ?, rating = ?, smoking = ?, hours = ?, morning = ?, night = ?, closed_day = ?, photo = ?, memo = ?
        WHERE id = ?
    ''', (name, address, rating, smoking, hours, morning, night, closed_day, photo, memo, cafe_id))
    conn.commit()
    conn.close()

    return redirect(f'/cafe/{cafe_id}')

#トップページの表示
@app.route('/')
def home():
    #URLについている検索条件を受け取る(何も選ばれていなければ空)
    #smokingは複数選択可能なため、getlist()でリストとして受け取る
    smoking_list = request.args.getlist('smoking')
    morning = request.args.get('morning')
    night = request.args.get('night')

    #ユーザーが選んだ検索条件を入れるリスト
    conditions = []
    #検索条件に対応する値を入れるリスト
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

    sql = "SELECT id, name, address, rating, photo FROM cafes"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    conn = sqlite3.connect('cafe.db') #① データベースファイルに接続する
    cur = conn.cursor() #② 操作するための道具(カーソル)を用意する
    cur.execute(sql, params) #③ 用意しておいたSQL文を実行する
    cafes = cur.fetchall() #④ 実行結果(該当する店のデータ)を全部受け取る
    conn.close() #⑤ データベースとの接続を切る

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

    for id, name, address, rating, photo in cafes:
        name = safe(name)
        address = safe(address)
        photo = safe(photo)
        star_display = "★" * rating + "☆" * (5 - rating)
        if photo:
            html += f'<li><a href="/cafe/{id}" style="text-decoration:none; color:inherit; display:flex; align-items:center;"><img src="/photo/{photo}" style="width:80px; height:80px; object-fit:cover; vertical-align:middle;"> {name}({star_display}) - {address}</a></li>'
        else:
            html += f'<li><a href="/cafe/{id}" style="text-decoration:none; color:inherit;">{name}({star_display}) - {address}</a></li>'

    return html

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=False)
