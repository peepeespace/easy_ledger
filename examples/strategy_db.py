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


res = requests.get('http://127.0.0.1:8000/api/user/?username=ppark9553&email=ppark9553@gmail.com')
result = res.json()['results'][0]
user_id = result['id']
print(user_id)


# data = {
#     'user': user_id,
#     'name': 'ledger_1'
# }
#
# res = requests.post('http://127.0.0.1:8000/api/ledger/', data=data, headers=header)
# print(res.json())

res = requests.get('http://127.0.0.1:8000/api/user/2/', headers=header)
result = res.json()
print(result)



