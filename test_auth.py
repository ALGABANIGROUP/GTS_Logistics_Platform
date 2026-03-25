import requests

url = 'http://localhost:8000/api/v1/auth/token'
data = {'username': 'admin@example.com', 'password': 'admin123'}

try:
    response = requests.post(url, data=data)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print('Login successful!')
        token = result.get('access_token', 'N/A')
        print(f'Token: {token[:50]}...')
        print(f'User: {result.get("user", {})}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')