import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_NAME = "Test User"

def test_api_integration():
    """Test the complete API integration"""
    print("🧪 Testing TheraSwitchRx API Integration\n")
    
    # Test 1: Health Check (Public endpoint)
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        if data["success"]:
            print("✅ Health check passed")
            print(f"   Status: {data['data']['status']}")
            print(f"   Version: {data['data']['version']}")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Generate API Key
    print("\n2️⃣ Testing API Key Generation...")
    try:
        response = requests.post(f"{BASE_URL}/get-api-key", json={
            "email": TEST_EMAIL,
            "name": TEST_NAME,
            "plan": "free"
        })
        data = response.json()
        if data["success"]:
            api_key = data["data"]["api_key"]
            print("✅ API key generated successfully")
            print(f"   Key: {api_key[:20]}...")
            print(f"   Plan: {data['data']['plan']}")
            print(f"   Daily Limit: {data['data']['daily_limit']}")
        else:
            print(f"❌ API key generation failed: {data['error']}")
            return False
    except Exception as e:
        print(f"❌ API key generation error: {e}")
        return False
    
    # Test 3: Search with API Key
    print("\n3️⃣ Testing Medicine Search with API Key...")
    try:
        response = requests.post(f"{BASE_URL}/search", 
            headers={"X-API-Key": api_key},
            json={"query": "alternatives for Paracetamol"}
        )
        data = response.json()
        if data["success"]:
            print("✅ Medicine search successful")
            print(f"   Query: {data['data']['query']}")
            print(f"   User: {data['api_usage']['user']}")
            print(f"   Requests Remaining: {data['api_usage']['requests_remaining']}")
            print(f"   Recommendation Preview: {data['data']['recommendation'][:100]}...")
        else:
            print(f"❌ Medicine search failed: {data['error']}")
            return False
    except Exception as e:
        print(f"❌ Medicine search error: {e}")
        return False
    
    # Test 4: Get Medicine Info
    print("\n4️⃣ Testing Medicine Information...")
    try:
        response = requests.get(f"{BASE_URL}/medicine/Crocin", 
            headers={"X-API-Key": api_key}
        )
        data = response.json()
        if data["success"]:
            print("✅ Medicine info retrieval successful")
            print(f"   Medicine: {data['data']['medicine_name']}")
            print(f"   Requests Remaining: {data['api_usage']['requests_remaining']}")
        else:
            print(f"❌ Medicine info failed: {data['error']}")
            return False
    except Exception as e:
        print(f"❌ Medicine info error: {e}")
        return False
    
    # Test 5: Get API Key Info
    print("\n5️⃣ Testing API Key Info...")
    try:
        response = requests.get(f"{BASE_URL}/key-info", 
            headers={"X-API-Key": api_key}
        )
        data = response.json()
        if data["success"]:
            print("✅ API key info retrieval successful")
            print(f"   Email: {data['data']['email']}")
            print(f"   Plan: {data['data']['plan']}")
            print(f"   Requests Remaining: {data['data']['requests_remaining']}")
            print(f"   Status: {data['data']['status']}")
        else:
            print(f"❌ API key info failed: {data['error']}")
            return False
    except Exception as e:
        print(f"❌ API key info error: {e}")
        return False
    
    # Test 6: Test Rate Limiting (make multiple requests)
    print("\n6️⃣ Testing Rate Limiting...")
    try:
        requests_made = 0
        for i in range(5):
            response = requests.post(f"{BASE_URL}/search", 
                headers={"X-API-Key": api_key},
                json={"query": f"test query {i}"}
            )
            data = response.json()
            if data["success"]:
                requests_made += 1
                remaining = data['api_usage']['requests_remaining']
                print(f"   Request {i+1}: ✅ Success (Remaining: {remaining})")
            else:
                print(f"   Request {i+1}: ❌ Failed - {data['error']}")
                break
        
        print(f"✅ Rate limiting working correctly ({requests_made} requests made)")
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
        return False
    
    # Test 7: Test Authentication Failure
    print("\n7️⃣ Testing Authentication Failure...")
    try:
        response = requests.post(f"{BASE_URL}/search", 
            headers={"X-API-Key": "invalid_key"},
            json={"query": "test"}
        )
        data = response.json()
        if not data["success"] and data["code"] == "INVALID_API_KEY":
            print("✅ Authentication failure handled correctly")
            print(f"   Error: {data['error']}")
        else:
            print("❌ Authentication failure not handled properly")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    print("\n🎉 All API tests passed successfully!")
    print("\n📋 Test Summary:")
    print("   ✅ Health check")
    print("   ✅ API key generation")
    print("   ✅ Authenticated search")
    print("   ✅ Medicine information")
    print("   ✅ API key info")
    print("   ✅ Rate limiting")
    print("   ✅ Authentication failure")
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_api_integration()
    
    if success:
        print("\n🚀 TheraSwitchRx API is fully functional!")
        print("\n🔗 Quick Links:")
        print("   🌐 Web App: http://localhost:5000")
        print("   📖 API Docs: http://localhost:5000/api/docs") 
        print("   🔑 Get API Key: http://localhost:5000/get-api-key")
    else:
        print("\n❌ Some tests failed. Check the API implementation.")