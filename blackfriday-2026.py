#!/usr/bin/env python3
"""Black Friday 2026 : promos sur 8 produits + activation collection."""
import json, shutil, copy

# --- Backup ---
for f in ("products.json", "collections.json"):
    shutil.copy(f, f + ".bak-bf")

# --- Produits en promo : id -> prix promo ---
PROMOS = {
    "halloween-hooded-blanket": 27.99,      # 39.99 -> -30%
    "personalised-scented-candle": 11.50,   # 14.50 -> -21%
    "wool-winter-scarf": 27.99,             # 34.99 -> -20%
    "thermal-touchscreen-gloves": 37.99,    # 49.99 -> -24%
    "fleece-throw-blanket": 17.99,          # 24.99 -> -28%
    "noel-arbre-mural-bois": 27.99,         # 34.99 -> -20%
    "noel-boule-photo-a": 9.99,             # 12.99 -> -23%
    "personalised-halloween-tapestry": 11.99, # 15.99 -> -25%
}

# --- products.json ---
p = json.load(open("products.json"))
prods = p if isinstance(p, list) else p["products"]
changed = []
for prod in prods:
    pid = prod["id"]
    if pid in PROMOS:
        prod["promo"] = PROMOS[pid]
        colls = prod.setdefault("collections", [])
        if "black-friday" not in colls:
            colls.append("black-friday")
        changed.append(pid)
    else:
        prod.pop("promo", None)  # nettoyage (aucun autre produit n'en a)
json.dump(p, open("products.json", "w"), ensure_ascii=False, indent=1)

# --- collections.json : activer black-friday ---
c = json.load(open("collections.json"))
cols = c if isinstance(c, list) else c["collections"]
for col in cols:
    if col.get("slug") == "black-friday":
        col["actif"] = True
json.dump(c, open("collections.json", "w"), ensure_ascii=False, indent=1)

print("Produits en promo:", len(changed))
for pid in changed:
    print(" -", pid)
