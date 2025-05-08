import streamlit as st
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# --- CONFIG ---
st.set_page_config(page_title="Trhacknon Energy", layout="wide")
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# --- ASSETS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

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

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='color:#fff000; text-shadow:0 0 10px #0080ffa;'>Trhacknon</h1>", unsafe_allow_html=True)
#st.sidebar.image("images/3oKIPeS0xvkjaIL6BG.gif", width=100)

# Affiche un GIF animé dans la sidebar sans bloquer l’animation
st.sidebar.markdown(
    """
    <img src="https://media4.giphy.com/media/3oKIPeS0xvkjaIL6BG/giphy.gif" width="100" style="margin-bottom: 10px;" />
    """,
    unsafe_allow_html=True
)
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
    st.image("images/redbull_apricot.jpeg", caption="Soutenez l'énergie libre")
    st.image("images/redbull_winter.jpeg", caption="Soutenez l'énergie libre")
    st.image("images/redbull_summer.jpeg", caption="Soutenez l'énergie libre")
    st.image("images/redbull_purple.jpeg", caption="Soutenez l'énergie libre")
    st.image("images/redbull_sea_blue.jpeg", caption="Soutenez l'énergie libre")

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
            st.markdown(f"**Prix : {p['price']}€**")
            st.markdown("---")

elif page == "Commander":
    st.header("Passe ta commande")
    products = load_products()
    choice = st.selectbox("Choisis ta boisson :", [p["name"] for p in products])
    nom = st.text_input("Ton nom")
    if st.button("Envoyer commande"):
        if nom and choice:
            orders = load_orders()
            orders[choice] = orders.get(choice, 0) + 1
            save_orders(orders)
            st.success("Commande envoyée !")
            msg = f"Nouvelle commande de {nom} pour une **{choice}**"
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}")
        else:
            st.warning("Remplis ton nom et choisis une boisson.")

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
    else:
        st.warning("Mot de passe requis pour l'accès admin.")

st.markdown(
    """
    <footer>
    by <strong>trhacknon</strong> | Digital Liberté &bull; Hacker Style &bull; Allobull Energy
    </footer>
    """,
    unsafe_allow_html=True
)
