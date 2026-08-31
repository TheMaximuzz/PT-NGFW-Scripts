import requests
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
obj_num = 2000 #enter the required number of objects
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

url = f"https://{mgmt_ip}/api/v2/ListNetworkObjects"
payload_list = {"deviceGroupId": global_gr_id, "objectKinds": ["OBJECT_NETWORK_KIND_IPV4_ADDRESS"], "offset": 0, "limit": 10000}
response = requests.post(url, json=payload_list, headers=headers, cookies=response_auth.cookies, verify=False)
if response.status_code == 200:
    data = response.json()
    dest_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("Dest")]
    src_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("Source")]
    print(f"Found {len(src_objects)} Source and {len(dest_objects)} Dest objects")
else:
    print(f"Error fetching IPs: {response.status_code} - {response.text}")
    exit(1)

url = f"https://{mgmt_ip}/api/v2/ListServices"
payload_list = {"deviceGroupId": global_gr_id, "objectOriginKinds": ["OBJECT_ORIGIN_KIND_CUSTOM"], "offset": 0, "limit": 10000}
response = requests.post(url, json=payload_list, headers=headers, cookies=response_auth.cookies, verify=False)
if response.status_code == 200:
    data = response.json()
    id_dict_services = [obj["id"] for obj in data["services"]]
    print(f"Found {len(id_dict_services)} custom services")
else:
    print(f"Error fetching Services: {response.status_code} - {response.text}")
    exit(1)

url = f"https://{mgmt_ip}/api/v2/ListZones"
payload_list = {"offset": 0, "limit": 10000}
response = requests.post(url, json=payload_list, headers=headers, cookies=response_auth.cookies, verify=False)
if response.status_code == 200:
    data = response.json()
    zones = [item["id"] for item in data["zones"] if not item["name"].startswith("Local")]
    print(f"Found {len(zones)} usable zones")
else:
    print(f"Error fetching Zones: {response.status_code} - {response.text}")
    exit(1)

possible_action = ["SECURITY_RULE_ACTION_DROP", "SECURITY_RULE_ACTION_ALLOW"]
possible_log = ["SECURITY_RULE_LOG_MODE_AT_SESSION_END", "SECURITY_RULE_LOG_MODE_AT_RULE_HIT"]

def create_security_rules():
    url_serv = f"https://{mgmt_ip}/api/v2/CreateSecurityRule"
    for i in range(obj_num):
        payload_rule = {
            "deviceGroupId": global_gr_id,
            "precedence": "pre",
            "position": i + 1,
            "enabled": True,
            "name": f"Random_Rule_{i}",
            "description": "",
            "sourceZone": {"kind": "RULE_KIND_LIST", "objects": {"array": [random.choice(zones)]}},
            "destinationZone": {"kind": "RULE_KIND_LIST", "objects": {"array": [random.choice(zones)]}},
            "sourceAddr": {"kind": "RULE_KIND_LIST", "objects": {"array": [random.choice(src_objects)]}},
            "destinationAddr": {"kind": "RULE_KIND_LIST", "objects": {"array": [random.choice(dest_objects)]}},
            "sourceUser": {"kind": "RULE_USER_KIND_ANY", "objects": {}},
            "service": {"kind": "RULE_KIND_LIST", "objects": {"array": [random.choice(id_dict_services)]}},
            "application": {"kind": "RULE_KIND_ANY", "objects": {}},
            "urlCategory": {"kind": "RULE_KIND_ANY", "objects": {}},
            "action": random.choice(possible_action),
            "logMode": random.choice(possible_log)
        }
        response_ser = requests.post(url_serv, json=payload_rule, headers=headers, verify=False, cookies=response_auth.cookies)
        print(f"Created Random_Rule_{i}: {response_ser.json()}")

create_security_rules()