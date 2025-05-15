# --- IMPORTS ---
import streamlit as st
import json
import os
import requests
from dotenv import load_dotenv
import streamlit.components.v1 as components
import random
import string
from datetime import datetime

# --- CONFIGURATION GÉNÉRALE ---
dotenv_path = ".env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

st.set_page_config(page_title="Trhacknon Energy", layout="wide")
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# --- STYLE PERSONNALISÉ ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

# --- FONCTIONS UTILITAIRES ---
def load_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([] if "orders" in file else {}, f)
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def load_products():
    return load_json("data/products.json")

def load_orders():
    return load_json("data/orders.json")

def save_orders(data):
    save_json("data/orders.json", data)

def load_promos():
    return load_json("data/promos.json")

def save_promos(data):
    save_json("data/promos.json", data)

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def apply_promo(code, total):
    promos = load_promos()
    if code in promos and not promos[code].get("used", False):
        return max(total - promos[code]["discount"], 0), True
    return total, False

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#fff000; text-shadow:0 0 10px #0080ffa;'>Trhacknon</h1>", unsafe_allow_html=True)
st.sidebar.markdown("""<img src="https://media4.giphy.com/media/3oKIPeS0xvkjaIL6BG/giphy.gif" width="100" />""", unsafe_allow_html=True)
st.sidebar.markdown("## Menu")
page = st.sidebar.radio("Navigation", ["Présentation", "Produits", "Commander", "Admin"])

# --- PAGES ---
if page == "Présentation":
    st.title("Découvrez les bonnes affaires sur des boissons Énergétiques")
    st.markdown("<h2 style='color:#0080ff; text-shadow:0 0 10px #ff073a;'>by Trhacknon</h2>", unsafe_allow_html=True)
    st.markdown("""<div class='intro'>
        **Boissons énergétiques rebelles pour les esprits libres.**  
        Propulsé par un style hacker & l’esprit de résistance.
    </div>""", unsafe_allow_html=True)
    for img in os.listdir("images"):
        if img.endswith((".jpeg", ".png")):
            st.image(f"images/{img}", caption="Faites le plein d'énergie libre")

elif page == "Produits":
    st.header("Nos Boissons")
    for p in load_products():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(p["image"], width=100)
        with col2:
            st.markdown(f"### {p['name']}")
            st.markdown(f"Goût : **{p['flavor']}**")
            st.markdown(f"**Prix : {p['price']}€**")
            st.markdown("---")

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
            commandes.append(commande)
            save_orders(commandes)

            promos = load_promos()
            if code_promo in promos:
                promos[code_promo]["used"] = True
                save_promos(promos)

            msg = f"Nouvelle commande de {nom} pour {quantite}x {choix} ({total_applique:.2f}€)\nContact: {contact}"
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
            st.success("Commande envoyée !")
        else:
            st.warning("Remplis tous les champs")

elif page == "Admin":
    st.header("Interface Admin")
    pw = st.text_input("Mot de passe admin", type="password")
    if pw == "trhackadmin":
        st.success("Accès autorisé")
        st.subheader("Commandes")
        commandes = load_orders()
        if commandes:
            st.table(commandes)
        else:
            st.info("Aucune commande enregistrée")

        if st.button("Réinitialiser commandes"):
            save_orders([])
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

# --- FOOTER ---
st.markdown("""
<div id="custom-footer">
    by <strong>trhacknon</strong> | énergie libre &bull; style hacker
</div>
""", unsafe_allow_html=True)

components.html("""
<script>
const footer = document.getElementById("custom-footer");
document.addEventListener("scroll", () => {
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    const bodyHeight = document.body.scrollHeight;
    if (scrollTop + windowHeight >= bodyHeight - 30) {
        footer.classList.add("visible");
    } else {
        footer.classList.remove("visible");
    }
});
</script>
""", height=0)
