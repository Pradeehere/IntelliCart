from app import app
import json

client = app.test_client()

response = client.get('/api/recommend/user-based/U001')
print("USER-BASED U001 STATUS:", response.status_code)
print("USER-BASED U001 DATA:", response.data.decode('utf-8'))

response = client.get('/api/recommend/item-based/U001')
print("ITEM-BASED U001 STATUS:", response.status_code)
print("ITEM-BASED U001 DATA:", response.data.decode('utf-8'))
