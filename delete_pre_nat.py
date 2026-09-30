import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- НАСТРОЙКИ ---
mgmt_ip = "UR_MGMT_SERVER'S_IP"
mgmt_login = "admin"
mgmt_pass = "MGMT_SERVER'S_Web_GUI_PASS"
obj_num = 500  # Максимальное количество запрашиваемых правил
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
        cookies = response_auth.cookies
        
        url_groups = f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
        r = requests.post(url_groups, json={"deviceGroupId": "global"}, headers=headers, verify=False, cookies=cookies)
        
        if r.status_code == 200:
            global_gr_id = r.json()["groups"][0]["id"]
            print(f"Target group ID: {global_gr_id}")
        else:
            print(f"Failed to get device groups: {r.text}")
            exit(1)
    else:
        print(f"Authentication failed: {response_auth.text}")
        exit(1)


def get_nat_rule_ids():
    url = f"https://{mgmt_ip}/api/v2/ListNatRules"
    payload = {
        "deviceGroupId": global_gr_id, 
        "offset": 0, 
        "limit": obj_num,
        "precedence": "pre"
    }
    
    resp = requests.post(url, json=payload, headers=headers, cookies=cookies, verify=False)
    
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        
        print(f"Total pre NAT rules fetched: {len(items)}")
        
        # Собираем ID всех правил без фильтрации по имени
        matched_ids = [item["id"] for item in items if "id" in item]
        
        return matched_ids
    else:
        print(f"Error fetching NAT rules: HTTP {resp.status_code} - {resp.text}")
        exit(1)


def delete_dnat_rules():
    auth()
    nat_rule_ids = get_nat_rule_ids()
    
    if not nat_rule_ids:
        print("No pre NAT rules found to delete.")
        return

    print(f"\nFound {len(nat_rule_ids)} rules to delete. Starting process...")
    url = f"https://{mgmt_ip}/api/v2/DeleteNatRule"
    
    deleted_count = 0
    for rule_id in nat_rule_ids:
        payload = {
            "deviceGroupId": global_gr_id,
            "id": rule_id
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, verify=False, cookies=cookies)
            if resp.status_code == 200:
                print(f"Successfully deleted NAT rule ID: {rule_id}")
                deleted_count += 1
            else:
                print(f"Failed to delete rule ID {rule_id}: HTTP {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"Error deleting rule ID {rule_id}: {e}")
            
    print(f"\nOperation complete. Successfully deleted {deleted_count} rules.")


if __name__ == "__main__":
    delete_dnat_rules()
