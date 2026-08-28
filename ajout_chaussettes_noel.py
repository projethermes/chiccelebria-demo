#!/usr/bin/env python3
"""Ajoute 5 produits (bas vintage tricotés + chaussettes tricot) au catalogue
ChicCelebria, crée les fiches sourcing, puis lance build.py."""
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
 dict(id="noel-bas-vintage-brode", prix=34.99, coll=["christmas", "personalised"], src_id="1005010242140679", src_prix=12.29,
      src_titre="Bas de Noël vintage personnalisé avec nom brodé et lettres personnalisables"),
 dict(id="noel-bas-vintage-sac", prix=36.99, coll=["christmas", "personalised"], src_id="1005010148844332", src_prix=12.89,
      src_titre="Bas de Noël personnalisé vintage avec nom brodé, sac cadeau de vacances"),
 dict(id="noel-bas-prenom-tricote", prix=11.99, coll=["christmas", "personalised"], src_id="1005010245908836", src_prix=3.79,
      src_titre="Bas de Noël tricoté personnalisé avec nom, pour enfants et famille"),
 dict(id="noel-chaussettes-alphabet", prix=11.99, coll=["christmas"], src_id="1005009711495818", src_prix=3.99,
      src_titre="Chaussettes de Noël en tricot avec lettres de l'alphabet, déco de sapin"),
 dict(id="noel-chaussette-torsade-brodee", prix=36.99, coll=["christmas", "personalised"], src_id="1005012924844410", src_prix=12.99,
      src_titre="Chaussette de Noël en tricot torsadé brodée sur mesure avec nom"),
]

# ---- Traductions 5 langues (en, es, fr, it, de)
def t(*vals):
    return dict(zip(["en", "es", "fr", "it", "de"], vals))

DATA = {
 "noel-bas-vintage-brode": dict(
   nom=t("Vintage Personalised Embroidered Christmas Stocking",
         "Calcetín navideño vintage personalizado con nombre bordado",
         "Bas de Noël vintage personnalisé, nom brodé",
         "Calza di Natale vintage personalizzata con nome ricamato",
         "Vintage-Weihnachtsstrumpf personalisiert mit gesticktem Namen"),
   desc=t("Classic knit stocking with your family name embroidered and customisable letters. Timeless fireplace decor, made to keep for years.",
          "Calcetín clásico de punto con el nombre de tu familia bordado y letras personalizables. Decoración de chimenea atemporal, para guardar años.",
          "Bas classique en tricot avec votre nom de famille brodé et lettres personnalisables. Déco de cheminée intemporelle, faite pour durer des années.",
          "Calza classica in maglia con il nome della tua famiglia ricamato e lettere personalizzabili. Decorazione per camino senza tempo, fatta per durare.",
          "Klassischer Strickstrumpf mit gesticktem Familiennamen und personalisierbaren Buchstaben. Zeitlose Kamin-Deko, gemacht für Jahre.")),
 "noel-bas-vintage-sac": dict(
   nom=t("Vintage Embroidered Christmas Stocking with Gift Bag",
         "Calcetín navideño vintage bordado con bolsa de regalo",
         "Bas de Noël vintage brodé avec sac cadeau",
         "Calza di Natale vintage ricamata con sacchetto regalo",
         "Vintage-Weihnachtsstrumpf mit Geschenktasche"),
   desc=t("Embroidered vintage stocking with your name, delivered with a matching gift bag. Ready to gift or to hang on the mantel.",
          "Calcetín vintage bordado con tu nombre, con bolsa de regalo a juego. Listo para regalar o colgar en la chimenea.",
          "Bas vintage brodé à votre nom, livré avec un sac cadeau assorti. Prêt à offrir ou à accrocher à la cheminée.",
          "Calza vintage ricamata con il tuo nome, con sacchetto regalo coordinato. Pronta da regalare o appendere al camino.",
          "Vintage-Strumpf mit gesticktem Namen, inklusive passender Geschenktasche. Fertig zum Verschenken oder Aufhängen.")),
 "noel-bas-prenom-tricote": dict(
   nom=t("Personalised Knitted Christmas Stocking (Kids)",
         "Calcetín navideño de punto personalizado (niños)",
         "Bas de Noël tricoté personnalisé (enfants)",
         "Calza di Natale in maglia personalizzata (bambini)",
         "Personalisierter Strick-Weihnachtsstrumpf (Kinder)"),
   desc=t("Hand-knitted look mini stocking with your child's name. A sweet personalised touch for the family tree or fireplace.",
          "Mini calcetín de aspecto tejido a mano con el nombre de tu hijo. Un toque personal dulce para el árbol o la chimenea.",
          "Mini bas tricoté avec le prénom de votre enfant. Une touche personnelle et douce pour le sapin ou la cheminée.",
          "Mini calza in stile lavorato a mano con il nome del tuo bambino. Un dolce tocco personale per l'albero o il camino.",
          "Mini-Strickstrumpf mit dem Namen Ihres Kindes. Eine süße persönliche Note für Baum oder Kamin.")),
 "noel-chaussettes-alphabet": dict(
   nom=t("Knitted Alphabet Christmas Stockings",
         "Calcetines navideños de punto con letras del alfabeto",
         "Chaussettes de Noël en tricot, lettres alphabet",
         "Calze di Natale in maglia con lettere dell'alfabeto",
         "Gestrickte Weihnachtsstrümpfe mit Alphabet-Buchstaben"),
   desc=t("Festive knitted stockings with alphabet letters and snowflakes — perfect as tree decorations or name-finding fun.",
          "Calcetines festivos de punto con letras del alfabeto y copos de nieve: perfectos como adornos o para encontrar los nombres.",
          "Chaussettes de Noël tricotées avec lettres de l'alphabet et flocons — parfaites en déco de sapin ou pour chercher son prénom.",
          "Calze festive in maglia con lettere dell'alfabeto e fiocchi: perfette come addobbi o per trovare i nomi.",
          "Festliche Strickstrümpfe mit Alphabet-Buchstaben und Schneeflocken — perfekt als Baumdeko oder zum Namen-Suchen.")),
 "noel-chaussette-torsade-brodee": dict(
   nom=t("Custom Embroidered Cable-Knit Christmas Stocking",
         "Calcetín navideño de punto trenzado bordado a medida",
         "Chaussette de Noël tricot torsadé brodée sur mesure",
         "Calza di Natale in maglia a treccia ricamata su misura",
         "Personalisierter Zopfmuster-Weihnachtsstrumpf"),
   desc=t("Cable-knit stocking embroidered with your name to order. A premium, personalised keepsake for the fireplace.",
          "Calcetín de punto trenzado bordado con tu nombre. Un recuerdo personalizado de primera calidad para la chimenea.",
          "Chaussette en tricot torsadé brodée à votre nom sur commande. Un souvenir personnalisé haut de gamme pour la cheminée.",
          "Calza a maglia treccia ricamata con il tuo nome su ordinazione. Un ricordo personalizzato di alta qualità per il camino.",
          "Zopfmuster-Strumpf mit auf Bestellung gesticktem Namen. Ein hochwertiges, personalisiertes Andenken für den Kamin.")),
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
