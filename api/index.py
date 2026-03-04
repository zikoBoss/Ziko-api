# api/index.py - Free Fire Friends API
# Developer: ZAKARIA
# يستقبل طلبات من موقعك ويتواصل مع البوت الخفي

from flask import Flask, request, jsonify
import requests
import json
import os
import time
import threading
from datetime import datetime

app = Flask(__name__)

# ==================== الإعدادات ====================
BOT_URL = "https://your-bot-service.com"  # ⚠️ غيّر هذا إلى رابط البوت الخفي بعد نشره
BOT_API_KEY = "ZAKARIA_SECRET_2024"  # مفتاح سري للتواصل مع البوت

# ملف التخزين (Vercel يسمح فقط بـ /tmp)
DATA_FILE = '/tmp/freefire_data.json'

# ==================== دوال التعامل مع الملف ====================
def load_data():
    """تحميل البيانات من الملف"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"friends": {}}  # friends: { "uid": {"added_at": timestamp, "expiry": timestamp} }

def save_data(data):
    """حفظ البيانات في الملف"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

# ==================== فحص الصلاحية تلقائياً ====================
def check_expired_friends():
    """دالة تعمل في الخلفية لفحص الأصدقاء منتهية الصلاحية وحذفهم"""
    while True:
        try:
            data = load_data()
            current_time = int(time.time())
            modified = False
            
            # قائمة بالأصدقاء الذين انتهت صلاحيتهم
            expired = []
            for uid, info in data["friends"].items():
                if info["expiry"] <= current_time:
                    expired.append(uid)
            
            # حذف كل من انتهت صلاحيته
            if expired:
                # إرسال طلب حذف إلى البوت الخلفي
                try:
                    response = requests.post(
                        f"{BOT_URL}/execute",
                        json={
                            'action': 'cleanup',
                            'expired_list': expired,
                            'api_key': BOT_API_KEY
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        for uid in expired:
                            del data["friends"][uid]
                            modified = True
                            print(f"[🗑️] تم حذف {uid} - انتهت الصلاحية")
                except:
                    print(f"[⚠️] فشل الاتصال بالبوت الخفي")
            
            if modified:
                save_data(data)
                
        except Exception as e:
            print(f"[⚠️] خطأ في فحص الصلاحية: {e}")
        
        # ننتظر ساعة قبل الفحص التالي
        time.sleep(3600)

# تشغيل فحص الصلاحية في خلفية منفصلة
threading.Thread(target=check_expired_friends, daemon=True).start()

# ==================== دوال مساعدة ====================
def format_time(seconds):
    """تحويل الثواني إلى نص مفهوم"""
    if seconds <= 0:
        return 'منتهية الصلاحية'
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    if days > 0:
        return f'{days} يوم و {hours} ساعة'
    elif hours > 0:
        return f'{hours} ساعة و {minutes} دقيقة'
    else:
        return f'{minutes} دقيقة'

# ==================== نقطة النهاية الرئيسية ====================
@app.route('/', methods=['GET'])
def home():
    """الصفحة الرئيسية"""
    data = load_data()
    current_time = int(time.time())
    
    # تحديث حالة كل صديق
    friends_list = []
    for uid, info in data["friends"].items():
        remaining = info["expiry"] - current_time
        friends_list.append({
            'uid': uid,
            'added_at': info['added_at'],
            'expiry': info['expiry'],
            'remaining_seconds': remaining,
            'remaining_text': format_time(remaining),
            'status': 'نشط' if remaining > 0 else 'منتهي'
        })
    
    return jsonify({
        'name': 'Free Fire Friends API',
        'version': '2.0.0',
        'developer': 'ZAKARIA',
        'documentation': 'https://your-website.com/api-docs',
        'endpoints': {
            '/add': 'إضافة صديق - /add?uid=123456789',
            '/remove': 'حذف صديق - /remove?uid=123456789',
            '/list': 'عرض جميع الأصدقاء - /list',
            '/check': 'التحقق من صديق - /check?uid=123456789'
        },
        'friends_count': len(friends_list),
        'friends': friends_list
    })

# ==================== 1️⃣ إضافة صديق ====================
@app.route('/add', methods=['GET'])
def add_friend():
    """
    إضافة صديق جديد
    /add?uid=123456789
    """
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({
            'success': False,
            'error': 'يجب إرسال uid'
        }), 400
    
    if not uid.isdigit():
        return jsonify({
            'success': False,
            'error': 'uid يجب أن يكون أرقاماً فقط'
        }), 400
    
    # تحميل البيانات
    data = load_data()
    
    # التحقق إذا كان الصديق موجوداً مسبقاً
    if uid in data["friends"]:
        remaining = data["friends"][uid]["expiry"] - int(time.time())
        if remaining > 0:
            return jsonify({
                'success': False,
                'error': 'هذا الصديق موجود بالفعل',
                'remaining_seconds': remaining,
                'remaining_text': format_time(remaining)
            }), 400
    
    # إرسال طلب إضافة إلى البوت الخفي
    try:
        response = requests.post(
            f"{BOT_URL}/execute",
            json={
                'action': 'add',
                'target_uid': uid,
                'api_key': BOT_API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            bot_result = response.json()
            
            if bot_result.get('success'):
                # حساب وقت انتهاء الصلاحية (24 ساعة)
                current_time = int(time.time())
                expiry_time = current_time + (24 * 3600)
                
                # حفظ الصديق
                data["friends"][uid] = {
                    'added_at': current_time,
                    'expiry': expiry_time
                }
                save_data(data)
                
                return jsonify({
                    'success': True,
                    'message': f'✅ تم إضافة {uid} بنجاح',
                    'uid': uid,
                    'added_at': current_time,
                    'expiry': expiry_time,
                    'expiry_text': format_time(24 * 3600)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': bot_result.get('error', 'فشل الإضافة')
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'البوت الخفي غير متاح'
            }), 503
            
    except requests.exceptions.RequestException:
        return jsonify({
            'success': False,
            'error': 'فشل الاتصال بالبوت الخفي'
        }), 503

# ==================== 2️⃣ حذف صديق ====================
@app.route('/remove', methods=['GET'])
def remove_friend():
    """
    حذف صديق
    /remove?uid=123456789
    """
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({
            'success': False,
            'error': 'يجب إرسال uid'
        }), 400
    
    # تحميل البيانات
    data = load_data()
    
    # التحقق من وجود الصديق
    if uid not in data["friends"]:
        return jsonify({
            'success': False,
            'error': 'هذا الصديق غير موجود'
        }), 404
    
    # إرسال طلب حذف إلى البوت الخفي
    try:
        response = requests.post(
            f"{BOT_URL}/execute",
            json={
                'action': 'remove',
                'target_uid': uid,
                'api_key': BOT_API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            bot_result = response.json()
            
            if bot_result.get('success'):
                # حذف من البيانات المحلية
                del data["friends"][uid]
                save_data(data)
                
                return jsonify({
                    'success': True,
                    'message': f'✅ تم حذف {uid} بنجاح'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': bot_result.get('error', 'فشل الحذف')
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'البوت الخفي غير متاح'
            }), 503
            
    except requests.exceptions.RequestException:
        return jsonify({
            'success': False,
            'error': 'فشل الاتصال بالبوت الخفي'
        }), 503

# ==================== 3️⃣ عرض جميع الأصدقاء ====================
@app.route('/list', methods=['GET'])
def list_friends():
    """
    عرض جميع الأصدقاء
    /list
    """
    data = load_data()
    current_time = int(time.time())
    
    friends_list = []
    for uid, info in data["friends"].items():
        remaining = info["expiry"] - current_time
        friends_list.append({
            'uid': uid,
            'added_at': info['added_at'],
            'added_at_text': datetime.fromtimestamp(info['added_at']).strftime('%Y-%m-%d %H:%M:%S'),
            'expiry': info['expiry'],
            'expiry_text': datetime.fromtimestamp(info['expiry']).strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_seconds': remaining,
            'remaining_text': format_time(remaining),
            'status': 'نشط' if remaining > 0 else 'منتهي'
        })
    
    # ترتيب حسب وقت الإضافة (الأحدث أولاً)
    friends_list.sort(key=lambda x: x['added_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'count': len(friends_list),
        'active_count': len([f for f in friends_list if f['status'] == 'نشط']),
        'expired_count': len([f for f in friends_list if f['status'] == 'منتهي']),
        'friends': friends_list
    })

# ==================== 4️⃣ التحقق من صديق معين ====================
@app.route('/check', methods=['GET'])
def check_friend():
    """
    التحقق من صديق معين
    /check?uid=123456789
    """
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({
            'success': False,
            'error': 'يجب إرسال uid'
        }), 400
    
    data = load_data()
    
    if uid not in data["friends"]:
        return jsonify({
            'success': False,
            'error': 'هذا الصديق غير موجود'
        }), 404
    
    info = data["friends"][uid]
    current_time = int(time.time())
    remaining = info["expiry"] - current_time
    
    return jsonify({
        'success': True,
        'uid': uid,
        'added_at': info['added_at'],
        'added_at_text': datetime.fromtimestamp(info['added_at']).strftime('%Y-%m-%d %H:%M:%S'),
        'expiry': info['expiry'],
        'expiry_text': datetime.fromtimestamp(info['expiry']).strftime('%Y-%m-%d %H:%M:%S'),
        'remaining_seconds': remaining,
        'remaining_text': format_time(remaining),
        'status': 'نشط' if remaining > 0 else 'منتهي'
    })

# ==================== 5️⃣ تحديث يدوي للصلاحية ====================
@app.route('/cleanup', methods=['GET'])
def manual_cleanup():
    """
    تنظيف الأصدقاء منتهية الصلاحية يدوياً
    /cleanup
    """
    try:
        data = load_data()
        current_time = int(time.time())
        expired = [uid for uid, info in data["friends"].items() if info["expiry"] <= current_time]
        
        if expired:
            response = requests.post(
                f"{BOT_URL}/execute",
                json={
                    'action': 'cleanup',
                    'expired_list': expired,
                    'api_key': BOT_API_KEY
                },
                timeout=10
            )
            
            if response.status_code == 200:
                for uid in expired:
                    del data["friends"][uid]
                save_data(data)
                
                return jsonify({
                    'success': True,
                    'message': f'✅ تم حذف {len(expired)} صديق منتهي الصلاحية',
                    'deleted': expired
                })
        
        return jsonify({
            'success': True,
            'message': 'لا يوجد أصدقاء منتهية الصلاحية'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# للاختبار المحلي
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)