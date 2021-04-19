import requests


# Login
req = {
    'email': 'ppark9553@naver.com',
    'password': '123123'
}

res = requests.post('http://127.0.0.1:8000/api/token/', data=req)
result = res.json()


# Auth page access
refresh_token = result['refresh']
access_token = result['access']

header = {
    'Authorization': f'Bearer {access_token}'
}

res = requests.get('http://127.0.0.1:8000/api/history/hello/', headers=header)
print(res.json())


# Refresh token
refresh_req = {
    'refresh': refresh_token
}
res = requests.post('http://127.0.0.1:8000/api/token/refresh/', data=refresh_req)
print(res.json())