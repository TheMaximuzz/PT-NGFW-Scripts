import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#This code delete all acl rulse (10k rules max)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
headers = {"Content-Type": "application/json"}

# 1. Auth
url_login = f"https://{mgmt_ip}/api/v2/Login"
payload_login = {"login": mgmt_login, "password": mgmt_pass}
response_auth = requests.post(url_login, json=payload_login, headers=headers, verify=False)

if response_auth.status_code != 200:
    print("Authentication failed")
    exit(1)
print("Authentication successful")
cookies = response_auth.cookies

# 2. Obtaining the Global device group ID
url_get_groups = f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
response_groups = requests.post(url_get_groups, json={"deviceGroupId": "global"}, headers=headers, verify=False, cookies=cookies)
groups_data = response_groups.json()

if 'groups' in groups_data and len(groups_data['groups']) > 0:
    global_gr_id = groups_data['groups'][0]['id']
    print(f"Target group ID: {global_gr_id}")
else:
    print("Failed to retrieve device groups")
    exit(1)


url_list_rules = f"https://{mgmt_ip}/api/v2/ListSecurityRules"
payload_list_rules = {
    "limit": 10000,
    "offset": 0,
    "deviceGroupId": global_gr_id,
    "precedence": "pre"
}

response_rules = requests.post(url_list_rules, json=payload_list_rules, headers=headers, cookies=cookies, verify=False)

if response_rules.status_code != 200:
    print(f"Error fetching rules: {response_rules.status_code} - {response_rules.text}")
    exit(1)

rules_data = response_rules.json()
items = rules_data.get("items", [])

if not items:
    print("No pre-rules found in the global device group.")
    exit(0)

print(f"Found {len(items)} pre-rules. Starting deletion...")

# 4. Deletion of found rules
url_delete_rule = f"https://{mgmt_ip}/api/v2/DeleteSecurityRule"
deleted_count = 0

for rule in items:
    rule_id = rule.get("id")
    rule_name = rule.get("name", "Unknown")
    
    if not rule_id:
        continue
        
    payload_delete = {"id": rule_id}
    response_delete = requests.post(url_delete_rule, json=payload_delete, headers=headers, cookies=cookies, verify=False)
    
    if response_delete.status_code == 200:
        print(f"Deleted rule: '{rule_name}' (ID: {rule_id})")
        deleted_count += 1
    else:
        print(f"Failed to delete rule '{rule_name}' (ID: {rule_id}): {response_delete.text}")

print(f"Operation complete. Successfully deleted {deleted_count} pre-rules.")