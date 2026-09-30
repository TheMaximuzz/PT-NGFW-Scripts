# PT NGFW v1.11 Scripts

## Requirements
```
pip3 install requests ipaddress
```

## Setup
Update these variables in every script:
```python
mgmt_ip = "YOUR_MGMT_IP"
mgmt_login = "YOUR_LOGIN"
mgmt_pass = "YOUR_PASSWORD"
```

## Run order
Scripts depend on each other — run in this exact order:

```
python3 random_ip.py          # Step 1: Creates N network objects (Source/Dest)
python3 random_service.py     # Step 2: Creates N services (TCP/UDP ports)
python3 random_rules.py       # Step 3: Creates N firewall rules referencing Steps 1 & 2
python3 gen_ip_dnat_v2.py     # Step 4: Creates N dst_ and N trans_ IP objects for NAT
python3 gen_rules_dnat_v2.py  # Step 5: Creates N DNAT rules mapping dst_ -> trans_
python3 delete_pre_acl.py     # Deletes all ACL rules in pre section
python3 delete_pre_nat.py     # Deletes all nat rules in pre section
```
