#!/usr/bin/env python3
"""
Test script to verify authentication endpoints are working correctly
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL
backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:5001')
print(f"Testing backend at: {backend_url}")

# Test the root endpoint
print("\n1. Testing root endpoint...")
try:
    response = requests.get(f"{backend_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test the health endpoint
print("\n2. Testing health endpoint...")
try:
    response = requests.get(f"{backend_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test the Google auth redirect endpoint
print("\n3. Testing Google auth redirect endpoint...")
try:
    response = requests.get(f"{backend_url}/api/auth/google-redirect")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test the login endpoint (without credentials)
print("\n4. Testing login endpoint (should fail without credentials)...")
try:
    response = requests.post(f"{backend_url}/api/auth/login", json={})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test the signup endpoint (without data)
print("\n5. Testing signup endpoint (should fail without data)...")
try:
    response = requests.post(f"{backend_url}/api/auth/signup", json={})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

print("\nTest completed!")