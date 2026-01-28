import requests
import json
import os

BASE_URL = "http://localhost:8080"

def test_health():
    print("\nTesting /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_single_correct():
    print("\nTesting /correct (single)...")
    payload = {
        "text": "Mosetsana o apea dijo.",
        "language": "tn"
    }
    try:
        response = requests.post(f"{BASE_URL}/correct", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_batch_correct():
    print("\nTesting /batch-correct...")
    
    # Create a dummy batch file
    batch_data = [
        {
            "id": "test_001",
            "text": "Mosetsana o apea dijo.",
            "lang": "tn"
        },
        {
            "id": "test_002",
            "text": "Umfana ufunda incwadi.",
            "lang": "zu"
        }
    ]
    
    filename = "temp_test_batch.json"
    with open(filename, "w") as f:
        json.dump(batch_data, f)
    
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "application/json")}
            response = requests.post(f"{BASE_URL}/batch-correct", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    print("Ensure the app is running locally on port 8080 before running this test.")
    # In a real scenario, we might start the app here, but for this environment, 
    # we assume the user might run it or we rely on unit tests. 
    # However, since I cannot start a background server easily and keep it running for the test 
    # in this environment without blocking, I will simulate the app logic or just ask the user to run it.
    
    # Wait! I can't easily run the server and test it in the same script in this environment 
    # because run_command is blocking or async but I need to coordinate.
    # Actually, I can use the python -c trick to run a simple test against the code directly 
    # if I import the app, rather than making network requests.
    pass
