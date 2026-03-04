from flask import Flask, request, jsonify
import requests
import json
import os
import time
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== إعدادات حساب Free Fire ====================
FF_UID = "4378068850"
FF_PASSWORD = "8C583277F6A0221993BAC8FBBD712BC25B171A445A34FB1DD0966609CB74729D"

app = Flask(__name__)

# ==================== دوال مساعدة من byte.py ====================
def encrypt_api(plain_text):
    """تشفير البيانات المرسلة"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def Encrypt_ID(number):
    """تشفير معرف اللاعب"""
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

# ==================== الحصول على توكن جديد ====================
def get_fresh_token():
    """جلب توكن جديد مباشرة من Garena"""
    try:
        print(f"[ℹ️] محاولة الحصول على توكن للحساب: {FF_UID}")
        
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "uid": FF_UID,
            "password": FF_PASSWORD,
            "response_type": "token",
            "client_type": "2",
            "client_id": "100067",
            "client_secret": ""
        }
        
        r = requests.post(url, headers=headers, data=data, timeout=15)
        
        if r.status_code == 200:
            token_data = r.json()
            access_token = token_data.get("access_token")
            print(f"[✅] تم الحصول على توكن جديد")
            return access_token
        else:
            print(f"[❌] فشل الحصول على توكن: {r.status_code}")
            print(f"[ℹ️] الاستجابة: {r.text}")
            return None
    except Exception as e:
        print(f"[❌] خطأ في get_fresh_token: {e}")
        return None

# ==================== إضافة صديق ====================
def add_friend_direct(token, target_uid):
    """إرسال طلب إضافة صديق"""
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        payload_bytes = bytes.fromhex(encrypt_api(payload))

        url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload_bytes)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Connection": "close",
        }
        
        response = requests.post(url, headers=headers, data=payload_bytes, timeout=10)
        
        if response.status_code == 200:
            print(f"[✅] تم إضافة {target_uid} بنجاح")
            return True, "تمت الإضافة بنجاح"
        else:
            print(f"[❌] فشل إضافة {target_uid}: {response.status_code}")
            return False, f"خطأ: {response.status_code}"
            
    except Exception as e:
        print(f"[❌] خطأ في add_friend_direct: {e}")
        return False, str(e)

# ==================== حذف صديق ====================
def remove_friend_direct(token, target_uid):
    """إرسال طلب حذف صديق"""
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        payload_bytes = bytes.fromhex(encrypt_api(payload))

        url = "https://clientbp.ggpolarbear.com/RemoveFriend"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload_bytes)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Connection": "close",
        }
        
        response = requests.post(url, headers=headers, data=payload_bytes, timeout=10)
        
        if response.status_code == 200:
            print(f"[✅] تم حذف {target_uid} بنجاح")
            return True, "تم الحذف بنجاح"
        else:
            print(f"[❌] فشل حذف {target_uid}: {response.status_code}")
            return False, f"خطأ: {response.status_code}"
            
    except Exception as e:
        print(f"[❌] خطأ في remove_friend_direct: {e}")
        return False, str(e)

# ==================== نقاط النهاية ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Free Fire Simple API',
        'version': '1.0.0',
        'developer': 'ZAKARIA',
        'endpoints': {
            '/add': 'إضافة صديق - /add?uid=123456789',
            '/remove': 'حذف صديق - /remove?uid=123456789'
        },
        'account': FF_UID
    })

@app.route('/add', methods=['GET'])
def add():
    """إضافة صديق"""
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({'success': False, 'error': 'يجب إرسال uid'}), 400
    
    if not uid.isdigit():
        return jsonify({'success': False, 'error': 'uid يجب أن يكون أرقاماً'}), 400
    
    # 1. الحصول على توكن جديد
    token = get_fresh_token()
    if not token:
        return jsonify({'success': False, 'error': 'فشل الحصول على توكن'}), 503
    
    # 2. إرسال طلب الإضافة
    success, message = add_friend_direct(token, uid)
    
    return jsonify({
        'success': success,
        'message': message,
        'uid': uid,
        'account': FF_UID
    })

@app.route('/remove', methods=['GET'])
def remove():
    """حذف صديق"""
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({'success': False, 'error': 'يجب إرسال uid'}), 400
    
    # 1. الحصول على توكن جديد
    token = get_fresh_token()
    if not token:
        return jsonify({'success': False, 'error': 'فشل الحصول على توكن'}), 503
    
    # 2. إرسال طلب الحذف
    success, message = remove_friend_direct(token, uid)
    
    return jsonify({
        'success': success,
        'message': message,
        'uid': uid,
        'account': FF_UID
    })

@app.route('/test', methods=['GET'])
def test():
    """اختبار الحساب"""
    token = get_fresh_token()
    if token:
        return jsonify({'success': True, 'message': 'الحساب يعمل', 'account': FF_UID})
    else:
        return jsonify({'success': False, 'message': 'فشل الاتصال بالحساب'}), 503

# للاختبار المحلي
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)