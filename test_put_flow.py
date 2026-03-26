import urllib.request
import json
payload = {"id":"ms_tab_1","label":"Motion Sensor-Flow","nodes":[]}
req = urllib.request.Request("https://piltiflows.piltismart.com/flow/ms_tab_1", data=json.dumps(payload).encode('utf-8'), method='PUT')
req.add_header('Content-Type', 'application/json')
req.add_header('User-Agent', 'curl/8.7.1')
try:
    with urllib.request.urlopen(req) as res:
        print(res.read().decode())
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
