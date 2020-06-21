# DB
import sqlite3
# フレームワークはflask
from flask import Flask, render_template, request, redirect, session
# 日時取ります
from datetime import datetime

# CSSフレームワークをつかいます
from flask_material import Material

# appにflaskを定義する
app = Flask(__name__)
# CSSフレームワークのための追記
Material(app)

# セッション
# セッション名は後で変えるう！！！！！
app.secret_key = "cook-gate"


# /以下に何も入力されていない場合、トップ画面へ自動遷移する
@app.route("/")
def go_index():
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
    # 登録ボタンクリックの日時取得
    reg_dt = datetime.now().strftime("%F %T")

    # 確認print
    print("-------------------------------")
    print(name)
    print(password)
    print(email)
    print(reg_dt)

    # 一つでも空の値がある場合、エラーを返すようにしたい。
    # 名前は2文字以上にしたい
    # パスワードは4文字以上にしたい
    # メールアドレスは「@」の有無チェックを入れたい
    # メールアドレスが既に登録済みの場合、ログイン画面へ誘導したい

    # DB接続
    conn = sqlite3.connect("service_cg.db")
    c = conn.cursor()
    c.execute("insert into user values(null,?,?,?,?)", (name,password,email,reg_dt,))
    conn.commit()
    c.close()

    return redirect("/login")



# ログイン
# ログイン画面を表示する
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

# ログイン画面で、「ログインする」ボタンを押した時の処理
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
        return render_template("/login")
    else:
        # セッションを作る
        session["user_id"] = user_id
        return redirect("/index")



# ログイントップ画面
# index.htmlに会員情報を表示させています。
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
        c.execute("select SUM(status) from course_status where user_id =? AND status > '0' GROUP BY course", (user_id,))
        # 完了しているコースの数を取得
        user_status = len(c.fetchall())
        print(user_status)

        # コース完了率を算出（％、整数になるよう四捨五入）
        # 全「2」コースとしてある。（豚肉と味噌汁）
        user_rate = round((user_status / 2) * 100)
        print("========================")
        print(user_rate)

        c.close()

        return render_template("index.html", user_info=user_info, user_status=user_status, user_rate=user_rate)
    else:
        return redirect("/login")


# コース選択情報を取る
@app.route("/course", methods=["POST"])
def select_course():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # 開始時点は、default:0 にする。
        status = 0

        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        # 豚肉：1
        # 味噌汁：2
        course = request.form.get("name")
        print("==========================")
        print(course)

        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # DBに開始情報を書き込む（新規登録）すでにあっても、ボタンを押すたびに登録される。
        c.execute("insert into course_status values(null,?,?,?)", (user_id,course,status,))
        # リダイレクトするコースのルーティングを取る。（どのhtmlファイルに行く？）
        c.execute("select page from course where id=?", (course,))
        page = c.fetchone()[0]
        print(page)

        conn.commit()
        c.close()

        return redirect(page)
    else:
        return redirect("/login")



# それぞれのコースの画面へリダイレクトする。
# pork（豚肉生姜焼き）の画面を表示する
@app.route("/pork")
def pork():
    return render_template("pork.html")

# soup（味噌汁）の画面を表示する
@app.route("/soup")
def soup():
    return render_template("soup.html")



# # 完了おめでとう処理
# 「pork」コースの完了ボタン（/complete）を押した時、
@app.route("/complete", methods=["POST"])
def complete():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # 完了ボタンクリックの日時取得
        comp_dt = datetime.now().strftime("%F %T")
        print("------------------------------------------")
        print(comp_dt)

        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        # 豚肉：1
        # 味噌汁：2
        course = request.form.get("name")
        print("================")
        print(course)

        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # DBに完了日時を書き込む（default:0 → 日時にする）
        c.execute("update course_status set status=? where user_id =? and course=? and status=?", (comp_dt,user_id,course,"0"))

        # ユーザー情報を取得し表示
        c.execute("select name from user where id = ?", (user_id,))
        user_info = c.fetchone()
        print("-------------------------")
        print(user_info)

        # コース名を取得するSQL文をここに書く。
        c.execute("select course_name from course where id = ?", (course,))
        user_course = c.fetchone()
        print("-------------------------")
        print(user_course)

        conn.commit()
        c.close()

        # 完了おめでとう画面へリダイレクトする。
        # この時、ユーザー名とコース名も一緒に持たせたいのだが、どうすれば？
        return render_template("complete.html",user_info=user_info,user_course=user_course)

    else:
        # ここは以下のように修正予定
        # もしセッションがない場合、「ゲストさん、おめでとう！」と表示させる。
        return redirect("/login")






# 未実装
# レベルアップ
# 写真アップロード
# 3コース目以降の動作追加








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
