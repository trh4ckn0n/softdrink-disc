import os
import json
import threading
import requests
import streamlit as st
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import Conflict

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Configuration de la page Streamlit
st.set_page_config(page_title="Faites le plein d'énergie", layout="wide")

# Chargement des produits
def load_products():
    with open("data/products.json", "r") as f:
        return json.load(f)

# Chargement des commandes
def load_orders():
    if not os.path.exists("data/orders.json"):
        with open("data/orders.json", "w") as f:
            json.dump({}, f)
    with open("data/orders.json", "r") as f:
        return json.load(f)

# Sauvegarde des commandes
def save_orders(data):
    with open("data/orders.json", "w") as f:
        json.dump(data, f)

# Fonction pour envoyer un message via Telegram
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur lors de l'envoi du message Telegram : {e}")

# Gestionnaire de la commande /commande
def handle_commande(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("Utilisation : /commande <NomBoisson> <TonContact>")
            return
        produit = args[0]
        nom_contact = ' '.join(args[1:])

        # Vérification si le produit existe
        products = load_products()
        product_names = [p["name"] for p in products]
        if produit not in product_names:
            update.message.reply_text("Produit non reconnu. Veuillez vérifier le nom.")
            return

        # Enregistrement de la commande
        orders = load_orders()
        orders[produit] = orders.get(produit, 0) + 1
        save_orders(orders)

        # Confirmation à l'utilisateur
        update.message.reply_text(f"Commande reçue : {produit} pour {nom_contact}")

        # Notification à l'admin
        msg = f"Nouvelle commande via Telegram : {nom_contact} pour une {produit}"
        send_telegram_message(ADMIN_CHAT_ID, msg)
    except Exception as e:
        print(f"Erreur dans handle_commande : {e}")

# Fonction pour démarrer le bot Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bienvenue ! Utilise /commande <NomBoisson> <TonContact> pour passer une commande.")

def handle_message(update: Update, context: CallbackContext):
    update.message.reply_text("Commande non reconnue. Utilise /commande <NomBoisson> <TonContact>.")
    
def start_telegram_bot():
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        print("[+] Bot Telegram lancé.")
        updater.start_polling()
        updater.idle()

    except Conflict:
        print("[!] Une autre instance du bot tourne déjà.")
# Démarrage du bot Telegram dans un thread séparé
bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
bot_thread.start()

# Chargement du CSS local
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

# Sidebar
st.sidebar.markdown("<h1 style='color:#fff000; text-shadow:0 0 10px #0080ffa;'>Trhacknon</h1>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <img src="https://media4.giphy.com/media/3oKIPeS0xvkjaIL6BG/giphy.gif" width="100" style="margin-bottom: 10px;" />
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("## Menu")
page = st.sidebar.radio("Navigation", ["Présentation", "Produits", "Commander", "Admin"])

# Pages
if page == "Présentation":
    st.title("Découvrez les bonnes affaires sur des boissons Énergétiques")
    st.markdown("<h2 style='color:#0080ff; text-shadow:0 0 10px #ff073a;'>by Trhacknon</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class='intro'>
        **Boissons énergétiques rebelles pour les esprits libres.**  
        Propulsé par un style hacker & l’esprit de résistance.
        </div>
    """, unsafe_allow_html=True)
    st.image("images/redbull_apricot.jpeg", caption="Faites le plein d'énergie libre")
    st.image("images/redbull_winter.jpeg", caption="Faites le plein d'énergie libre")
    st.image("images/redbull_summer.jpeg", caption="Faites le plein d'énergie libre")
    st.image("images/redbull_purple.jpeg", caption="Faites le plein d'énergie libre")
    st.image("images/redbull_spring.png", caption="Faites le plein d'énergie libre")
    st.image("images/redbull_sea_blue.jpeg", caption="Faites le plein d'énergie libre")

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
    nom = st.text_input("Ton nom et contact où tu veux qu'on te joigne (telegram/snapchat/messenger/...).")
    if st.button("Envoyer commande"):
        if nom and choice:
            orders = load_orders()
            orders[choice] = orders.get(choice, 0) + 1
            save_orders(orders)
            st.success("Commande envoyée !")
            msg = f"Nouvelle commande de {nom} pour une {choice}"
            send_telegram_message(ADMIN_CHAT_ID, msg)
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

# Footer
st.markdown("""
<div id="custom-footer">
    by <strong>trhacknon</strong> | Faites le plein d'énergie &bull; style hacker
</div>
""", unsafe_allow_html=True)
