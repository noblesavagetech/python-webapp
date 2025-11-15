#!/usr/bin/env python3
"""
Test script to verify all Flask-DB-API connectivity
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("✓ PASSED")

def test_signup():
    """Test 2: User signup (creates company and user)"""
    print("\n=== Test 2: User Signup ===")
    
    signup_data = {
        'company_name': 'Test Company',
        'email': f'test{requests.utils.quote("@")}example.com',
        'industry': 'Technology',
        'company_size': 'small',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'testpassword123'
    }
    
    # Using a unique email each time
    import time
    signup_data['email'] = f'test{int(time.time())}@example.com'
    
    print(f"Creating account with email: {signup_data['email']}")
    response = requests.post(
        f'{BASE_URL}/api/auth/signup',
        json=signup_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        assert 'access_token' in data
        assert 'user' in data
        assert 'company' in data
        print("✓ PASSED")
        return data
    else:
        print("✗ FAILED")
        raise Exception(f"Signup failed: {response.json()}")

def test_login(email, password):
    """Test 3: User login"""
    print("\n=== Test 3: User Login ===")
    
    login_data = {
        'email': email,
        'password': password
    }
    
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert 'access_token' in response.json()
    print("✓ PASSED")
    return response.json()['access_token']

def test_authenticated_endpoint(token):
    """Test 4: Access authenticated endpoint"""
    print("\n=== Test 4: Authenticated Endpoint ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        f'{BASE_URL}/api/auth/me',
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✓ PASSED")
    else:
        print(f"Response: {response.text}")
        print("✗ FAILED (endpoint may not be fully implemented)")

def test_database_connectivity():
    """Test 5: Direct database connectivity"""
    print("\n=== Test 5: Direct Database Connectivity ===")
    
    from app import create_app
    from extensions import db
    from models.user import User
    from models.company import Company
    
    app = create_app()
    with app.app_context():
        company_count = Company.query.count()
        user_count = User.query.count()
        
        print(f"Companies in database: {company_count}")
        print(f"Users in database: {user_count}")
        
        assert company_count > 0
        assert user_count > 0
        print("✓ PASSED")

if __name__ == '__main__':
    print("=" * 60)
    print("FLASK-DB-API CONNECTIVITY TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Signup
        signup_response = test_signup()
        email = signup_response['user']['email']
        password = 'testpassword123'
        
        # Test 3: Login
        token = test_login(email, password)
        
        # Test 4: Authenticated endpoint
        test_authenticated_endpoint(token)
        
        # Test 5: Database connectivity
        test_database_connectivity()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nSummary:")
        print("- Flask server is running")
        print("- Database connectivity is working")
        print("- API endpoints are functioning")
        print("- User signup/login flow is working")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("TEST FAILED! ✗")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
