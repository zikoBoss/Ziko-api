# bot/bot_service.py - البوت الخفي (يعمل 24/7)

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إضافة المسار للوصول إلى byte.py (الموجود في نفس المجلد)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from byte import Encrypt_ID, encrypt_api

# ==================== الإعدادات ====================
BOT_API_KEY = "ZAKARIA_SECRET_2024"  # مفتاح سري للتواصل مع API

# بيانات حساب Free Fire الخاص بك
UID = "4378068850"
PASSWORD = "8C583277F6A0221993BAC8FBBD712BC25B171A445A34FB1DD0966609CB74729D"

JwT_tokw = None  # التوكن الحالي
TOKEN_REFRESH_INTERVAL = 300  # 5 دقائق

# ==================== دوال التشفير (موجودة في byte.py) ====================
# ملاحظة: هذه الدوال مستوردة من byte.py

# ==================== صانع التوكن ====================
def TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid):
    """إنشاء توكن جديد من خلال MajorLogin"""
    now = datetime.now()
    now = str(now)[:len(str(now)) - 7]

    # هذا الهيكس الكبير - نفس الموجود في البوت الأصلي
    data = bytes.fromhex(
        '1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366'
    )

    # استبدال البيانات القديمة بالجديدة
    data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
    data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())

    # تشفير الحزمة
    encrypted = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(encrypted)

    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'ob52',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Authorization': 'Bearer ...',
        'Content-Length': '928',
        'User-Agent': 'Dalvik/2.1.0',
        'Host': 'loginbp.ggpolarbear.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    response = requests.post(url, headers=headers, data=Final_Payload, verify=False)

    if response.status_code == 200:
        if len(response.text) < 10:
            return False

        base = response.text[
            response.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):
            -1
        ]

        second_dot = base.find(".", base.find(".") + 1)
        base = base[:second_dot + 44]
        return base
    return False

# ==================== جلب التوكن ====================
def fetch_token():
    """تحديث التوكن بشكل دوري"""
    global JwT_tokw

    try:
        print(f"[ℹ️] تحديث التوكن للحساب: {UID}")

        # الخطوة 1: الحصول على توكن من Garena
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "uid": UID,
            "password": PASSWORD,
            "response_type": "token",
            "client_type": "2",
            "client_id": "100067",
            "client_secret": ""
        }

        r = requests.post(url, headers=headers, data=data)
        
        if r.status_code != 200:
            print(f"[❌] فشل الاتصال بـ Garena: {r.status_code}")
            threading.Timer(TOKEN_REFRESH_INTERVAL, fetch_token).start()
            return

        d = r.json()
        NEW_ACCESS_TOKEN = d.get("access_token")
        NEW_OPEN_ID = d.get("open_id")

        if not NEW_ACCESS_TOKEN or not NEW_OPEN_ID:
            print("[❌] لم يتم استلام التوكن من Garena")
            threading.Timer(TOKEN_REFRESH_INTERVAL, fetch_token).start()
            return

        print(f"[✅] تم الحصول على التوكن من Garena")

        # البيانات القديمة (ثابتة)
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID = "4306245793de86da425a52caadf21eed"

        # الخطوة 2: إنشاء التوكن النهائي
        token = TOKEN_MAKER(
            OLD_ACCESS_TOKEN,
            NEW_ACCESS_TOKEN,
            OLD_OPEN_ID,
            NEW_OPEN_ID,
            UID
        )

        if token:
            JwT_tokw = token
            print("[✅] تم تحديث التوكن بنجاح!")
        else:
            print("[❌] فشل تحديث التوكن")

    except Exception as e:
        print(f"[❌] خطأ في fetch_token: {e}")

    # جدولة التحديث التالي
    threading.Timer(TOKEN_REFRESH_INTERVAL, fetch_token).start()

# ==================== دوال تنفيذ المهام ====================
def add_friend(target_uid):
    """إرسال طلب إضافة صديق"""
    if not JwT_tokw:
        return False, "التوكن غير متاح"

    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        payload_bytes = bytes.fromhex(encrypt_api(payload))

        url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
        headers = {
            "Authorization": f"Bearer {JwT_tokw}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload_bytes)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Connection": "close",
        }
        
        response = requests.post(url, headers=headers, data=payload_bytes)
        if response.status_code == 200:
            return True, "تمت الإضافة بنجاح"
        return False, f"خطأ في API: {response.status_code}"
    except Exception as e:
        return False, str(e)

def remove_friend(target_uid):
    """إرسال طلب حذف صديق"""
    if not JwT_tokw:
        return False, "التوكن غير متاح"

    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        payload_bytes = bytes.fromhex(encrypt_api(payload))

        url = "https://clientbp.ggpolarbear.com/RemoveFriend"
        headers = {
            "Authorization": f"Bearer {JwT_tokw}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB52",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload_bytes)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Connection": "close",
        }
        
        response = requests.post(url, headers=headers, data=payload_bytes)
        if response.status_code == 200:
            return True, "تم الحذف بنجاح"
        return False, f"خطأ في API: {response.status_code}"
    except Exception as e:
        return False, str(e)

# ==================== تنظيف الأصدقاء منتهية الصلاحية ====================
def cleanup_expired_friends():
    """هذه الدالة تستقبل طلب من API لحذف أصدقاء معينين"""
    # API سيرسل لنا قائمة بالأصدقاء الذين انتهت صلاحيتهم
    pass

# ==================== تشغيل خادم داخلي ====================
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    """تنفيذ الأوامر القادمة من API الرئيسي"""
    data = request.json
    
    # التحقق من المفتاح السري
    if data.get('api_key') != BOT_API_KEY:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    action = data.get('action')
    target_uid = data.get('target_uid')
    
    if not action or not target_uid:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
    
    if action == 'add':
        success, message = add_friend(target_uid)
        return jsonify({'success': success, 'error': None if success else message})
    
    elif action == 'remove':
        success, message = remove_friend(target_uid)
        return jsonify({'success': success, 'error': None if success else message})
    
    elif action == 'cleanup':
        # هنا نستقبل قائمة الأصدقاء للحذف
        expired_list = data.get('expired_list', [])
        results = []
        for uid in expired_list:
            success, _ = remove_friend(uid)
            results.append({'uid': uid, 'success': success})
        return jsonify({'success': True, 'results': results})
    
    else:
        return jsonify({'success': False, 'error': 'Unknown action'}), 400

@app.route('/health', methods=['GET'])
def health():
    """فحص حالة البوت"""
    return jsonify({
        'status': 'alive',
        'token': 'valid' if JwT_tokw else 'waiting',
        'uid': UID
    })

def run_server():
    """تشغيل الخادم"""
    app.run(host='0.0.0.0', port=8080)

# ==================== التشغيل الرئيسي ====================
if __name__ == '__main__':
    print("="*50)
    print("🤖 Free Fire Bot Service (خفي)")
    print("👤 Developer: ZAKARIA")
    print("="*50)
    
    # بدء تحديث التوكن في الخلفية
    fetch_token()
    
    # تشغيل الخادم
    run_server()