import datetime
import requests
from pprint import pprint

print('RAW:\n------------------------------')
query = 'ray_num_events_processed'
response = requests.get('http://localhost:9090/api/v1/query', params={
    'query': query
}).json()

result = response.get('data').get('result')
pprint(result)
value = result[0].get('value')[1]
ts = result[0].get('value')[0]
dt = datetime.datetime.fromtimestamp(ts)

print(f'latest:\n    time: {dt}\n    value: {value}')

print('RATE:\n------------------------------')
query = 'avg_over_time(ray_process_time[1m])'
response = requests.get('http://localhost:9090/api/v1/query', params={
    'query': query
}).json()

result = response.get('data').get('result')
pprint(result)
value = result[0].get('value')[1]
ts = result[0].get('value')[0]
dt = datetime.datetime.fromtimestamp(ts)

print(f'latest:\n    time: {dt}\n    value: {value}')
