from jwt_auth_middleware import JWTConfig, create_access_token, token_required, revoke_token, is_token_blacklisted, initialize_blacklist_system
import flask
from flask_cors import CORS
import os

app = flask.Flask(__name__)
CORS(app)

# 設定環境變數（使用你的 MongoDB API）
os.environ['MONGODB_API_URL'] = 'https://db-operation-xbbbehjawk.cn-shanghai.fcapp.run'
os.environ['JWT_BLACKLIST_COLLECTION'] = 'jwt_blacklist'
os.environ['JWT_ENABLE_BLACKLIST'] = 'true'

# 模擬使用者資料庫
users_db = {}

@app.route('/register', methods=['POST'])
def register():
    data = flask.request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return flask.jsonify({"error": "Email and password required"}), 400
    if email in users_db:
        return flask.jsonify({"error": "User already exists"}), 400
    users_db[email] = {"password": password, "roles": ["user"]}
    return flask.jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = flask.request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users_db.get(email)
    if not user or user['password'] != password:
        return flask.jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token({
        "sub": email,
        "email": email,
        "roles": user['roles']
    })
    return flask.jsonify({
        "access_token": token,
        "token_type": "bearer"
    })

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    auth_header = flask.request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(token, reason="user_logout")
        return flask.jsonify({"message": "Logout successful (token blacklisted)"})
    return flask.jsonify({"error": "No token provided"}), 400

@app.route('/protected')
@token_required
def protected(current_user):
    return flask.jsonify({
        "message": "This is a protected route",
        "user": current_user
    })

@app.route('/is_blacklisted', methods=['POST'])
def check_blacklist():
    data = flask.request.get_json()
    token = data.get('token')
    if not token:
        return flask.jsonify({"error": "No token provided"}), 400
    return flask.jsonify({"is_blacklisted": is_token_blacklisted(token)})

@app.route('/blacklist_stats')
def blacklist_stats():
    """取得黑名單統計資訊"""
    from jwt_auth_middleware import get_blacklist_statistics
    stats = get_blacklist_statistics()
    return flask.jsonify({"blacklist_statistics": stats})

@app.route('/cleanup_blacklist')
def cleanup_blacklist():
    """清理過期的黑名單 tokens"""
    from jwt_auth_middleware import cleanup_expired_blacklist_tokens
    cleaned_count = cleanup_expired_blacklist_tokens()
    return flask.jsonify({"cleaned_tokens": cleaned_count})

if __name__ == '__main__':
    import threading
    import time
    import requests

    # 初始化黑名單系統
    print("初始化黑名單系統...")
    success = initialize_blacklist_system()
    if success:
        print("✅ 黑名單系統初始化成功")
    else:
        print("❌ 黑名單系統初始化失敗")

    # 啟動 Flask 伺服器（背景執行）
    def run_app():
        app.run(port=5001, debug=False)
    server = threading.Thread(target=run_app, daemon=True)
    server.start()
    time.sleep(1)  # 等待伺服器啟動

    base = 'http://127.0.0.1:5001'
    s = requests.Session()

    print("[1] 註冊...")
    r = s.post(f'{base}/register', json={"email": "test@example.com", "password": "abc123"})
    print(r.json())

    print("[2] 登入...")
    r = s.post(f'{base}/login', json={"email": "test@example.com", "password": "abc123"})
    print(r.json())
    token = r.json().get('access_token')

    print("[3] 訪問受保護路由 (應該成功)...")
    r = s.get(f'{base}/protected', headers={"Authorization": f"Bearer {token}"})
    print(r.json())

    print("[4] 登出 (token 進黑名單)...")
    r = s.post(f'{base}/logout', headers={"Authorization": f"Bearer {token}"})
    print(r.json())

    print("[5] 再次訪問受保護路由 (應該失敗)...")
    r = s.get(f'{base}/protected', headers={"Authorization": f"Bearer {token}"})
    print(r.json())

    print("[6] 查詢 token 是否在黑名單...")
    r = s.post(f'{base}/is_blacklisted', json={"token": token})
    print(r.json())

    print("[7] 查看黑名單統計...")
    r = s.get(f'{base}/blacklist_stats')
    print(r.json())

    print("[8] 清理過期 tokens...")
    r = s.get(f'{base}/cleanup_blacklist')
    print(r.json())

    print("測試結束！")
    # 關閉 Flask 伺服器（Ctrl+C 結束即可）