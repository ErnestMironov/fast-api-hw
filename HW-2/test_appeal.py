import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_appeal():
    appeal_data = {
        "surname": "Иванов",
        "name": "Иван",
        "birth_date": "1990-01-01",
        "phone": "+79001234567",
        "email": "ivan@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/appeals/", json=appeal_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_appeals():
    response = requests.get(f"{BASE_URL}/appeals/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_invalid_data():
    invalid_data = {
        "surname": "ivanov",
        "name": "ivan",
        "birth_date": "1990-01-01",
        "phone": "123",
        "email": "invalid-email"
    }
    
    response = requests.post(f"{BASE_URL}/appeals/", json=invalid_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 422

if __name__ == "__main__":
    print("Testing valid appeal creation...")
    test_create_appeal()
    
    print("\nTesting get all appeals...")
    test_get_appeals()
    
    print("\nTesting invalid data validation...")
    test_invalid_data() 