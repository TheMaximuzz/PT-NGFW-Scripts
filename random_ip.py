import requests
import random
import ipaddress
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

ip_range_start = ipaddress.IPv4Address('1.0.0.0')
ip_range_end = ipaddress.IPv4Address('9.255.255.255')
rule_name_masks = ["Source", "Dest"]

def create_network_objects():
    url_serv = f"https://{mgmt_ip}/api/v2/CreateNetworkObject"
    for rule_name_mask in rule_name_masks:
        for i in range(obj_num):
            random_ip = str(ipaddress.IPv4Address(random.randint(int(ip_range_start), int(ip_range_end))))
            payload_serv = {
                "name": f"{rule_name_mask}_{random_ip.replace('.', '_')}",
                "deviceGroupId": global_gr_id,
                "description": "Auto-generated network object",
                "value": {"inet": {"inet": f"{random_ip}/32"}}
            }
            response_ser = requests.post(url_serv, json=payload_serv, headers=headers, verify=False, cookies=response_auth.cookies)
            print(f"Created {rule_name_mask}_{random_ip.replace('.', '_')}: {response_ser.json()}")

create_network_objects()