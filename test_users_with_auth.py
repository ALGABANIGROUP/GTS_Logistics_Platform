import requests

# Test the users endpoint with authentication
try:
    # First login to get token
    login_response = requests.post('http://127.0.0.1:8000/auth/token', data={
        'username': 'admin@gts.com',
        'password': 'admin123'
    })

    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token')
        print(f'Login successful, got token: {token[:20]}...')

        # Now test the users endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://127.0.0.1:8000/api/v1/admin/users/management', headers=headers)

        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Total users: {data.get("total_users", 0)}')
            print(f'Users returned: {len(data.get("users", []))}')
            if data.get('users'):
                print('Sample user:')
                user = data['users'][0]
                print(f'  ID: {user.get("id")}')
                print(f'  Email: {user.get("email")}')
                print(f'  Role: {user.get("role")}')
                print(f'  Status: {user.get("status")}')
        else:
            print(f'Error: {response.text}')
    else:
        print(f'Login failed: {login_response.status_code} - {login_response.text}')

except Exception as e:
    print(f'Error: {e}')