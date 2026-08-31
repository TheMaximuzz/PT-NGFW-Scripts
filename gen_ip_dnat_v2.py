import requests
import ipaddress
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
headers = {"Content-Type": "application/json"}

dst_network = "11.11.224.0/21" #You can change the mask to change the number of addresses objects.
translated_net = "48.0.224.0/21" #You can change the mask to change the number of addresses objects.

global_gr_id = ""
cookies = ""

def auth():
    global global_gr_id, cookies
    url = f"https://{mgmt_ip}/api/v2/Login"
    payload = {"login": mgmt_login, "password": mgmt_pass}
    response_auth = requests.post(url, json=payload, headers=headers, verify=False)
    if response_auth.status_code == 200:
        print("Authentication successful")
        url = f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
        r = requests.post(url, json={"deviceGroupId": "global"}, headers=headers, verify=False, cookies=response_auth.cookies)
        cookies = response_auth.cookies
        global_gr_id = r.json()["groups"][0]["id"]
        print(f"Target group ID: {global_gr_id}")
    else:
        print("Authentication failed")
        exit(1)

def send_ip(net, name_prefix):
    url_create_ip = f"https://{mgmt_ip}/api/v2/CreateNetworkObject"
    created = 0
    skipped = 0
    network = ipaddress.ip_network(net)
    for ip in network.hosts():
        obj_name = f"{name_prefix}_{ip}"
        payload = {
            "name": obj_name,
            "deviceGroupId": global_gr_id,
            "description": "DNAT object",
            "value": {"inet": {"inet": f"{ip}/32"}}
        }
        try:
            resp = requests.post(url_create_ip, headers=headers, json=payload, verify=False, cookies=cookies)
            if resp.status_code == 200:
                created += 1
            elif resp.status_code == 400 and "not unique" in resp.text.lower():
                skipped += 1
            else:
                print(f"Failed {obj_name}: {resp.status_code} {resp.text[:100]}")
        except Exception as e:
            print(f"Request error {obj_name}: {e}")
    print(f"[{name_prefix}] Created: {created}, Skipped: {skipped}")

auth()
send_ip(dst_network, "dst")
send_ip(translated_net, "trans")