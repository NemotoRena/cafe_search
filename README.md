# cafe search
喫茶店情報を検索・管理できるWebアプリケーション  

https://github.com/user-attachments/assets/18cdfef8-72db-4560-b8de-3408117f3afb

## 使用技術
・Python  
・Bottle (Webフレームワーク)  
・Flask (Webフレームワーク)  
・SQLite  
・HTML/CSS/JavaScript  

## 開発環境
・エディタ:Visual Studio Code  
・OS:Ubuntu  
・Python のバージョン:3.12  
・リモート接続:VS Code Remote - SSH  

## 主な機能
・条件検索  
　- 喫煙区分（禁煙のみ・禁煙+分煙・全席喫煙可）  
　- モーニング有無  
　- 夜営業有無  
・店舗ごとの詳細ページ(写真・星評価・営業時間・定休日・メモなど)  
・店舗情報の編集・削除機能  
・検索条件を選択した状態のまま結果ページに反映(JavaScriptでラジオボタンの選択解除も実装)

## データベース設計
Excelで店舗情報を管理し、CSV形式（cafe_list.csv）として保存しています。  
create_db.pyを実行すると、CSVを読み込んでSQLiteデータベース（cafe.db）を作成します。  

| カラム名 | 内容 |
|----------|------|
| id | 店舗ID（自動採番） |
| name | 店名 |
| address | 住所 |
| rating | 星評価（1〜5） |
| smoking | 喫煙区分（禁煙・分煙・全席喫煙可） |
| hours | 営業時間 |
| morning | モーニング有無 |
| night | 夜営業有無 |
| closed_day | 定休日 |
| photo | 写真ファイル名 |
| memo | メモ |　　

## 実行方法

1.必要なライブラリをインストールする  
```bash
#Bottleの場合
pip install bottle  

#Flaskの場合
pip install flask
```

2.データベースを作成、CSVデータを登録   
```bash
#windowsの場合  
python create_db.py

#Linuxの場合  
python3 create_db.py  
```

3.サーバーを起動する  
```bash
# Bottle版  
python bottle/app.py  

# Flask版  
python flask/app_flask.py  

※ Windowsでは「python」、Linux/macOSでは「python3」を使用。  
```

起動後、ブラウザで http://localhost:8080 を開く、  
もしくはVScodeの場合右下の「ブラウザを開く」を押下するとサイトが表示されます。
