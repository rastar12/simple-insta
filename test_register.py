import json
import urllib.request

def test_register():
    url = "http://127.0.0.1:8000/auth/register"
    data = {
        "email": "test@example.com",
        "password": "password"
    }
    json_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.getcode()}")
            print(f"Body: {response.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()