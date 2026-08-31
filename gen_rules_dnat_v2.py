import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
zone_name = "Trusted"
obj_num = 500 #enter the required number of objects
precedence = "pre"
headers = {"Content-Type": "application/json"}


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

def get_ip_objects():
    url = f"https://{mgmt_ip}/api/v2/ListNetworkObjects"
    payload = {"deviceGroupId": global_gr_id, "objectKinds": ["OBJECT_NETWORK_KIND_IPV4_ADDRESS"], "offset": 0, "limit": 10000}
    resp = requests.post(url, json=payload, headers=headers, cookies=cookies, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        dst_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("dst_")]
        trans_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("trans_")]
        print(f"Found {len(dst_objects)} dst and {len(trans_objects)} trans objects")
        return dst_objects, trans_objects
    else:
        print(f"Error fetching IPs: {resp.status_code} {resp.text}")
        exit(1)

def get_zones():
    url = f"https://{mgmt_ip}/api/v2/ListZones"
    payload = {"offset": 0, "limit": 100}
    resp = requests.post(url, json=payload, headers=headers, cookies=cookies, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        return [item["id"] for item in data["zones"] if item["name"].startswith(zone_name)]
    else:
        print(f"Error fetching zones: {resp.status_code} {resp.text}")
        exit(1)

def create_dnat_rules():
    auth()
    zones = get_zones()
    dst_objects, trans_objects = get_ip_objects()
    limit = min(obj_num, len(dst_objects), len(trans_objects))
    if limit == 0:
        print("No matching IP objects found. Run gen_ip_dnat_v2.py first.")
        return

    url = f"https://{mgmt_ip}/api/v2/CreateNatRule"
    for x in range(limit):
        payload = {
            "deviceGroupId": global_gr_id,
            "precedence": precedence,
            "position": x + 1,
            "enabled": True,
            "name": f"dnat_{x}",
            "description": "",
            "srcTranslationType": "NAT_SOURCE_TRANSLATION_TYPE_NONE",
            "dstTranslationType": "NAT_DESTINATION_TRANSLATION_TYPE_ADDRESS_POOL",
            "srcTranslationAddrType": "NAT_SOURCE_TRANSLATION_ADDRESS_TYPE_NONE",
            "sourceZone": {"kind": "RULE_KIND_LIST", "objects": {"array": zones}},
            "destinationZone": {"kind": "RULE_KIND_LIST", "objects": {"array": zones}},
            "sourceAddr": {"kind": "RULE_KIND_ANY", "objects": {}},
            "destinationAddr": {"kind": "RULE_KIND_LIST", "objects": {"array": [dst_objects[x]]}},
            "service": {"kind": "RULE_KIND_ANY", "objects": {}},
            "dstTranslatedAddress": [trans_objects[x]],
            "dstTranslatedPort": 0
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, verify=False, cookies=cookies)
            if resp.status_code == 200:
                print(f"Created DNAT rule {x}")
            else:
                print(f"Failed rule {x}: {resp.status_code} {resp.text[:100]}")
        except Exception as e:
            print(f"Error creating rule {x}: {e}")

create_dnat_rules()