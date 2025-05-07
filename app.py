import streamlit as st
import json
import requests

st.set_page_config(page_title="Trhacknon Energy", layout="wide")

def load_orders():
    with open("data/orders.json", "r") as f:
        return json.load(f)

def save_orders(data):
    with open("data/orders.json", "w") as f:
        json.dump(data, f)

def update_order(product_name):
    data = load_orders()
    data[product_name] += 1
    save_orders(data)

def notify_order(name, flavor):
    message = f"Nouvelle commande de {name} : {flavor}"
    bot_token = "TON_BOT_TOKEN"
    chat_id = "TON_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-hacker">
    <h2>trhacknon.energy</h2>
    <ul>
        <li><a href="#presentation">Présentation</a></li>
        <li><a href="#produits">Produits</a></li>
        <li><a href="#achat">Acheter</a></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Présentation
st.markdown('<div id="presentation"></div>', unsafe_allow_html=True)
st.title("Bienvenue sur Trhacknon Energy")
st.write("Une marque rebelle, au cœur de la résistance, propulsée par l'énergie des taureaux et l'esprit de la liberté.")
st.image("images/redbull.png", width=300)

# Produits
st.markdown('<div id="produits"></div>', unsafe_allow_html=True)
st.header("Nos Produits")

with open("data/products.json") as f:
    products = json.load(f)

cols = st.columns(len(products))
for i, product in enumerate(products):
    with cols[i]:
        st.image(f"images/{product['image']}", width=150)
        st.subheader(product["name"])
        st.caption(product["desc"])
        st.markdown(f"**Prix :** {product['price']}€")

# Achat
st.markdown('<div id="achat"></div>', unsafe_allow_html=True)
st.header("Acheter maintenant")

orders = load_orders()

st.subheader("Statistiques")
for p in products:
    st.text(f"{p['name']} vendues : {orders[p['name']]}")

st.subheader("Passer une commande")

with st.form("order_form"):
    name = st.text_input("Votre prénom")
    flavor = st.selectbox("Boisson souhaitée", [p["name"] for p in products])
    submit = st.form_submit_button("Commander")

    if submit:
        update_order(flavor)
        notify_order(name, flavor)
        st.success(f"Commande enregistrée : {name} veut {flavor}")
