import OpenSSL 

def create_cert(cert_file_name, key_file_name):
    """TLS証明書（cert）を作成."""

    # # 公開鍵･秘密鍵キーペアの作成する。 「openssl genrsa -out test.key 2048」コマンドに近い
    # https://pyopenssl.org/en/stable/api/crypto.html #OpenSSL.crypto.PKey.generate_key
    key = OpenSSL.crypto.PKey()
    #RSA 2048bit鍵長のキーペア
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048) #キータイプとビット数を指定し､キーペアを生成します。

    # # X.509インスタンスを生成
    # X.509ストアは、証明書を検証するコンテキストを記述するために使用されます。
    # コンテキストの説明には、信頼する証明書のセット、証明書失効リストのセット、検証フラグなどが含まれる場合があります。
    # 説明にすぎないX.509ストアを単独で使用して、証明書を検証することはできません。
    cert = OpenSSL.crypto.X509()

    # # 証明書の公開鍵を追加
    cert.set_pubkey(key) #証明書の公開鍵を設定します。
    cert.set_serial_number(1000) #証明書のシリアル番号を設定します。
    
    # # 自己署名する。
    cert.sign(key, 'sha256')#このキーとダイジェストタイプを使用して証明書に署名します。

    # # 信頼できる証明書の追加
    # このストアに信頼できる証明書を追加します。
    # この方法で証明書を追加すると、この証明書が信頼できる証明書として追加 されます。
    # cert.add_cert(cert)

    # # 証明書失効リストを追加
    # このストアに証明書失効リストを追加します。
    # ストアに追加された証明書失効リストは、
    # 関連するフラグが証明書失効リストをチェックするように構成されている場合にのみ使用されます。
    # cert.add_crl(crl)

    # # 証明書チェーンの追加
    # X509Storeに、証明書チェーンの信頼できる証明書がどこにあるかを知らせます。
    # 証明書はPEM形式である必要があることに注意してください。
    #cert.load_locations（cafile, capath = None ）

    # 有効期限を設定 今回の場合1年
    cert.gmtime_adj_notBefore(0) #証明書が有効になり始めるタイムスタンプを調整します。
    cert.gmtime_adj_notAfter(1*365*24*60*60) #証明書が無効になるタイムスタンプを調整します。

    #サーバー情報の追加
    cert.get_subject().C = 'JP' #国の名前 JP
    cert.get_subject().ST = 'ore' #組織の住所（都道府県名） Tokyo
    cert.get_subject().L = 'ore' #組織の住所（市区町村名） Minato-ku
    cert.get_subject().O = 'ore' #組織名 Cybertrust Japan Co., Ltd.
    cert.get_subject().OU = 'ore' #組織の部署名 Public Relations
    cert.get_subject().CN = 'ore' #コモンネーム サーバー名 www.cybertrust.ne.jp
    cert.set_issuer(cert.get_subject()) #この証明書の発行者情報を設定します。

    # x.509 v3で生成するように設定する。
    cert.set_version(2)#証明書のバージョン番号を設定。バージョン値はゼロベースである｡値0はV1です。

  
    # v3の拡張属性の設定を行う。
    # add_extensionsで設定を追加することができ、その中でX509Extensionを使う。
    # https://www.openssl.org/docs/manmaster/man5/x509v3_config.html
    # https://www.ipa.go.jp/security/pki/033.html
    # .encode('ascii')でエンコードしないとエラーとなるので注意。
    cert.add_extensions([
        OpenSSL.crypto.X509Extension(#basicConstraints 基本制約 証明書がCA証明書であるか否か 今回はFalse
            'basicConstraints'.encode('ascii'), False, 'CA:FALSE'.encode('ascii')),
        OpenSSL.crypto.X509Extension(#keyUsage 許可される鍵の使い方を設定する拡張設定
            'keyUsage'.encode('ascii'), True, 'digitalSignature, keyEncipherment'.encode('ascii')),
        OpenSSL.crypto.X509Extension(#extendedKeyUsage 鍵の用途について詳細
            'extendedKeyUsage'.encode('ascii'), True, 'serverAuth'.encode('ascii')),
    ])


    # 証明書の情報を取り出し､ファイルに書き込む
    # https://pyopenssl.org/en/stable/api/crypto.html#OpenSSL.crypto.dump_certificate
    with open(cert_file_name, mode='wt') as f:
        f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert).decode('utf-8'))

    # 秘密鍵の情報を取り出し､ファイルに書き込む
    # https://pyopenssl.org/en/stable/api/crypto.html#OpenSSL.crypto.dump_privatekey
    with open(key_file_name, mode='wt') as f:
        f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key).decode('utf-8'))





if __name__ =='__main__':
    cert_file_name = 'flask_Application/ssl_server_secret.crt'
    key_file_name = 'flask_Application/ssl_server_secret.key'

    create_cert(cert_file_name, key_file_name)
    print('complete!!')

# ドメイン認証（DV） ドメイン名が正しいかどうか認証
# 実在証明型（OV）
# ドメイン名に加え、会社名も証明
# ワイルドカード証明書を使用可能
# 実在証明拡張型（EV）
# DV、OVよりも厳格な審査を受けて発行さる｡
# 証明書は、ドメイン名、実在証明を行う｡
# アドレスバーに組織情報が表示されるようになる
# ワイルドカード証明書を使用不可



# Key Usage（鍵の用途）
# これは許可される鍵の使い方の配列を設定する多値の拡張設定である。
# 設定できる値: 
# digitalSignature ディジタル署名の検証
# nonRepudiation 否証防止サービスにおけるディジタル署名の検証
# keyEncipherment 鍵転送時などの暗号鍵の暗号化
# dataEncipherment データの暗号化
# keyAgreement 鍵交換 
# keyCertSign 証明書の署名検証
# cRLSign CRLの署名検証
# encipherOnly 鍵交換時のデータ暗号化
# decipherOnly 鍵交換時のデータ復号化
# 例:
# keyUsage=digitalSignature, nonRepudiation
# keyUsage=critical, keyCertSign
# クライアント証明書用（[ usr_cert ]）：
# keyUsage = nonRepudiation, digitalSignature, keyEncipherment
# 証明書署名要求用（[ v3_req ]）：
# keyUsage = nonRepudiation, digitalSignature, keyEncipherment
# CA証明書用（[ v3_ca ]）：
# keyUsage = cRLSign, keyCertSign
# 標準･SSLサーバ 
# ディジタル署名の検証, 鍵転送時などの暗号鍵の暗号化



