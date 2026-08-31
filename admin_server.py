#!/usr/bin/env python3
"""Chic Celebria — Back-office (serveur admin).

API CRUD sur products.json / collections.json (source de vérité), upload de
photos dans assets/sourcing/, relance du build statique. Stdlib uniquement.

Lancement :  python3 admin_server.py [port]
Défaut port : 8766

Auth : token de session dans ~/.hermes/state/cc-admin-token.txt (généré au
premier lancement). Envoyez-le via l'en-tete X-Admin-Token (ou ?token=).
Pages statiques (/) : accessibles sans token ; API : token requis.
"""

import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "es", "fr", "it", "de"]
LANG_NAMES = {"fr": "Français", "en": "English", "de": "Deutsch",
              "it": "Italiano", "es": "Español"}
PRODUCTS_JSON = os.path.join(BASE, "products.json")
COLLECTIONS_JSON = os.path.join(BASE, "collections.json")
ASSETS_DIR = os.path.join(BASE, "assets", "sourcing")
BACKUP_DIR = os.path.join(BASE, "admin", "backups")
TOKEN_FILE = os.path.expanduser("~/.hermes/state/cc-admin-token.txt")
UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin", "admin.html")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SETTINGS_JSON = os.path.join(BASE, "settings.json")
DEFAULT_SETTINGS = {"site_url": ""}


def load_settings():
    if os.path.exists(SETTINGS_JSON):
        try:
            with open(SETTINGS_JSON, encoding="utf-8") as f:
                s = json.load(f)
            if isinstance(s, dict):
                return s
        except (OSError, ValueError):
            pass
    return dict(DEFAULT_SETTINGS)


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            t = f.read().strip()
        if t:
            return t
    t = secrets.token_urlsafe(24)
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(t + "\n")
    os.chmod(TOKEN_FILE, 0o600)
    return t


TOKEN = get_token()


# --------------------------------------------------------------------------
# Lecture / écriture JSON avec backup automatique
# --------------------------------------------------------------------------
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def backup(path):
    if not os.path.exists(path):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    name = os.path.basename(path).replace(".json", "")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{name}.{stamp}.json")
    shutil.copy2(path, dest)
    # ne garder que les 15 derniers backups de ce fichier
    olds = sorted(f for f in os.listdir(BACKUP_DIR) if f.startswith(name + "."))
    for old in olds[:-15]:
        os.remove(os.path.join(BACKUP_DIR, old))


def save_json(path, data):
    backup(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def err(msg, code=400):
    return {"ok": False, "error": msg}, code


def check_lang_dict(obj, field, allow_empty=True):
    if not isinstance(obj, dict):
        return err(f"'{field}' doit etre un objet a 5 langues")
    missing = [l for l in LANGS if l not in obj]
    if missing:
        return err(f"'{field}' : langues manquantes {missing}")
    for l in LANGS:
        v = obj[l]
        if not isinstance(v, str):
            return err(f"'{field}.{l}' doit etre une chaine")
        if not allow_empty and not v.strip():
            return err(f"'{field}.{l}' ne peut pas etre vide")
    return None


def validate_image(img):
    if isinstance(img, str):
        return None if img.strip() else err("chemin d'image vide")
    if isinstance(img, dict) and isinstance(img.get("src"), str) and img["src"].strip():
        leg = img.get("legende")
        if leg is not None:
            e = check_lang_dict(leg, "legende")
            if e:
                return e
        return None
    return err("image invalide (attendu : chaine ou {src, legende})")


def validate_product(p, is_new):
    e = check_lang_dict(p.get("nom"), "nom", allow_empty=False)
    if e:
        return e
    e = check_lang_dict(p.get("description"), "description")
    if e:
        return e
    try:
        prix = float(p["prix"])
    except (KeyError, TypeError, ValueError):
        return err("'prix' doit etre un nombre")
    if prix < 0:
        return err("'prix' ne peut pas etre negatif")
    promo = p.get("promo")
    if promo is not None:
        try:
            promo = float(promo)
        except (TypeError, ValueError):
            return err("'promo' doit etre un nombre")
    if not isinstance(p.get("images"), list):
        return err("'images' doit etre une liste")
    for img in p["images"]:
        e = validate_image(img)
        if e:
            return e
    if not isinstance(p.get("collections"), list):
        return err("'collections' doit etre une liste")
    if not isinstance(p.get("actif"), bool):
        p["actif"] = True
    if not isinstance(p.get("stock"), bool):
        p["stock"] = True
    if is_new and not ID_RE.match(p["id"]):
        return err("id invalide : minuscules, chiffres, tirets (ex: tapis-halloween)")
    return None


def validate_collection(c, is_new):
    e = check_lang_dict(c.get("label"), "label", allow_empty=False)
    if e:
        return e
    if is_new and not ID_RE.match(c["slug"]):
        return err("slug invalide : minuscules, chiffres, tirets")
    try:
        ordre = int(c.get("ordre", 99))
    except (TypeError, ValueError):
        return err("'ordre' doit etre un entier")
    if c.get("type") not in ("occasion", "theme"):
        c["type"] = "occasion"
    if not isinstance(c.get("actif"), bool):
        c["actif"] = True
    return None


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def run_build():
    try:
        r = subprocess.run([sys.executable, "build.py"], cwd=BASE,
                           capture_output=True, text=True, timeout=180)
        out = (r.stdout or "").strip()
        if r.returncode != 0:
            return {"ok": False, "output": out + "\n" + (r.stderr or "")}
        return {"ok": True, "output": out}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Build interrompu (timeout 180s)"}
    except Exception as ex:  # pragma: no cover
        return {"ok": False, "output": f"Erreur build : {ex}"}


# --------------------------------------------------------------------------
# Serveur HTTP
# --------------------------------------------------------------------------
class AdminHandler(BaseHTTPRequestHandler):
    server_version = "CCAdmin/1.0"

    def log_message(self, fmt, *args):  # silencieux
        pass

    # --- helpers ---------------------------------------------------------
    def _auth(self):
        q = parse_qs(urlparse(self.path).query)
        tok = self.headers.get("X-Admin-Token") or (q.get("token") or [""])[0]
        if not secrets.compare_digest(tok, TOKEN):
            self._json({"ok": False, "error": "Token invalide ou manquant"}, 401)
            return False
        return True

    def _json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self, max_bytes=10 * 1024 * 1024):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return None
        if length > max_bytes:
            return None
        return self.rfile.read(length)

    def _read_json_body(self):
        raw = self._read_body()
        if raw is None:
            return None, err("corps de requete vide ou trop volumineux")
        try:
            return json.loads(raw.decode("utf-8")), None
        except (ValueError, UnicodeDecodeError):
            return None, err("JSON invalide")

    # --- routes ----------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json({"ok": True, "service": "chic-celebria-admin"})
            return
        if path == "/":
            path = "/admin.html"
        if path == "/admin.html":
            if os.path.exists(UI_FILE):
                with open(UI_FILE, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self._json({"ok": False, "error": "admin.html introuvable"}, 500)
            return
        if path == "/api/state":
            if not self._auth():
                return
            products = load_json(PRODUCTS_JSON)
            collections = load_json(COLLECTIONS_JSON)
            self._json({"ok": True, "langs": LANGS, "lang_names": LANG_NAMES,
                        "products": products, "collections": collections,
                        "settings": load_settings()})
            return
        if path == "/api/settings":
            if not self._auth():
                return
            self._json({"ok": True, "settings": load_settings()})
            return
        self._json({"ok": False, "error": "404"}, 404)

    def do_PUT(self):
        path = urlparse(self.path).path
        if not self._auth():
            return
        m = re.match(r"^/api/products/([^/]+)$", path)
        if m:
            self._put_product(m.group(1))
            return
        m = re.match(r"^/api/collections/([^/]+)$", path)
        if m:
            self._put_collection(m.group(1))
            return
        if path == "/api/upload":
            self._upload()
            return
        if path == "/api/settings":
            self._put_settings()
            return
        self._json({"ok": False, "error": "404"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if not self._auth():
            return
        if path == "/api/products":
            self._post_product()
            return
        if path == "/api/collections":
            self._post_collection()
            return
        if path == "/api/build":
            res = run_build()
            self._json({"ok": res["ok"], "build": res["output"],
                        "error": None if res["ok"] else res["output"]})
            return
        self._json({"ok": False, "error": "404"}, 404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        if not self._auth():
            return
        m = re.match(r"^/api/products/([^/]+)$", path)
        if m:
            pid = m.group(1)
            products = load_json(PRODUCTS_JSON)
            before = len(products)
            products = [p for p in products if p["id"] != pid]
            if len(products) == before:
                self._json({"ok": False, "error": "produit introuvable"}, 404)
                return
            save_json(PRODUCTS_JSON, products)
            build = run_build()
            self._json({"ok": True, "deleted": pid, "build": build["output"],
                        "build_ok": build["ok"]})
            return
        m = re.match(r"^/api/collections/([^/]+)$", path)
        if m:
            slug = m.group(1)
            collections = load_json(COLLECTIONS_JSON)
            before = len(collections)
            collections = [c for c in collections if c["slug"] != slug]
            if len(collections) == before:
                self._json({"ok": False, "error": "collection introuvable"}, 404)
                return
            save_json(COLLECTIONS_JSON, collections)
            build = run_build()
            self._json({"ok": True, "deleted": slug, "build": build["output"],
                        "build_ok": build["ok"]})
            return
        self._json({"ok": False, "error": "404"}, 404)

    # --- produits --------------------------------------------------------
    def _post_product(self):
        data, e = self._read_json_body()
        if e:
            self._json(*e)
            return
        pid = data.get("id", "")
        if not ID_RE.match(pid):
            self._json(err("id invalide : minuscules, chiffres, tirets (ex: tapis-halloween)"))
            return
        e = validate_product(data, is_new=True)
        if e:
            self._json(*e)
            return
        products = load_json(PRODUCTS_JSON)
        if any(p["id"] == pid for p in products):
            self._json(err(f"un produit avec l'id '{pid}' existe deja"))
            return
        products.append(data)
        save_json(PRODUCTS_JSON, products)
        build = run_build()
        self._json({"ok": True, "id": pid, "build": build["output"],
                    "build_ok": build["ok"]})

    def _put_product(self, pid):
        data, e = self._read_json_body()
        if e:
            self._json(*e)
            return
        data["id"] = pid
        e = validate_product(data, is_new=False)
        if e:
            self._json(*e)
            return
        products = load_json(PRODUCTS_JSON)
        idx = next((i for i, p in enumerate(products) if p["id"] == pid), None)
        if idx is None:
            self._json({"ok": False, "error": "produit introuvable"}, 404)
            return
        products[idx] = data
        save_json(PRODUCTS_JSON, products)
        build = run_build()
        self._json({"ok": True, "id": pid, "build": build["output"],
                    "build_ok": build["ok"]})

    # --- collections -----------------------------------------------------
    def _post_collection(self):
        data, e = self._read_json_body()
        if e:
            self._json(*e)
            return
        slug = data.get("slug", "")
        if not ID_RE.match(slug):
            self._json(err("slug invalide : minuscules, chiffres, tirets"))
            return
        e = validate_collection(data, is_new=True)
        if e:
            self._json(*e)
            return
        collections = load_json(COLLECTIONS_JSON)
        if any(c["slug"] == slug for c in collections):
            self._json(err(f"une collection avec le slug '{slug}' existe deja"))
            return
        collections.append(data)
        save_json(COLLECTIONS_JSON, collections)
        build = run_build()
        self._json({"ok": True, "slug": slug, "build": build["output"],
                    "build_ok": build["ok"]})

    def _put_collection(self, slug):
        data, e = self._read_json_body()
        if e:
            self._json(*e)
            return
        data["slug"] = slug
        e = validate_collection(data, is_new=False)
        if e:
            self._json(*e)
            return
        collections = load_json(COLLECTIONS_JSON)
        idx = next((i for i, c in enumerate(collections) if c["slug"] == slug), None)
        if idx is None:
            self._json({"ok": False, "error": "collection introuvable"}, 404)
            return
        collections[idx] = data
        save_json(COLLECTIONS_JSON, collections)
        build = run_build()
        self._json({"ok": True, "slug": slug, "build": build["output"],
                    "build_ok": build["ok"]})

    # --- settings --------------------------------------------------------
    def _put_settings(self):
        data, e = self._read_json_body()
        if e:
            self._json(*e)
            return
        if not isinstance(data, dict):
            self._json(err("body invalide"))
            return
        if "site_url" in data and not isinstance(data["site_url"], str):
            self._json(err("site_url doit être une chaîne"))
            return
        cur = load_settings()
        cur.update({k: v for k, v in data.items() if v is not None})
        backup(SETTINGS_JSON)
        save_json(SETTINGS_JSON, cur)
        self._json({"ok": True, "settings": cur})

    # --- upload ----------------------------------------------------------
    def _upload(self):
        q = parse_qs(urlparse(self.path).query)
        name = (q.get("name") or [""])[0].strip()
        if not name:
            self._json(err("parametre 'name' requis (ex: ?name=tapis.jpg)"))
            return
        name = os.path.basename(name.replace("\\", "/"))
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
        ext = os.path.splitext(name)[1].lower()
        if ext not in ALLOWED_EXT:
            self._json(err(f"extension non autorisee ({sorted(ALLOWED_EXT)})"))
            return
        raw = self._read_body(max_bytes=20 * 1024 * 1024)
        if raw is None:
            self._json(err("fichier vide ou trop volumineux (>20 Mo)"))
            return
        os.makedirs(ASSETS_DIR, exist_ok=True)
        dest = os.path.join(ASSETS_DIR, name)
        with open(dest, "wb") as f:
            f.write(raw)
        src = f"assets/sourcing/{name}"
        self._json({"ok": True, "src": src, "path": dest})


def main():
    port = 8766
    if len(sys.argv) > 1:
        if sys.argv[1] == "--port" and len(sys.argv) > 2:
            port = int(sys.argv[2])
        else:
            port = int(sys.argv[1])
    server = ThreadingHTTPServer(("0.0.0.0", port), AdminHandler)
    print(f"Back-office Chic Celebria : http://0.0.0.0:{port}/")
    print(f"Token (a garder secret)  : {TOKEN}")
    server.serve_forever()


if __name__ == "__main__":
    main()
