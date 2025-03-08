from controller.shopee.shopee_connector import ShopeeConnector
import json
import requests
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_shopee_signature(partner_id, path, timestamp, access_token, shop_id, partner_key):
    """Generate Shopee API signature using the correct parameter order."""
    # Concatenate parameters in correct order: partner_id + path + timestamp + access_token + shop_id
    base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        partner_key.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def test_shopee_request():
    """Test Shopee API request with correct signature generation."""
    # API parameters
    partner_id = 1270769
    shop_id = 135062
    access_token = "567245696d537548446b5565577a7a43"
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())  # Use current timestamp
    
    # Get partner key from environment
    partner_key = os.getenv('SHOPEE_PARTNER_KEY')
    if not partner_key:
        print("Error: SHOPEE_PARTNER_KEY not found in .env file")
        return
    
    # Generate signature
    sign = generate_shopee_signature(partner_id, path, timestamp, access_token, shop_id, partner_key)
    
    # Build the URL
    host = "https://partner.test-stable.shopeemobile.com"
    url = f"{host}{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}&access_token={access_token}&shop_id={shop_id}"
    
    # Make the request
    response = requests.get(url, headers={}, data={}, allow_redirects=False)
    
    print("\n=== Shopee API Test ===")
    print(f"Timestamp: {timestamp}")
    print(f"Signature: {sign}")
    print(f"URL: {url}")
    print("\nResponse:")
    print(response.text)

def test_shopee_apis():
    # Initialize Shopee connector
    shopee = ShopeeConnector()
    
    # Load access token from previous authentication
    print("\nEnter your access token from the previous authentication:")
    access_token = input().strip()
    
    if not access_token:
        print("No access token provided. Test ended.")
        return
    
    # Set the access token
    shopee.access_token = access_token
    
    # Test different API endpoints
    print("\n=== Testing Shopee APIs ===\n")
    
    # 1. Get Shop Info
    print("1. Getting shop information...")
    shop_info = shopee.get_shop_info()
    print("Shop Info Response:")
    print(json.dumps(shop_info, indent=2))
    print("\n" + "="*50 + "\n")
    
    # 2. Get Shop Performance
    print("2. Getting shop performance...")
    performance = shopee.get_shop_performance()
    print("Shop Performance Response:")
    print(json.dumps(performance, indent=2))
    print("\n" + "="*50 + "\n")
    
    # 3. Get Merchant Info
    print("3. Getting merchant information...")
    merchant_info = shopee.get_merchant_info()
    print("Merchant Info Response:")
    print(json.dumps(merchant_info, indent=2))

def test_signature_calculation():
    """Reverse engineer the signature calculation based on the example."""
    # Known parameters from the example
    partner_id = 1270769
    api_id = 536
    shop_id = 135062
    access_token = "567245696d537548446b5565577a7a43"
    url = "https://partner.test-stable.shopeemobile.com/api/v2/shop/get_shop_info"
    timestamp = 1741285075
    expected_sign = "095fdf0e5ada5af23a29d44c48b5d9d6a624f4d73e8dac5ffc18eb354ce05a67"
    
    # Extract path from URL
    path = "/api/v2/shop/get_shop_info"
    
    # Get partner key from environment
    partner_key = os.getenv('SHOPEE_PARTNER_KEY')
    if not partner_key:
        print("Error: SHOPEE_PARTNER_KEY not found in .env file")
        return
    
    print("=== Signature Reverse Engineering ===")
    print("Parameters:")
    print(f"partner_id: {partner_id}")
    print(f"path: {path}")
    print(f"timestamp: {timestamp}")
    print(f"access_token: {access_token}")
    print(f"shop_id: {shop_id}")
    print(f"Expected signature: {expected_sign}")
    
    # Try different base string combinations
    test_strings = [
        # Test 1: Original format from docs
        f"{partner_id}{path}{timestamp}",
        
        # Test 2: Include access_token
        f"{partner_id}{path}{timestamp}{access_token}",
        
        # Test 3: Include shop_id
        f"{partner_id}{path}{timestamp}{shop_id}",
        
        # Test 4: All parameters
        f"{partner_id}{path}{timestamp}{access_token}{shop_id}",
        
        # Test 5: Different order
        f"{partner_id}{access_token}{path}{timestamp}{shop_id}",
        
        # Test 6: Just URL parameters in order
        f"{partner_id}{timestamp}{access_token}{shop_id}",
        
        # Test 7: Partner ID + Access Token + Path + Timestamp
        f"{partner_id}{access_token}{path}{timestamp}",
        
        # Test 8: Partner ID + Path + Timestamp + Access Token
        f"{partner_id}{path}{timestamp}{access_token}"
    ]
    
    print("\nTesting different base string combinations:")
    for i, base_string in enumerate(test_strings, 1):
        print(f"\nTest {i}:")
        print(f"Base string: {base_string}")
        sign = hmac.new(
            partner_key.encode(),
            base_string.encode(),
            hashlib.sha256
        ).hexdigest()
        print(f"Generated sign: {sign}")
        print(f"Matches expected: {sign == expected_sign}")

if __name__ == "__main__":
    # test_shopee_apis()
    # test_signature_calculation()
    test_shopee_request()  # Run the new clean implementation 