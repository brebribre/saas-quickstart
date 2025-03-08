from controller.shopee.shopee_connector import ShopeeConnector
import webbrowser
import json
import os
from dotenv import load_dotenv
import time
import hmac
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

load_dotenv()

# Global variable to store the authorization code
authorization_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        # Parse the URL and extract the code parameter
        query_components = parse_qs(urlparse(self.path).query)
        authorization_code = query_components.get('code', [None])[0]
        
        # Send response to browser
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authorization successful! You can close this window.")
        
        # Stop the server
        threading.Thread(target=self.server.shutdown).start()

def start_callback_server(port=8000):
    server = HTTPServer(('localhost', port), CallbackHandler)
    server.serve_forever()

def generate_shopee_signature(partner_id, path, timestamp, access_token=None, shop_id=None):
    """Generate Shopee API signature using the correct parameter order."""
    partner_key = os.getenv('SHOPEE_PARTNER_KEY')
    if not partner_key:
        raise ValueError("SHOPEE_PARTNER_KEY not found in .env file")

    # Base string varies depending on the API call
    if access_token and shop_id:
        # For authenticated shop API calls
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        # For authentication URL generation
        base_string = f"{partner_id}{path}{timestamp}"
    
    return hmac.new(
        partner_key.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def test_shopee_auth():
    """Test Shopee authentication flow."""
    # Initialize Shopee connector
    shopee = ShopeeConnector()
    
    # Generate auth URL with proper signature
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    sign = generate_shopee_signature(shopee.partner_id, path, timestamp)
    
    # Build auth URL with production redirect URL
    params = {
        'partner_id': shopee.partner_id,
        'redirect': "https://lobster-app-vch6q.ondigitalocean.app/api/shopee/callback",  # Production callback URL
        'timestamp': timestamp,
        'sign': sign
    }
    
    auth_url = f"{shopee.base_url}{path}?partner_id={params['partner_id']}&redirect={params['redirect']}&timestamp={params['timestamp']}&sign={params['sign']}"
    
    print("\n=== Shopee API Test ===")
    print(f"\nYour Partner ID: {shopee.partner_id}")
    print(f"Base URL: {shopee.base_url}")
    print(f"Redirect URL: {params['redirect']}")
    print(f"\nAuthentication URL: {auth_url}")
    print("\nInstructions:")
    print("1. The authentication URL will open in your browser")
    print("2. You'll be redirected to Shopee's sandbox login page")
    print("3. Use these test credentials:")
    print("   Shop ID: 135062")
    print("   Username: SANDBOX.3539468aac6eb5b81ac7")
    print("   Password: e58cbda6a1b1fc89")
    print("\nImportant Notes:")
    print("- This is an Indonesia region sandbox account (ID)")
    print("- Seller center URL: https://seller.test-stable.shopee.co.id")
    print("- After login, you'll be redirected to the callback URL")
    print("\nOpening authentication URL in your browser...")
    
    webbrowser.open(auth_url)
    
    print("\nAfter being redirected, copy the 'code' parameter from the URL and paste it here:")
    code = input().strip()
    
    if not code:
        print("No code provided. Test ended.")
        return
        
    print("\nExchanging code for access token...")
    # Get access token with proper signature
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    sign = generate_shopee_signature(shopee.partner_id, path, timestamp)
    
    result = shopee.get_access_token(code)
    print("\nAPI Response:")
    print(json.dumps(result, indent=2))
    
    if result and 'access_token' in result:
        print("\nAccess token received successfully!")
        print("You can now use this access token to make authenticated API calls.")
        print("\nAccess Token:", result['access_token'])
        print("Refresh Token:", result.get('refresh_token'))
        print("Shop ID:", result.get('shop_id'))
        print("Merchant ID:", result.get('merchant_id'))
        
        # Automatically get shop info
        print("\n=== Getting Shop Information ===")
        shopee.access_token = result['access_token']
        shop_info = shopee.get_shop_info()
        print("\nShop Info Response:")
        print(json.dumps(shop_info, indent=2))
        
        # Get shop performance
        print("\n=== Getting Shop Performance ===")
        performance = shopee.get_shop_performance()
        print("\nShop Performance Response:")
        print(json.dumps(performance, indent=2))
        
        # Get merchant info
        print("\n=== Getting Merchant Information ===")
        merchant_info = shopee.get_merchant_info()
        print("\nMerchant Info Response:")
        print(json.dumps(merchant_info, indent=2))
    else:
        print("\nFailed to get access token. Please check the error message above.")

def test_with_token(access_token):
    """Test Shopee API endpoints with an existing access token."""
    # Initialize Shopee connector
    shopee = ShopeeConnector()
    shopee.access_token = access_token
    shopee.shop_id = 135062  # Sandbox shop ID
    
    print("\n=== Testing Shopee APIs with Access Token ===")
    print(f"Using access token: {access_token}")
    
    # Get shop info
    print("\n=== Getting Shop Information ===")
    shop_info = shopee.get_shop_info()
    print("\nShop Info Response:")
    print(json.dumps(shop_info, indent=2))
    
    # Get shop performance
    print("\n=== Getting Shop Performance ===")
    performance = shopee.get_shop_performance()
    print("\nShop Performance Response:")
    print(json.dumps(performance, indent=2))
    
    # Get merchant info
    print("\n=== Getting Merchant Information ===")
    merchant_info = shopee.get_merchant_info()
    print("\nMerchant Info Response:")
    print(json.dumps(merchant_info, indent=2))

if __name__ == "__main__":
    # If you have an access token, you can test directly with it
    access_token = input("\nEnter your access token (or press Enter to go through auth flow): ").strip()
    if access_token:
        test_with_token(access_token)
    else:
        test_shopee_auth()