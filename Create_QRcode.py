import qrcode
import json

# jsonの読み出し
LabTable = json.load(open('LabTable.json', 'r', encoding='UTF-8'))


for LaboID in LabTable:
    # データの読み出し
    Lab_name = LabTable[LaboID]['Lab_name']
    print('LaboID:', LaboID)
    print('研究室名', Lab_name)
    
    # QRコードに埋め込むテキストデータの作成
    ipaddress = '192.168.10.50'
    ports = '58426'
    QRtext = 'https://'+ ipaddress +':'+ports+'/OpenLabo?LaboID='+LaboID
    print(QRtext)
    
    # QRコードの作成と画像の保存
    QRimg = qrcode.make(QRtext)
    QRimg.save('QRcodefile/'+Lab_name+'.png') #[QRcodefile]フォルダ内に保存

    print('サイズ', QRimg.size)
