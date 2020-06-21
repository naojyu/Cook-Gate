# DB
import sqlite3
# フレームワークはflask
from flask import Flask, render_template, request, redirect, session
# 日時取ります
# from datetime import datetime

# appにflaskを定義する
app = Flask(__name__)

# セッション
# セッション名は後で変えるう！！！！！
app.secret_key = "cook-gate"


# /以下に何も入力されていない場合、トップ画面へ自動遷移する
@app.route("/")
def go_index():
    # どこに送るか未定。とりあえずテキスト表示させておく。
    return render_template("cookgate.html")

# トップ画面
@app.route("/cookgate")
def cg_top():
    return render_template("cookgate.html")



# 会員登録
# 会員登録画面を表示する
@app.route("/regist", methods=["GET"])
def regist_get():
    return render_template("regist.html")

# 会員登録画面で、「登録」ボタンを押した時の処理
@app.route("/regist", methods=["POST"])
def regist_post():
    # ユーザー情報を取得
    name = request.form.get("name")
    password = request.form.get("password")
    email = request.form.get("email")

    # 確認print
    print("-------------------------------")
    print(name)
    print(password)
    print(email)

    # 一つでも空の値がある場合、エラーを返すようにしたい。
    # 名前は2文字以上にしたい
    # パスワードは4文字以上にしたい
    # メールアドレスは「@」の有無チェックを入れたい
    # メールアドレスが既に登録済みの場合、ログイン画面へ誘導したい

    # DB接続
    conn = sqlite3.connect("service_cg.db")
    c = conn.cursor()
    c.execute("insert into user values(null,?,?,?)", (name,password,email,))
    conn.commit()
    c.close()

    return redirect("/login")



# ログイン
# ログイン画面を表示する
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

# 会員登録画面で、「登録」ボタンを押した時の処理
@app.route("/login", methods=["POST"])
def login_post():
    # ログイン情報を取得
    name = request.form.get("name")
    password = request.form.get("password")
    email = request.form.get("email")

    # 確認print
    print("-------------------------------")
    print(name)
    print(password)
    print(email)

    # 一つでも空の値がある場合、エラーを返すようにしたい。
    # 名前は2文字以上にしたい
    # パスワードは4文字以上にしたい
    # メールアドレスは「@」の有無チェックを入れたい

    # DB接続
    conn = sqlite3.connect("service_cg.db")
    c = conn.cursor()
    # ユーザ名、PW、メールアドレスの全てが一致するidを検索
    c.execute("select id from user where name=? and password=? and email=?", (name,password,email,))
    user_id = c.fetchone()

    # 確認print
    print("-----------------------------")
    print(user_id)
    c.close()

    if user_id is None:
        return render_template("login.html")
    else:
        # セッションを作る
        session["user_id"] = user_id
        return redirect("/index")



# ログイントップ画面
# index.htmlに会員情報を表示させています。
# →もしbase.htmlに会員情報を表示させる場合、ルーティングと表示先を変えます。
@app.route("/index")
def dbtest():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # DB接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # ユーザー情報を取得し表示
        c.execute("select id,name,password,email from user where id = ?", (user_id,))
        user_info = c.fetchone()
        print("-------------------------")
        print(user_info)
        
        # コース完了状況の取得
        c.execute("select SUM(pork_01) from course_pork where user_id =?", (user_id,))
        user_status = c.fetchone()[0]
        print("-------------------------")
        print(user_status)

        if user_status is None:
            user_status = 0
        elif user_status >= 1:
            user_status = 1
        else:
            user_status = 0

        print("-------------------------")
        print(user_status)

        user_rate = round((user_status / 1) * 100)
        print("-------------------------")
        print(user_rate)
        
        c.close()

        return render_template("index.html", user_info=user_info, user_status=user_status, user_rate=user_rate)
    else:
        return redirect("/login")


# コース選択情報を取る
# 「pork」コースのリンクをクリックした時、
@app.route("/clk-pork", methods=["POST"])
def pork_post():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # default:0
        btn = 0
        print(btn)

        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # DBに開始情報があるか確認する、を追加予定。
        # 既に開始情報があれば参照のみ、無ければ書き込む、のif文を追加予定。

        # DBに開始情報を書き込む（新規登録）
        c.execute("insert into course_pork values(null,?,?)", (user_id,btn,))
        conn.commit()
        c.close()

        # pork（豚肉生姜焼き）ページへリダイレクトする
        return redirect("/pork")
    else:
        return redirect("/login")


# pork（豚肉生姜焼き）の画面を表示する
@app.route("/pork")
def pork():
    return render_template("pork.html")


# # 完了おめでとう処理
# 「pork」コースの完了ボタン（/complete）を押した時、
@app.route("/complete", methods=["POST"])
def complete_pork():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # default:0
        btn = 1
        print(btn)

        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # DBに完了情報を書き込む（更新する）
        c.execute("update course_pork set pork_01=? where user_id =?", (btn,user_id,))
        conn.commit()
        c.close()
        
        # DB接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # ユーザー情報を取得し表示
        c.execute("select name from user where id = ?", (user_id,))
        user_info = c.fetchone()
        print("-------------------------")
        print(user_info)

        # pork（豚肉生姜焼き）ページへリダイレクトする
        return render_template("complete.html", user_info=user_info)

    else:
        return redirect("/login")



# ログアウト機能
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/cookgate")



# 403エラー
@app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'

# 404エラー
@app.errorhandler(404)
def notfound404(code):
    return "404だよ！！見つからないよ！！！"


# 開発用サーバ設定
if __name__ == "__main__":
    app.run(debug=True)
