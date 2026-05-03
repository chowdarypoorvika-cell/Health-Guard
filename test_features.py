"""
Comprehensive Feature Testing Script for Cybher
Tests all endpoints and features
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"{method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ SUCCESS (Status: {response.status_code})")
                if isinstance(result, dict) and len(result) < 10:
                    print(f"Response: {json.dumps(result, indent=2)}")
                return True
            except:
                print(f"✅ SUCCESS (Status: {response.status_code}) - Non-JSON response")
                return True
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            print(f"Error: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Server not running?")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("CYBHER COMPREHENSIVE FEATURE TEST")
    print("="*60)
    
    results = []
    
    # 1. Root endpoint
    results.append(("Root", test_endpoint("GET", "/", description="Homepage")))
    
    # 2. Stream endpoint (test multiple times)
    print("\nTesting Stream Endpoint (5 packets)...")
    for i in range(5):
        results.append((f"Stream {i+1}", test_endpoint("GET", "/stream", description=f"Stream packet {i+1}")))
        time.sleep(0.5)
    
    # 3. System Stats
    results.append(("System Stats", test_endpoint("GET", "/system-stats", description="System Statistics")))
    
    # 4. Session Stats
    results.append(("Session Stats", test_endpoint("GET", "/session-stats", description="Session Statistics")))
    
    # 5. Threat Intel
    results.append(("Threat Intel", test_endpoint("GET", "/threat-intel", description="Threat Intelligence")))
    
    # 6. Patients
    results.append(("Patients", test_endpoint("GET", "/patients", description="Get All Patients")))
    
    # 7. Current Patient
    results.append(("Current Patient", test_endpoint("GET", "/patients/current", description="Current Patient")))
    
    # 8. Switch Patient
    results.append(("Switch Patient", test_endpoint("POST", "/patients/switch", 
                                                   data={"patient_id": "P002"}, 
                                                   description="Switch to Patient P002")))
    
    # 9. Model Status
    results.append(("Model Status", test_endpoint("GET", "/model/status", description="ML Model Status")))
    
    # 10. Attack Types
    results.append(("Attack Types", test_endpoint("GET", "/attack-types", description="Available Attack Types")))
    
    # 11. Inject Attacks (test all types)
    attack_types = ['spike', 'flatline', 'spoof', 'noise', 'replay', 'mitm']
    for attack_type in attack_types:
        results.append((f"Inject {attack_type}", 
                       test_endpoint("POST", "/inject-attack", 
                                   data={"type": attack_type, "duration": 3},
                                   description=f"Inject {attack_type} attack")))
        time.sleep(0.3)
    
    # 12. Clear Attack
    results.append(("Clear Attack", test_endpoint("POST", "/clear-attack", description="Clear Active Attack")))
    
    # 13. Federated Learning
    results.append(("Federated Learning", 
                   test_endpoint("POST", "/train-fl", 
                               data={"rounds": 3},
                               description="Run Federated Learning (3 rounds)")))
    
    # 14. Model Retrain
    results.append(("Retrain Model", test_endpoint("POST", "/model/retrain", description="Retrain ML Model")))
    
    # 15. Invalid endpoints (should fail gracefully)
    print("\n" + "="*60)
    print("Testing Error Handling...")
    test_endpoint("GET", "/invalid-endpoint", description="Invalid Endpoint (should 404)")
    test_endpoint("POST", "/inject-attack", 
                 data={"type": "invalid"}, 
                 description="Invalid Attack Type (should 400)")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ Failed Tests:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
    
    print("="*60)

if __name__ == "__main__":
    main()

