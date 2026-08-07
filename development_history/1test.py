from bottle import route, run

@route('/')
def home():
    return "<h1>喫茶店マップサイト準備中</h1>"

run(host='localhost', port=8080, debug=True)