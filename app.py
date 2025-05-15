import streamlit as st
import json
import os
import requests
from dotenv import load_dotenv
import streamlit.components.v1 as components
import random
import string

# Charger les variables d'environnement
dotenv_path = ".env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# --- CONFIG ---
st.set_page_config(page_title="Trhacknon Energy", layout="wide")
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# --- ASSETS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/styles.css")

# --- LOAD DATA ---
def load_products():
    with open("data/products.json", "r") as f:
        return json.load(f)

def load_orders():
    if not os.path.exists("data/orders.json"):
        with open("data/orders.json", "w") as f:
            json.dump({}, f)
    with open("data/orders.json", "r") as f:
        return json.load(f)

def save_orders(data):
    with open("data/orders.json", "w") as f:
        json.dump(data, f)

def load_promos():
    if not os.path.exists("data/promos.json"):
        with open("data/promos.json", "w") as f:
            json.dump({}, f)
    with open("data/promos.json", "r") as f:
        return json.load(f)

def save_promos(data):
    with open("data/promos.json", "w") as f:
        json.dump(data, f)

# --- FONCTION PROMO ---
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def apply_promo(code, total):
    promos = load_promos()
    if code in promos and not promos[code].get("used", False):
        return max(total - promos[code]["discount"], 0), True
    return total, False

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#fff000; text-shadow:0 0 10px #0080ffa;'>Trhacknon</h1>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <img src="https://media4.giphy.com/media/3oKIPeS0xvkjaIL6BG/giphy.gif" width="100" style="margin-bottom: 10px;" />
    """, unsafe_allow_html=True)
st.sidebar.markdown("## Menu")
page = st.sidebar.radio("Navigation", ["Présentation", "Produits", "Commander", "Admin"])

# --- PAGES ---
if page == "Présentation":
    st.title("Découvrez les bonnes affaires sur des boissons Energetiques")
    st.markdown("<h2 style='color:#0080ff; text-shadow:0 0 10px #ff073a;'>by Trhacknon</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class='intro'>
        **Boissons énergétiques rebelles pour les esprits libres.**  
        Propulsé par un style hacker & l’esprit de résistance.
        </div>
    """, unsafe_allow_html=True)
    for img in ["redbull_apricot.jpeg", "redbull_winter.jpeg", "redbull_summer.jpeg", "redbull_purple.jpeg", "redbull_spring.png", "redbull_sea_blue.jpeg"]:
        st.image(f"images/{img}", caption="Faites le plein d'énergie libre")

elif page == "Produits":
    st.header("Nos Boissons")
    products = load_products()
    for p in products:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(p["image"], width=100)
        with col2:
            st.markdown(f"### {p['name']}")
            st.markdown(f"Goût : **{p['flavor']}**")
            st.markdown(f"Description : **{p['desc']}**")
            st.markdown(f"**Prix : {p['price']}€**")
            st.markdown("---")

elif page == "Commander":
    st.header("Passe ta commande")
    products = load_products()
    product_names = [p["name"] for p in products]
    choice = st.selectbox("Choisis ta boisson :", product_names)
    selected_product = next((p for p in products if p["name"] == choice), None)
    nom = st.text_input("Ton nom.")
    contact = st.text_input("Contact où tu veux qu'on te joigne (telegram/snapchat/messenger/...).")
    quantite = st.selectbox("Nombre de boissons souhaitées :", list(range(1, 12)), index=0)
    promo_code = st.text_input("Code promo (facultatif)")

    if selected_product:
        try:
            total = float(selected_product["price"]) * quantite
            total_applique, promo_applied = apply_promo(promo_code.strip(), total)
            st.info(f"Prix unitaire : {selected_product['price']}€ | Total : {total_applique:.2f}€")
        except ValueError:
            st.warning("Erreur : le prix du produit est invalide.")

    if st.button("Envoyer commande"):
        if nom and choice and contact:
            orders = load_orders()
            orders[choice] = orders.get(choice, 0) + quantite
            save_orders(orders)
            promos = load_promos()
            if promo_code in promos:
                promos[promo_code]["used"] = True
                save_promos(promos)
            st.success("Commande envoyée !")
            msg = (
                f"Nouvelle commande de {nom} pour **{quantite}x {choice}** "
                f"(prix total : {total_applique:.2f}€). Contact : {contact}"
            )
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        else:
            st.warning("Remplis tous les champs avant d'envoyer ta commande.")

elif page == "Admin":
    st.header("Interface Admin")
    password = st.text_input("Mot de passe admin", type="password")
    if password == "trhackadmin":
        st.success("Accès autorisé")
        orders = load_orders()
        st.subheader("Commandes enregistrées")
        for k, v in orders.items():
            st.markdown(f"- **{k}** : {v} ventes")
        if st.button("Réinitialiser les ventes"):
            save_orders({k: 0 for k in orders})
            st.success("Ventes réinitialisées")

        st.subheader("Codes promos")
        promos = load_promos()
        for code, infos in promos.items():
            st.markdown(f"- {code} | -{infos['discount']:.2f}€ | utilisé: {infos.get('used', False)}")

        # Nouveau : input pour choisir le montant du code promo
        discount_value = st.number_input("Montant de la réduction (€)", min_value=0.1, max_value=100.0, value=1.0, step=0.1, format="%.2f")

        if st.button("Générer un nouveau code promo"):
            code = generate_code()
            promos[code] = {"discount": float(discount_value), "used": False}
            save_promos(promos)
            st.success(f"Code promo généré : {code} (-{discount_value:.2f}€)")
    else:
        st.warning("Mot de passe requis pour l'accès admin.")

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
