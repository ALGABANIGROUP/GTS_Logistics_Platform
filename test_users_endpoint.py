import requests

# Test the users endpoint
try:
    response = requests.get('http://127.0.0.1:8000/api/v1/admin/users/management')
    print(f'Status: {response.status_code}')
    if response.status_code == 401:
        print('Endpoint exists but requires authentication - this is expected')
    elif response.status_code == 200:
        data = response.json()
        print(f'Total users: {data.get("total_users", 0)}')
        print(f'Users returned: {len(data.get("users", []))}')
        if data.get('users'):
            print('First user sample:', data['users'][0])
    else:
        print(f'Unexpected response: {response.text}')
except Exception as e:
    print(f'Error connecting to server: {e}')
    print('Make sure the backend server is running on port 8000')