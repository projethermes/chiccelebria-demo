#!/usr/bin/env python3
"""Génère les 8 fiches Etsy Noël pour ChicCelebria (format etsy_listing.py)."""
import json, os
from pathlib import Path

OUT = Path("/Users/openclaw/projets/chiccelebria-demo/fiches-etsy-noel")
OUT.mkdir(exist_ok=True)

def desc(ty, personalization=None):
    base = (
        f"Add a warm, personal touch to your home this {ty.lower()}. "
        "This item is made to order and carefully shipped with tracking, "
        "so you can gift it with confidence.\n\n"
        "✨ Perfect for:\n"
        "- Christmas decoration & cozy seasonal styling\n"
        "- A thoughtful, unique gift for family and friends\n\n"
    )
    if personalization:
        base += (
            f"🎁 Personalization: {personalization} "
            "Simply leave the details in the 'Personalization' box at checkout.\n\n"
        )
    base += (
        "Please note: colors may vary slightly due to screen settings. "
        "Each item is checked before shipping. If you have any questions, "
        "message us — we usually reply within a few hours. 😊"
    )
    return base

FICHES = [
    # (id_fichier, title, price, taxonomy_keyword, tags, materials, desc)
    ("noel-sapin-table",
     "Wooden Christmas Tree Table Decor, DIY Mini Christmas Tree, Rustic Farmhouse Holiday Centerpiece, Scandinavian Wood Ornament",
     16.99, "Christmas Trees",
     ["christmas tree", "wooden christmas decor", "farmhouse christmas", "tabletop tree", "rustic decor", "mini christmas tree", "wood ornament", "scandinavian decor", "christmas centerpiece", "holiday table decor"],
     ["Wood", "Metal"],
     desc("Christmas")),
    ("noel-deco-bois-24",
     "Set of 24 Wooden Christmas Ornaments, Painted Santa Wood Decor, Rustic Farmhouse Christmas Tree Ornaments, Handmade Holiday Decor",
     14.99, "Ornaments",
     ["wooden ornaments", "santa claus decor", "farmhouse ornaments", "christmas tree decor", "rustic christmas", "handmade ornaments", "wood christmas", "holiday ornaments", "santa ornaments", "tree decorations"],
     ["Wood", "Acrylic"],
     desc("Christmas")),
    ("noel-arbre-mural",
     "Wooden Wall Christmas Tree, Rustic Ladder Tree Wall Decor, Farmhouse Christmas Wall Art, Scandinavian Holiday Wall Hanging",
     34.99, "Panels & Wall Hangings",
     ["wall christmas tree", "wooden wall decor", "farmhouse wall art", "ladder christmas tree", "rustic wall decor", "christmas wall hanging", "scandinavian decor", "holiday wall art", "wood wall art", "christmas home decor"],
     ["Wood", "Metal"],
     desc("Christmas")),
    ("noel-boule-photo",
     "Personalized Christmas Ornament, Photo Christmas Ball, Custom Name Ornament, Christmas Keepsake Gift, Glass Ball Decoration",
     12.99, "Ornaments",
     ["personalized ornament", "photo ornament", "christmas keepsake", "custom name ornament", "glass ball ornament", "memory ornament", "xmas gift", "family ornament", "personalized christmas", "keepsake gift"],
     ["Glass", "Metal"],
     desc("Christmas", "Add a photo or a name — we'll print it inside the glass ball before shipping.")),
    ("noel-boule-prenom",
     "Custom Name Christmas Ornament, Personalized Text Glass Ball, Monogram Christmas Decoration, Family Name Ornament Gift",
     13.99, "Ornaments",
     ["custom name ornament", "monogram ornament", "name christmas ball", "personalized ornament", "family name decor", "custom christmas", "text ornament", "glass ball gift", "holiday personalization", "christmas monogram"],
     ["Glass", "Metal"],
     desc("Christmas", "Add the name or text you want printed — perfect for names, dates or short messages.")),
    ("noel-boule-sublimation",
     "Sublimation Christmas Ornament Blank, 8cm DIY Photo Ball, Personalized Craft Ornament, Christmas Craft Blank",
     15.99, "Ornaments",
     ["sublimation ornament", "diy ornament", "craft blank", "photo ball", "blank ornament", "personalized craft", "christmas craft", "8cm ornament", "sublimation blank", "holiday craft"],
     ["Glass", "Plastic"],
     desc("Christmas", "Sublimation blank — print your own design with a sublimation printer.")),
    ("noel-chaussettes-prenom",
     "Personalized Christmas Stockings, Custom Name Stocking, Family Christmas Stockings Set, Holiday Gift Sock",
     16.99, "Stockings",
     ["christmas stocking", "personalized stocking", "name stocking", "family stocking", "custom stocking", "christmas sock", "holiday stocking", "stocking gift", "personalized christmas", "xmas stocking"],
     ["Polyester", "Cotton"],
     desc("Christmas", "Add the name to embroider on the stocking.")),
    ("noel-chemin-table-renne",
     "Christmas Table Runner, Reindeer Holiday Table Runner, Rustic Farmhouse Christmas Table Decoration, 180cm Festive Linen",
     19.99, "Table Runners",
     ["table runner", "christmas table decor", "reindeer decor", "farmhouse runner", "holiday table runner", "christmas tablecloth", "rustic table decor", "festive runner", "winter table decor", "xmas table"],
     ["Polyester"],
     desc("Christmas")),
]

for fname, title, price, tax, tags, mats, d in FICHES:
    fiche = {
        "title": title,
        "description": d,
        "price": price,
        "quantity": 1,
        "taxonomy_keyword": tax,
        "tags": tags,
        "materials": mats,
        "when_made": "made_to_order",
    }
    path = OUT / f"{fname}.json"
    path.write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")
    # Validation contraintes Etsy
    assert len(title) <= 140, f"Titre trop long {fname}: {len(title)}"
    tags = [t[:20] for t in tags]
    print(f"OK {fname} — titre {len(title)}c, {len(tags)} tags")
print(f"\n{len(FICHES)} fiches écrites dans {OUT}")
