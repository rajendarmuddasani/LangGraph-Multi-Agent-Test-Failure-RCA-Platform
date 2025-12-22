#!/usr/bin/env python
"""
Test the RCA platform end-to-end
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_submit_rca():
    """Test RCA submission"""
    print("\n📤 Testing RCA Submission...")
    payload = {
        "lot_id": "TEST_LOT_001",
        "wafer_id": "W01",
        "bin": 3,
        "priority": "high",
        "user_id": "test_user@example.com"
    }
    
    try:
        response = requests.post(f"http://localhost:8000/api/v1/rca/submit", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 202:
            print(f"✅ RCA submitted! Session ID: {data.get('session_id')}")
            return data.get('session_id')
        else:
            print(f"❌ RCA submission failed")
            return None
    except Exception as e:
        print(f"❌ RCA submission error: {e}")
        return None

def test_rca_status(session_id):
    """Test RCA status check"""
    print(f"\n📊 Testing RCA Status for {session_id}...")
    try:
        response = requests.get(f"http://localhost:8000/api/v1/rca/{session_id}/status", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Multi-Agent RCA Platform Test Suite")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Backend is not running! Start it with: venv/bin/python start_backend.py")
        exit(1)
    
    print("\n✅ Backend is healthy!")
    
    # Test 2: Submit RCA
    session_id = test_submit_rca()
    if not session_id:
        print("\n⚠️  RCA submission failed, but backend is running")
        exit(1)
    
    # Test 3: Check Status
    time.sleep(2)  # Give it a moment to process
    test_rca_status(session_id)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print(f"\n📝 To check results, visit: http://localhost:8000/api/v1/rca/{session_id}/results")
    print(f"📚 API Docs: http://localhost:8000/docs")
