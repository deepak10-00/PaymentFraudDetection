import urllib.request
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def wait_for_service():
    print("Waiting for service to be available...")
    for i in range(30):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/docs") as response:
                if response.status == 200:
                    print("Service is UP!")
                    return True
        except Exception:
            pass
        time.sleep(2)
    print("Service timed out.")
    return False

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    jsondata = json.dumps(data).encode('utf-8')
    req.add_header('Content-Length', len(jsondata))
    
    try:
        with urllib.request.urlopen(req, jsondata) as response:
            print(f"Status: {response.status}")
            print(f"Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

def test_legit_transaction():
    print("\nTesting Legitimate Transaction...")
    payload = {
        "Time": 406, "V1": -2.312226542, "V2": 1.951992011, "V3": -1.609850732, "V4": 3.997905588,
        "V5": -0.522187865, "V6": -1.426545318, "V7": -2.537387306, "V8": 1.391657248, "V9": -2.770089273,
        "V10": -2.772272145, "V11": 3.202033207, "V12": -2.899907388, "V13": -0.595221881, "V14": -4.289253782,
        "V15": 0.38972412, "V16": -1.14074718, "V17": -2.830055675, "V18": -0.016822468, "V19": 0.416955705,
        "V20": 0.126910559, "V21": 0.517232371, "V22": -0.035049369, "V23": -0.465211076, "V24": 0.320198199,
        "V25": 0.044519167, "V26": 0.177839798, "V27": 0.261145003, "V28": -0.143275875, "Amount": 0.00
    }
    post_json("/api/process_transaction", payload)

def test_suspicious_transaction():
    print("\nTesting Suspicious Transaction...")
    payload = {
        "Time": 472, "V1": -3.043540624, "V2": -3.157307121, "V3": 1.08846278, "V4": 2.288643618,
        "V5": 1.35980513, "V6": -1.064822523, "V7": 0.325574266, "V8": -0.067793652, "V9": -0.270952836,
        "V10": -0.838586565, "V11": -0.414575448, "V12": -0.50314086, "V13": -0.112648836, "V14": -0.2878846,
        "V15": -0.516953578, "V16": 0.72474261, "V17": -0.883201154, "V18": -0.259094365, "V19": -0.63305379,
        "V20": -0.29344635, "V21": 0.661695925, "V22": 0.43547723, "V23": 1.375965743, "V24": -0.293803152,
        "V25": -0.14538251, "V26": -0.21526691, "V27": -0.549368106, "V28": 0.138203646, "Amount": 529.00
    }
    post_json("/api/process_transaction", payload)

if __name__ == "__main__":
    if wait_for_service():
        test_legit_transaction()
        test_suspicious_transaction()
