
import requests
resp = requests.post('https://python-webapp-production.up.railway.app/api/auth/login', json={'email': 'wut@wut.wut', 'password': 'wut@wut.wut'})
if resp.status_code == 200:
    token = resp.json()['access_token']
    sync_resp = requests.post('https://python-webapp-production.up.railway.app/api/wave/sync', headers={'Authorization': f'Bearer {token}'})
    logs = sync_resp.json()['logs']
    print('Products in logs:', 'products' in logs.lower())
    print('Bills in logs:', 'bills' in logs.lower())
    print('Last few lines:')
    for line in logs.split('\n')[-5:]:
        print(line)

