#!/usr/bin/env python3
"""
Test script to verify the complete authentication flow
"""

import os
import requests
import json
from urllib.parse import urlparse, parse_qs

# Get the backend URL
backend_url = "http://localhost:5001"
print(f"Testing backend at: {backend_url}")

# Test 1: Check if we can access the Google OAuth redirect endpoint
print("\n1. Testing Google OAuth redirect endpoint...")
try:
    response = requests.get(f"{backend_url}/api/auth/google-redirect")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        auth_url = response.json().get('auth_url')
        print(f"   Auth URL: {auth_url}")
        
        # Parse the URL to check its components
        parsed_url = urlparse(auth_url)
        print(f"   Provider: {parsed_url.query}")
        
        # Extract query parameters
        query_params = parse_qs(parsed_url.query)
        provider = query_params.get('provider', [None])[0]
        print(f"   Provider parameter: {provider}")
        
        if provider == 'google':
            print("   ✓ Google OAuth URL is correctly formatted")
        else:
            print("   ✗ Provider is not 'google'")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Check if we can access the me endpoint (should return 401 for unauthenticated users)
print("\n2. Testing /auth/me endpoint (should return 401 for unauthenticated users)...")
try:
    response = requests.get(f"{backend_url}/api/auth/me")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✓ Correctly returns 401 for unauthenticated users")
    else:
        print(f"   ✗ Expected 401, got {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Check if we can access the login endpoint
print("\n3. Testing /auth/login endpoint...")
try:
    response = requests.post(f"{backend_url}/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print("   ✓ Correctly rejects invalid login attempts")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\nTest completed!")