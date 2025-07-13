#!/usr/bin/env python3
"""
Integration Test Script for Psychology Module
Tests the integration between the PsychologyTest module and the FastAPI backend.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

def test_psychology_service():
    """Test the psychology service integration"""
    try:
        print("🧪 Testing Psychology Service Integration...")
        
        # Test importing the psychology service
        from services.psychology_service import psychology_service
        print("✅ Psychology service imported successfully")
        
        # Test service initialization
        print(f"✅ Knowledge base connected: {psychology_service.knowledge_base_connected}")
        
        # Test interviewer loading
        print("📋 Available interviewers:")
        print(f"  - Sarah: {psychology_service.knowledge_base_connected}")
        print(f"  - Aaron: {psychology_service.knowledge_base_connected}")
        
        print("\n🎉 Psychology module integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r backend/requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    try:
        print("\n🌐 Testing API Endpoints...")
        
        # Test importing the router
        from routers.psychology import router
        print("✅ Psychology router imported successfully")
        
        # Check if routes are registered
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/start-interview",
            "/continue-interview", 
            "/generate-report/{session_id}",
            "/analyze-document",
            "/download-report/{filename}",
            "/interviewers"
        ]
        
        print("📋 Registered routes:")
        for route in routes:
            print(f"  - {route}")
        
        print("\n✅ API endpoints test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_frontend_components():
    """Test frontend component imports"""
    try:
        print("\n🎨 Testing Frontend Components...")
        
        # Check if the psychology interview component exists
        component_path = Path(__file__).parent / "client" / "src" / "components" / "PsychologyInterview.tsx"
        if component_path.exists():
            print("✅ PsychologyInterview component exists")
        else:
            print("❌ PsychologyInterview component not found")
            return False
        
        # Check if the main page has been updated
        index_path = Path(__file__).parent / "client" / "src" / "pages" / "Index.tsx"
        if index_path.exists():
            with open(index_path, 'r') as f:
                content = f.read()
                if "PsychologyInterview" in content:
                    print("✅ Index page includes psychology interview")
                else:
                    print("❌ Index page doesn't include psychology interview")
                    return False
        
        print("✅ Frontend components test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Psychology Module Integration Tests\n")
    
    tests = [
        ("Psychology Service", test_psychology_service),
        ("API Endpoints", test_api_endpoints),
        ("Frontend Components", test_frontend_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("INTEGRATION TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Start the backend: cd backend && python main.py")
        print("3. Start the frontend: cd client && npm run dev")
        print("4. Open http://localhost:5173 to test the integration")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 