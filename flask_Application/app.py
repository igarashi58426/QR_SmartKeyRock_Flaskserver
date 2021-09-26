from flask import Flask, render_template, request, redirect
from flask import url_for, abort, make_response
from flask import send_from_directory   

from flask_login import LoginManager, login_user, logout_user
from flask_login import login_required, UserMixin, current_user

from flask_bcrypt import Bcrypt

import ssl
import subprocess
from datetime import datetime

import json
import os

#Flaskアプリケーションの起動
app = Flask(__name__)

# セッションのクッキーを安全に署名するために使われるsecret key。
with open("secret_key.txt", mode='r', encoding='utf-8') as f:
    app.config['SECRET_KEY'] = f.read()
#セッションのクッキーの名前です。同じ名前を使ったクッキーを既に持っている場合には、変更が可能です。標準設定: 'session'
app.config['SESSION_COOKIE_NAME'] = 'flask_session_cookie'
#セッションのクッキーが有効になるドメイン｡標準設定: NoneDefault: ``None``
app.config['SESSION_COOKIE_DOMAIN'] = None
#セッションのクッキーが有効となるパス
app.config['SESSION_COOKIE_PATH'] = None
#セキュリティのためにクッキーへJavaScriptがアクセスできない｢HTTP only属性｣を付加する｡標準設定: True
app.config['SESSION_COOKIE_HTTPONLY'] = True
#セキュリティのためにHTTPSのリクエストに場合のみそのクッキーを送信する｢secure属性｣を付加する｡標準設定: False
app.config['SESSION_COOKIE_SECURE'] = True
#app.session_cookie_secure = True
#ドメインをまたぐ外部サイトへのリクエストにおいてクッキーが送信されるかについて｢SameSite属性｣を付加する｡標準設定: None
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
#セッションのクッキーの消滅期限までの秒数を設定｡
#datetime.timedeltaまたはintのいずれかが可能
#標準設定: timedelta(days=31) (2678400 秒)
app.config['PERMANENT_SESSION_LIFETIME'] = 30*24*60*60
#session.permanent がtrueのとき、すべてのレスポンスでクッキーを送信するかを設定｡標準設定: True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config["JSON_AS_ASCII"] = False


#ホームとなるページ
@app.route('/',)
@app.route('/index',)
def home():
    return render_template('index.html',)

#QRコードwebリーダー
@app.route('/QRreader',)
def QRreader():
    return render_template('QRreader.html',)

#アイコン処理
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'), 'favicon.ico', )

#エラー処理
@app.errorhandler(404)
def Not_Found(error):
    return render_template('Not_Found.html')


# #---------------------------login_manager初期化処理-------------------------


# LoginManagerの起動
login_manager = LoginManager()
login_manager.init_app(app)
#コンピューター識別子（IPアドレスとUAのハッシュ）を保存し、セッションを検証する  # オプション: None, "basic","strong" デフォルト:"basic"
login_manager.session_protection = None

#ログイン時のUserオブジェクト作成
class User(UserMixin):
    def __init__(self, id,):
        self.id = id

#user_loader ログインが必要なページに行くたびに呼ばれるコールバック関数
#セッションからユーザーをリロードする
@login_manager.user_loader
def user_loader(id):
    return User(id)
 
#unauthorized_handler	ログイン必須ページで認証が確認できなかった場合の処理
@login_manager.unauthorized_handler
def unauthorized_handler():
    LaboID = request.args.get('LaboID')
    return redirect('/login'+'?LaboID='+LaboID)


# #---------------------------必要ファイル読み込み-------------------------

# 研究室ごとのパスワードjsonの読み込み
hashLabTable = json.load(open('hashLabTable.json', 'r', encoding='UTF-8'))

#研究室ごとのLaboID.txtを読み込む
with open("LaboID.txt" , mode="r" , encoding="UTF-8") as f:
    hardwareLaboID = f.read()

# #---------------------------解錠ページ･施錠ページ-------------------------

# 解錠ページ (解錠スクリプトの起動)
@app.route('/OpenLabo',)
@login_required
def OpenLabo():
    try:
        URLLaboID=request.args.get('LaboID')
        Lab_name = hashLabTable.get(URLLaboID)['Lab_name']
        #ラズパイが設置してある研究室に対応するIDの場合にモーターを動作
        if current_user.id == URLLaboID == hardwareLaboID :
            print('OPEN Move Motor')
            # 子プロセスで open.pyを実行する
            subprocess.Popen(["python3", "open.py"])
            return render_template('comprat_open.html', Lab_name=Lab_name, LaboID=URLLaboID )
        else:
            return render_template('miss_login.html', LaboID=URLLaboID)      
    except:
        return abort(404)


# 施錠ページ(施錠スクリプトの起動)
@app.route('/LockLabo',)
@login_required
def LockLabo():
    try:
        URLLaboID=request.args.get('LaboID')
        Lab_name = hashLabTable.get(URLLaboID)['Lab_name']
        #ラズパイが設置してある研究室に対応するIDの場合にモーターを動作
        if current_user.id == URLLaboID == hardwareLaboID :
            print('Lock Move Motor')
            # 子プロセスで lock.pyを実行する
            subprocess.Popen(["python3", "lock.py"])
            return render_template('comprat_lock.html', Lab_name=Lab_name, LaboID=URLLaboID )
        else:
            return render_template('miss_login.html', LaboID=URLLaboID)      
    except:
        return abort(404)


# #---------------------------ログイン関係-------------------------

#ログインフォーム
@app.route('/login',)
def login():
    #ログインフォームのページを表示
    LaboID = request.args.get('LaboID')
    return render_template('login.html',LaboID=LaboID)

#ハッシュパスワードの検証
def password_inspection(LaboID,password):
    bcrypt = Bcrypt()
    if LaboID in hashLabTable:
        # ハッシュ化されたパスワードの読み込み
        hash_pw = hashLabTable.get(LaboID)['password'] 
        # ハッシュ化されたパスワードと入力パスワードの比較
        inspection_bool = bcrypt.check_password_hash(hash_pw, password)
    else:
        inspection_bool = False
    return inspection_bool #成否をbool値で返す

# 入室のログを記録
def RoomEntrylog(Studentnumber, member_name, member_status,):
    with open("RoomEntrylog.csv" , mode="a" , encoding="UTF-8") as f:
        #write(現在時刻, 学籍番号, 名前,  ステータス)
        f.write(str(datetime.now()) +','+
                str(Studentnumber)+','+
                member_name+','+
                member_status+"\n")


#ログイン情報の検証･セッション発行
@app.route('/login_check', methods=['GET', 'POST'])
def login_check():
    if request.method == 'POST': #POSTの場合はチェック
        LaboID = request.args.get('LaboID')#URLクエリより取得
        #ポスト情報を格納
        Studentnumber = request.form['Studentnumber'] 
        member_name = request.form['member_name']
        member_status = request.form['member_status']
        password = request.form['password']

        #検証
        if password_inspection(LaboID,password):
            print('loginOK')
            if member_status == 'member':
                login_user(User(int(LaboID)) ,remember=True )#セッション付与(自動ログイン)
            if member_status == 'guest':
                login_user(User(int(LaboID)) ,remember=False )#セッション付与(自動ログインなし)
            
            RoomEntrylog(Studentnumber, member_name, member_status)
            return redirect('/OpenLabo?LaboID='+LaboID)

        else:#ログイン失敗
            return render_template('miss_login.html', LaboID=LaboID)      
    else :#エラー処理
        return abort(404)


# #---------------------------ログアウト関係-------------------------

#ログイン状態の削除
#ページなしで削除処理後リダイレクト
@app.route('/logout')
@login_required
def logout():
    logout_user()#logout_user()#ユーザーはログアウトされ、セッションのCookieはすべて削除される。
    return redirect('/')




############################################

if __name__ == '__main__':

    #TLS接続セッション設定
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #CRTファイルと秘密鍵ファイル
    context.load_cert_chain('ssl_server_secret.crt', 'ssl_server_secret.key')

    #サーバホスト･ポート設定
    host = '0.0.0.0'
    port = 58426
    print('HTTP_server host:', host)
    print('HTTP_server port:', port)

    app.run(host=host, port=port, threaded=True, ssl_context=context, debug=True)    







