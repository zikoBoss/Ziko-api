# byte.py - دوال التشفير الأساسية
# من مشروعك الأصلي - بدون تعديل

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from protobuf_decoder.protobuf_decoder import Parser
import json
import random

# ==================== دوال التشفير الأساسية ====================

def encrypt_api(plain_text):
    """تشفير البيانات باستخدام AES"""
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def decrypt_api(cipher_text):
    """فك تشفير البيانات"""
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(bytes.fromhex(cipher_text)), AES.block_size)
    return plain_text.hex()

# ==================== تشفير وفك تشفير المعرف ====================

def Encrypt_ID(number):
    """تشفير معرف اللاعب (UID)"""
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

def Decrypt_ID(encoded_hex):
    """فك تشفير معرف اللاعب"""
    if encoded_hex is None:
        return None
    
    # قوائم المساعدة لفك التشفير
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', 
           '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 
           'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 
           'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 
           'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 
           'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 
           'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 
           'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    
    x = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', 
         '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', 
         '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', 
         '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', 
         '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', 
         '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', 
         '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', 
         '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    
    if len(encoded_hex) == 10:
        w = 128
        xxx = len(encoded_hex)/2 - 1
        xxx = str(xxx)[:1]
        for i in range(int(xxx)-1):
            w = w * 128
        x1 = encoded_hex[:2]
        x2 = encoded_hex[2:4]
        x3 = encoded_hex[4:6]
        x4 = encoded_hex[6:8]
        x5 = encoded_hex[8:10]
        return str(w * x.index(x5) + (dec.index(x2) * 128) + dec.index(x1) + (dec.index(x3) * 128 * 128) + (dec.index(x4) * 128 * 128 * 128))
    
    elif len(encoded_hex) == 8:
        w = 128
        xxx = len(encoded_hex)/2 - 1
        xxx = str(xxx)[:1]
        for i in range(int(xxx)-1):
            w = w * 128
        x1 = encoded_hex[:2]
        x2 = encoded_hex[2:4]
        x3 = encoded_hex[4:6]
        x4 = encoded_hex[6:8]
        return str(w * x.index(x4) + (dec.index(x2) * 128) + dec.index(x1) + (dec.index(x3) * 128 * 128))
    
    return None

# ==================== دوال مساعدة ====================

def generate_random_hex_color():
    """توليد لون عشوائي"""
    top_colors = [
        "FF4500", "FFD700", "32CD32", "87CEEB", "9370DB",
        "FF69B4", "8A2BE2", "00BFFF", "1E90FF", "20B2AA",
        "00FA9A", "008000", "FFFF00", "FF8C00", "DC143C",
        "FF6347", "FFA07A", "FFDAB9", "CD853F", "D2691E",
        "BC8F8F", "F0E68C", "556B2F", "808000", "4682B4",
        "6A5ACD", "7B68EE", "8B4513", "C71585", "4B0082",
        "B22222", "228B22", "8B008B", "483D8B", "556B2F",
        "800000", "008080", "000080", "800080", "808080",
        "A9A9A9", "D3D3D3", "F0F0F0"
    ]
    return random.choice(top_colors)

def dec_to_hex(ask):
    """تحويل رقم عشري إلى هيكس"""
    ask_result = hex(ask)
    final_result = str(ask_result)[2:]
    if len(final_result) == 1:
        final_result = "0" + final_result
        return final_result
    else:
        return final_result

def encode_varint(number):
    """تشفير varint"""
    if number < 0:
        raise ValueError("Number must be non-negative")
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes)

# ==================== دوال تحليل الحزم ====================

class ParsedResult:
    def __init__(self, field, wire_type, data):
        self.field = field
        self.wire_type = wire_type
        self.data = data

class ParsedResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ParsedResult):
            return {"field": obj.field, "wire_type": obj.wire_type, "data": obj.data}
        return super().default(obj)

def parse_results(parsed_results):
    """تحليل نتائج Parser"""
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def get_available_room(input_text):
    """الحصول على معلومات الغرفة من الحزمة"""
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"error {e}")
        return None

def get_leader(packet):
    """استخراج قائد الفريق من الحزمة"""
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]["1"]["data"]["8"]["data"]
    return str(json_data)

def get_target(packet):
    """استخراج الهدف من الحزمة"""
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]["1"]["data"]["1"]["data"]
    return str(json_data)

def get_player_status(packet):
    """الحصول على حالة اللاعب من الحزمة"""
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]
    keys = list(json_data.keys())
    data = keys[1]
    keys = list(json_data[data].keys())
    try:
        data = json_data[data]
        data = data['1']
        data = data['data']
        data = data['3']
    except KeyError:
        return ["OFFLINE", packet]
    
    if data['data'] == 1:
        target = get_target(packet)
        return ["SOLO", target]
    
    if data['data'] == 2:
        target = get_target(packet)
        leader = get_leader(packet)
        group_count = json_data["5"]["data"]["1"]["data"]["9"]["data"]
        return ["INSQUAD", target, leader, group_count]
    
    if data['data'] == 3:
        target = get_target(packet)
        return ["INGAME", target]
    
    if data['data'] == 5:
        target = get_target(packet)
        return ["INGAME", target]
    
    if data['data'] == 7 or data['data'] == 6:
        target = get_target(packet)
        return ["IN SOCIAL ISLAND MODE ..", target]
    
    return "NOTFOUND"