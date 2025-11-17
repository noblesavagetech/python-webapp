#!/usr/bin/env python3
import requests

# Test if new data types are deployed
resp = requests.post('https://python-webapp-production.up.railway.app/api/auth/login',
                    json={'email': 'wut@wut.wut', 'password': 'wut@wut.wut'})
if resp.status_code == 200:
    token = resp.json()['access_token']
    sync_resp = requests.post('https://python-webapp-production.up.railway.app/api/wave/sync',
                             headers={'Authorization': f'Bearer {token}'})
    if sync_resp.status_code == 200:
        logs = sync_resp.json()['logs']
        has_products = 'products' in logs.lower()
        has_bills = 'bills' in logs.lower()
        print(f'New data types deployed: Products={has_products}, Bills={has_bills}')
        if has_products or has_bills:
            print('SUCCESS! Your app now syncs additional financial data!')
            print('Available: Customers, Invoices, Products, Bills/Expenses')
        else:
            print('Still deploying old version...');