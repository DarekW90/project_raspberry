import requests

def check_server():
    url = "http://127.0.0.1:5000"  # Adres lokalny i port serwera Flask
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Server is running! Response: {response.text}")
        else:
            print(f"Server responded with status code: {response.status_code}")
    except requests.ConnectionError:
        print("Failed to connect to the server.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_server()
