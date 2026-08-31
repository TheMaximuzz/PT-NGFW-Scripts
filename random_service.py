import requests
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
obj_num = 3000 #enter the required number of objects
headers = {"Content-Type": "application/json"}

url = f"https://{mgmt_ip}/api/v2/Login"
payload = {"login": mgmt_login, "password": mgmt_pass}
response_auth = requests.post(url, json=payload, headers=headers, verify=False)
if response_auth.status_code != 200:
    print("Authentication failed")
    exit(1)
print("Authentication successful")

url = f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
r = requests.post(url, json={"deviceGroupId": "global"}, headers=headers, verify=False, cookies=response_auth.cookies)
response_data = r.json()
if 'groups' in response_data and len(response_data['groups']) > 0:
    global_gr_id = response_data['groups'][0]['id']
    print(f"Target group ID: {global_gr_id}")
else:
    print("Failed to retrieve device groups")
    exit(1)

PROTOCOL_MAP = {"TCP": 6, "UDP": 17}

def create_services():
    url_serv = f"https://{mgmt_ip}/api/v2/CreateService"
    for i in range(obj_num):
        random_port = random.randrange(1024, 65536)
        proto_name = random.choice(list(PROTOCOL_MAP.keys()))
        proto_num = PROTOCOL_MAP[proto_name]
        payload_serv = {
            "name": f"r_{random_port}",
            "deviceGroupId": global_gr_id,
            "description": "",
            "protocol": proto_num,
            "srcPorts": [],
            "dstPorts": [{"singlePort": {"port": random_port}}]
        }
        response_ser = requests.post(url_serv, json=payload_serv, headers=headers, verify=False, cookies=response_auth.cookies)
        print(f"Created {proto_name}:{random_port} -> {response_ser.json()}")

create_services()