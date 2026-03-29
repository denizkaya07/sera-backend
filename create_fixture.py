import json
import random
from datetime import datetime

data = []
pk = 1

# ---------------- USERS ----------------
users = []

def create_user(role, i):
    global pk
    user = {
        "model": "users.user",
        "pk": pk,
        "fields": {
            "username": f"{role}{i}",
            "password": "pbkdf2_sha256$260000$testhash",
            "role": role,
            "first_name": f"{role.capitalize()}{i}",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False
        }
    }
    pk += 1
    return user

# 100 çiftçi
for i in range(100):
    users.append(create_user("farmer", i))

# 50 danışman
for i in range(50):
    users.append(create_user("consultant", i))

# 10 bayi
for i in range(10):
    users.append(create_user("dealer", i))

# 4 üretici
for i in range(4):
    users.append(create_user("producer", i))

data += users

# ---------------- FARMS ----------------
farms = []
farm_pk = 1

farmer_ids = [u["pk"] for u in users if u["fields"]["role"] == "farmer"]

for i in range(180):
    farms.append({
        "model": "farms.farm",
        "pk": farm_pk,
        "fields": {
            "name": f"Elmalı İşletme {i}",
            "owner": random.choice(farmer_ids),
            "city": "Antalya",
            "district": "Elmalı",
            "soil_analysis": {
                "pH": round(random.uniform(5.5, 7.5), 1),
                "N": random.randint(10, 50),
                "P": random.randint(5, 30),
                "K": random.randint(5, 30)
            }
        }
    })
    farm_pk += 1

data += farms

# ---------------- PRODUCTS ----------------
products = []
product_pk = 1

for i in range(500):
    products.append({
        "model": "products.product",
        "pk": product_pk,
        "fields": {
            "name": f"İlaç{i}",
            "type": "ilac"
        }
    })
    product_pk += 1

for i in range(500):
    products.append({
        "model": "products.product",
        "pk": product_pk,
        "fields": {
            "name": f"Gübre{i}",
            "type": "gubre"
        }
    })
    product_pk += 1

data += products

# ---------------- PRESCRIPTIONS ----------------
prescriptions = []
pres_pk = 1

consultant_ids = [u["pk"] for u in users if u["fields"]["role"] == "consultant"]

for farm in farms:
    for _ in range(random.randint(1, 3)):
        prescriptions.append({
            "model": "prescriptions.prescription",
            "pk": pres_pk,
            "fields": {
                "farm": farm["pk"],
                "created_by": random.choice(consultant_ids),
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "details": {
                    "ilaclar": [f"İlaç{random.randint(0,499)}" for _ in range(2)],
                    "gubreler": [f"Gübre{random.randint(0,499)}" for _ in range(2)]
                }
            }
        })
        pres_pk += 1

data += prescriptions

# ---------------- SAVE ----------------
with open("db_fixture.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ db_fixture.json hazır!")