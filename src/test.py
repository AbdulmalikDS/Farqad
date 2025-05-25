# test_connection.py
import requests

try:
    response = requests.get("http://10.255.255.254:51030/api/tags")
    if response.status_code == 200:
        print("Connection successful!")
        print(response.json())
    else:
        print(f"Connection failed with status code: {response.status_code}")
except Exception as e:
    print(f"Connection error: {e}")