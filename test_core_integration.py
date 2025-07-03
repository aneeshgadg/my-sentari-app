"""
Test script to verify core pipeline integration
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_user_123"

def test_core_health():
    """Test core health endpoint"""
    print("Testing core health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/core/health")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success') and data.get('core_available'):
            print("✅ Core pipeline is available")
            return True
        else:
            print("❌ Core pipeline is not available")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_process_transcript():
    """Test transcript processing endpoint"""
    print("\nTesting transcript processing endpoint...")
    
    # Test data
    test_data = {
        "transcript": "I'm feeling really excited about my new painting project! The colors are just amazing and I can't wait to see how it turns out.",
        "meta": {
            "device": "mobile",
            "silence_ms": 1000,
            "entry_id": "test_entry_456"
        }
    }
    
    try:
        # Note: This would normally require authentication
        # For testing, we'll just check if the endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/core/process-transcript",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint exists (authentication required as expected)")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Transcript processing successful")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Transcript processing failed: {e}")
        return False

def test_backend_core_library():
    """Test the backend-core library directly"""
    print("\nTesting backend-core library directly...")
    
    try:
        import sys
        import os
        
        # Add backend-core to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend-core'))
        
        from backend_core import process_transcript, TranscriptMeta
        import asyncio
        
        # Test data
        user_id = "test_user_123"
        transcript = "I'm feeling really excited about my new painting project!"
        meta = TranscriptMeta(
            timestamp="2024-01-15T10:30:00Z",
            device="mobile",
            entry_id="test_entry_456"
        )
        
        # Process transcript
        result = asyncio.run(process_transcript(user_id, transcript, meta))
        
        print(f"✅ Library test successful")
        print(f"Response: {result.response_text}")
        print(f"Profile updated: {result.updated_profile.user_id}")
        print(f"Debug logs: {len(result.debug_log)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Library test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Core Pipeline Integration")
    print("=" * 50)
    
    # Test 1: Core health
    health_ok = test_core_health()
    
    # Test 2: Backend core library
    library_ok = test_backend_core_library()
    
    # Test 3: API endpoint (if health check passed)
    api_ok = False
    if health_ok:
        api_ok = test_process_transcript()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Core Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Library Test: {'✅ PASS' if library_ok else '❌ FAIL'}")
    print(f"API Endpoint: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if health_ok and library_ok:
        print("\n🎉 Core pipeline integration is working!")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 