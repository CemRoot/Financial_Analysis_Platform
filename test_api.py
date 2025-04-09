import requests
import json
import sys

def test_login_and_fetch_stock_data():
    """
    Test login and fetch stock data to verify API connectivity
    """
    print("Starting API test...")
    
    # 1. Login to get a valid token
    login_url = "http://localhost:8002/api/accounts/direct-login/"
    login_data = {
        "email": "test@example.com",  # Replace with a valid user email
        "password": "password123"      # Replace with a valid password
    }
    
    try:
        print(f"Attempting login to {login_url}...")
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()
        
        response_data = login_response.json()
        print("Login successful!")
        
        # Extract token from response
        token = response_data.get('access') or response_data.get('token')
        if not token:
            print("Login succeeded but no token was received!")
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            return
            
        print(f"Token received: {token[:10]}...")
        
        # 2. Use token to fetch historical stock data
        symbol = "AAPL"
        period = "1mo"
        interval = "1d"
        
        stock_url = f"http://localhost:8002/api/stocks/{symbol}/historical/?period={period}&interval={interval}"
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\nFetching stock data from {stock_url}...")
        stock_response = requests.get(stock_url, headers=headers)
        stock_response.raise_for_status()
        
        stock_data = stock_response.json()
        data_length = len(stock_data)
        
        print(f"Successfully retrieved {data_length} data points for {symbol}!")
        print(f"First data point: {json.dumps(stock_data[0], indent=2)}")
        print(f"Last data point: {json.dumps(stock_data[-1], indent=2)}")
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        print(f"Response status code: {e.response.status_code}")
        print(f"Response content: {e.response.text}")
    
    except Exception as e:
        print(f"Error occurred: {e}")
    
    return False

if __name__ == "__main__":
    success = test_login_and_fetch_stock_data()
    sys.exit(0 if success else 1)
