import requests

# Test login with existing user
try:
    r = requests.post('http://127.0.0.1:8000/auth/token', data={
        'username': 'admin@example.com',
        'password': 'admin123'
    })
    print(f'Auth status: {r.status_code}')
    if r.status_code == 200:
        print('Login successful!')
        token_data = r.json()
        token = token_data.get('access_token')
        print(f'Token: {token[:30]}...')

        # Test users endpoint
        headers = {'Authorization': f'Bearer {token}'}
        users_response = requests.get('http://127.0.0.1:8000/api/v1/admin/users/management', headers=headers)
        print(f'Users endpoint status: {users_response.status_code}')
        if users_response.status_code == 200:
            data = users_response.json()
            print(f'Success! Total users: {data.get("total_users", 0)}')
            print(f'Users returned: {len(data.get("users", []))}')
            if data.get('users'):
                print('First user:', data['users'][0])
        else:
            print(f'Users endpoint failed: {users_response.text}')
    else:
        print(f'Login failed: {r.text}')
except Exception as e:
    print(f'Error: {e}')