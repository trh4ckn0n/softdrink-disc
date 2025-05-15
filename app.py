import streamlit as st
import json
import os
import random
import string
from datetime import datetime
import requests
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Drink Commander", layout="centered")
bot_token = "TON_TOKEN_TELEGRAM"
chat_id = "TON_CHAT_ID_TELEGRAM"

# --- FICHIERS ---
PRODUCTS_FILE = "data/products.json"
ORDERS_FILE = "data/orders.json"
PROMOS_FILE = "data/promos.json"

# --- FONCTIONS FICHIER ---
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def load_products():
    return load_json(PRODUCTS_FILE, [])

def load_orders():
    return load_json(ORDERS_FILE, {})

def save_orders(data):
    save_json(ORDERS_FILE, data)

def load_promos():
    return load_json(PROMOS_FILE, {})

def save_promos(data):
    save_json(PROMOS_FILE, data)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def apply_promo(code, total):
    promos = load_promos()
    if code in promos and not promos[code]["used"]:
        discount = promos[code]["discount"]
        return max(total - discount, 0), True
    return total, False

# --- UI ---
menu = ["Accueil", "Commander", "Admin"]
page = st.sidebar.selectbox("Navigation", menu)

# --- ACCUEIL ---
if page == "Accueil":
    st.title("Bienvenue sur Drink Commander")
    st.markdown("**Choisis, commande et rafraîchis-toi !**")

# --- COMMANDER ---
elif page == "Commander":
    st.header("Passe ta commande")
    products = load_products()
    noms_produits = [p["name"] for p in products]
    choix = st.selectbox("Choisis ta boisson :", noms_produits)
    produit = next(p for p in products if p["name"] == choix)
    nom = st.text_input("Ton nom")
    contact = st.text_input("Ton contact (Telegram, Insta...)")
    quantite = st.selectbox("Quantité", range(1, 12))
    code_promo = st.text_input("Code promo (facultatif)").strip()

    try:
        total = float(produit["price"]) * quantite
        total_applique, promo_applied = apply_promo(code_promo, total)
        st.info(f"Total : {total_applique:.2f}€")
    except Exception as e:
        st.error("Erreur avec le prix du produit")

    if st.button("Envoyer commande"):
        if nom and contact:
            commandes = load_orders()
            commande = {
                "nom": nom,
                "produit": choix,
                "quantite": quantite,
                "contact": contact,
                "total": round(total_applique, 2),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if choix in commandes:
                commandes[choix].append(commande)
            else:
                commandes[choix] = [commande]
            save_orders(commandes)

            promos = load_promos()
            if code_promo in promos:
                promos[code_promo]["used"] = True
                save_promos(promos)

            msg = f"Nouvelle commande de {nom} pour {quantite}x {choix} ({total_applique:.2f}€)\nContact: {contact}"
            try:
                requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
            except:
                st.warning("Message non envoyé à Telegram.")
            st.success("Commande envoyée !")
        else:
            st.warning("Remplis tous les champs")

# --- ADMIN ---
elif page == "Admin":
    st.header("Interface Admin")
    pw = st.text_input("Mot de passe admin", type="password")
    if pw == "trhackadmin":
        st.success("Accès autorisé")

        st.subheader("Commandes")
        commandes = load_orders()
        if commandes:
            for produit, liste_commandes in commandes.items():
                st.markdown(f"<h4 style='color:#ff073a;'>{produit} ({len(liste_commandes)} commande(s))</h4>", unsafe_allow_html=True)
                for cmd in liste_commandes:
                    st.markdown(f"- **{cmd['date']}** | {cmd['nom']} x{cmd['quantite']} | {cmd['total']}€ | {cmd['contact']}")

            if st.button("Exporter en CSV"):
                toutes = []
                for produit, liste in commandes.items():
                    for cmd in liste:
                        toutes.append(cmd)
                df = pd.DataFrame(toutes)
                st.download_button("Télécharger CSV", df.to_csv(index=False).encode("utf-8"), file_name="commandes.csv", mime="text/csv")
        else:
            st.info("Aucune commande enregistrée")

        if st.button("Réinitialiser commandes"):
            produits = load_products()
            empty_structure = {p["name"]: [] for p in produits}
            save_orders(empty_structure)
            st.success("Commandes supprimées.")

        st.subheader("Promos")
        promos = load_promos()
        for c, info in promos.items():
            st.markdown(f"- {c} (-{info['discount']}€) utilisé : {info['used']}")

        if st.button("Générer nouveau code promo"):
            code = generate_code()
            promos[code] = {"discount": 1, "used": False}
            save_promos(promos)
            st.success(f"Code généré : {code}")
    else:
        st.warning("Accès restreint")
