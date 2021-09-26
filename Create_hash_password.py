from flask_bcrypt import Bcrypt
import json

bcrypt = Bcrypt()
#generate_password_hash()を実行するとハッシュ値が生成されます。実行するたびに異なるハッシュ値が生成されます。
print(bcrypt.generate_password_hash('testing').decode('utf-8'))
#check_password_hash()を使うとハッシュ値が指定した文字列のものと一致しているか判定することができます。
hash_pw = bcrypt.generate_password_hash('testing').decode('utf-8')
print(bcrypt.check_password_hash(hash_pw, 'password'))
print(bcrypt.check_password_hash(hash_pw, 'testing'))


# 研究室ごとのパスワードjsonの読み込み
LabTable = json.load(open('LabTable.json', 'r', encoding='UTF-8'))

#同じ構造の辞書オブジェクトを作成
hashLabTable = LabTable.copy()

#確認
print(LabTable)

#全要素に対してpasswordをハッシュ値に変換
for i in LabTable:
    transpassword = bcrypt.generate_password_hash(LabTable[i]['password']).decode('utf-8') 
    hashLabTable[i]['password'] = transpassword

#確認
print(hashLabTable)

# #テスト
# LaboID = '6685182479135826'
# hash_pw = hashLabTable[LaboID]['password']
# print(hash_pw)
# user_pw = '0000'
# print(bcrypt.check_password_hash(hash_pw, user_pw))


#ファイルに保存
with open('flask_Application/hashLabTable.json', mode='wt', encoding='utf-8') as file:
    json.dump(hashLabTable, file, ensure_ascii=False, indent=4)


