# os
import os
# DB
import sqlite3
# フレームワークはflask
from flask import Flask, render_template, request, redirect, session, send_from_directory
# 日時取ります
from datetime import datetime
# ファイル名チェック用(片方で良い気もするが検証が間に合わないので両方残し！)
import werkzeug
from werkzeug.utils import secure_filename


# CSSフレームワークをつかいます
from flask_material import Material

# appにflaskを定義する
app = Flask(__name__)
# CSSフレームワークのための追記
Material(app)

# セッション
# セッション名は後で変えるう！！！！！
app.secret_key = "cook-gate"


# ～～～～～～～～～～～～～～～～～～～～
# /以下に何も入力されていない場合、トップ画面へ自動遷移する
@app.route("/")
def go_index():
    return redirect("/index")
    return render_template("cookgate.html")

# トップ画面
@app.route("/cookgate")
def cg_top():
    return redirect("/index")
    return render_template("cookgate.html")


# ～～～～～～～～～～～～～～～～～～～～
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
    # 完了コース数 default:0
    # メールアドレスは何を入力しても「email」と登録するよう設定してます。
    c.execute("insert into user values(null,?,?,?,?,?)", (name,password,email,reg_dt,"0"))
    conn.commit()
    c.close()

    return redirect("/login")


# ～～～～～～～～～～～～～～～～～～～～
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
    # email = request.form.get("email")

    # 確認print
    print("-------------------------------")
    print(name)
    print(password)
    # print(email)

    # 一つでも空の値がある場合、エラーを返すようにしたい。
    # 名前は2文字以上にしたい
    # パスワードは4文字以上にしたい
    # メールアドレスは「@」の有無チェックを入れたい

    # DB接続
    conn = sqlite3.connect("service_cg.db")
    c = conn.cursor()
    # ユーザ名、PW、メールアドレスの全てが一致するidを検索
    c.execute("select id from user where name=? and password=?", (name,password,))
    user_id = c.fetchone()

    # 確認print
    print("-----------------------------")
    print(user_id)
    c.close()

    # 未登録の場合、ログインページを表示し続ける
    if user_id is None:
        return redirect("/login")
    # 登録ありの場合、セッションを作りログイントップへ（index.html）
    else:
        # セッションを作る
        session["user_id"] = user_id
        return redirect("/index")


# ～～～～～～～～～～～～～～～～～～～～
# ログイントップ画面
# index.htmlに会員情報を表示させています。
@app.route("/index")
def dbtest():
    # ユーザーがログインしている場合
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # DB接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # ログインユーザー名とコース完了率を取得
        c.execute("select name,comp_course from user where id = ?", (user_id,))
        info = c.fetchone()
        user_info = info[0]
        user_status = info[1]
        if user_status is None:
            user_status = 0
        print("user_info",user_info)
        print("user_status",user_status)
        # 全コース数を取得
        c.execute("select COUNT(id) from course where id >0")
        course_num = c.fetchone()[0]

        # お料理ステータス：まだ実装してない。
        # コース毎の完了状況
        c.execute("SELECT course_name,status FROM course LEFT OUTER JOIN course_status ON course.id = course_status.course AND user_id=? ORDER BY course.id", (user_id,))
        user_list = c.fetchall()
        print("user_list",user_list)



        # コース完了率の算出（％、整数になるよう四捨五入）
        user_rate = round((user_status / course_num) * 100)
        print(user_rate)

        # レベル合計
        c.execute("select SUM(level) from course_level where user_id=?", (user_id,))
        level_sum = c.fetchone()[0]
        if level_sum is None:
            level_sum = 0
        print(level_sum)
        # レベル上限の合計を取得
        c.execute("SELECT SUM(maxlevel) FROM course")
        level_max = c.fetchone()[0]
        print(level_max)

        # user's photo-album
        c.execute("SELECT img_pass,course_name FROM photos WHERE user_id=?",(user_id,))
        photo_list = c.fetchall()
        print("photos:",photo_list)

        photo_num = len(photo_list)

        c.close()

        return render_template("index.html", user_info=user_info, user_status=user_status, user_rate=user_rate, course_num=course_num,level_sum=level_sum,level_max=level_max,photo_list=photo_list, user_id=user_id,user_list=user_list,photo_num=photo_num)

    # ログインしていない場合：ゲストさん表示
    else:
        user_info = "ゲスト"
        user_status = "-"
        user_rate = "-"
        course_num = "-"
        # ゲスト/ユーザーで表記分け用コード（消さないで！！）
        user_id = 0
        print(user_id)
        return render_template("index.html", user_info=user_info, user_status=user_status, user_rate=user_rate, course_num=course_num,user_id=user_id)


# ～～～～～～～～～～～～～～～～～～～～
# 各コースのボタンをクリックした時、各コースの画面へ遷移する。
# DBのstatusテーブルとlevelテーブルに情報書き込む。
@app.route("/course", methods=["POST"])
def select_course():
    # ユーザーがログインしている場合
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # 開始時点は、default:0 にする。
        status = 0

        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print("==========================")
        print(course)

        # DBに接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # 完了状況
        # DBのstatusテーブルに、既に登録があるか調べる
        c.execute("select id from course_status where user_id=? and course=? and status=?", (user_id,course,"0"))
        status = len(c.fetchall())
        # もし無ければ、DBのstatusテーブルに開始情報を書き込む（新規登録）
        if status == 0:
            # DBのstatusテーブルに開始情報を書き込む（新規登録）すでに登録があっても、ボタンを押すたびに登録される。
            c.execute("insert into course_status values(null,?,?,?)", (user_id,course,status,))

        # レベル状況
        # DBのlevelテーブルに、既に登録があるか調べる
        c.execute("select id from course_level where user_id=? and course_id=?", (user_id,course))
        level = len(c.fetchall())
        # もし無ければ、DBのlevelテーブルに開始情報を書き込む（新規登録）
        if level == 0:
            c.execute("insert into course_level values(null,?,?,?)", (user_id,course,status,))

        # リダイレクトするコースのルーティングをDBのcourseテーブルから取得（どのhtmlファイルに行く？）
        c.execute("select page from course where id=?", (course,))
        page = c.fetchone()[0]
        print(page)

        conn.commit()
        c.close()

        # 取得したページへリダイレクト
        return redirect(page)
    else:
        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print("==========================")
        print(course)

        # DBに接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # リダイレクトするコースのルーティングを取る。（どのhtmlファイルに行く？）
        # DBのcourseステーブルから取得。
        c.execute("select page from course where id=?", (course,))
        page = c.fetchone()[0]
        print(page)

        conn.commit()
        c.close()

        user_info = "ゲスト"

        # 取得したページへリダイレクト
        return redirect(page)


# ～～～～～～～～～～～～～～～～～～～～
# それぞれのコースの画面へリダイレクトする。
# pork（豚肉生姜焼き）の画面を表示する
@app.route("/pork")
def pork():
    # ユーザーがログインしている場合
    if "user_id" in session:
        # セッションからユーザーID取得
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # DB開く
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # ログインユーザー名とコース完了率を取得
        c.execute("select name,comp_course from user where id = ?", (user_id,))
        info = c.fetchone()
        user_info = info[0]
        user_status = info[1]
        if user_status is None:
            user_status = 0
        print("user_info",user_info)
        print("user_status",user_status)
        # 全コース数を取得
        c.execute("select COUNT(id) from course where id >0")
        course_num = c.fetchone()[0]
        # コース完了率の算出（％、整数になるよう四捨五入）
        user_rate = round((user_status / course_num) * 100)
        print("user_rate",user_rate)

        conn.commit()
        c.close()

        return render_template("pork.html", user_info=user_info, user_status=user_status, user_rate=user_rate, course_num=course_num,user_id=user_id)

    else:
        user_info = "ゲスト"
        return render_template("pork.html", user_info=user_info)


# soup（味噌汁）の画面を表示する
@app.route("/soup")
def soup():
    # ユーザーがログインしている場合
    if "user_id" in session:
        # セッションからユーザーID取得
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # DB開く
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # ログインユーザー名とコース完了率を取得
        c.execute("select name,comp_course from user where id = ?", (user_id,))
        info = c.fetchone()
        user_info = info[0]
        user_status = info[1]
        if user_status is None:
            user_status = 0
        print("user_info",user_info)
        print("user_status",user_status)
        # 全コース数を取得
        c.execute("select COUNT(id) from course where id >0")
        course_num = c.fetchone()[0]
        # コース完了率の算出（％、整数になるよう四捨五入）
        user_rate = round((user_status / course_num) * 100)
        print("user_rate",user_rate)

        conn.commit()
        c.close()

        return render_template("soup.html", user_info=user_info, user_status=user_status, user_rate=user_rate, course_num=course_num,user_id=user_id)

    else:
        user_info = "ゲスト"
        return render_template("soup.html", user_info=user_info)




# ～～～～～～～～～～～～～～～～～～～～
# # 完了おめでとう処理
# If user access 完了おめでとう-view directory, redirect to index.html
@app.route("/complete", methods=["GET"])
def complete_get():
    return redirect("/index")

# If user access course(pork, soup), display 完了おめでとう-view
# 完了おめでとう処理
@app.route("/complete", methods=["POST"])
def complete_post():
    # ログインしている場合
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print("user_id",user_id)
        # 完了ボタンクリックの日時取得
        comp_dt = datetime.now().strftime("%F %T")
        print("comp_dt",comp_dt)
        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print("course:",course)

        # DB開く
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # コース完了状況
        c.execute("SELECT status FROM course_status WHERE user_id =? and course=?", (user_id,course,))
        user_status = len(c.fetchall())
        print("user_status",user_status)
        # コース完了日時を書き込む
        c.execute("UPDATE course_status SET status=? WHERE user_id =? and course=? and status=?", (comp_dt,user_id,course,"0"))

        # もしこれが1回目の完了ならば、
        if user_status == 1:
            # ユーザーテーブルに完了率を書き込む。
            c.execute("UPDATE user SET comp_course= comp_course+1 WHERE id=?", (user_id,))
        
        # ユーザー名を取得
        c.execute("SELECT name FROM user WHERE id = ?", (user_id,))
        user_info = c.fetchone()[0]
        print("-------------------------")
        print(user_info)

        # コース名を取得
        c.execute("select course_name from course where id = ?", (course,))
        user_course = c.fetchone()[0]
        print("-------------------------")
        print(user_course)

        conn.commit()
        c.close()

        # 完了おめでとう画面へリダイレクトする。
        # この時、ユーザー名とコース名も一緒に持たせている。
        return render_template("complete.html",user_info=user_info,user_course=user_course, course=course,user_id=user_id)

    # ログインしていない場合：ゲストさん表示
    else:
        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print("================")
        print(course)

        # DBに接続
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # リダイレクトするコースの名前を取る。（どのhtmlファイルに行く？）
        # DBのcourseステーブルから取得。
        c.execute("select course_name from course where id=?", (course,))
        user_course = c.fetchone()[0]
        print(user_course)
        conn.commit()
        c.close()

        # ユーザー名はゲストさん
        user_info = "ゲスト"

        user_id = 0

        return render_template("complete.html",user_info=user_info,user_course=user_course,user_id=user_id)


# ～～～～～～～～～～～～～～～～～～～～
# レベルアップ表示
# 動作はするけどリロードするので使い勝手的にはダメ。
# HTMLにボタン付けてません。なのでこのコード丸ごと消してもOK
@app.route("/level", methods=["POST"])
def check():
    # ログインユーザーの場合
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("--------------------------")
        print(user_id)

        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print(course)

        # レベルチェックボタンの情報を取得
        name = request.form.get("check")
        print(name)

        # DB開く
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()

        # レベル上限と登録レベルを比較（引き算）
        c.execute("select (maxlevel-level) from course_level INNER JOIN course ON course.id=course_level.course_id where user_id=? AND course_id=? ", (user_id,course,))
        level_now = c.fetchone()[0]
        print(level_now)

        if level_now > 0:
            # DBにレベルを書き込む
            c.execute("update course_level set level = level + 1 where user_id=? and course_id=?", (user_id,course,))
        # リダイレクトするコースのルーティングを取る。（どのhtmlファイルに行く？）
        # DBのcourseステーブルから取得。
        c.execute("select page from course where id=?", (course,))
        page = c.fetchone()[0]
        print(page)

        conn.commit()
        c.close()
        # 取得したページへリダイレクト
        return redirect(page)
    else:
        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print(course)

        # DB開く
        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # リダイレクトするコースのルーティングを取る。（どのhtmlファイルに行く？）
        # DBのcourseステーブルから取得。
        c.execute("select page from course where id=?", (course,))
        page = c.fetchone()[0]
        print(page)
        conn.commit()
        c.close()
        # 取得したページへリダイレクト
        return redirect(page)


# ～～～～～～～～～～～～～～～～～～～～
# 写真アップロード
# ファイルサイズ制限：1MBまで
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


# 写真アップロード
@app.route('/uploads/<filename>')
# ファイルを表示する
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/upload",methods=["POST"])
def do_upload():
    if "user_id" in session:
        # セッションからユーザーIDを取得する。
        user_id = session["user_id"][0]
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(user_id)

        # course番号を取得(コース番号は、DBのcourseテーブルを見てね)
        course = request.form.get("name")
        print("==========================")
        print(course)

        # もし画像選択なくボタンを押した場合、トップページに遷移します。
        if "upload" not in request.files:
            return redirect("/index")

        # upload photo
        upload = request.files["upload"]
        if not upload.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return "画像ファイルは.png, .jpg, .jpegのみ（ブラウザの戻るボタンで戻ってください）"
        
        # For other def
        save_path = get_save_path()
        print(save_path)

        # ファイルのチェック
        # if upload and allowed_file(upload.filename):
        filename = secure_filename(upload.filename)
        print(filename)

        # ファイル名取得＆ファイル名変更
        filename = upload.filename
        filename = datetime.now().strftime("%y%m%d_%H%M%S_") \
            + werkzeug.utils.secure_filename(filename)
        upload.save(os.path.join(save_path,filename))
        print(filename)

        conn = sqlite3.connect("service_cg.db")
        c = conn.cursor()
        # コース番号からコース名を取得
        c.execute("select course_name from course where id=?", (course,))
        course_name = c.fetchone()[0]
        print(course_name)
        # 画像テーブルに書き込む
        c.execute("insert into photos values(null,?,?,?)", (user_id,course_name,filename))
        conn.commit()
        c.close()

        return redirect("/index")
    # ゲストさんがアクセスしたら、トップページへリダイレクト
    else:
        return redirect("/index")


def get_save_path():
    path_dir = "./static/user_img"
    return path_dir


# 写真のサイズが大きすぎるとき
# まだうまく実装できてないんだけど一応入れておきます。誰か直してー！！
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print("werkzeug.exceptions.RequestEntityTooLarge")
    return 'result : file size is overed.'












# 未実装
# 3コース目以降の動作追加
# ユーザー情報の変更
# 手持ちの器具から逆検索




# ～～～～～～～～～～～～～～～～～～～～
@app.route("/error")
def error():
    return render_template("error.html")


# ～～～～～～～～～～～～～～～～～～～～
# ログアウト機能（セッション削除）
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/cookgate")


# ～～～～～～～～～～～～～～～～～～～～
# 403エラー
@app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'

# 404エラー
@app.errorhandler(404)
def notfound404(code):
    return "404だよ！！見つからないよ！！！"


# ～～～～～～～～～～～～～～～～～～～～
# 開発用サーバ設定
if __name__ == "__main__":
    app.run(debug=True)
