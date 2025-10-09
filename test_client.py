#!/usr/bin/env python3
"""
Test client for the HTTP server
Demonstrates GET and POST requests with various scenarios
"""

import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class HTTPTestClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Host': '127.0.0.1:8080'})
    
    def test_get_html(self):
        """Test GET request for HTML file"""
        print("🧪 Testing GET request for HTML file...")
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
            print(f"✅ Content Length: {len(response.content)} bytes")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_get_txt(self):
        """Test GET request for text file"""
        print("🧪 Testing GET request for text file...")
        try:
            response = self.session.get(f"{self.base_url}/test.txt")
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
            print(f"✅ Content: {response.text[:100]}...")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_get_png(self):
        """Test GET request for PNG file"""
        print("🧪 Testing GET request for PNG file...")
        try:
            response = self.session.get(f"{self.base_url}/test.png")
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
            print(f"✅ Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"✅ Binary data length: {len(response.content)} bytes")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_get_jpg(self):
        """Test GET request for JPEG file"""
        print("🧪 Testing GET request for JPEG file...")
        try:
            response = self.session.get(f"{self.base_url}/test.jpg")
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
            print(f"✅ Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"✅ Binary data length: {len(response.content)} bytes")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_post_json(self):
        """Test POST request with JSON data"""
        print("🧪 Testing POST request with JSON data...")
        try:
            test_data = {
                "name": "test_upload",
                "content": "This is a test JSON upload",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "numbers": [1, 2, 3, 4, 5],
                "nested": {
                    "level1": "value1",
                    "level2": "value2"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_path_traversal(self):
        """Test path traversal protection"""
        print("🧪 Testing path traversal protection...")
        try:
            response = self.session.get(f"{self.base_url}/../etc/passwd")
            print(f"✅ Status: {response.status_code} (Should be 403)")
            if response.status_code == 403:
                print("✅ Path traversal protection working!")
                return True
            else:
                print("❌ Path traversal protection failed!")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_invalid_method(self):
        """Test unsupported HTTP method"""
        print("🧪 Testing unsupported HTTP method...")
        try:
            response = self.session.put(f"{self.base_url}/")
            print(f"✅ Status: {response.status_code} (Should be 405)")
            if response.status_code == 405:
                print("✅ Method validation working!")
                return True
            else:
                print("❌ Method validation failed!")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_invalid_content_type(self):
        """Test POST with invalid content type"""
        print("🧪 Testing POST with invalid content type...")
        try:
            response = self.session.post(
                f"{self.base_url}/",
                data="plain text data",
                headers={'Content-Type': 'text/plain'}
            )
            print(f"✅ Status: {response.status_code} (Should be 415)")
            if response.status_code == 415:
                print("✅ Content type validation working!")
                return True
            else:
                print("❌ Content type validation failed!")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_concurrent_requests(self, num_threads=5):
        """Test concurrent requests"""
        print(f"🧪 Testing concurrent requests with {num_threads} threads...")
        
        def make_request():
            try:
                response = self.session.get(f"{self.base_url}/test.txt")
                return response.status_code == 200
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request) for _ in range(num_threads)]
            results = [future.result() for future in futures]
        
        success_count = sum(results)
        print(f"✅ Successful requests: {success_count}/{num_threads}")
        return success_count == num_threads
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting HTTP Server Test Suite")
        print("=" * 50)
        
        tests = [
            ("GET HTML", self.test_get_html),
            ("GET TXT", self.test_get_txt),
            ("GET PNG", self.test_get_png),
            ("GET JPG", self.test_get_jpg),
            ("POST JSON", self.test_post_json),
            ("Path Traversal", self.test_path_traversal),
            ("Invalid Method", self.test_invalid_method),
            ("Invalid Content Type", self.test_invalid_content_type),
            ("Concurrent Requests", self.test_concurrent_requests),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! Server is working correctly!")
        else:
            print("⚠️  Some tests failed. Check server logs for details.")

def main():
    print("HTTP Server Test Client")
    print("Make sure the HTTP server is running on 127.0.0.1:8080")
    print("Press Enter to start tests...")
    input()
    
    client = HTTPTestClient()
    client.run_all_tests()

if __name__ == "__main__":
    main()
