#!/usr/bin/env python3
"""Ajoute 12 produits (Noël + Anniversaire) à ChicCelebria, active la collection
anniversaire, ajoute les fiches sourcing, puis lance build.py."""
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
# (nom/description 5 langues générés ensuite par template)
NEW = [
 dict(id="noel-sapin-table-bois", prix=16.99, coll=["christmas"], src_id="1005013007711256", src_prix=3.09,
      src_titre="Sapin de Noël en bois à assembler, ornement de table"),
 dict(id="noel-deco-bois-24pcs", prix=14.99, coll=["christmas"], src_id="1005009881191116", src_prix=2.59,
      src_titre="Décorations en bois Père Noël, 24 pièces"),
 dict(id="noel-arbre-mural-bois", prix=34.99, coll=["christmas"], src_id="1005010547459942", src_prix=13.59,
      src_titre="Arbre de Noël tenture murale, échelle en bois shabby"),
 dict(id="noel-boule-photo-a", prix=12.99, coll=["christmas", "personalised"], src_id="1005007602787892", src_prix=1.48,
      src_titre="Boule de Noël photo transparente personnalisée"),
 dict(id="noel-boule-photo-b", prix=13.99, coll=["christmas", "personalised"], src_id="1005012745432540", src_prix=2.06,
      src_titre="Boule de Noël photo transparente personnalisable"),
 dict(id="noel-boule-sublimation", prix=15.99, coll=["christmas", "personalised"], src_id="1005009931921490", src_prix=3.89,
      src_titre="Boule de Noël personnalisée par sublimation 3,15 pouces"),
 dict(id="noel-chaussettes-texte", prix=16.99, coll=["christmas", "personalised"], src_id="1005012047933732", src_prix=3.89,
      src_titre="Chaussettes de Noël personnalisées texte/nom imprimé"),
 dict(id="noel-chemin-table-renne", prix=19.99, coll=["christmas"], src_id="1005012589922831", src_prix=5.89,
      src_titre="Chemin de table de Noël motif renne"),
 dict(id="anniv-banniere-age", prix=17.99, coll=["anniversaire", "personalised"], src_id="1005009501894315", src_prix=4.59,
      src_titre="Bannière d'anniversaire personnalisée numéro d'âge / photo"),
 dict(id="anniv-banniere-photo", prix=19.99, coll=["anniversaire", "personalised"], src_id="1005011975758887", src_prix=6.29,
      src_titre="Bannière photo personnalisée anniversaire, chapeau de fête"),
 dict(id="anniv-guirlande-fanions", prix=12.99, coll=["anniversaire"], src_id="1005005702425417", src_prix=2.10,
      src_titre="Guirlande de fanions arc-en-ciel 4 m, 12 pièces"),
 dict(id="anniv-drapeaux", prix=15.99, coll=["anniversaire", "personalised"], src_id="1005012388314742", src_prix=4.39,
      src_titre="6 drapeaux personnalisés 'Joyeux Anniversaire'"),
]

# ---- Traductions 5 langues (en, es, fr, it, de)
def t(*vals):
    return dict(zip(["en","es","fr","it","de"], vals))

DATA = {
 "noel-sapin-table-bois": dict(
   nom=t("Wooden Table Christmas Tree (DIY)","Árbol de Navidad de madera de mesa (DIY)","Sapin de table en bois (DIY)","Albero di Natale da tavola in legno (DIY)","Tisch-Weihnachtsbaum aus Holz (DIY)"),
   desc=t("Flat-pack wooden mini Christmas tree to assemble yourself. Rustic table decor, reusable every year. ~23 cm.","Mini árbol de Navidad de madera para montar. Decoración rústica de mesa, reutilizable cada año. ~23 cm.","Mini sapin en bois à monter soi-même. Déco de table rustique, réutilisable chaque année. ~23 cm.","Mini albero di Natale in legno da montare. Decorazione rustica da tavolo, riutilizzabile ogni anno. ~23 cm.","Kleiner Holz-Weihnachtsbaum zum Selbstaufbauen. Rustikale Tischdeko, jedes Jahr wiederverwendbar. ~23 cm.")),
 "noel-deco-bois-24pcs": dict(
   nom=t("Wooden Santa Ornaments — Set of 24","Adornos de madera de Papá Noel — Set de 24","Décorations bois Père Noël — Lot de 24","Decorazioni in legno Babbo Natale — Set da 24","Holz-Weihnachtsmann-Anhänger — Set aus 24"),
   desc=t("24 assorted wooden hanging ornaments (Santa, snowflakes, Christmas tree). Perfect for garlands, gift tags or festive tables.","24 adornos colgantes de madera variados (Papá Noel, copos, árbol). Ideales para guirnaldas, etiquetas o mesas festivas.","24 décorations suspendues en bois variées (Père Noël, flocons, sapin). Parfaites en guirlande, étiquettes cadeaux ou table de fête.","24 decorazioni appese in legno assortite (Babbo Natale, fiocchi, albero). Perfette per ghirlande, etichette o tavole festive.","24 gemischte Holz-Anhänger (Weihnachtsmann, Schneeflocken, Tannenbaum). Ideal für Girlanden, Geschenkanhänger oder Festtafeln.")),
 "noel-arbre-mural-bois": dict(
   nom=t("Shabby Chic Wooden Wall Christmas Tree","Árbol de Navidad de pared de madera shabby chic","Arbre de Noël mural en bois shabby chic","Albero di Natale da parete in legno shabby chic","Shabby-Chic-Wand-Weihnachtsbaum aus Holz"),
   desc=t("Decorative ladder-style wooden wall tree, shabby chic finish. Space-saving alternative to a real tree.","Árbol de pared estilo escalera en madera, acabado shabby chic. Alternativa que ahorra espacio al árbol real.","Arbre mural en bois style échelle, finition shabby chic. Alternative gain de place au vrai sapin.","Albero da parete stile scala in legno, finitura shabby chic. Alternativa salvaspazio al vero albero.","Wandbaum im Leiterstil aus Holz, Shabby-Chic-Finish. Platzsparende Alternative zum echten Baum.")),
 "noel-boule-photo-a": dict(
   nom=t("Personalised Photo Christmas Bauble","Bola de Navidad personalizada con foto","Boule de Noël personnalisée photo","Pallina di Natale personalizzata con foto","Personalisierte Foto-Weihnachtskugel"),
   desc=t("Transparent bauble you fill with your own photo. Personalised keepsake, ready to hang on the tree.","Bola transparente que se rellena con tu foto. Recuerdo personalizado, lista para colgar.","Boule transparente à remplir avec votre photo. Souvenir personnalisé, prête à accrocher.","Pallina trasparente da riempire con la tua foto. Ricordo personalizzato, pronta da appendere.","Transparente Kugel zum Befüllen mit eigenem Foto. Personalisiertes Andenken, fertig zum Aufhängen.")),
 "noel-boule-photo-b": dict(
   nom=t("Custom Photo Christmas Ornament","Adorno navideño personalizado con foto","Ornement de Noël photo personnalisé","Ornamento di Natale personalizzato con foto","Personalisierter Foto-Weihnachtsschmuck"),
   desc=t("Personalised transparent bauble with your photo inside. A unique Christmas keepsake for family and friends.","Bola transparente personalizada con tu foto dentro. Recuerdo navideño único para familia y amigos.","Boule transparente personnalisée avec votre photo à l'intérieur. Souvenir de Noël unique.","Pallina trasparente personalizzata con la tua foto dentro. Ricordo di Natale unico.","Personalisierte transparente Kugel mit Foto im Inneren. Einzigartiges Weihnachtsandenken.")),
 "noel-boule-sublimation": dict(
   nom=t("Sublimation Photo Bauble 8 cm","Bola de sublimación con foto 8 cm","Boule photo par sublimation 8 cm","Pallina a sublimazione con foto 8 cm","Sublimations-Fotokugel 8 cm"),
   desc=t("Printed personalised bauble (photo or text), 8 cm. Great for custom gifts and memory trees.","Bola impresa personalizada (foto o texto), 8 cm. Ideal para regalos y árboles de recuerdos.","Boule imprimée personnalisable (photo ou texte), 8 cm. Idéale pour cadeaux sur mesure.","Pallina stampata personalizzabile (foto o testo), 8 cm. Perfetta per regali personalizzati.","Bedruckte, personalisierbare Kugel (Foto oder Text), 8 cm. Ideal für personalisierte Geschenke.")),
 "noel-chaussettes-texte": dict(
   nom=t("Personalised Christmas Stockings (Text)","Calcetines de Navidad personalizados (texto)","Chaussettes de Noël personnalisées (texte)","Calze di Natale personalizzate (testo)","Personalisierte Weihnachtsstrümpfe (Text)"),
   desc=dict(
     en="Festive stockings printed with your names or message. Fun and personal Christmas decor for the fireplace.",
     es="Calcetines festivos impresos con nombres o mensaje. Decoración navideña divertida y personal para la chimenea.",
     fr="Chaussettes de Noël imprimées avec vos prénoms ou un message. Déco de cheminée festive et personnelle.",
     it="Calze festive stampate con nomi o messaggio. Decorazione natalizia divertente e personale per il camino.",
     de="Festliche Strümpfe mit Namen oder Botschaft bedruckt. Lustige, persönliche Weihnachtsdeko für den Kamin.")),
 "noel-chemin-table-renne": dict(
   nom=t("Reindeer Christmas Table Runner","Camino de mesa navideño de reno","Chemin de table de Noël renne","Tovaglia runner di Natale renna","Weihnachtstischläufer Rentier"),
   desc=t("Festive reindeer print table runner. Instant Christmas table styling, machine washable.","Camino de mesa festivo con estampado de reno. Mesa navideña al instante, lavable a máquina.","Chemin de table festif motif renne. Table de Noël instantanée, lavable en machine.","Runner festivo con stampa renna. Tavola di Natale istantanea, lavabile in lavatrice.","Festlicher Tischläufer mit Rentierdruck. Weihnachtstafel im Handumdrehen, maschinenwaschbar.")),
 "anniv-banniere-age": dict(
   nom=t("Personalised Birthday Banner (Age + Photo)","Banner de cumpleaños personalizado (edad + foto)","Bannière d'anniversaire personnalisée (âge + photo)","Stendardo di compleanno personalizzato (età + foto)","Personalisierte Geburtstagsbanner (Alter + Foto)"),
   desc=t("Custom birthday banner with age number and photo. Perfect for milestone birthdays and parties.","Banner de cumpleaños personalizado con número de edad y foto. Perfecto para cumpleaños importantes.","Bannière d'anniversaire personnalisée avec âge et photo. Parfaite pour les anniversaires marquants.","Stendardo personalizzato con numero di età e foto. Perfetto per compleanni importanti.","Personalisierte Banner mit Alter und Foto. Perfekt für runde Geburtstage und Partys.")),
 "anniv-banniere-photo": dict(
   nom=t("Photo Birthday Banner with Party Hats","Banner de cumpleaños con foto y gorros de fiesta","Bannière photo anniversaire avec chapeaux de fête","Stendardo foto di compleanno con cappellini","Foto-Geburtstagsbanner mit Partymützen"),
   desc=dict(
     en="Fun banner printed with your photos and party hats. A personalised touch for any celebration.",
     es="Banner divertido impreso con tus fotos y gorros de fiesta. Un toque personal para cualquier celebración.",
     fr="Bannière ludique imprimée avec vos photos et chapeaux de fête. Une touche personnelle pour toute célébration.",
     it="Stendardo divertente stampato con le tue foto e cappellini. Un tocco personale per ogni festa.",
     de="Lustige Banner mit Fotos und Partymützen bedruckt. Eine persönliche Note für jede Feier.")),
 "anniv-guirlande-fanions": dict(
   nom=t("Rainbow Bunting Banner 4 m","Guirnalda de banderines arcoíris 4 m","Guirlande de fanions arc-en-ciel 4 m","Ghirlanda di bandierine arcobaleno 4 m","Regenbogen-Wimpelkette 4 m"),
   desc=dict(
     en="4 m colourful bunting with 12 flags. Instant party decoration for birthdays and celebrations.",
     es="Guirnalda de colores de 4 m con 12 banderines. Decoración de fiesta al instante.",
     fr="Guirlande colorée de 4 m avec 12 fanions. Déco de fête instantanée pour anniversaires.",
     it="Ghirlanda colorata di 4 m con 12 bandierine. Decorazione istantanea per feste di compleanno.",
     de="4 m bunte Wimpelkette mit 12 Fahnen. Sofortige Partydeko für Geburtstage.")),
 "anniv-drapeaux": dict(
   nom=t("Personalised 'Happy Birthday' Bunting","Banderín personalizado 'Feliz cumpleaños'","Drapeaux personnalisés 'Joyeux Anniversaire'","Bandierine personalizzate 'Buon Compleanno'","Personalisierte 'Happy Birthday' Wimpel"),
   desc=dict(
     en="6 personalised bunting flags with your name or message. Birthday decor that feels truly made for you.",
     es="6 banderines personalizados con tu nombre o mensaje. Decoración de cumpleaños hecha para ti.",
     fr="6 fanions personnalisés avec votre prénom ou message. Une déco d'anniversaire vraiment à vous.",
     it="6 bandierine personalizzate con nome o messaggio. Decorazione di compleanno fatta per te.",
     de="6 personalisierte Wimpel mit Name oder Botschaft. Geburtstagsdeko, die wirklich zu dir passt.")),
}

# ---- Construction des produits
products = load("products.json")
existing_ids = {p["id"] for p in products}
added = 0
for n in NEW:
    if n["id"] in existing_ids:
        print("SKIP (existe):", n["id"]); continue
    d = DATA[n["id"]]
    img = f"assets/sourcing/{n['id'].replace('noel-','noel-').replace('anniv-','anniv-')}.jpg"
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

# ---- Activer la collection anniversaire
cols = load("collections.json")
for c in cols:
    if c["slug"] == "anniversaire" and not c.get("actif"):
        c["actif"] = True
        print("Collection 'anniversaire' activée")
save("collections.json", cols)

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
        "date": "2026-08-26",
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
