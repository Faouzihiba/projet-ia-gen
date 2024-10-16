from io import StringIO
import streamlit as st  # Importer Streamlit
import os
import openai
import sys
from datetime import date
from fpdf import FPDF
from requests.exceptions import Timeout
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.chat_models import ChatOpenAI
from requests.exceptions import Timeout
from langchain.docstore.document import Document
#from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.vectorstores import DocArrayInMemorySearch
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
#from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from PyPDF2 import PdfWriter, PdfReader
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
sys.path.append('../..')

# Charger les variables d'environnement
_ = load_dotenv(find_dotenv())  # Lire le fichier .env local



# URLs à charger
urls = [
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-autriche",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-algerie",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-russie",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-angleterre/grande-bretagne",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-maldives",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-malaisie",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-pays-bas",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-bresil",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-suede",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-portugal",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/recherche-voyage/voyage-italie",
    "https://www.voyageursdumonde.fr/voyage-sur-mesure/magazine-voyage/24-heures-a-bruxelles",
    "https://www.evaneos.fr/tunisie/circuits-novembre/",
    "https://planificateur.a-contresens.net/afrique/pays-TN-tunisie.html",
    "https://voyageforum.com/rechercher/aller-en-novembre-en-tunisie-d5515273/",
    "https://www.ou-et-quand.net/vols/tunisie/tunis/",
    "https://touringtravel.tn/voyages-a-la-carte/liste",
    "https://www.ou-et-quand.net/preparer-son-voyage/tunisie/conseils/",
    "https://lesglobeblogueurs.com/visite-tunisie/",
    "https://www.nadiallita.com/post/itin%C3%A9raire-de-15-jours-en-tunisie",
    "https://edit.org/fr/blog/modeles-itineraires-de-voyage-impression",
    "https://mademoisellebonplan.fr/2020/01/24/voyage-en-tunisie-decouvrir-tunis/",
    "https://www.promovacances.com/vacances-sejour-hotel/voyage-inde/?utm_source=google&utm_medium=cpc&utm_campaign=PMVC%20-%20Performance%20Max%20-%20Tunisie&utm_id=21742443275&gad_source=1&gclid=CjwKCAjwvKi4BhABEiwAH2gcw-rJQArKdM_79rsj_y8KMmgKDyX1r8p5YoeIMYVFkTuCi9pJPRkwRxoCfkYQAvD_BwE#activeEngineType=voyage&durationRangeMax=9&durationRangeMin=5&departureDate=28/02/2025&flexi=60&themespace=sejour-voyage&destinationsZones=1687&destinationLabel=Inde&destinationType=ZONE",
    "https://www.tunisiepromo.tn/hotel/hotel-ain-drahem/el-mouradi-hammam-bourguiba/2025-04-15/7?pays=tn",
    "https://www.promovacances.com/vacances/vacances-et-sejours/voyage-tout-inclus-tunisie/theme,7/pays,219/ville,/#activeEngineType=voyage&durationRangeMax=9&durationRangeMin=5&departureDate=30/11/2024&flexi=60&themes=7&themespace=vacances-et-sejours&destinationsZones=1849&destinationLabel=Tunisie&destinationType=ZONE",
    "https://www.tourmag.com/Organiser-son-voyage-en-Tunisie_a112253.html",
    "https://www.routard.com/fr/guide/a/itineraires-conseilles/afrique/tunisie#une-semaine-en-tunisie",
    "https://www.edreams.fr/vol/tunis/TUN/",
    "https://www.ou-et-quand.net/budget/tunisie/",
    "https://voyages.carrefour.fr/accueil/sejour-etranger",
    "https://www.skyscanner.fr/itineraires/tun/pari/tunis-carthage-a-paris.html?&utm_source=google&utm_medium=cpc&utm_campaign=XY-Flights-Search-FR-DSA&utm_term=DYNAMIC+SEARCH+ADS&associateID=SEM_FLI_19465_00000&campaign_id=13523065083&adgroupid=118778511250&keyword_id=dsa-932305094831&gad_source=1&gclid=CjwKCAjwvKi4BhABEiwAH2gcw6qOlAcYhQ7bW1ZxD3RBgS5RGku0OhZ4vqZgbf_6qxrAqyCOjsortRoCyJ0QAvD_BwE&gclsrc=aw.ds",
    "https://planificateur.a-contresens.net/budget-pays-FR-france.html",
    "https://www.clicktripz.com/c24k/v1/index.html?pageview_uuid=null&alias=0b3700c807ea4eef984e7c654079e1c9_ou-et-quand.net&siteName=ou-et-quand.net&ctzpid=4fc901fb-7a4d-4c7c-9a97-b5a87288491e&product=interstitial&siteId=0b3700c807ea4eef984e7c654079e1c9_ou-et-quand.net&publisherHash=0b3700c807ea4eef984e7c654079e1c9&aid=be8029b1-2a95-478b-b1b1-be6f080beef9_desktop_interstitial&optMaxChecked=2&optMaxAdvertisers=7&optRotationStrategy=1&optPopUnder=1&optLocalization=fr&trafficSource=https%3A%2F%2Fwww.google.com",
    "https://tripkygo.com/guides-pays",
    "https://www.ef.tn/fr/blog/language/les-4-meilleures-destinations-pour-des-vacances-intelligentes/",
    "https://www.routard.com/fr/guide/a/itineraires-conseilles/afrique/tunisie",
    "https://www.mifuguemiraison.com/fr/voyage-tunisie-conseils-itineraire/",
    "https://tripkygo.com/",
    "https://tripkygo.com/planificateur-voyage/83877",
    "https://tn.tunisiebooking.com/hotels-tunisie.html",
    "https://www.booking.com/country/it.fr.html",
    "https://www.kayak.fr/news/destinations-plage-pres-de-france/",
    "https://lemagdelaconso.ouest-france.fr/dossier-326-top-10-des-destinations-de-vacances-au-soleil-pas-cheres.html",
    "https://www.promovacances.com/vacances-sejour-hotel/voyage-tunisie/?utm_source=google&utm_medium=cpc&utm_campaign=PMVC%20-%20Performance%20Max%20-%20Tunisie",
    "https://www.globe-trotting.com/le-top-des-voyages-sans-touristes",
    "https://www.trip.com/hotels/list/searchresults?city=789&hotelid=9437839&locale=en_xx",
    "https://www.exotismes.fr/voyages/6-sejour-martinique/13459-karibea-caribia.jsf?mtm_campaign=FDF&mtm_source=Googleads&mtm_group=googleads2023&gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL89e2k4G_TZv_i_5pu2QfMtHX7JVTZzkuh8GfUvR0vmHbDBcODGpFRoClKgQAvD_BwE",
    "https://www.mifuguemiraison.com/fr/voyage-tunisie-conseils-itineraire/",
    "https://pass-rome.fr/rome-3-jours/?gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL3QCh62wslhTB704irHyaXseeS4wqs3PAX_AacBxEICrRCWghNvRixoCQbQQAvD_BwE",
    "https://www.booking.com/country/fr.fr.html?aid=301664;label=fr-a59Z6Y2V6pKlPBCsd1nIrwS525562346389:pl:ta:p157000:p2:ac:ap:neg:fi:tikwd-2584518484:lp9198474:li:dec:dm:pp"
]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction d'envoi d'e-mail
def send_email(subject, body, from_email, password, to_email):
    # Configuration du contenu de l'email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        # Connexion au serveur SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Identifie avec le serveur SMTP
        server.starttls()  # Sécurise la connexion
        server.ehlo()  # Identifie à nouveau après le chiffrement
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        
        return "Email envoyé avec succès."
    except Exception as e:
        return f"Erreur lors de l'envoi de l'email : {e}"


# Fonction de scraping
@st.cache_data(show_spinner=False)
def scrape_website(url):
    """Scraper un site web et extraire le texte principal."""
    try:
        response = requests.get(url, timeout=10)  # Timeout de 10 secondes
        response.raise_for_status()  # Vérifie si la requête a réussi
    except requests.exceptions.Timeout:
        st.error(f"Le site {url} a mis trop de temps à répondre.")
        return ""
    except requests.RequestException as e:
        st.error(f"Erreur lors de l'accès à {url} : {e}")
        return ""
    
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text

# Fonction pour charger la base de données
@st.cache_resource(show_spinner=False)
def load_db(urls, chain_type, k):
    """Charge les données depuis des sites web pour créer une base de recherche."""
    documents = []
    for url in urls:
        scraped_text = scrape_website(url)
        if scraped_text:
            documents.append(Document(page_content=scraped_text))

    # Diviser les documents en segments de texte
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    # Créer des embeddings à partir des documents
    embeddings = OpenAIEmbeddings()
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)

    # Créer le retriever pour la recherche par similarité
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})

    # Créer la chaîne de conversation avec retrieval
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0),
        chain_type=chain_type,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa

class Chatbot:
    def __init__(self):
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        self.qa = None

    def load_urls(self, urls):
        """Charger et initialiser la base de données depuis des URLs."""
        self.qa = load_db(urls, "stuff", 4)
        return "Les données ont été chargées avec succès."

    def conversation(self, query):
        if not query:
            return "Veuillez entrer une question."
        if not self.qa:
            return "Veuillez charger des URLs pour initialiser la base de données."
        
        result = self.qa({"question": query, "chat_history": st.session_state["chat_history"]})
        st.session_state["chat_history"].append((query, result["answer"]))
        return result['answer']

# Initialiser le chatbot
cb = Chatbot()

# Interface utilisateur
st.title(":blue[Bienvenue sur]")
st.title("Planificateur de voyages :sunglasses:")
st.write("Planifiez vos vacances, road-trips ou tours du monde en créant votre itinéraire de voyage....")

# Saisie de la clé API avec disparition automatique après validation
if "api_key_verified" not in st.session_state:
    ask_api_key()
else:
    st.info("")

# Charger les URLs pour initialiser la base de données
cb.load_urls(urls)
st.success("Cool.")

# Fonction pour réinitialiser le chat
def reset_chat():
    st.session_state["chat_history"] = []

# Bouton pour démarrer un nouveau chat
if st.sidebar.button("💬", help="démarrer un nouveau chat."):
    reset_chat()

# Afficher l'historique dans la barre latérale
with st.sidebar:
    st.subheader("Historique")
    if st.session_state["chat_history"]:
        for exchange in st.session_state["chat_history"]:
            st.write(f"**Utilisateur :** {exchange[0]}")
            st.write(f"**Planificateur :** {exchange[1]}")

# Champ de saisie pour poser des questions
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Fonction pour soumettre la requête
def submit():
    if st.session_state["user_input"]:
        response = cb.conversation(st.session_state["user_input"])
        st.session_state["user_input"] = ""  # Efface la saisie après soumission

# Afficher l'historique avant de soumettre
if st.session_state["chat_history"]:
    for exchange in st.session_state["chat_history"]:
        st.markdown(f"**Utilisateur :** {exchange[0]}")
        st.write(f"**Planificateur :** {exchange[1]}")

# Champ de saisie
st.text_input("Comment puis-je vous aider ?", value=st.session_state["user_input"], key="user_input", on_change=submit)

# Gestion de la négociation et de la planification
col1, col2 = st.columns(2)

# Afficher le bouton Négociation dans la première colonne
with col1:
    if st.button("Négociation"):
        st.session_state["negociation_active"] = True

# Afficher le bouton Planifier le voyage dans la deuxième colonne
with col2:
    if st.button("Planifier le voyage"):
        st.session_state["planification_active"] = True

# Formulaire de négociation si activé
if st.session_state.get("negociation_active", False):
    st.write("Entrez vos préférences de voyage pour obtenir une meilleure offre.")
    
    # Formulaire de négociation
    destination = st.text_input("Destination :", value="Tunisie")
    budget = st.number_input("Budget (en euros) :", min_value=100, value=1000, step=100)
    preferences = st.text_area("Préférences spécifiques (transport, logement, activités, etc.)")

    # Saisie des informations de l'utilisateur pour l'envoi de l'email
    from_email = st.text_input("Votre email :", placeholder="Entrez votre email")
    password = st.text_input("Mot de passe de votre email :", type="password", placeholder="Entrez votre mot de passe")
    to_email = st.text_input("Email du destinataire :", placeholder="Entrez l'email du destinataire")

    # Bouton pour soumettre la négociation
    if st.button("Soumettre la négociation"):
        st.write(f"Vous avez choisi la destination **{destination}** avec un budget de **{budget}€**.")
        st.write(f"Vos préférences : **{preferences if preferences else 'Pas de préférences spécifiées'}**.")
        
        # Créer le contenu de l'e-mail
        negotiation_data = f"Destination : {destination}\nBudget : {budget}€\nPréférences : {preferences if preferences else 'Pas de préférences spécifiées'}"
        
        # Envoyer l'e-mail
        email_status = send_email("Négociation de voyage", negotiation_data, from_email, password, to_email)
        st.write(email_status)
        
        st.success("Votre négociation a été envoyée avec succès par e-mail !")
        st.session_state["negociation_active"] = False

# Formulaire de planification si activé
if st.session_state.get("planification_active", False):
    st.write("Entrez les détails pour planifier votre voyage.")
    
    start_date = st.date_input("Date de départ :", value=date.today())
    end_date = st.date_input("Date de retour :", value=date.today())
    activities = st.text_area("Activités prévues :")

    # Saisie des informations de l'utilisateur pour l'envoi de l'email
    from_email = st.text_input("Votre email :", placeholder="Entrez votre email")
    password = st.text_input("Mot de passe de votre email :", type="password", placeholder="Entrez votre mot de passe")
    to_email = st.text_input("Email du destinataire :", placeholder="Entrez l'email du destinataire")

    # Bouton pour soumettre la planification
    if st.button("Soumettre la planification"):
        st.write(f"Voyage planifié du **{start_date}** au **{end_date}**.")
        st.write(f"Activités prévues : **{activities if activities else 'Aucune activité spécifiée'}**.")
        
        planification_data = f"Voyage du {start_date} au {end_date}\nActivités prévues : {activities if activities else 'Aucune activité spécifiée'}"
        
        # Envoyer l'e-mail
        email_status = send_email("Planification de voyage", planification_data, from_email, password, to_email)
        st.write(email_status)
        
        st.success("Votre planification a été envoyée avec succès par e-mail !")
        st.session_state["planification_active"] = False
