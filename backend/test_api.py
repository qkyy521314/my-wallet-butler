import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    # 1. 测试注册用户
    print("Testing user registration...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }

    try:
        register_resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Registration response: {register_resp.status_code}")
        if register_resp.status_code == 200:
            print("✓ Registration successful")
        else:
            print(f"✗ Registration failed: {register_resp.text}")
    except Exception as e:
        print(f"✗ Registration error: {e}")

    # 2. 测试登录
    print("\nTesting user login...")
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    try:
        login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login response: {login_resp.status_code}")
        if login_resp.status_code == 200:
            response_data = login_resp.json()
            token = response_data.get('data', {}).get('access_token')
            print(f"✓ Login successful, token: {token[:20]}..." if token else "✗ No token in response")
        else:
            print(f"✗ Login failed: {login_resp.text}")
    except Exception as e:
        print(f"✗ Login error: {e}")

    # 3. 测试获取当前用户信息（需要token）
    print("\nTesting getting current user info...")
    if 'token' in locals() and token:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            me_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"Get user info response: {me_resp.status_code}")
            if me_resp.status_code == 200:
                print("✓ Get user info successful")
            else:
                print(f"✗ Get user info failed: {me_resp.text}")
        except Exception as e:
            print(f"✗ Get user info error: {e}")

if __name__ == "__main__":
    test_api()