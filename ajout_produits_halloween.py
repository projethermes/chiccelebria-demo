#!/usr/bin/env python3
"""Ajoute 4 produits gothic halloween (vase crâne 3D, Grim Reaper, main démon,
corbeaux noirs) au catalogue ChicCelebria, crée les fiches sourcing, puis build."""
import json, os, subprocess

BASE = "/Users/openclaw/projets/chiccelebria-demo"

def load(n):
    with open(os.path.join(BASE, n), encoding="utf-8") as f:
        return json.load(f)

def save(n, data):
    with open(os.path.join(BASE, n), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

# ---- Nouveaux produits : id, prix_vente, collections, source AliExpress (id, prix, titre)
NEW = [
 dict(id="gothique-vase-crane-3d", prix=32.99, coll=["halloween"], src_id="1005011854630196", src_prix=10.19,
      src_titre="Vase décoratif en forme de crâne 3D, porte-fleurs en résine noire, décoration gothique"),
 dict(id="gothique-grim-reaper", prix=29.99, coll=["halloween"], src_id="1005012776726174", src_prix=8.89,
      src_titre="Statue gothique esthétique effrayante de Grim Reaper assis pour la décoration de la maison"),
 dict(id="gothique-main-demon", prix=29.99, coll=["halloween"], src_id="1005010449718368", src_prix=9.79,
      src_titre="Statue de main divine Berserk de démon créatif, décor gothique d'Halloween, art en résine"),
 dict(id="gothique-corbeaux-noirs", prix=29.99, coll=["halloween"], src_id="1005007580017478", src_prix=9.79,
      src_titre="Corbeaux artificiels réalistes, ornement de fête, décorations d'Halloween"),
]

# ---- Traductions 5 langues (en, es, fr, it, de) — mot-clé filon "gothic decore"
def t(*vals):
    return dict(zip(["en", "es", "fr", "it", "de"], vals))

DATA = {
 "gothique-vase-crane-3d": dict(
   nom=t("Gothic Skull Vase 3D Resin Flower Holder - Halloween Gothic Decore",
         "Jarrón calavera 3D de resina gótica - Decoración gótica de Halloween",
         "Vase crâne 3D en résine - Déco gothique Halloween",
         "Vaso teschio 3D in resina gotica - Decorazione gotica Halloween",
         "Gotische 3D-Schädelvase aus Harz - Gotische Halloween-Deko"),
   desc=t("Statement gothic skull vase in black resin, 3D sculpted with fine detail. Use it as a flower holder, candle display or centrepiece. Bold gothic decore that transforms any shelf or table into a dark masterpiece.",
          "Jarrón gótico de calavera en resina negra, esculpido en 3D con fino detalle. Úsalo como florero, portavelas o centro de mesa. Decoración gótica que convierte cualquier estante en una obra oscura.",
          "Vase gothique en résine noire en forme de crâne, sculpté 3D avec un fin détail. Idéal comme porte-fleurs, support de bougie ou pièce maîtresse. Une déco gothique qui transforme toute étagère en œuvre sombre.",
          "Vaso gotico a teschio in resina nera, scolpito in 3D con dettaglio fine. Perfetto come portafiori, portacandele o centrotavola. Una decorazione gotica che trasforma ogni mensola in un capolavoro oscuro.",
          "Gotische Schädelvase aus schwarzem Harz, 3D-geformt mit feinem Detail. Perfekt als Blumenhalter, Kerzenhalter oder Mittelstück. Gotische Deko, die jedes Regal in ein dunkles Meisterwerk verwandelt.")),
 "gothique-grim-reaper": dict(
   nom=t("Grim Reaper Statue Sitting - Gothic Halloween Decore Figurine",
         "Estatua del Segador sentado - Decoración gótica de Halloween",
         "Statue du Faucheur assis - Figurine déco gothique Halloween",
         "Statua del Mietitore seduto - Decorazione gotica Halloween",
         "Sensenmann-Statue sitzend - Gotische Halloween-Deko Figur"),
   desc=t("Eerie Grim Reaper statue seated with his scythe, crafted in textured resin. A striking gothic decore piece for the living room, shelf or dark academia shelf styling.",
          "Escalofriante estatua del Segador sentado con su guadaña, en resina texturizada. Una pieza de decoración gótica llamativa para el salón o la estantería.",
          "Statue effrayante du Faucheur assis avec sa faux, en résine texturée. Une pièce de déco gothique saisissante pour le salon ou l'étagère.",
          "Statua inquietante del Mietitore seduto con la sua falce, in resina testurizzata. Un pezzo di decorazione gotica sorprendente per il soggiorno o la mensola.",
          "Unheimliche Sensenmann-Statue mit Sense, aus strukturiertem Harz. Ein eindrucksvolles Stück gotischer Deko für Wohnzimmer oder Regal.")),
 "gothique-main-demon": dict(
   nom=t("Gothic Demon Hand Resin Statue - Halloween Gothic Decore Art",
         "Estatua de mano de demonio en resina - Arte decorativo gótico Halloween",
         "Statue main de démon en résine - Art déco gothique Halloween",
         "Statua mano di demone in resina - Arte decorativa gotica Halloween",
         "Gotische Dämonenhand-Statue aus Harz - Gothic Decore Kunst"),
   desc=t("Bold sculpted demon hand statue in black resin with fine claw detail. A collector piece and edgy gothic decore art for desks, shelves and altars.",
          "Audaz estatua de mano de demonio en resina negra con fino detalle de garras. Pieza de colección y arte decorativo gótico para escritorios y estanterías.",
          "Statue de main de démon sculptée en résine noire, détail de griffes fin. Pièce de collection et art déco gothique pour bureaux et étagères.",
          "Audace statua di mano di demone in resina nera con fine dettaglio di artigli. Pezzo da collezione e arte decorativa gotica per scrivanie e mensole.",
          "Kühne Dämonenhand-Statue aus schwarzem Harz mit feinem Klauendetail. Sammlerstück und gotische Deko-Kunst für Schreibtisch und Regal.")),
 "gothique-corbeaux-noirs": dict(
   nom=t("Realistic Black Crows Set - Gothic Halloween Decore Ravens",
         "Set de cuervos negros realistas - Decoración gótica Halloween",
         "Lot de corbeaux noirs réalistes - Déco gothique Halloween",
         "Set di corvi neri realistici - Decorazione gotica Halloween",
         "Set realistischer schwarzer Raben - Gotische Halloween-Deko"),
   desc=t("Set of realistic black crows with detailed feathers and matte finish. Perfect perched on shelves, wreaths or candle displays for a dark gothic decore vibe.",
          "Set de cuervos negros realistas con plumas detalladas y acabado mate. Perfectos en estanterías, coronas o portavelas para un ambiente gótico oscuro.",
          "Lot de corbeaux noirs réalistes, plumes détaillées et finition mate. Parfaits perchés sur étagères, couronnes ou bougeoirs pour une ambiance gothique sombre.",
          "Set di corvi neri realistici con piume dettagliate e finitura opaca. Perfetti su mensole, corone o portacandele per un'atmosfera gotica oscura.",
          "Set realistischer schwarzer Raben mit detaillierten Federn und mattem Finish. Perfekt auf Regalen, Kränzen oder Kerzenhaltern für eine dunkle Gothic-Stimmung.")),
}

# ---- Construction des produits
products = load("products.json")
existing_ids = {p["id"] for p in products}
added = 0
for n in NEW:
    if n["id"] in existing_ids:
        print("SKIP (existe):", n["id"]); continue
    d = DATA[n["id"]]
    products.append({
        "id": n["id"],
        "nom": d["nom"],
        "description": d["desc"],
        "prix": n["prix"],
        "images": [f"assets/sourcing/{n['id']}.jpg"],
        "collections": n["coll"],
        "stock": True,
        "actif": True,
    })
    added += 1
save("products.json", products)
print(f"Produits ajoutés : {added}")

# ---- Fiches sourcing (fiches.json)
fiches = load("fiches.json")
ids_done = {f.get("source", {}).get("lien", "") for f in fiches["fiches"]}
start = len(fiches["fiches"]) + 1
for i, n in enumerate(NEW):
    lien = f"https://fr.aliexpress.com/item/{n['src_id']}.html"
    if lien in ids_done:
        continue
    fiches["fiches"].append({
        "id": f"F-{start+i:03d}",
        "date": "2026-08-28",
        "statut": "en-attente",
        "produit": {
            "nom": DATA[n["id"]]["nom"]["fr"],
            "prix": n["prix"],
            "description": f"Produit {DATA[n['id']]['nom']['fr'].lower()} — à vendre sur Etsy (ChicCelebria) et eBay. Prix de vente calculé pour marge 20-40 % après frais et envoi suivi.",
            "photo": f"assets/sourcing/{n['id']}.jpg",
        },
        "source": {
            "nom": n["src_titre"],
            "prix": n["src_prix"],
            "fournisseur": "AliExpress",
            "photo": f"assets/sourcing/{n['id']}.jpg",
            "lien": lien,
            "lien_label": "Voir la fiche AliExpress",
        },
    })
save("fiches.json", fiches)
print(f"Fiches sourcing : {len(fiches['fiches'])} au total")

# ---- Build
r = subprocess.run(["python3", "build.py"], cwd=BASE, capture_output=True, text=True)
print("BUILD exit:", r.returncode)
print(r.stdout[-800:] if r.stdout else "")
print(r.stderr[-800:] if r.stderr else "")
