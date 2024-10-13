from io import StringIO
import streamlit as st  # Importer Streamlit
import os
import openai
import sys
from langchain.embeddings import OpenAIEmbeddings

#from langchain.vectorstores import DocArrayInMemorySearch  # ou langchain_community.vectorstores
from langchain.document_loaders import PyPDFLoader  # ou langchain_community.document_loaders
from langchain.chat_models import ChatOpenAI  # ou langchain_community.chat_models

#from langchain_community.embeddings import OpenAIEmbeddings
#from langchain_community.vectorstores import DocArrayInMemorySearch
#from langchain_community.chat_models import ChatOpenAI

from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from PyPDF2 import PdfWriter, PdfReader
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

sys.path.append('../..')

# Charger les variables d'environnement
_ = load_dotenv(find_dotenv())  # Lire le fichier .env local

openai.api_key = 'sk-49RoKskvSfdc2VsgMcH3qhm5l8_pjH4E9tFt74pKLlT3BlbkFJraXhQF7U8iuyisdldJVIDMCmES89P83MrvdBNjSfMA'
os.environ["OPENAI_API_KEY"] = openai.api_key

llm_name = "gpt-3.5-turbo"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
os.environ["LANGCHAIN_API_KEY"] = "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"
# URLs à charger
urls = [
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
    "https://www.fr.lastminute.com/sejour/tn_tunisie",
    "https://www.tourmag.com/Organiser-son-voyage-en-Tunisie_a112253.html",
    "https://www.fr.lastminute.com/sejour/tn_tunisie/tunis-d1507155014?cq_plac=&cq_net=g&cq_med=&cq_plt=gp&cq_cmp=21393360673&cq_con=163540753813&cq_term=voyage%20tunis&cq_src=google_ads&cq_pos=&utm_source=google&utm_medium=cpc&utm_campaign=LMN_FR-INT_DP_autofeed-SE_nonbrand_Destination-Beach_FR_Mix_Google_1&gad_source=1&gclid=CjwKCAjwvKi4BhABEiwAH2gcw3WJJoK3f-XnoBe5jxv4AQwCmQIwTYTsfDqmHUWLZ4Ni6aMkOhEZoxoCRcgQAvD_BwE&gclsrc=aw.ds"
    "https://www.petitfute.com/idees-de-sejours/5753-l-essentiel-de-la-tunisie-en-trois-semaines.html",
    "https://www.routard.com/fr/guide/a/itineraires-conseilles/afrique/tunisie#une-semaine-en-tunisie",
    "https://www.edreams.fr/vol/tunis/TUN/",
    "https://www.ou-et-quand.net/budget/tunisie/",
    "https://voyages.carrefour.fr/accueil/sejour-etranger",
    "https://www.skyscanner.fr/itineraires/tun/pari/tunis-carthage-a-paris.html?&utm_source=google&utm_medium=cpc&utm_campaign=XY-Flights-Search-FR-DSA&utm_term=DYNAMIC+SEARCH+ADS&associateID=SEM_FLI_19465_00000&campaign_id=13523065083&adgroupid=118778511250&keyword_id=dsa-932305094831&gad_source=1&gclid=CjwKCAjwvKi4BhABEiwAH2gcw6qOlAcYhQ7bW1ZxD3RBgS5RGku0OhZ4vqZgbf_6qxrAqyCOjsortRoCyJ0QAvD_BwE&gclsrc=aw.ds",
    "https://www.exotismes.fr/voyages/6-sejour-martinique/13437-carayou-hotel-spa-tout-compris.jsf?mtm_campaign=FDF&mtm_source=Googleads&mtm_group=googleads2023&gclid=CjwKCAjwvKi4BhABEiwAH2gcw0PksRLpwcKZjt0Hc1ypHPsC4LZAcquBAujCnoVlW2QZ7xXjKxrSuhoCwwYQAvD_BwE",
    "https://planificateur.a-contresens.net/budget-pays-FR-france.html",
    "https://www.clicktripz.com/c24k/v1/index.html?pageview_uuid=null&alias=0b3700c807ea4eef984e7c654079e1c9_ou-et-quand.net&siteName=ou-et-quand.net&ctzpid=4fc901fb-7a4d-4c7c-9a97-b5a87288491e&product=interstitial&siteId=0b3700c807ea4eef984e7c654079e1c9_ou-et-quand.net&publisherHash=0b3700c807ea4eef984e7c654079e1c9&aid=be8029b1-2a95-478b-b1b1-be6f080beef9_desktop_interstitial&optMaxChecked=2&optMaxAdvertisers=7&optRotationStrategy=1&optPopUnder=1&optLocalization=fr&trafficSource=https%3A%2F%2Fwww.google.com%2F&adults=1&destination=Tunis%2C%20Tunisie%2C%20TN&audiences=%5Bobject%20Object%5D&enabled=true&tabbedMode=1&userForcedTabbedMode=1&campaignIDs[0]=25882&&campaignNames[0]=Booking.com&isOneWay=false&city=Tunis%2C%20Tunisie%2C%20TN&guests=1&rooms=1&numTravelers=1&type=1&checkInDate=10%2F20%2F2024&checkOutDate=10%2F21%2F2024&publisherAlias=0b3700c807ea4eef984e7c654079e1c9_ou-et-quand.net&publisherID=3495&referralURL=usingRuntimeExperiments%7C%7Cfalse%3A%3A%3AvscVersion%7C%7C387%3A%3A%3Ahttps%3A%2F%2Fwww.ou-et-quand.net%2Fbudget%2Ftunisie%2F&hostname=www.clicktripz.com&isPopUnder=true&searchKey=67fccf4f51279c60e89d3db8b304dc11&auctionType=100&productType=exit_unit&maxSearchesPerDay=9999&hardLimitSearchCap=9999&hardLimitSearchCapSeconds=86400&notifyNoCaps=false&auction_id=3a110dad-45d4-4ee5-b726-478171f42a77&adUnit=interstitial&generator=ctCore&device=Desktop",
    "https://tripkygo.com/guides-pays",
    "https://www.ef.tn/fr/blog/language/les-4-meilleures-destinations-pour-des-vacances-intelligentes/",
    "https://www.routard.com/fr/guide/a/itineraires-conseilles/afrique/tunisie",
    "https://www.mifuguemiraison.com/fr/voyage-tunisie-conseils-itineraire/",
    "https://www.exotismes.fr/voyages/6-sejour-martinique/13459-karibea-caribia.jsf?mtm_campaign=FDF&mtm_source=Googleads&mtm_group=googleads2023&gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL89e2k4G_TZv_i_5pu2QfMtHX7JVTZzkuh8GfUvR0vmHbDBcODGpFRoClKgQAvD_BwE",
    "https://tripkygo.com/",
    "https://tn.tunisiebooking.com/hotels-tunisie.html",
    "https://fr.hotels.com/co10233055/hotels-en-france/",
    "https://www.booking.com/country/it.fr.html",
    "https://www.kayak.fr/news/destinations-plage-pres-de-france/",
    "https://lemagdelaconso.ouest-france.fr/dossier-326-top-10-des-destinations-de-vacances-au-soleil-pas-cheres.html",
    "https://www.promovacances.com/vacances-sejour-hotel/voyage-tunisie/?utm_source=google&utm_medium=cpc&utm_campaign=PMVC%20-%20Performance%20Max%20-%20Tunisie",
    "https://www.globe-trotting.com/le-top-des-voyages-sans-touristes",
    "https://www.trip.com/hotels/list/searchresults?city=789&hotelid=9437839&locale=en_xx",
    "https://www.exotismes.fr/voyages/6-sejour-martinique/13459-karibea-caribia.jsf?mtm_campaign=FDF&mtm_source=Googleads&mtm_group=googleads2023&gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL89e2k4G_TZv_i_5pu2QfMtHX7JVTZzkuh8GfUvR0vmHbDBcODGpFRoClKgQAvD_BwE",
    "https://www.mifuguemiraison.com/fr/voyage-tunisie-conseils-itineraire/",
    "https://pass-rome.fr/rome-3-jours/?gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL3QCh62wslhTB704irHyaXseeS4wqs3PAX_AacBxEICrRCWghNvRixoCQbQQAvD_BwE",
    "https://www.liligo.fr/?gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL4jlXrFfb4e9107JQOjtzFsoNOstvn3MxTMFybw2jHzyV7ah4qUHMhoCZxMQAvD_BwE",
    "https://www.booking.com/country/fr.fr.html?aid=301664;label=fr-a59Z6Y2V6pKlPBCsd1nIrwS525562346389:pl:ta:p157000:p2:ac:ap:neg:fi:tikwd-2584518484:lp9198474:li:dec:dm:ppccp=UmFuZG9tSVYkc2RlIyh9YSNxgVPQVI7AMnn1KDvPMRs;ws=&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL83Kz6W5O4POUHNo1NTzEt1hSmOfUIwQJKlwMurtsZxYEv5mRjNFNhoCqpoQAvD_BwE",
    "https://fr.wikipedia.org/wiki/Liste_des_h%C3%B4tels_class%C3%A9s_cinq_%C3%A9toiles_en_France",
    "https://www.govoyages.com/vols-pas-cher/?mktportal=google&utm_id=go_cmp-1419601141_adg-56542546780_ad-636638937113_kwd-10488051_dev-c_ext-_locphy-9198474_mtype-b_ntw-g&gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL0eWBjRbP0hTyN3vVffQ-QdWPKh217OIYzMg-D-pEAlNn70Ny1IL0xoCHpwQAvD_BwE",
    "https://www.evaneos.fr/italie/?utm_source=google&utm_medium=cpc&utm_campaign=G_DES_CTH-Italie_FR_fr_FR_D:10&utm_term=tourisme%20italie&gad_source=1&gclid=CjwKCAjwmaO4BhAhEiwA5p4YL3hSwhZYxcx0uEXT5d_3KWU-Ww4fJ9oJO8nNwu2W8DawDV_hHdDzSxoCafYQAvD_BwE&gclsrc=aw.ds"
]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Fonction pour scraper un site web
def scrape_website(url):
    """Scraper un site web et extraire le texte principal."""
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Supposons que le texte pertinent soit dans des balises <p> (paragraphe)
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text

# Fonction pour charger la base de données à partir d'URLs
def load_db(urls, chain_type, k):
    """Charge les données depuis des sites web pour créer une base de recherche."""
    # Scraper et combiner le contenu des sites web
    documents = []
    for url in urls:
        scraped_text = scrape_website(url)
        # Créer un document avec un attribut 'page_content'
        documents.append(Document(page_content=scraped_text))

    # Diviser les documents en segments de texte
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    # Créer des embeddings à partir des documents
    embeddings = OpenAIEmbeddings()
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)

    # Créer le retriever qui fera la recherche par similarité
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
        return "Cool."

    def conversation(self, query):
        if not query:
            return "Veuillez entrer une question."
        if not self.qa:
            return "Veuillez charger des URLs pour initialiser la base de données."
        
        result = self.qa({"question": query, "chat_history": st.session_state["chat_history"]})
        # Ajouter à l'historique
        st.session_state["chat_history"].append((query, result["answer"]))
        return result['answer']

# Initialiser le chatbot
cb = Chatbot()

# Interface utilisateur
st.title(":blue[Bienvenue sur]")
st.title("Planificateur de voyages :sunglasses:")
st.write("Planifiez vous-mêmes vos vacances, road-trips ou tours du monde en créant votre itinéraire de voyage....")

# Charger les URLs au démarrage
cb.load_urls(urls)
st.success("Cool.")

# Afficher l'historique dans la barre latérale à gauche
with st.sidebar:
    st.subheader("Historique")
    if st.session_state["chat_history"]:
        for exchange in st.session_state["chat_history"]:
            st.write(f"**Utilisateur :** {exchange[0]}")
            st.write(f"**Planificateur :** {exchange[1]}")

# Champ de saisie pour poser des questions
user_input = st.text_input("Comment puis-je vous aider ?")

if user_input:
    # Ajouter la réponse du chatbot
    bot_response = cb.conversation(user_input)
    # Afficher la conversation dans la page principale
    st.markdown(f"**Utilisateur**: {user_input}")
    st.markdown(f"**Planificateur**: {bot_response}")
