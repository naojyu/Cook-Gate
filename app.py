import sqlite3
from flask import Flask, render_template, request, redirect, session

# 宣言：appという名前でFlaskアプリを作るよ！
app = Flask(__name__)

# session
app.secret_key = "cookgate20200618"

# ===ここからコードを書いていくよ！===
@app.route("/")
def helloworld():
    return "Hello World."


@app.route("/index")
def index():
    return render_template("index.html")



# GETメソッドの場合
@app.route("/test1")
def test1():
    favs = request.args.getlist("fav")
    print("favs:", favs) # ['1','2','3']
    return "ok"

# POSTメソッドの場合
@app.route("/test2", methods=['POST'])
def test2():
    favs = request.form.getlist("fav")
    print("favs:", favs) # ['1','2','3']
    return "ok"



# 404ページを作る
# https://liginc.co.jp/426034
@app.errorhandler(404)
def page_not_found(error):
    # return "お探しのページがココにあると…どうしてそんなことを思いついてしまったのかね……？"
    return render_template("error.html")


# ###################################
if __name__ == "__main__":
    # Flaskの開発用サーバを実行します。
    app.run(debug=True)
