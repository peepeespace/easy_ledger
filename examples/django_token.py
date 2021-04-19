import requests

req = {
    'email': 'ppark9553@naver.com',
    'password': '123123'
}

res = requests.post('http://127.0.0.1:8000/api-token-auth/', data=req)
print(res)