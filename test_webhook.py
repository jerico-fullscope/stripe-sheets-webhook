"""
Test script to simulate Stripe webhook events locally
Run this after starting your Flask app to test the integration
"""

import requests
import json
import time
import hmac
import hashlib

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
WEBHOOK_SECRET = "whsec_test_secret"  # Replace with your actual secret from .env

def generate_stripe_signature(payload, secret):
    """Generate a valid Stripe signature for testing"""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def test_new_customer():
    """Test creating a new customer"""
    print("\n" + "="*60)
    print("TEST 1: New Customer - Should create new row")
    print("="*60)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_test_new_12345",
                "subscription": "sub_test_12345",
                "amount_total": 99900,  # $999.00 in cents
                "currency": "usd"
            }
        }
    }

    payload = json.dumps(event)
    signature = generate_stripe_signature(payload, WEBHOOK_SECRET)

    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": signature
    }

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ New customer test passed!")
        else:
            print("❌ New customer test failed!")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_existing_customer():
    """Test updating an existing customer"""
    print("\n" + "="*60)
    print("TEST 2: Existing Customer - Should update Status & Timestamp")
    print("="*60)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_RK1GEaHIp03TRT",  # FullScope Services Inc. from your sheet
                "subscription": "sub_updated_67890",
                "amount_total": 149900,  # $1499.00 in cents
                "currency": "usd"
            }
        }
    }

    payload = json.dumps(event)
    signature = generate_stripe_signature(payload, WEBHOOK_SECRET)

    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": signature
    }

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ Existing customer test passed!")
        else:
            print("❌ Existing customer test failed!")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_invalid_signature():
    """Test webhook signature validation"""
    print("\n" + "="*60)
    print("TEST 3: Invalid Signature - Should reject request")
    print("="*60)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_test_invalid",
                "subscription": "sub_test_invalid",
                "amount_total": 50000,
                "currency": "usd"
            }
        }
    }

    payload = json.dumps(event)

    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "t=123456789,v1=invalid_signature"
    }

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 400:
            print("✅ Invalid signature test passed!")
        else:
            print("❌ Invalid signature test failed!")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Health Check - Should return healthy status")
    print("="*60)

    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200 and response.json().get('status') == 'healthy':
            print("✅ Health check test passed!")
        else:
            print("❌ Health check test failed!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Stripe Webhook Integration Test Suite")
    print("="*60)
    print("\nMake sure your Flask app is running on localhost:5000")
    print("Update WEBHOOK_SECRET in this file to match your .env")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)

    # Run all tests
    test_health_endpoint()
    test_new_customer()
    test_existing_customer()
    test_invalid_signature()

    print("\n" + "="*60)
    print("Test Suite Complete!")
    print("="*60)
    print("\nCheck your Google Sheet to verify:")
    print("1. New customer row was created")
    print("2. Existing customer Status and Timestamp were updated")
    print("3. No duplicate rows were created")
