import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import pydeck as pdk
import streamlit.components.v1 as components


# 1. Configurazione della pagina
st.set_page_config(layout="wide", page_title="App Tour de France")


# ==========================================
# FUNZIONE PER CARICARE I DATI 
# ==========================================
@st.cache_data
def load_all_datasets():
    # Link ai dataset esistenti
    url_storico = "https://docs.google.com/spreadsheets/d/1hI6y5tDpw176v0DhJN-P5hzsmXrtRSB0/export?format=xlsx"
    url_stage_h = "https://docs.google.com/spreadsheets/d/1bYnt9BfbKk-HMYR8bekqQfaKH02eZBWq/export?format=xlsx" 
    url_tour_w = "https://docs.google.com/spreadsheets/d/1GrXwBG2Cda93AvOsWa-oDT19gwWCaF-2/export?format=xlsx"
    
    # 1. NUOVO LINK GOOGLE DRIVE PER LE COORDINATE
    url_coords = "https://docs.google.com/spreadsheets/d/1NoKnm0M5WCKIwTvu2wwGEWRgG3EKBoeJ/export?format=xlsx"
    # Caricamento file esistenti
    try:
        df_storico = pd.read_excel(url_storico, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Storico: {e}")
        df_storico = pd.DataFrame()

    try:
        df_stage_h = pd.read_excel(url_stage_h, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Stage_h: {e}")
        df_stage_h = pd.DataFrame()

    try:
        df_tour_w = pd.read_excel(url_tour_w, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Tour_w: {e}")
        df_tour_w = pd.DataFrame()

    # 2. CARICAMENTO NUOVO FILE COORDINATE
    try:
        df_coords = pd.read_excel(url_coords, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Coordinate: {e}")
        df_coords = pd.DataFrame()
    
    # Filtro Anno: dal 1913 in poi
    if not df_storico.empty and 'Year' in df_storico.columns:
        df_storico = df_storico[df_storico['Year'] >= 1913]
        
    if not df_stage_h.empty and 'Year' in df_stage_h.columns:
        df_stage_h = df_stage_h[df_stage_h['Year'] >= 1913]
        
    if not df_tour_w.empty and 'Year' in df_tour_w.columns:
        df_tour_w = df_tour_w[df_tour_w['Year'] >= 1913]

    # Applichiamo il filtro anche al nuovo dataframe se necessario
    if not df_coords.empty and 'Year' in df_coords.columns:
        df_coords = df_coords[df_coords['Year'] >= 1913]

    return df_storico, df_stage_h, df_tour_w, df_coords

# 3. CHIAMATA 
df_storico, df_stage_h, df_tour_w, df_coords = load_all_datasets()

# 1. Configurazione della pagina
st.set_page_config(layout="wide", page_title="App Tour de France")

# ==========================================
# 2. GESTIONE DELLA NAVIGAZIONE (CORE LOGIC)
# ==========================================

# A. Se l'utente clicca sul logo, l'URL conterrà "?nav=home". Lo intercettiamo:
if "nav" in st.query_params and st.query_params["nav"] == "home":
    st.session_state.pagina_corrente = "home"
    del st.query_params["nav"] # Puliamo l'URL dopo averlo letto

# B. Inizializziamo lo stato se è la prima volta che si apre l'app
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "home"


# ==========================================
# 3. CSS E STILE DELLA BARRA NERA E SFONDO
# ==========================================
st.markdown("""
    <style>
    /* ---> 1. IMPORTIAMO IL FONT GIORNALISTICO DA GOOGLE FONTS <--- */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

    /* ---> 2. APPLICHIAMO IL FONT A TUTTI I TESTI DELL'APP <--- */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Merriweather', Georgia, 'Times New Roman', serif !important;
        color: #FFFFFF !important;
    }

    /* ---> 3. SFONDO GIALLO GIORNALE <--- */
    .stApp {
        background-color: #F4F1EA; /* Un giallo carta antico/giornale molto elegante */
    }

    /* Nasconde la barra spaziatrice superiore di default di Streamlit */
    [data-testid="stHeader"] { 
        display: none; 
    }
    
    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sfondo nero per l'intera riga della navigazione */
    [data-testid="stHorizontalBlock"] {
        background-color: #000000;
        align-items: center;
        padding: 10px 20px;
        margin-bottom: 20px;
    }
    
    /* Stile base dei bottoni (i bottoni manterranno il font scelto sopra!) */
    div.stButton > button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        border-bottom: 4px solid transparent !important; 
        border-radius: 0px !important;
        box-shadow: none !important;
        font-weight: bold;
        font-size: 16px;
        letter-spacing: 1px;
        padding-bottom: 8px;
        transition: border-color 0.2s ease-in-out;
    }
    
    /* Effetto hover (quando passi il cursore) */
    div.stButton > button:hover, 
    div.stButton > button:focus, 
    div.stButton > button:active {
        color: #FFFFFF !important;
        border-bottom: 4px solid #FFCC00 !important;
        background-color: transparent !important;
    }
    
    [data-testid="column"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    [data-testid="stMarkdownContainer"] p {
        margin-bottom: 0 !important;
    }
    
    /* Margini per il contenuto delle pagine sotto la barra */
    /* Margini globali per il contenuto di tutte le pagine sotto la barra nera */
.contenuto-pagina {
    padding: 2rem 7% !important; /* Aumenta il rientro laterale al 7% della larghezza dello schermo */
    max-width: 1400px;           /* Evita che il testo si allarghi troppo su schermi giganti */
    margin: 0 auto;              /* Centra perfettamente tutto il blocco nella pagina */
}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. COSTRUZIONE DELLA BARRA DI NAVIGAZIONE
# ==========================================
col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5], vertical_alignment="center")

with col1:
    # Se clicchi, lo stato cambia in "classifica"
    if st.button("STANDINGS", use_container_width=True):
        st.session_state.pagina_corrente = "classifica"
with col2:
    if st.button("RIDERS", use_container_width=True):
        st.session_state.pagina_corrente = "corridori"

with col3:
    url_logo = "https://www.brandforum.it/wp-content/uploads/2019/03/38020191021104459.png"
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; transform: translateY(-8px);">
            <a href="?nav=home" target="_self" title="Back to Home">
                <img src="{url_logo}" 
                     style="width: 100%; max-width: 140px; background-color: white; padding: 2px 8px; border-radius: 8px; cursor: pointer;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    if st.button("STAGES", use_container_width=True):
        st.session_state.pagina_corrente = "tappe"

with col5:
    if st.button("TEAMS", use_container_width=True):
        st.session_state.pagina_corrente = "teams"

# ==========================================
# 5. CONTENUTO DELLE PAGINE
# ==========================================
st.markdown('<div class="contenuto-pagina">', unsafe_allow_html=True)


if st.session_state.pagina_corrente == "home":

    URL_HERO      = "https://cdn.artphotolimited.com/images/5c2e191bd96b2e012e7a7fc5/1000x1000/tour-de-france-1937.jpg"
    URL_CAV       = "https://imgresizer.eurosport.com/unsafe/1200x0/filters:format(jpeg)/origin-imgresizer.eurosport.com/2021/06/29/3163795-64831628-2560-1440.jpg"
    URL_POIS      = "https://lh3.googleusercontent.com/d/1sOEebeyDAuhP0Mt6I5L4poKbahfv3xky"
    URL_ALPE      = "https://static.independent.co.uk/2022/07/13/21/GettyImages-51103079.jpg"
    URL_DESGRANGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Henri_Desgrange_1914.jpg/960px-Henri_Desgrange_1914.jpg"
    FULL_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&display=swap');

    body {
        margin: 0;
        padding: 0;
        background-color: #F4F1EA;
    }
    .np {
      font-family: 'Merriweather', Georgia, 'Times New Roman', serif;
      color: #111;
      background: #F4F1EA;
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 0 60px 0;
    }
    .np-masthead { border-top: 6px solid #111; border-bottom: 3px solid #111; padding: 12px 16px 8px; text-align: center; }
    .np-date { font-size: 11px; letter-spacing: 2px; color: #666; text-transform: uppercase; margin-bottom: 4px; font-family: Arial, sans-serif; }
    .np-logo { font-size: 58px; font-weight: 900; font-style: italic; line-height: 1; color: #111; letter-spacing: -2px; }
    .np-tagline { font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: #666; font-family: Arial, sans-serif; border-top: 1px solid #bbb; margin-top: 6px; padding-top: 5px; }
    .np-ribbon { background: #111; color: #F4F1EA; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; text-align: center; padding: 5px 0; font-family: Arial, sans-serif; margin-bottom: 14px; }
    .np-kpi { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 2px solid #111; border-bottom: 1px solid #bbb; margin: 0 16px 16px; }
    .np-kpi-cell { text-align: center; padding: 10px 8px; border-right: 1px solid #bbb; }
    .np-kpi-cell:last-child { border-right: none; }
    .np-kpi-num { font-size: 30px; font-weight: 900; color: #111; line-height: 1; }
    .np-kpi-lbl { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: #777; font-family: Arial, sans-serif; margin-top: 2px; }
    .np-main { display: grid; grid-template-columns: 2fr 1fr; gap: 0; padding: 0 16px 16px; border-bottom: 2px solid #111; margin-bottom: 16px; }
    .np-lead { padding-right: 20px; border-right: 1px solid #bbb; }
    .np-sidebar { padding-left: 16px; display: flex; flex-direction: column; gap: 14px; }
    .np-section-tag { font-size: 10px; letter-spacing: 3px; text-transform: uppercase; font-family: Arial, sans-serif; color: #111; font-weight: 700; display: block; margin-bottom: 4px; }
    .np-rule { border: none; border-top: 2px solid #111; margin: 4px 0 8px; }
    .np-rule-thin { border: none; border-top: 1px solid #bbb; margin: 10px 0; }
    .np-headline-xl { font-size: 34px; font-weight: 900; line-height: 1.05; color: #111; margin-bottom: 8px; }
    .np-deck { font-size: 14px; font-style: italic; color: #333; border-left: 3px solid #111; padding-left: 10px; margin-bottom: 10px; line-height: 1.45; }
    .np-body { font-size: 12.5px; line-height: 1.7; color: #222; column-count: 2; column-gap: 16px; }
    .np-body p { margin-bottom: 8px; }
    .np-drop::first-letter { font-size: 50px; font-weight: 900; float: left; line-height: 0.8; margin: 6px 6px 0 0; color: #111; }
    .np-photo { 
      width: 100%; 
      height: 240px; /* Alziamo un po' la foto per dare più respiro all'immagine */
      object-fit: cover; 
      object-position: center 85%; /* 🪄 IL TRUCCO: sposta il ritaglio verso il basso, inquadrando le bici! */
      filter: grayscale(100%) contrast(1.1); 
      margin-bottom: 4px; 
      display: block; 
    }
    .np-photo-sm { 
      width: 100%; 
      height: 120px; 
      object-fit: cover; 
      object-position: center 15%; /* Per le foto piccole (es. Cavendish) salva la parte alta con i visi */
      filter: grayscale(100%) contrast(1.1); 
      margin-bottom: 4px; 
      display: block; 
    }
    .np-modal-img { 
      width: auto !important;
      max-width: 100%; 
      height: auto !important;             
      max-height: 380px;        /* Dà respiro al ritratto senza uscire dallo schermo */
      object-fit: contain !important;      
      object-position: center;  
      filter: grayscale(100%) contrast(1.1); 
      margin: 0 auto 15px auto; 
      display: block; 
    }
    .np-caption { font-size: 10px; color: #666; font-style: italic; text-align: right; font-family: Arial, sans-serif; margin-bottom: 8px; }
    .np-side-art { cursor: pointer; padding: 4px 2px; transition: background 0.15s; }
    .np-side-art:hover { background: rgba(0,0,0,0.04); }
    .np-side-tag { font-size: 9px; letter-spacing: 2px; text-transform: uppercase; font-family: Arial, sans-serif; color: #888; display: block; margin-bottom: 2px; }
    .np-side-hl { font-size: 14px; font-weight: 700; line-height: 1.2; color: #111; margin-bottom: 4px; }
    .np-side-body { font-size: 11px; line-height: 1.55; color: #555; }
    .np-read-more { font-size: 9.5px; color: #111; font-family: Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; text-decoration: underline; cursor: pointer; margin-top: 3px; display: inline-block; }
    .np-pullquote { border-top: 2px solid #111; border-bottom: 2px solid #111; padding: 10px 4px; text-align: center; font-size: 14px; font-style: italic; line-height: 1.35; color: #111; margin-top: 4px; }
    .np-pullquote-attr { font-size: 10px; margin-top: 6px; color: #666; font-style: normal; font-family: Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; }
    .np-bottom { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; padding: 0 16px; margin-bottom: 20px; }
    .np-bot-art { padding: 0 16px 0 0; border-right: 1px solid #bbb; cursor: pointer; transition: background 0.15s; }
    .np-bot-art:hover { background: rgba(0,0,0,0.03); }
    .np-bot-art:last-child { border-right: none; padding-right: 0; padding-left: 16px; }
    .np-bot-art:nth-child(2) { padding-left: 16px; }
    .np-bot-hl { font-size: 16px; font-weight: 900; line-height: 1.15; color: #111; margin-bottom: 6px; }
    .np-bot-body { font-size: 11px; line-height: 1.6; color: #444; }
    .np-bot-byline { font-size: 9px; color: #888; font-family: Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; margin-top: 6px; }
    .np-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.58); z-index: 9999; align-items: flex-start; justify-content: center; padding-top: 5vh; }
    .np-overlay.open { display: flex; }
    .np-modal { background: #F4F1EA; border-top: 6px solid #111; max-width: 600px; width: 92%; padding: 28px 30px; position: relative; max-height: 82vh; overflow-y: auto; font-family: 'Merriweather', Georgia, serif; }
    .np-modal-close { position: absolute; top: 12px; right: 16px; font-size: 24px; cursor: pointer; color: #111; background: none; border: none; font-family: Georgia, serif; line-height: 1; }
    .np-modal-tag { font-size: 10px; letter-spacing: 3px; text-transform: uppercase; font-family: Arial, sans-serif; color: #888; display: block; margin-bottom: 6px; }
    .np-modal-title { font-size: 26px; font-weight: 900; line-height: 1.1; color: #111; margin-bottom: 10px; }
    .np-modal-deck { font-style: italic; font-size: 14px; color: #333; border-left: 3px solid #111; padding-left: 10px; margin-bottom: 14px; line-height: 1.45; }
    .np-modal-img { width: 100%; height: 200px; object-fit: cover; filter: grayscale(100%) contrast(1.1); margin-bottom: 6px; display: block; }
    .np-modal-caption { font-size: 10px; color: #666; font-style: italic; text-align: right; font-family: Arial, sans-serif; margin-bottom: 12px; }
    .np-modal-body { font-size: 13px; line-height: 1.75; color: #222; }
    .np-modal-body p { margin-bottom: 12px; }
    </style>
    </head>
    <body>
    <div class="np" id="np-root">

      <div class="np-masthead">
        <div class="np-date">Édition Spéciale  ·  From 1903 to Today  ·  112 Editions</div>
        <div class="np-logo">Le Tour de France</div>
        <div class="np-tagline">The complete historical archive of the Grande Boucle for Fans ·  All the data, all the riders, all the stages</div>
      </div>

      <div class="np-ribbon">Breaking Peloton  ·  Daily Dispatch  ·  Alpe d'Huez Edition</div>

      <div class="np-kpi">
        <div class="np-kpi-cell">
          <div class="np-kpi-num">112</div>
          <div class="np-kpi-lbl">Editions Held</div>
        </div>
        <div class="np-kpi-cell">
          <div class="np-kpi-num">~3,500</div>
          <div class="np-kpi-lbl">Km per Edition</div>
        </div>
        <div class="np-kpi-cell">
          <div class="np-kpi-num">21</div>
          <div class="np-kpi-lbl">Stages</div>
        </div>
      </div>

      <div class="np-main">
        <div class="np-lead">
          <span class="np-section-tag">Front Page · History</span>
          <hr class="np-rule">
          <div class="np-headline-xl">Over a Century of Dust, Pain, and the Yellow Jersey</div>
          <div class="np-deck">Since 1903, the Tour rewrites the limits of human endurance every summer. A journey through the numbers, secrets, and legends of the Grande Boucle.</div>
          <img class="np-photo" src="HERO_URL" alt="Tour de France 1937">
          <div class="np-caption">Guy Lapébie, winner of the 1937 edition. ©Historical Archives</div>
          <div class="np-body np-drop">
            <p>The Tour de France is not merely a bicycle race. It is a traveling monument, forged on the asphalt of France every July since 1903. Born from the imagination of journalist Henri Desgrange — who wanted to sell more copies of his newspaper L'Auto — it has become the greatest annual sports spectacle on the planet.</p>
            <p>The numbers speak for themselves: over 112 editions, more than 3,500 kilometers of racing, 21 stages that cross plains, climb legendary passes, and decide destinies. The Alps and Pyrenees have seen giants break and unknown champions crowned.</p>
            <p>This portal was created to analyze every aspect of the race. Explore the standings, discover the riders who made history, analyze every stage, and dive into the data of a century of cycling.</p>
          </div>
        </div>

        <div class="np-sidebar">
          <div>
            <span class="np-section-tag">Curiosities</span>
            <hr class="np-rule">
          </div>

          <div class="np-side-art" onclick="npOpen('yellow')">
            <span class="np-side-tag">The Yellow Jersey</span>
            <div class="np-side-hl">Why is the leader's jersey yellow?</div>
            <div class="np-side-body">The answer lies in a newspaper and a happy accident in 1919…</div>
            <span class="np-read-more">Read more →</span>
            <hr class="np-rule-thin">
          </div>

          <div class="np-side-art" onclick="npOpen('desgrange')">
            <span class="np-side-tag">The Founder</span>
            <div class="np-side-hl">Desgrange: the tyrant who invented the Tour</div>
            <div class="np-side-body">He wanted only a single rider to reach Paris. His obsession forged a legend.</div>
            <span class="np-read-more">Read more →</span>
            <hr class="np-rule-thin">
          </div>

          <div class="np-side-art" onclick="npOpen('doping')">
            <span class="np-side-tag">Dark Side</span>
            <div class="np-side-hl">The ghost years: seven titles erased from history</div>
            <div class="np-side-body">From 1999 to 2005, no winner was officially proclaimed.</div>
            <span class="np-read-more">Read more →</span>
          </div>

          <div class="np-pullquote">
            «The ideal Tour would be one in which only a single rider managed to reach Paris.»
            <div class="np-pullquote-attr">— Henri Desgrange, founder</div>
          </div>
        </div>
      </div>

<div class="np-bottom">
        <div class="np-bot-art" onclick="npOpen('cavendish')">
          <span class="np-section-tag">Sprint</span>
          <hr class="np-rule">
          <img class="np-photo-sm" src="CAV_URL" alt="Mark Cavendish" style="object-position: center 10%;">
          <div class="np-caption">Cavendish celebrates at the finish line. ©Eurosport/Getty</div>
          <div class="np-bot-hl">Cavendish and the seemingly impossible record</div>
          <div class="np-bot-body">35 stage wins. A number no one believed could be surpassed — until July 2024 in Saint-Vulbas.</div>
          <div class="np-bot-byline">Stage Wins · Points Classification</div>
        </div>

        <div class="np-bot-art" onclick="npOpen('polkadot')">
          <span class="np-section-tag">The Mountains</span>
          <hr class="np-rule">
          <img class="np-photo-sm" src="POIS_URL" alt="Polka-dot jersey" style="object-fit: contain; object-position: center;">
          <div class="np-caption">The red and white polka-dot jersey. ©TDF Archive</div>
          <div class="np-bot-hl">The polka-dot jersey: a king born in 1975</div>
          <div class="np-bot-body">The KOM classification has existed since 1933, but its iconic jersey only appeared 42 years later.</div>
          <div class="np-bot-byline">Mountains Classification · Jerseys</div>
        </div>

        <div class="np-bot-art" onclick="npOpen('alpe')">
          <span class="np-section-tag">Mythical Climbs</span>
          <hr class="np-rule">
          <img class="np-photo-sm" src="ALPE_URL" alt="Alpe d'Huez" style="object-position: center 70%;">
          <div class="np-caption">The 21 hairpins of Alpe d'Huez. ©Getty Images</div>
          <div class="np-bot-hl">Alpe d'Huez: 21 hairpins, infinite legends</div>
          <div class="np-bot-body">Since its first appearance in 1952, this Alpine giant has been the stage for the Tour's most dramatic battles.</div>
          <div class="np-bot-byline">Climbs · Alpine Stages</div>
        </div>
      </div>
    <div class="np-overlay" id="np-overlay" onclick="npCloseOnBg(event)">
      <div class="np-modal" id="np-modal">
        <button class="np-modal-close" onclick="npClose()">✕</button>
        <span class="np-modal-tag"     id="np-m-tag"></span>
        <div  class="np-modal-title"   id="np-m-title"></div>
        <div  class="np-modal-deck"    id="np-m-deck"></div>
        <img  class="np-modal-img"     id="np-m-img" src="" alt="" style="display:none">
        <div  class="np-modal-caption" id="np-m-caption"></div>
        <div  class="np-modal-body"    id="np-m-body"></div>
      </div>
    </div>

    <script>
    var NP_ARTICLES = {
      yellow: {
        tag:     "Trivia - The Yellow Jersey",
        title:   "Why is the leader's jersey yellow?",
        deck:     "A color that became a symbol, born almost by chance in 1919.",
        img:     "",
        caption: "",
        body:     "<p>In 1919, Tour director Henri Desgrange decided to make the leader easily identifiable in the peloton. The solution was simple: a jersey of an unmistakable color.</p><p>The chosen color was yellow, and it was no coincidence. L'Auto, the sports newspaper organizing the Tour, was printed on yellow paper to stand out from its rival Le Velo, printed on green paper. The yellow jersey was, literally, a walking advertisement.</p><p>Eugene Christophe was the first rider to wear it in the 1919 edition. From that day on, the maillot jaune became the most coveted garment in cycling: a symbol of prestige, suffering, and glory.</p>"
      },
      desgrange: {
        tag:     "History - The Founder",
        title:   "Desgrange: the visionary tyrant who invented the Tour",
        deck:     "He imagined a race so brutal that only one rider would survive.",
        img:     "DESGRANGE_URL",
        caption: "Henri Desgrange, founder and director of the Tour.",
        body:     "<p>Henri Desgrange was a former cyclist, a journalist, and above all an iron-fisted visionary. In 1903, as director of L'Auto, he launched a challenge that seemed insane: a bicycle race around the whole of France, for nearly 2,500 kilometers.</p><p>His philosophy was brutal. He wanted a race that pushed men to the limit, where suffering was a virtue and withdrawing was a disgrace.</p><p>His commercial goal was clear: beat Le Velo and sell more copies. The Tour fulfilled this mission far beyond expectations. L'Auto's circulation exploded and the race became a national institution. Desgrange directed the Tour until 1936.</p>"
      },
      doping: {
        tag:     "Dark Chapter - Doping Era",
        title:   "The ghost years: seven titles erased from history",
        deck:     "From 1999 to 2005, no winner was officially proclaimed.",
        img:     "",
        caption: "",
        body:     "<p>For seven consecutive years, Lance Armstrong crossed the finish line on the Champs-Elysees with his arms raised. It was the story of the decade: a cancer survivor who conquered the hardest race in the world seven times in a row.</p><p>In 2012, USADA published its investigation: Armstrong had orchestrated the most sophisticated doping program in the history of the sport. All seven titles were revoked. The UCI chose not to reassign the victories to the runners-up, leaving seven editions without an official champion.</p><p>Floyd Landis' 2006 title was also revoked for doping.</p>"
      },
      cavendish: {
        tag:     "Sprint - Record",
        title:   "Cavendish and the stage wins record",
        deck:     "35 wins: a number that rewrote what was thought possible.",
        img:     "CAV_URL",
        caption: "Mark Cavendish celebrates at the 2021 Tour.",
        body:     "<p>For decades, Eddy Merckx's record of 34 stage wins seemed untouchable. Then came Mark Cavendish from the Isle of Man, with his explosive sprint and hunger for victories.</p><p>In 2021 he equaled the record. In 2024, at 39 years old, he surpassed it. Stage 5 to Saint-Vulbas: Cavendish crossed the finish line first and entered history with his 35th victory, becoming the rider with the most stage wins in Tour history.</p><p>His is also a story of resilience: he had almost left cycling due to health issues and painful crashes, before returning to make history.</p>"
      },
      polkadot: {
        tag:     "Jerseys - Mountains",
        title:   "The polka-dot jersey: a king born in 1975",
        deck:     "The most recognizable jersey in cycling has a surprisingly recent origin.",
        img:     "POIS_URL",
        caption: "The red and white polka-dot jersey.",
        body:     "<p>The Mountains Classification at the Tour de France dates back to 1933, rewarding the best climbers on the high-altitude passes. For over 40 years, however, the winner was identified only by points: no distinctive jersey.</p><p>It was only in 1975 that the iconic red and white polka-dot jersey officially appeared, introduced by the chocolate manufacturer Chocolat Poulain, whose packaging had a similar pattern.</p><p>Today the maillot a pois is one of the most recognizable garments in world sports. The battles for the King of the Mountains are among the most spectacular in the entire Tour.</p>"
      },
      alpe: {
        tag:     "Climbs - Legend",
        title:   "Alpe d'Huez: 21 hairpins, infinite legends",
        deck:     "The most mythical mountain in the history of the Tour de France.",
        img:     "ALPE_URL",
        caption: "The 21 hairpins of Alpe d'Huez.",
        body:     "<p>Alpe d'Huez made its Tour de France debut in 1952, when Fausto Coppi climbed it first on his way to victory. Since then, its 21 numbered hairpins, each bearing the name of a stage winner, have become a place of pilgrimage for cycling fans worldwide.</p><p>The climb rises 1,071 meters over 13.8 kilometers, with an average gradient of 7.9%. On race day, hundreds of thousands of fans crowd the roadside.</p><p>The most legendary ascent remains that of Marco Pantani in 1997: he climbed it in 37 minutes and 35 seconds, a record that still stands today.</p>"
      }
    };

    function npOpen(key) {
      var a = NP_ARTICLES[key];
      document.getElementById('np-m-tag').textContent   = a.tag;
      document.getElementById('np-m-title').textContent = a.title;
      document.getElementById('np-m-deck').textContent  = a.deck;
      document.getElementById('np-m-body').innerHTML    = a.body;
      var imgEl = document.getElementById('np-m-img');
      var capEl = document.getElementById('np-m-caption');
      if (a.img && !a.img.includes("_URL")) {
        imgEl.src           = a.img;
        imgEl.alt           = a.title;
        imgEl.style.display = 'block';
        capEl.textContent   = a.caption;
      } else {
        imgEl.style.display = 'none';
        capEl.textContent   = '';
      }
      document.getElementById('np-overlay').classList.add('open');
    }
    function npClose() {
      document.getElementById('np-overlay').classList.remove('open');
    }
    function npCloseOnBg(e) {
      if (e.target === document.getElementById('np-overlay')) npClose();
    }
    </script>
    </body>
    </html>
    """

    FULL_HTML = FULL_HTML.replace("HERO_URL",      URL_HERO)
    FULL_HTML = FULL_HTML.replace("DESGRANGE_URL", URL_DESGRANGE)
    FULL_HTML = FULL_HTML.replace("CAV_URL",       URL_CAV)
    FULL_HTML = FULL_HTML.replace("POIS_URL",      URL_POIS)
    FULL_HTML = FULL_HTML.replace("ALPE_URL",      URL_ALPE)

    components.html(FULL_HTML, height=1300, scrolling=True)

elif st.session_state.pagina_corrente == "classifica":

    # ----------------------------------------------------------
    # 0. CSS GLOBALE DELLA SEZIONE
    # ----------------------------------------------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

/* ── Selectbox scura ── */
        div[data-testid="stSelectbox"] label p { color: #f0ece4 !important; font-family: 'Merriweather', serif !important; font-weight: 700 !important; }
        div[data-baseweb="select"] > div { background-color: #111 !important; color: #fff !important; border: 1px solid #444 !important; border-radius: 3px !important; }
        div[data-baseweb="popover"] ul, ul[data-baseweb="menu"], ul[role="listbox"] { background-color: #111 !important; }
        div[data-baseweb="popover"] li, ul[data-baseweb="menu"] li, ul[role="listbox"] li { color: #fff !important; background-color: #111 !important; }
        div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover { background-color: #2a2a2a !important; }
        ul[role="listbox"] li[aria-selected="true"] { color: #FFCC00 !important; }

/* ── Sticky nav bar ── */
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stSelectbox"]) {
            position: sticky; top: 16px; z-index: 999;
            background-color: #0d0d0d !important;
            padding: 10px 24px !important;
            border: 1px solid #222 !important; /* Stesso bordino elegante degli altri grafici */
            border-bottom: 2px solid #FFCC00 !important;
            border-radius: 4px !important;
            width: calc(100% - 32px) !important; /* Lascia 16 pixel di respiro per lato */
            margin: 16px auto 30px auto !important; /* Centra la barra e le dà spazio sopra e sotto */
            box-shadow: 0 6px 12px rgba(0,0,0,0.4); /* Leggera ombra per farla galleggiare sul testo */
        }
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stSelectbox"]) > div { background-color: transparent !important; }
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stSelectbox"]) .stSelectbox label { color: #f0ece4 !important; font-size: 13px !important; letter-spacing: 1px; text-transform: uppercase; }
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stSelectbox"]) div[data-baseweb="select"] > div { background-color: #1a1a1a !important; border: 1px solid #FFCC00 !important; }  
        /* ── Metric cards ── */
        [data-testid="stMetric"] { background: #0d0d0d; border: 1px solid #2a2a2a; border-radius: 4px; padding: 14px 18px !important; }
        [data-testid="stMetricLabel"] p { color: #888 !important; font-family: 'Merriweather', serif !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1.5px; }
        [data-testid="stMetricValue"] { color: #FFCC00 !important; font-family: 'Merriweather', serif !important; }

        /* ── Sezione testata stile giornale ── */
        .st-standings-header {
            font-family: 'Merriweather', Georgia, serif;
            border-top: 5px solid #1a1a1a;
            border-bottom: 2px solid #1a1a1a;
            padding: 12px 0 8px;
            text-align: center;
            margin-bottom: 24px;
        }
        .st-section-rule { border: none; border-top: 1px solid #c8bfad; margin: 22px 0; }
        .st-section-label {
            font-family: 'Merriweather', serif;
            font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
            color: #666; display: block; margin-bottom: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 1. TESTATA GIORNALISTICA
    # ----------------------------------------------------------
    st.markdown("""
        <div class="st-standings-header">
            <span style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#888;font-family:Arial,sans-serif;">
                General Classification · Full Historical Archive
            </span>
            <h1 style="font-family:'Merriweather',Georgia,serif;font-size:42px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 2px;letter-spacing:-1px;">
                Standings & Roll of Honour
            </h1>
            <div style="font-size:10px;letter-spacing:2px;color:#888;font-family:Arial,sans-serif;
                        border-top:1px solid #c8bfad;padding-top:6px;margin-top:6px;">
                From 1903 to today · Every edition · Every rider · Every gap
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not df_storico.empty:

        # ----------------------------------------------------------
        # 2. SELECTBOX EDIZIONE (sticky)
        # ----------------------------------------------------------
        anni_disponibili = sorted(df_storico['Year'].dropna().unique(), reverse=True)
        anno_selezionato = st.selectbox("📅  Select an edition:", anni_disponibili)

        df_anno = df_storico[df_storico['Year'] == anno_selezionato].reset_index(drop=True)
        df_anno['Rank_Num'] = pd.to_numeric(df_anno['Rank'], errors='coerce')
        anni_revocati = list(range(1999, 2006)) + [2006]
        titolo_revocato = int(anno_selezionato) in anni_revocati

        # ----------------------------------------------------------
        # 3. BANNER TITOLO REVOCATO
        # ----------------------------------------------------------
        if titolo_revocato:
            st.markdown("""
                <div style="background:#1a0000;border:1px solid #cc0000;border-left:5px solid #cc0000;
                            padding:12px 18px;border-radius:3px;margin:16px 0;font-family:'Merriweather',serif;">
                    <span style="color:#cc0000;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:1px;">
                        ⚠ Doping Era
                    </span>
                    <p style="color:#e8c8c8;margin:4px 0 0;font-size:12px;line-height:1.5;">
                        The official winner of this edition was subsequently stripped of the title following 
                        doping violations. The UCI chose not to reassign the victory. This record reflects 
                        the rider who crossed the finish line first.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        # ----------------------------------------------------------
        # 4. PODIO — stile giornale copertina
        # ----------------------------------------------------------
        st.markdown(f"""
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:20px;font-weight:900;color:#1a1a1a; margin-left: 16px; margin-bottom: 4px;">
                The Podium of the {int(anno_selezionato)} Edition
            </h3>
        """, unsafe_allow_html=True)

        try:
            def safe_get(row_idx, col, default="N/A"):
                if row_idx >= len(df_anno): return default
                val = df_anno.iloc[row_idx].get(col, default)
                return default if pd.isna(val) else str(val)

            r1 = safe_get(0, "Rider"); t1 = safe_get(0, "Team")
            r2 = safe_get(1, "Rider"); g2 = safe_get(1, "Gap"); t2 = safe_get(1, "Team")
            r3 = safe_get(2, "Rider"); g3 = safe_get(2, "Gap"); t3 = safe_get(2, "Team")
        
            flag_map = {
                "france": "🇫🇷", "italy": "🇮🇹", "belgium": "🇧🇪", "spain": "🇪🇸",
                "netherlands": "🇳🇱", "luxembourg": "🇱🇺", "switzerland": "🇨🇭",
                "ireland": "🇮🇪", "germany": "🇩🇪", "usa": "🇺🇸", "united states": "🇺🇸",
                "denmark": "🇩🇰", "colombia": "🇨🇴", "slovenia": "🇸🇮",
                "united kingdom": "🇬🇧", "great britain": "🇬🇧", "australia": "🇦🇺",
                "portugal": "🇵🇹", "colombia": "🇨🇴", "kazakhstan": "🇰🇿", "norway": "🇳🇴"
            }
            # Cerchiamo la nazione del vincitore nel dataset Tour_Winners
            winner_row = df_tour_w[df_tour_w['Year'] == anno_selezionato] if not df_tour_w.empty else pd.DataFrame()
            nazione_vincitore = ""
            if not winner_row.empty:
                naz = winner_row.iloc[0].get('Country', '')
                nazione_vincitore = flag_map.get(str(naz).strip(), "")

            doping_marker = ' <span style="font-size:11px;color:#cc0000;vertical-align:middle;">✕</span>' if titolo_revocato else ""
            def get_flag(rider_name):
                # Cerchiamo la riga del corridore nel df_anno per trovarne la nazionalità
                row = df_anno[df_anno['Rider'] == rider_name]
                if not row.empty:
                    naz = str(row.iloc[0].get('Country', '')).strip().lower()
                    return flag_map.get(naz, "")
                return ""
            html_podio = f"""
            <style>
            .podium-wrap {{ display:flex; justify-content:center; align-items:flex-end; gap:0; margin:30px 0 40px; font-family:'Merriweather',Georgia,serif; }}
            .podium-col {{ display:flex; flex-direction:column; align-items:center; width:200px; }}
            .podium-rider {{ text-align:center; margin-bottom:18px; }}
            .podium-pos {{ font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial,sans-serif; }}
            .podium-name {{ font-size:15px;font-weight:900;color:#1a1a1a;line-height:1.2;margin:4px 0; }}
            .podium-gap  {{ font-size:12px;font-style:italic;color:#666; }}
            .podium-team {{ font-size:10px;color:#999;letter-spacing:.5px;margin-top:3px; }}
            .podium-block {{
                width:100%; display:flex; justify-content:center; align-items:center;
                background:linear-gradient(to right,#1a1a1a 0%,#555 30%,#1a1a1a 70%,#111 100%);
                border-radius:0 0 40% 40%/0 0 20px 20px;
                position:relative;
            }}
            .podium-block::before {{
                content:""; position:absolute; top:-20px; left:0; width:100%;
                height:40px; border-radius:50%; z-index:2;
            }}
            .pb-1 {{ height:180px; }} .pb-2 {{ height:120px; }} .pb-3 {{ height:90px; }}
            .pb-1::before {{ background:radial-gradient(ellipse at 30% 30%,#FFE566,#b8860b); }}
            .pb-2::before {{ background:radial-gradient(ellipse at 30% 30%,#f0f0f0,#888); }}
            .pb-3::before {{ background:radial-gradient(ellipse at 30% 30%,#e8a07a,#7a3a10); }}
            .podium-num {{ font-size:52px;font-weight:900;font-family:Arial,sans-serif;z-index:4;margin-top:12px;opacity:.85; }}
            .pn-1 {{ color:#FFD700;text-shadow:2px 2px 6px #000; }}
            .pn-2 {{ color:#e8e8e8;text-shadow:2px 2px 6px #000; }}
            .pn-3 {{ color:#cd7f32;text-shadow:2px 2px 6px #000; }}
            .podium-rule {{ width:80%;border:none;border-top:2px solid #1a1a1a;margin:0 0 14px; }}
            </style>

            <div class="podium-wrap">
              <!-- 2nd -->
                <div class="podium-col">
                <div class="podium-rider">
                  <div class="podium-pos">Runner-up</div>
                  <div class="podium-name">{r2}</div>
                  <div class="podium-gap">{g2}</div>
                  <div class="podium-team">{t2}</div>  </div>
                <hr class="podium-rule">
                <div class="podium-block pb-2"><div class="podium-num pn-2">2</div></div>
              </div>
              <!-- 1st -->
              <div class="podium-col" style="margin-bottom:0; z-index:3;">
                <div class="podium-rider">
                  <div class="podium-pos">Champion {nazione_vincitore}</div>
                  <div class="podium-name" style="font-size:19px;">{r1}{doping_marker}</div>
                  <div class="podium-gap">+00h 00' 00"</div>
                  <div class="podium-team">{t1}</div>
                </div>
                <hr class="podium-rule" style="border-color:#FFCC00;">
                <div class="podium-block pb-1"><div class="podium-num pn-1">1</div></div>
              </div>
              <!-- 3rd -->
                <div class="podium-col">
                <div class="podium-rider">
                  <div class="podium-pos">Third Place</div>
                  <div class="podium-name">{r3}</div>
                  <div class="podium-gap">{g3}</div>
                  <div class="podium-team">{t3}</div>  </div>
                <hr class="podium-rule">
                <div class="podium-block pb-3"><div class="podium-num pn-3">3</div></div>
              </div>
            </div>
            """
            st.markdown(html_podio, unsafe_allow_html=True)
        except Exception:
            st.warning("Podium data incomplete for this edition.")

        # ----------------------------------------------------------
        # 5. METRICHE EDIZIONE (Allineate ai margini)
        # ----------------------------------------------------------
        hr_style = "<hr class='st-section-rule'>"
        st.markdown(hr_style, unsafe_allow_html=True)
        vincitore_row = df_anno.iloc[0]
        tempi_validi = pd.notna(vincitore_row.get('TotalSeconds')) and vincitore_row.get('TotalSeconds', 0) > 0

        # 1. Prepariamo i valori (uguale a prima, ma salvati in variabili)
        val_dist = f"{vincitore_row.get('Distance (km)', 'N/A')} km"
        val_stages = str(vincitore_row.get('Number of stages', 'N/A'))
        if tempi_validi:
            ore = vincitore_row['TotalSeconds'] / 3600
            vel = vincitore_row['Distance (km)'] / ore
            val_speed = f"{vel:.1f} km/h"
        else:
            val_speed = "N/A"
            
        finishers = df_anno[df_anno['ResultType'] == 'time']['Rank_Num'].count() if 'ResultType' in df_anno.columns else len(df_anno)
        val_fin = str(int(finishers)) if finishers else "N/A"

        # 2. Costruiamo la riga delle metriche con HTML e CSS per margini perfetti
        metrics_html = f"""
        <style>
        .metrics-container {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            /* 🪄 FIX: Margini identici al resto della dashboard */
            margin: 16px auto 30px auto;
            width: calc(100% - 32px);
            box-sizing: border-box;
        }}
        .metric-box {{
            flex: 1;
            background-color: #0d0d0d;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 16px 20px;
            font-family: 'Merriweather', Georgia, serif;
        }}
        .metric-title {{
            font-size: 11px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: #888;
            font-family: Arial, sans-serif;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: #f0ece4;
        }}
        </style>

        <div class="metrics-container">
            <div class="metric-box">
                <div class="metric-title">📍 DISTANCE</div>
                <div class="metric-value">{val_dist}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">🏁 STAGES</div>
                <div class="metric-value">{val_stages}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">⚡ AVG SPEED</div>
                <div class="metric-value">{val_speed}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">✅ FINISHERS</div>
                <div class="metric-value">{val_fin}</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

        # ----------------------------------------------------------
        # 7. PIRAMIDE DEL TEMPO
        # ----------------------------------------------------------

        st.markdown(hr_style, unsafe_allow_html=True)
        
        # Inseriamo tutto in un div con margine sinistro per coerenza totale
        st.markdown(f"""
            <div style="margin-left: 16px;">
                <span class="st-section-label">· Time Gap Anatomy ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:20px;font-weight:900;color:#1a1a1a;margin:8px 0 4px 0;">
                    The Time Pyramid - {int(anno_selezionato)}
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                    Each bar is a rider's gap from the winner. The wider the pyramid, the more dominant the victory.
                </p>
            </div>
        """, unsafe_allow_html=True)
        df_pyr = df_anno[df_anno['Rank_Num'].notna()].sort_values('Rank_Num').head(15).copy()
        df_pyr = df_pyr[df_pyr['GapSeconds'].notna()]
        gap_dati_disponibili = df_pyr[df_pyr['GapSeconds'] > 0]['GapSeconds'].count() >= 2

        if not gap_dati_disponibili:
            st.markdown("""
                <div style="background:#111;border:1px solid #2a2a2a;border-radius:4px;
                            padding:16px 20px;font-family:'Merriweather',serif;color:#888;font-style:italic;">
                    Time gap data not available for this early edition of the Tour.
                </div>
            """, unsafe_allow_html=True)
        else:
            def fmt_gap_pyr(s):
                if s == 0: return "Leader"
                h = int(s) // 3600
                m = (int(s) % 3600) // 60
                sec = int(s) % 60
                if h > 0: return f"+{h}h {m:02d}'{sec:02d}\""
                if m > 0: return f"+{m}'{sec:02d}\""
                return f"+{sec}\""

            max_gap = df_pyr['GapSeconds'].max()
            MAX_BAR_PX = 200
            BAR_COLORS = [
                "#FFCC00","#5DCAA5","#378ADD","#EF9F27",
                "#D85A30","#7F77DD","#D4537E","#639922",
                "#888780","#E24B4A","#1D9E75","#BA7517",
                "#185FA5","#993556","#5F5E5A",
            ]

            rows_pyr = ""
            for i, row in enumerate(df_pyr.itertuples()):
                rank    = int(row.Rank_Num)
                name    = str(row.Rider).title()
                gap_s   = float(row.GapSeconds)
                gap_txt = fmt_gap_pyr(gap_s)
                team    = str(row.Team) if hasattr(row, 'Team') and row.Team else ""

                is_winner = (rank == 1)
                bar_w = 0 if is_winner else max(4, int((gap_s / max_gap) * MAX_BAR_PX))
                col   = BAR_COLORS[min(i, len(BAR_COLORS)-1)]

                # Alterna sinistra/destra per i corridori dopo il vincitore
                if is_winner:
                    rows_pyr += f"""
                    <div class="pyr-row pyr-winner-row">
                      <div class="pyr-left" style="justify-content:flex-end;">
                        <span class="pyr-name" style="font-weight:700;color:#FFCC00;">{name}</span>
                        <span class="pyr-team">{team}</span>
                      </div>
                      <div class="pyr-center">
                        <div class="pyr-axis-dot" style="background:#FFCC00;"></div>
                      </div>
                      <div class="pyr-right">
                        <span class="pyr-gap" style="color:#FFCC00;">Leader</span>
                      </div>
                    </div>"""
                elif rank % 2 == 0:
                    # pari → barra verso sinistra, nome a destra
                    rows_pyr += f"""
                    <div class="pyr-row">
                      <div class="pyr-left">
                        <div class="pyr-bar" style="width:{bar_w}px;background:{col};"></div>
                        <span class="pyr-gap-left">{gap_txt}</span>
                      </div>
                      <div class="pyr-center"><div class="pyr-axis-dot"></div></div>
                      <div class="pyr-right">
                        <span class="pyr-rank">#{rank}</span>
                        <span class="pyr-name">{name}</span>
                      </div>
                    </div>"""
                else:
                    # dispari → barra verso destra, nome a sinistra
                    rows_pyr += f"""
                    <div class="pyr-row">
                      <div class="pyr-left" style="justify-content:flex-end;">
                        <span class="pyr-name">{name}</span>
                        <span class="pyr-rank">#{rank}</span>
                      </div>
                      <div class="pyr-center"><div class="pyr-axis-dot"></div></div>
                      <div class="pyr-right">
                        <div class="pyr-bar" style="width:{bar_w}px;background:{col};"></div>
                        <span class="pyr-gap-right">{gap_txt}</span>
                      </div>
                    </div>"""

            doping_note = ""
            if titolo_revocato:
                doping_note = """<div style="margin-top:10px;font-size:11px;color:#cc0000;
                    font-family:'Merriweather',serif;font-style:italic;">
                    ✕ Title subsequently stripped — gaps shown reflect race result.</div>"""

            pyramid_html = f"""
            <style>
            body {{ margin: 0; background: transparent; overflow: hidden; }}
            .pyr-wrap {{
                font-family: 'Merriweather', Georgia, serif;
                background: #0d0d0d;
                border: 1px solid #222;
                border-radius: 4px;
                padding: 20px 12px 16px;
                margin: 16px auto;
                width: calc(100% - 32px);
                box-sizing: border-box;
                position: relative;
            }}
            .pyr-axis-line {{
                position: absolute;
                left: 50%; top: 0; bottom: 0;
                width: 1px;
                background: #2a2a2a;
                transform: translateX(-0.5px);
                pointer-events: none;
            }}
            .pyr-row {{
                display: grid;
                grid-template-columns: 1fr 16px 1fr;
                align-items: center;
                height: 32px;
                margin-bottom: 3px;
            }}
            .pyr-winner-row {{ height: 38px; margin-bottom: 6px; }}
            .pyr-left  {{ display:flex; align-items:center; gap:6px; justify-content:flex-end; padding-right:8px; overflow:hidden; }}
            .pyr-right {{ display:flex; align-items:center; gap:6px; justify-content:flex-start; padding-left:8px; overflow:hidden; }}
            .pyr-center {{ display:flex; align-items:center; justify-content:center; }}
            .pyr-axis-dot {{
                width: 6px; height: 6px;
                border-radius: 50%;
                background: #444;
                flex-shrink: 0;
            }}
            .pyr-bar {{
                height: 18px;
                border-radius: 2px;
                flex-shrink: 0;
                transition: width 0.5s ease;
            }}
            .pyr-name {{
                font-size: 12px;
                color: #d0ccc4;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 150px;
            }}
            .pyr-team {{
                font-size: 10px;
                color: #555;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 120px;
                margin-left: 6px;
                font-style: italic;
            }}
            .pyr-rank {{
                font-size: 10px;
                color: #555;
                flex-shrink: 0;
                font-weight: 700;
            }}
            .pyr-gap-left  {{ font-size: 11px; color: #888; white-space: nowrap; font-family: monospace; }}
            .pyr-gap-right {{ font-size: 11px; color: #888; white-space: nowrap; font-family: monospace; }}
            .pyr-gap {{ font-size: 12px; white-space: nowrap; font-family: monospace; }}
            .pyr-scale {{
                margin-top: 14px;
                padding-top: 10px;
                border-top: 1px solid #1e1e1e;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 16px;
            }}
            .pyr-scale-bar {{
                height: 3px;
                background: #333;
                border-radius: 1px;
            }}
            .pyr-scale-label {{ font-size: 10px; color: #555; letter-spacing: 1px; text-transform: uppercase; font-family: Arial, sans-serif; }}
            </style>

            <div class="pyr-wrap">
              <div class="pyr-axis-line"></div>
              {rows_pyr}
              <div class="pyr-scale">
                <span class="pyr-scale-label">← wider = bigger gap from leader →</span>
                <div class="pyr-scale-bar" style="width:{MAX_BAR_PX}px;"></div>
                <span class="pyr-scale-label">{fmt_gap_pyr(int(max_gap))}</span>
              </div>
            </div>
            {doping_note}
            """
            import streamlit.components.v1 as components
            pyr_height = 38 + (len(df_pyr) - 1) * 35 + 60
            components.html(pyramid_html, height=pyr_height, scrolling=False)

# ----------------------------------------------------------
        # 8. GRAFICO RADIALE STORICO (D3.js)
        # ----------------------------------------------------------
        st.markdown(hr_style, unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-left: 16px;">
                <span class="st-section-label">· Historical Competitiveness ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:20px;font-weight:900;color:#1a1a1a;margin:8px 0 4px 0;">
                    The Ring of Suffering
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                    A radial timeline of the Tour. Each arc is an edition; length represents the time gap between 1st and 2nd place.
                </p>
            </div>
        """, unsafe_allow_html=True)

        RADIAL_HTML = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
<style>
          :root {
            /* Variabili colore iniettate per mappare il grafico sul tuo tema Streamlit scuro */
            --color-background-primary: #0d0d0d;
            --color-text-primary: #f0ece4;
            --color-text-secondary: #aaa;
            --color-text-tertiary: #666;
            --color-border-secondary: #444;
            --color-border-tertiary: #2a2a2a;
            --font-serif: 'Merriweather', Georgia, serif;
            --border-radius-md: 4px;
          }
          
body { 
            background: transparent; 
            font-family: sans-serif; 
            margin: 0; 
            overflow: hidden; /* 🪄 Nasconde la barra di scorrimento laterale */
          }

          .wrap {
            display: grid;
            grid-template-columns: 1fr 240px;
            gap: 10px;
            align-items: start;
            background: #0d0d0d;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 24px 30px 24px 12px;
            
            margin: 16px auto; /* Aggiunge 16px di spazio fisico esterno su tutti i lati e centra */
            width: calc(100% - 32px); /* Dice al box di occupare il 100% MENO i 16+16px dei margini */
            box-sizing: border-box;
          }
.chart-col {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
          }
          
          #rv {
            width: 100%;
            max-width: 460px; /* Leggermente ridotto per dare margine */
            height: auto;
            aspect-ratio: 1 / 1; /* 🪄 Il segreto per non far tagliare MAI gli SVG */
            display: block;
            margin: 0; 
          }

          .info-col {
            padding: 10px 0 10px 20px; /* Spazio a sinistra per staccarsi dal grafico */
            border-left: 1px solid var(--color-border-tertiary);
          }
          .info-year{font-size:28px;font-weight:500;color:var(--color-text-primary);font-family:var(--font-serif);line-height:1}
          .info-badge{display:inline-block;margin-top:6px;font-size:11px;font-weight:500;padding:3px 8px;border-radius:99px}
          .badge-epic{background:#1a0a0a;color:#ff6b6b}
          .badge-dom{background:#1a1400;color:#FFCC00}
          .badge-norm{background:#0a0a1a;color:#7bafd4}
          .info-winner{font-size:13px;font-weight:500;color:var(--color-text-primary);margin-top:12px;line-height:1.3}
          .info-label{font-size:10px;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:1px;margin-top:10px}
          .info-gap{font-size:22px;font-weight:500;font-family:monospace;color:var(--color-text-primary);line-height:1.2;margin-top:2px}
          .info-note{font-size:11px;color:var(--color-text-secondary);margin-top:10px;line-height:1.5;font-style:italic}
          .legend{display:flex;align-items:center;gap:8px;margin-top:16px;padding-top:12px;border-top:0.5px solid var(--color-border-tertiary)}
          .leg-bar{height:6px;border-radius:3px;flex:1}
          .leg-label{font-size:10px;color:var(--color-text-tertiary);white-space:nowrap}
          .controls{margin-top:14px;padding-top:12px;border-top:0.5px solid var(--color-border-tertiary)}
          .ctrl-label{font-size:10px;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
          .filter-btn{font-size:11px;padding:4px 10px;border-radius:var(--border-radius-md);border:0.5px solid var(--color-border-secondary);background:transparent;color:var(--color-text-secondary);cursor:pointer;margin-right:4px;margin-bottom:4px;transition:background .15s,color .15s}
          .filter-btn.on{background:var(--color-text-primary);color:var(--color-background-primary);border-color:transparent}
          .hint{font-size:10px;color:var(--color-text-tertiary);text-align:center;margin-top:6px}
        </style>
        </head>
        <body>
        <div class="wrap">
          <div class="chart-col">
            <svg id="rv" width="100%" viewBox="0 0 440 440"></svg>
            <p class="hint">Hover or tap an arc to explore · Arc length = gap from leader to runner-up</p>
          </div>
          <div class="info-col" id="info-col">
            <div style="font-size:12px;color:var(--color-text-tertiary);font-style:italic;margin-top:20px">Hover an arc to see edition details</div>
            <div class="legend" style="margin-top:24px">
              <span class="leg-label">tight</span>
              <div class="leg-bar" style="background:linear-gradient(to right,#FFCC00,#ff8c00,#cc3300)"></div>
              <span class="leg-label">dominated</span>
            </div>
            <div class="controls">
              <div class="ctrl-label">Highlight era</div>
              <button class="filter-btn on" data-era="all">All</button>
              <button class="filter-btn" data-era="pre">Pre-1950</button>
              <button class="filter-btn" data-era="mid">1950–1989</button>
              <button class="filter-btn" data-era="mod">1990–today</button>
            </div>
          </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
        <script>
        const DATA = [
          {y:1903,w:"Maurice Garin",g:10761},{y:1904,w:"Henri Cornet",g:8174},
          {y:1913,w:"Philippe Thys",g:517},{y:1914,w:"Philippe Thys",g:110},
          {y:1919,w:"Firmin Lambot",g:6174},{y:1920,w:"Philippe Thys",g:3441},
          {y:1921,w:"Léon Scieur",g:1116},{y:1922,w:"Firmin Lambot",g:2475},
          {y:1923,w:"Henri Pélissier",g:1841},{y:1924,w:"Ottavio Bottecchia",g:2136},
          {y:1925,w:"Ottavio Bottecchia",g:3260},{y:1926,w:"Lucien Buysse",g:4945},
          {y:1927,w:"Nicolas Frantz",g:6501},{y:1928,w:"Nicolas Frantz",g:3007},
          {y:1929,w:"Maurice De Waele",g:2663},{y:1930,w:"André Leducq",g:853},
          {y:1931,w:"Antonin Magne",g:776},{y:1932,w:"André Leducq",g:1443},
          {y:1933,w:"Georges Speicher",g:241},{y:1934,w:"Antonin Magne",g:1651},
          {y:1935,w:"Romain Maes",g:1072},{y:1936,w:"Sylvère Maes",g:1615},
          {y:1937,w:"Roger Lapébie",g:437},{y:1938,w:"Gino Bartali",g:1107},
          {y:1939,w:"Sylvère Maes",g:1838},{y:1947,w:"Jean Robic",g:238},
          {y:1948,w:"Gino Bartali",g:1612},{y:1949,w:"Fausto Coppi",g:655},
          {y:1950,w:"Ferdi Kübler",g:570},{y:1951,w:"Hugo Koblet",g:1320},
          {y:1952,w:"Fausto Coppi",g:1697},{y:1953,w:"Louison Bobet",g:858},
          {y:1954,w:"Louison Bobet",g:949},{y:1955,w:"Louison Bobet",g:293},
          {y:1956,w:"Roger Walkowiak",g:85},{y:1957,w:"Jacques Anquetil",g:896},
          {y:1958,w:"Charly Gaul",g:190},{y:1959,w:"Federico Bahamontes",g:241},
          {y:1960,w:"Gastone Nencini",g:302},{y:1961,w:"Jacques Anquetil",g:734},
          {y:1962,w:"Jacques Anquetil",g:299},{y:1963,w:"Jacques Anquetil",g:215},
          {y:1964,w:"Jacques Anquetil",g:55},{y:1965,w:"Felice Gimondi",g:160},
          {y:1966,w:"Lucien Aimar",g:67},{y:1967,w:"Roger Pingeon",g:220},
          {y:1968,w:"Jan Janssen",g:38},{y:1969,w:"Eddy Merckx",g:1074},
          {y:1970,w:"Eddy Merckx",g:761},{y:1971,w:"Eddy Merckx",g:591},
          {y:1972,w:"Eddy Merckx",g:641},{y:1973,w:"Luis Ocaña",g:951},
          {y:1974,w:"Eddy Merckx",g:484},{y:1975,w:"Bernard Thévenet",g:167},
          {y:1976,w:"Lucien Van Impe",g:254},{y:1977,w:"Bernard Thévenet",g:48},
          {y:1978,w:"Bernard Hinault",g:236},{y:1979,w:"Bernard Hinault",g:787},
          {y:1980,w:"Joop Zoetemelk",g:415},{y:1981,w:"Bernard Hinault",g:874},
          {y:1982,w:"Bernard Hinault",g:381},{y:1983,w:"Laurent Fignon",g:244},
          {y:1984,w:"Laurent Fignon",g:632},{y:1985,w:"Bernard Hinault",g:102},
          {y:1986,w:"Greg LeMond",g:190},{y:1987,w:"Stephen Roche",g:40},
          {y:1988,w:"Pedro Delgado",g:433},{y:1989,w:"Greg LeMond",g:8,epic:true,note:"8 seconds — the closest finish in Tour history"},
          {y:1990,w:"Greg LeMond",g:136},{y:1991,w:"Miguel Indurain",g:216},
          {y:1992,w:"Miguel Indurain",g:275},{y:1993,w:"Miguel Indurain",g:299},
          {y:1994,w:"Miguel Indurain",g:339},{y:1995,w:"Miguel Indurain",g:275},
          {y:1996,w:"Bjarne Riis",g:101},{y:1997,w:"Jan Ullrich",g:549},
          {y:1998,w:"Marco Pantani",g:201},
          {y:2006,w:"Oscar Pereiro",g:32,note:"Landis stripped — Pereiro awarded"},{y:2007,w:"Alberto Contador",g:23,epic:true,note:"23 seconds — second closest ever"},
          {y:2008,w:"Carlos Sastre",g:58},{y:2009,w:"Alberto Contador",g:251},
          {y:2010,w:"Andy Schleck",g:181},{y:2011,w:"Cadel Evans",g:94},
          {y:2012,w:"Bradley Wiggins",g:201},{y:2013,w:"Chris Froome",g:260},
          {y:2014,w:"Vincenzo Nibali",g:457},{y:2015,w:"Chris Froome",g:72},
          {y:2016,w:"Chris Froome",g:245},{y:2017,w:"Chris Froome",g:54},
          {y:2018,w:"Geraint Thomas",g:111},{y:2019,w:"Egan Bernal",g:71},
          {y:2020,w:"Tadej Pogacar",g:59,note:"Roglic lost in final TT — stunning reversal"},
          {y:2021,w:"Tadej Pogacar",g:320},{y:2022,w:"Jonas Vingegaard",g:163},
          {y:2023,w:"Jonas Vingegaard",g:449},{y:2024,w:"Tadej Pogacar",g:377},
          {y:2025,w:"Tadej Pogacar",g:264}
        ];

        const EPIC_THRESHOLD = 60;
        const DOM_THRESHOLD  = 1200;

        function fmtGap(s){
          if(s<60) return s+'″';
          const m=Math.floor(s/60),sec=s%60;
          if(m<60) return m+"'"+String(sec).padStart(2,'0')+'″';
          const h=Math.floor(m/60),rm=m%60;
          return h+'h '+String(rm).padStart(2,'0')+"'"+String(sec).padStart(2,'0')+'″';
        }

        function gapColor(g){
          const t = Math.min(1, Math.log(g+1)/Math.log(DOM_THRESHOLD+1));
          const stops = [
            [255,204,0],[255,140,0],[204,60,0],[140,20,0]
          ];
          const i = Math.min(stops.length-2, Math.floor(t*(stops.length-1)));
          const f = t*(stops.length-1)-i;
          const a=stops[i], b=stops[i+1];
          return `rgb(${Math.round(a[0]+(b[0]-a[0])*f)},${Math.round(a[1]+(b[1]-a[1])*f)},${Math.round(a[2]+(b[2]-a[2])*f)})`;
        }

        function badgeClass(g){ return g<=EPIC_THRESHOLD?'badge-epic':g>=DOM_THRESHOLD?'badge-dom':'badge-norm'; }
        function badgeLabel(g){ return g<=EPIC_THRESHOLD?'epic — photo finish':g>=DOM_THRESHOLD?'dominated':'competitive'; }

        let activeEra='all';

        function eraMatch(d){
          if(activeEra==='all') return true;
          if(activeEra==='pre') return d.y<1950;
          if(activeEra==='mid') return d.y>=1950&&d.y<=1989;
          if(activeEra==='mod') return d.y>1989;
        }

        const svg = d3.select('#rv');
        const W=440, CX=220, CY=220;
        const R_IN=72, R_MAX=200;
        const gapLog = d => Math.log(d.g+1);
        const maxLog  = Math.log(d3.max(DATA,d=>d.g)+1);
        const minLog  = Math.log(d3.min(DATA,d=>d.g)+1);
        const scaleR  = g => R_IN + ((Math.log(g+1)-minLog)/(maxLog-minLog))*(R_MAX-R_IN);

        const N = DATA.length;
        const GAP_RAD = 0.012;
        const arcSpan = (2*Math.PI - N*GAP_RAD) / N;

        const arc = d3.arc();

        const gMain = svg.append('g').attr('transform',`translate(${CX},${CY})`);

        gMain.append('circle').attr('r',R_IN-6).attr('fill','none')
          .attr('stroke','var(--color-border-tertiary)').attr('stroke-width',0.5);

        [1,2,3].forEach(i=>{
          gMain.append('circle')
            .attr('r', R_IN + i*(R_MAX-R_IN)/3)
            .attr('fill','none')
            .attr('stroke','var(--color-border-tertiary)')
            .attr('stroke-width',0.5)
            .attr('stroke-dasharray','3 4');
        });

        const arcs = gMain.selectAll('path.arc')
          .data(DATA).enter().append('path').attr('class','arc')
          .attr('d',(d,i)=>{
            const startA = -Math.PI/2 + i*(arcSpan+GAP_RAD);
            return arc({innerRadius:R_IN, outerRadius:scaleR(d.g), startAngle:startA, endAngle:startA+arcSpan});
          })
          .attr('fill', d=>gapColor(d.g))
          .attr('opacity', d=>eraMatch(d)?1:0.12)
          .attr('stroke','none')
          .style('cursor','pointer');

        const epicRing = gMain.selectAll('circle.epic')
          .data(DATA.filter(d=>d.epic)).enter().append('circle')
          .attr('class','epic')
          .attr('cx',(d,i)=>{
            const idx=DATA.indexOf(d);
            const a=-Math.PI/2+idx*(arcSpan+GAP_RAD)+arcSpan/2;
            return Math.cos(a)*(scaleR(d.g)+8);
          })
          .attr('cy',(d)=>{
            const idx=DATA.indexOf(d);
            const a=-Math.PI/2+idx*(arcSpan+GAP_RAD)+arcSpan/2;
            return Math.sin(a)*(scaleR(d.g)+8);
          })
          .attr('r',3).attr('fill','#ff4444').attr('opacity',0.9);

        
        const DECADE_YEARS = [1910, 1930, 1950, 1970, 1990, 2010];
        
        DECADE_YEARS.forEach(yr => {
          const idx = DATA.findIndex(d => d.y >= yr);
          if (idx < 0) return;
          
          // Il segreto dell'allineamento: calcoliamo l'angolo al CENTRO esatto della barra, non al bordo
          const a = -Math.PI/2 + idx * (arcSpan + GAP_RAD) + (arcSpan / 2);

          // Raggio tratteggiato elegante e sottile. Si ferma a R_MAX, così è impossibile che venga tagliato!
          gMain.append('line')
            .attr('x1', Math.cos(a) * (R_IN - 4))
            .attr('y1', Math.sin(a) * (R_IN - 4))
            .attr('x2', Math.cos(a) * R_MAX) 
            .attr('y2', Math.sin(a) * R_MAX)
            .attr('stroke', 'var(--color-border-tertiary)')
            .attr('stroke-width', 0.8)
            .attr('stroke-dasharray', '2 4');

          // Testo orizzontale, pulito e perfettamente centrato
          const lx = Math.cos(a) * (R_IN - 18), ly = Math.sin(a) * (R_IN - 18);
          gMain.append('text')
            .attr('x', lx)
            .attr('y', ly)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'central')
            .attr('font-size', 10)
            .attr('font-family', 'var(--font-serif)') // Usa lo stesso font elegante Merriweather
            .attr('fill', 'var(--color-text-secondary)')
            .text(yr);
        });

        let highlighted=null;
        function showInfo(d){
          highlighted=d;
          const bc=badgeClass(d.g), bl=badgeLabel(d.g);
          document.getElementById('info-col').innerHTML=`
            <div class="info-year">${d.y}</div>
            <span class="info-badge ${bc}">${bl}</span>
            <div class="info-label" style="margin-top:14px">Winner</div>
            <div class="info-winner">${d.w}</div>
            <div class="info-label">Gap to runner-up</div>
            <div class="info-gap">+${fmtGap(d.g)}</div>
            ${d.note?`<div class="info-note">${d.note}</div>`:''}
            <div class="legend">
              <span class="leg-label">tight</span>
              <div class="leg-bar" style="background:linear-gradient(to right,#FFCC00,#ff8c00,#cc3300)"></div>
              <span class="leg-label">dominated</span>
            </div>
            <div class="controls">
              <div class="ctrl-label">Highlight era</div>
              ${['all','pre','mid','mod'].map(e=>`<button class="filter-btn${activeEra===e?' on':''}" data-era="${e}">${{all:'All',pre:'Pre-1950',mid:'1950–1989',mod:'1990–today'}[e]}</button>`).join('')}
            </div>
          `;
          bindEraButtons();
        }

arcs.on('mouseover',(ev,d)=>{
          // IL FIX 1: Se l'arco non fa parte dell'epoca selezionata, ignora il mouse!
          if (!eraMatch(d)) return; 
          
          arcs.attr('opacity',x=>x===d?1:(eraMatch(x)?0.35:0.08));
          showInfo(d);
        }).on('mouseout',()=>{
          arcs.attr('opacity',d=>eraMatch(d)?1:0.12);
        });

        function bindEraButtons(){
          document.querySelectorAll('.filter-btn').forEach(btn=>{
            btn.addEventListener('click',()=>{
              activeEra=btn.dataset.era;
              document.querySelectorAll('.filter-btn').forEach(b=>b.classList.toggle('on',b.dataset.era===activeEra));
              arcs.attr('opacity',d=>eraMatch(d)?1:0.12);
              
              // IL FIX 2: Resetta il pannello laterale quando si cambia filtro
              document.getElementById('info-col').innerHTML = `
                <div style="font-size:12px;color:var(--color-text-tertiary);font-style:italic;margin-top:20px">Hover an active arc to see edition details</div>
                <div class="legend" style="margin-top:24px">
                  <span class="leg-label">tight</span>
                  <div class="leg-bar" style="background:linear-gradient(to right,#FFCC00,#ff8c00,#cc3300)"></div>
                  <span class="leg-label">dominated</span>
                </div>
                <div class="controls">
                  <div class="ctrl-label">Highlight era</div>
                  ${['all','pre','mid','mod'].map(e=>`<button class="filter-btn${activeEra===e?' on':''}" data-era="${e}">${{all:'All',pre:'Pre-1950',mid:'1950–1989',mod:'1990–today'}[e]}</button>`).join('')}
                </div>
              `;
              bindEraButtons(); // Riattacca gli eventi ai nuovi bottoni ricreati
            });
          });
        }
        bindEraButtons();

        const centerLabel = gMain.append('text').attr('text-anchor','middle').attr('dominant-baseline','central')
          .attr('font-size',10).attr('fill','var(--color-text-tertiary)').attr('y',-6).text('Gap');
        const centerLabel2 = gMain.append('text').attr('text-anchor','middle').attr('dominant-baseline','central')
          .attr('font-size',10).attr('fill','var(--color-text-tertiary)').attr('y',6).text('1st → 2nd');
        </script>
        </body>
        </html>
        """

        import streamlit.components.v1 as components
        components.html(RADIAL_HTML, height=500)
        # ----------------------------------------------------------
        # 8. LEADERBOARD ANIMATA — stile videogioco/archivio
        # ----------------------------------------------------------
        st.markdown(hr_style, unsafe_allow_html=True)
        
        # Tutto racchiuso in un div con margine sinistro
        st.markdown(f"""
            <div style="margin-left: 16px;">
                <span class="st-section-label">· Full Classification ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:20px;font-weight:900;color:#1a1a1a;margin:8px 0 4px 0;">
                    General Classification - {int(anno_selezionato)}
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                    Hover a row to highlight. Click a column header to sort.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Prepariamo i dati
        df_lb = df_anno.copy()
        df_lb = df_lb.rename(columns={'B': 'Bonus', 'P': 'Penalty'})
        df_lb['GapMin_display'] = df_lb['GapSeconds'].apply(
            lambda x: "–" if (pd.isna(x) or x == 0) else f"+{int(x)//3600:02d}h {(int(x)%3600)//60:02d}' {int(x)%60:02d}\""
        )
        df_lb['Bar_pct'] = df_lb['GapSeconds'].apply(
            lambda x: 0 if pd.isna(x) or x == 0 else min(100, (x / df_lb['GapSeconds'].max()) * 100) if df_lb['GapSeconds'].max() > 0 else 0
        )

        # Costruiamo la leaderboard come HTML animato
        rows_html = ""
        medal_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}

        for i, row in df_lb.head(30).iterrows():
            rank = row.get('Rank', i + 1)
            rider = str(row.get('Rider', 'N/A'))
            team = str(row.get('Team', ''))
            times = str(row.get('Times', ''))
            gap_disp = row.get('GapMin_display', '–')
            bar = row.get('Bar_pct', 0)

            try:
                rank_int = int(float(str(rank)))
            except:
                rank_int = 99

            medal = medal_colors.get(rank_int, None)
            rank_cell_style = f"color:{medal};font-weight:900;" if medal else "color:#888;font-weight:600;"
            row_highlight = "lb-row-top3" if rank_int <= 3 else "lb-row"
            doping_badge = ' <span style="color:#cc0000;font-size:9px;vertical-align:super;">✕</span>' if (titolo_revocato and rank_int == 1) else ""

            bar_html = f"""
                <div style="width:100%;height:3px;background:#1e1e1e;border-radius:2px;margin-top:4px;">
                    <div style="width:{bar:.1f}%;height:100%;background:linear-gradient(to right,#FFCC00,#ff8c00);border-radius:2px;transition:width 0.6s ease;"></div>
                </div>
            """ if bar > 0 else ""

            rows_html += f"""
            <div class="{row_highlight}">
              <div class="lb-rank" style="{rank_cell_style}">{rank}</div>
              <div class="lb-rider">
                <div class="lb-name">{rider}{doping_badge}</div>
                <div class="lb-team">{team}</div>
                {bar_html}
              </div>
              <div class="lb-time">{times}</div>
              <div class="lb-gap">{gap_disp}</div>
            </div>
            """

        leaderboard_html = f"""
        <style>

        .lb-wrap {{ 
            font-family:'Merriweather',Georgia,serif; 
            background:#0d0d0d; 
            border:1px solid #222; 
            border-radius:4px; 
            overflow:hidden; 
            /* 🪄 FIX: Margini allineati alla barra di navigazione */
            margin: 16px 16px 30px 16px !important; 
            width: calc(100% - 32px) !important;
            box-sizing: border-box !important;
        }}
        .lb-head {{ 
            display:grid; grid-template-columns:48px 1fr 160px 120px;
            background:#111; 
            padding:10px 24px !important; /* Allineato al padding della barra */
            border-bottom:2px solid #FFCC00; 
        }}
        .lb-head span {{ 
            font-size:9px; letter-spacing:2px; text-transform:uppercase; color:#FFCC00; font-family:Arial,sans-serif; 
        }}
        .lb-row, .lb-row-top3 {{
            display:grid; grid-template-columns:48px 1fr 160px 120px;
            padding:10px 24px !important; /* Allineato al padding della barra */
            border-bottom:1px solid #1a1a1a;
            transition:background 0.15s;
            animation: fadeSlideIn 0.4s ease both;
        }}
        .lb-row:hover {{ background:#181818; }}
        .lb-row-top3 {{ background:rgba(255,204,0,0.04); }}
        .lb-row-top3:hover {{ background:rgba(255,204,0,0.09); }}
        @keyframes fadeSlideIn {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}
        .lb-rank {{ font-size:18px; display:flex; align-items:center; }}
        .lb-rider {{ display:flex; flex-direction:column; justify-content:center; padding-right:12px; }}
        .lb-name {{ font-size:13px; font-weight:700; color:#f0ece4; line-height:1.2; }}
        .lb-team {{ font-size:10px; color:#666; margin-top:2px; font-style:italic; }}
        .lb-time {{ font-size:12px; color:#aaa; display:flex; align-items:center; font-family:monospace; }}
        .lb-gap {{ font-size:12px; color:#FFCC00; display:flex; align-items:center; font-family:monospace; }}

        </style>
        <div class="lb-wrap">
          <div class="lb-head">
            <span>#</span><span>Rider</span><span>Time</span><span>Gap</span>
          </div>
          {rows_html}
        </div>
        """

        import streamlit.components.v1 as components
        components.html(leaderboard_html, height=min(950, 32 * min(30, len(df_lb)) + 60), scrolling=True)

    else:
        st.warning("Data unavailable. Check the dataset connection.")


# ==========================================
# SEZIONE RIDERS — CODICE COMPLETO
# Sostituisce il blocco: elif st.session_state.pagina_corrente == "corridori":
# ==========================================

elif st.session_state.pagina_corrente == "corridori":

    # ----------------------------------------------------------
    # 0. PREPARAZIONE DATI GLOBALI
    # ----------------------------------------------------------
    import json

    # Carriera normalizzata (anno_carriera = Tour #1, #2, #3...)
    df_r_norm = df_storico.copy()
    df_r_norm['Rank_Num'] = pd.to_numeric(df_r_norm['Rank'], errors='coerce')
    df_r_norm = df_r_norm.sort_values(['Rider', 'Year'])
    df_r_norm['anno_carriera'] = df_r_norm.groupby('Rider').cumcount() + 1

    # Tour Winners puliti
    df_w_clean = df_tour_w.copy()
    df_w_clean['Country_clean'] = df_w_clean['Country'].str.strip().replace({
        'United States': 'USA', 'Dnmark': 'Denmark'
    })
    df_w_clean['rt_clean'] = df_w_clean['rider_type_(PPS)'].str.strip()
    df_w_clean['decade'] = (df_w_clean['Year'] // 10) * 10

    # Country → ISO3 per choropleth
    ISO_MAP = {
        'France': 'FRA', 'Belgium': 'BEL', 'Spain': 'ESP', 'Italy': 'ITA',
        'USA': 'USA', 'United Kingdom': 'GBR', 'Luxembourg': 'LUX',
        'Denmark': 'DNK', 'Slovenia': 'SVN', 'Netherlands': 'NLD',
        'Switzerland': 'CHE', 'Colombia': 'COL', 'Australia': 'AUS',
        'Germany': 'DEU', 'Ireland': 'IRL'
    }
    df_w_clean['ISO'] = df_w_clean['Country_clean'].map(ISO_MAP)

    # Colori nazioni
    COUNTRY_COLORS = {
        'France': '#0055A4', 'Belgium': '#FAE042', 'Spain': '#AA151B',
        'Italy': '#009246', 'USA': '#B22234', 'United Kingdom': '#CF142B',
        'Luxembourg': '#00A2E8', 'Denmark': '#C60C30', 'Slovenia': '#003DA5',
        'Netherlands': '#FF6600', 'Switzerland': '#FF0000',
        'Colombia': '#FCD116', 'Australia': '#00843D', 'Germany': '#000000',
        'Ireland': '#169B62'
    }

    # ----------------------------------------------------------
    # 1. CSS GLOBALE SEZIONE RIDERS
    # ----------------------------------------------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

        /* ── Tab navigation ── */
        .riders-tab-bar {
            display: flex;
            gap: 0;
            border-bottom: 3px solid #1a1a1a;
            margin-bottom: 32px;
        }
        .riders-tab {
            padding: 12px 28px;
            font-family: 'Merriweather', serif;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #888;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -3px;
            background: transparent;
            border-top: none;
            border-left: none;
            border-right: none;
            transition: color 0.2s, border-color 0.2s;
        }
        .riders-tab.active {
            color: #1a1a1a;
            border-bottom: 3px solid #FFCC00;
        }
        .riders-tab:hover { color: #1a1a1a; }

        /* ── Masthead ── */
        .riders-masthead {
            border-top: 5px solid #1a1a1a;
            border-bottom: 2px solid #1a1a1a;
            padding: 12px 0 8px;
            text-align: center;
            margin-bottom: 8px;
        }

        /* ── Section label ── */
        .r-section-label {
            font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
            color: #888; font-family: Arial, sans-serif;
            display: block; margin-bottom: 4px;
        }
        .r-rule { border: none; border-top: 1px solid #c8bfad; margin: 24px 0; }

        /* ── Selectbox dark ── */
        div[data-testid="stSelectbox"] label p { color: #1a1a1a !important; font-family: 'Merriweather', serif !important; font-weight: 700 !important; }
        div[data-baseweb="select"] > div { background-color: #111 !important; color: #fff !important; border: 1px solid #444 !important; border-radius: 3px !important; }
        div[data-baseweb="popover"] ul, ul[data-baseweb="menu"], ul[role="listbox"] { background-color: #111 !important; }
        div[data-baseweb="popover"] li, ul[data-baseweb="menu"] li, ul[role="listbox"] li { color: #fff !important; background-color: #111 !important; }
        div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover { background-color: #2a2a2a !important; }
        ul[role="listbox"] li[aria-selected="true"] { color: #FFCC00 !important; }

        /* ── Multiselect dark ── */
        div[data-testid="stMultiSelect"] label p { color: #1a1a1a !important; font-family: 'Merriweather', serif !important; font-weight: 700 !important; }

        /* ── H2H Fighter card ── */
        .fighter-card {
            background: #0d0d0d;
            border: 1px solid #2a2a2a;
            border-radius: 4px;
            padding: 20px;
            font-family: 'Merriweather', Georgia, serif;
            position: relative;
            overflow: hidden;
        }
        .fighter-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
        }
        .fighter-card-1::before { background: #FFCC00; }
        .fighter-card-2::before { background: #FF6B6B; }
        .fighter-card-3::before { background: #4ECDC4; }

        .fighter-name {
            font-size: 22px; font-weight: 900; color: #f0ece4;
            line-height: 1.1; margin-bottom: 6px; text-transform: uppercase;
            letter-spacing: -0.5px;
        }
        .fighter-country { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #888; margin-bottom: 14px; }
        .fighter-stat-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .fighter-stat-label { font-size: 10px; letter-spacing: 1px; text-transform: uppercase; color: #666; font-family: Arial; }
        .fighter-stat-val { font-size: 16px; font-weight: 900; color: #FFCC00; }
        .fighter-bar-wrap { width: 100%; height: 4px; background: #1e1e1e; border-radius: 2px; margin-top: 3px; }
        .fighter-bar { height: 100%; border-radius: 2px; transition: width 0.8s ease; }

        /* ── VS badge ── */
        .vs-badge {
            display: flex; align-items: center; justify-content: center;
            font-family: 'Merriweather', serif;
            font-size: 28px; font-weight: 900;
            color: #FFCC00;
            text-shadow: 0 0 20px rgba(255,204,0,0.4);
            height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 2. TESTATA GIORNALISTICA
    # ----------------------------------------------------------
    st.markdown("""
        <div class="riders-masthead">
            <span style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#888;font-family:Arial,sans-serif;">
                Riders Archive · From 1903 to Today · 3,601 Athletes
            </span>
            <h1 style="font-family:'Merriweather',Georgia,serif;font-size:42px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 2px;letter-spacing:-1px;">
                The Men of the Grande Boucle
            </h1>
            <div style="font-size:10px;letter-spacing:2px;color:#888;font-family:Arial,sans-serif;
                        border-top:1px solid #c8bfad;padding-top:6px;margin-top:6px;">
                Champions · Careers · Rivalries · Nations
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 3. TAB NAVIGATION
    # ----------------------------------------------------------
    if "riders_tab" not in st.session_state:
        st.session_state.riders_tab = "champions"

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        if st.button("🏆  THE CHAMPIONS", use_container_width=True,
                     type="primary" if st.session_state.riders_tab == "champions" else "secondary"):
            st.session_state.riders_tab = "champions"
    with col_t2:
        if st.button("📈  CAREER EXPLORER", use_container_width=True,
                     type="primary" if st.session_state.riders_tab == "career" else "secondary"):
            st.session_state.riders_tab = "career"
    with col_t3:
        if st.button("⚔️  HEAD-TO-HEAD", use_container_width=True,
                     type="primary" if st.session_state.riders_tab == "h2h" else "secondary"):
            st.session_state.riders_tab = "h2h"
    with col_t4:
        if st.button("🌍  NATIONS", use_container_width=True,
                     type="primary" if st.session_state.riders_tab == "nations" else "secondary"):
            st.session_state.riders_tab = "nations"

    st.markdown("""
        <style>
        button[kind="primary"] {
            background-color: #1a1a1a !important;
            color: #FFCC00 !important;
            border: none !important;
            border-radius: 0 !important;
            border-bottom: 3px solid #FFCC00 !important;
            font-family: 'Merriweather', serif !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            padding: 12px !important;
        }
        button[kind="secondary"] {
            background-color: transparent !important;
            color: #888 !important;
            border: none !important;
            border-radius: 0 !important;
            border-bottom: 3px solid #c8bfad !important;
            font-family: 'Merriweather', serif !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            padding: 12px !important;
        }
        button[kind="secondary"]:hover {
            color: #1a1a1a !important;
            border-bottom-color: #888 !important;
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    hr = "<hr class='r-rule'>"

    # ══════════════════════════════════════════════════════════
    # TAB 1 — THE CHAMPIONS
    # ══════════════════════════════════════════════════════════
    if st.session_state.riders_tab == "champions":

        st.markdown("""
            <span class="r-section-label">· The Golden Age ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Age of Glory — When Champions Conquered the Tour
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:8px;">
                Each dot is a Tour winner. Position on Y-axis = age at victory. Color = nation. Hover to explore.
            </p>
        """, unsafe_allow_html=True)

        # ── BEESWARM: età vincitori per anno ──
        df_bee = df_w_clean.dropna(subset=['age']).copy()
        df_bee['Winner_display'] = df_bee['Winner'].str.title()
        df_bee['rt_display'] = df_bee['rt_clean'].str.title()

        fig_bee = px.strip(
            df_bee, x='Year', y='age',
            color='Country_clean',
            hover_name='Winner_display',
            hover_data={'Country_clean': True, 'rt_display': True, 'age': True, 'Year': True},
            labels={'age': 'Age at Victory', 'Year': 'Edition', 'Country_clean': 'Nation', 'rt_display': 'Rider Type'},
            color_discrete_map=COUNTRY_COLORS,
            stripmode='overlay'
        )
        fig_bee.update_traces(marker=dict(size=11, opacity=0.85, line=dict(width=1, color='rgba(0,0,0,0.3)')), jitter=0.3)

        # Linea media mobile
        df_bee_yr = df_bee.groupby('Year')['age'].mean().reset_index()
        fig_bee.add_scatter(
            x=df_bee_yr['Year'], y=df_bee_yr['age'],
            mode='lines', line=dict(color='#1a1a1a', width=1.5, dash='dot'),
            name='Average age', hoverinfo='skip'
        )
        # Annotazione Pogacar
        fig_bee.add_annotation(
            x=2020, y=21, text="Pogacar, 21<br>youngest modern winner",
            showarrow=True, arrowhead=2, arrowcolor='#1a1a1a',
            font=dict(size=10, color='#1a1a1a', family='Arial'),
            bgcolor='rgba(255,204,0,0.85)', borderpad=4, ax=60, ay=-30
        )
        fig_bee.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=420, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                title='Nation', orientation='v', x=1.01, y=1,
                font=dict(size=10), bgcolor='rgba(244,241,234,0.9)',
                bordercolor='#c8bfad', borderwidth=1
            ),
            xaxis=dict(title='Edition', showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(title='Age', showgrid=True, gridcolor='#e8e4da', gridwidth=1),
        )
        st.plotly_chart(fig_bee, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── BUMP CHART: dominanza nazioni per decade ──
        st.markdown("""
            <span class="r-section-label">· National Dynasties ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                The Rise & Fall of Nations — A Century of Dominance
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:8px;">
                Victories per decade for the top 8 nations. Hover each line to track the shift of power.
            </p>
        """, unsafe_allow_html=True)

        TOP_NATIONS = ['France', 'Belgium', 'Spain', 'Italy', 'USA', 'United Kingdom', 'Luxembourg', 'Denmark']
        df_bump = df_w_clean[df_w_clean['Country_clean'].isin(TOP_NATIONS)].groupby(['decade', 'Country_clean']).size().reset_index(name='wins')

        fig_bump = go.Figure()
        for nation in TOP_NATIONS:
            df_n = df_bump[df_bump['Country_clean'] == nation].sort_values('decade')
            if df_n.empty:
                continue
            color = COUNTRY_COLORS.get(nation, '#888')
            fig_bump.add_trace(go.Scatter(
                x=df_n['decade'], y=df_n['wins'],
                mode='lines+markers+text',
                name=nation,
                line=dict(color=color, width=2.5),
                marker=dict(size=8, color=color, line=dict(width=1.5, color='white')),
                text=df_n['wins'].astype(str),
                textposition='top center',
                textfont=dict(size=9, color=color),
                hovertemplate=f'<b>{nation}</b><br>Decade: %{{x}}s<br>Victories: %{{y}}<extra></extra>'
            ))
        fig_bump.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(size=10)),
            xaxis=dict(title='Decade', tickvals=list(range(1900, 2030, 10)),
                       ticktext=[f"{d}s" for d in range(1900, 2030, 10)],
                       showgrid=False),
            yaxis=dict(title='Victories', showgrid=True, gridcolor='#e8e4da'),
        )
        # Annotazioni ere storiche
        for x0, x1, label in [(1914, 1918, 'WWI'), (1939, 1947, 'WWII')]:
            fig_bump.add_vrect(x0=x0, x1=x1, fillcolor='#888', opacity=0.12, line_width=0,
                               annotation_text=label, annotation_position='inside top',
                               annotation_font=dict(size=9, color='#666'))
        st.plotly_chart(fig_bump, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── RIDER TYPE HEATMAP per decade ──
        st.markdown("""
            <span class="r-section-label">· Tactical Evolution ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Who Wins the Tour? — The Rider Type Revolution
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:8px;">
                Heatmap of winning rider types per decade. From the early sprinters to the modern pure climbers.
            </p>
        """, unsafe_allow_html=True)

        df_heat = df_w_clean.groupby(['decade', 'rt_clean']).size().reset_index(name='count')
        df_heat_pivot = df_heat.pivot(index='rt_clean', columns='decade', values='count').fillna(0)

        fig_heat = go.Figure(data=go.Heatmap(
            z=df_heat_pivot.values,
            x=[f"{int(c)}s" for c in df_heat_pivot.columns],
            y=[t.title() for t in df_heat_pivot.index],
            colorscale=[[0, '#F4F1EA'], [0.01, '#FFF3CD'], [0.4, '#FFCC00'], [0.7, '#FF8C00'], [1, '#1a1a1a']],
            text=df_heat_pivot.values.astype(int),
            texttemplate='%{text}',
            textfont=dict(size=13, family='Merriweather, serif'),
            hovertemplate='<b>%{y}</b><br>%{x}<br>Victories: %{z}<extra></extra>',
            showscale=False,
        ))
        fig_heat.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=220, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(side='bottom', tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_heat, use_container_width=True)


    # ══════════════════════════════════════════════════════════
    # TAB 2 — CAREER EXPLORER
    # ══════════════════════════════════════════════════════════
    elif st.session_state.riders_tab == "career":

        st.markdown("""
            <span class="r-section-label">· Individual Archive ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Career Explorer — Track Any Rider Through Time
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                Select a rider to explore their complete Tour de France career. Add others to compare on a normalized timeline.
            </p>
        """, unsafe_allow_html=True)

        all_riders_list = sorted(df_r_norm['Rider'].dropna().unique())

        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            rider_main = st.selectbox("🚴 Main rider:", all_riders_list,
                                      index=all_riders_list.index('TADEJ POGACAR') if 'TADEJ POGACAR' in all_riders_list else 0)
        with col_sel2:
            altri = [r for r in all_riders_list if r != rider_main]
            riders_extra = st.multiselect("➕ Add for comparison (max 2):", altri, max_selections=2)

        riders_sel = [rider_main] + riders_extra
        PALETTE = ['#FFCC00', '#FF6B6B', '#4ECDC4']

        # ── CAREER ARC normalizzato ──
        st.markdown(hr, unsafe_allow_html=True)
        st.markdown(f"""
            <span class="r-section-label">· Normalized Career Arc ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Final GC Rank — Tour #1, #2, #3... (Career-Normalized)
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                X-axis = participation number in career, not the calendar year. Allows true peer comparison.
            </p>
        """, unsafe_allow_html=True)

        fig_arc = go.Figure()
        for i, rider in enumerate(riders_sel):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num']).sort_values('anno_carriera')
            if df_rd.empty:
                continue
            color = PALETTE[i]
            fig_arc.add_trace(go.Scatter(
                x=df_rd['anno_carriera'],
                y=df_rd['Rank_Num'],
                mode='lines+markers',
                name=rider.title(),
                line=dict(color=color, width=3),
                marker=dict(size=10, color=color, line=dict(width=2, color='white')),
                hovertemplate=(
                    f'<b>{rider.title()}</b><br>'
                    'Tour #%{x} of career<br>'
                    'GC Rank: #%{y}<br>'
                    '<extra></extra>'
                ),
                customdata=df_rd[['Year', 'Team']].values,
            ))
            # Annotazione anno reale sui punti
            for _, row in df_rd.iterrows():
                fig_arc.add_annotation(
                    x=row['anno_carriera'], y=row['Rank_Num'],
                    text=str(int(row['Year'])),
                    showarrow=False,
                    font=dict(size=8, color=color, family='Arial'),
                    yshift=14, xshift=0,
                )

        fig_arc.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=420, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center', font=dict(size=11)),
            xaxis=dict(
                title='Tour participation in career',
                tickmode='linear', dtick=1,
                tickvals=list(range(1, 17)),
                ticktext=[f'Tour #{n}' for n in range(1, 17)],
                showgrid=False, tickfont=dict(size=9),
            ),
            yaxis=dict(
                title='GC Final Rank', autorange='reversed',
                showgrid=True, gridcolor='#e8e4da',
                tickmode='linear', dtick=5,
            ),
        )
        # Fascia top-10
        fig_arc.add_hrect(y0=1, y1=10, fillcolor='rgba(255,204,0,0.06)',
                          line_width=0, annotation_text='Top 10 zone',
                          annotation_position='right', annotation_font=dict(size=9, color='#aaa'))
        st.plotly_chart(fig_arc, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── PHYSICAL OUTLIER STRIP (solo per vincitori) ──
        st.markdown("""
            <span class="r-section-label">· Physical Profile ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Physical Outlier Detector — Is This Champion Atypical?
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                Distribution of all Tour winners (grey). Red dot = selected rider. Only available for GC winners.
            </p>
        """, unsafe_allow_html=True)

        PHYSICAL_COLS = {
            'age': ('Age at Victory', 'years'),
            'BMI': ('BMI', 'kg/m²'),
            'weight_(Kg)': ('Weight', 'kg'),
        }

        df_phys = df_w_clean.dropna(subset=['age', 'BMI', 'weight_(Kg)'])

        # Cerca se il rider principale è un vincitore
        rider_main_norm = rider_main.title().lower()
        winner_match = df_phys[df_phys['Winner'].str.lower().str.strip() == rider_main_norm.strip()]
        if winner_match.empty:
            # Prova parziale
            winner_match = df_phys[df_phys['Winner'].str.lower().str.contains(rider_main.split()[0].lower())]

        fig_strips = go.Figure()
        metrics_list = list(PHYSICAL_COLS.items())
        y_positions = [3, 2, 1]

        for idx, (col, (label, unit)) in enumerate(metrics_list):
            y_val = y_positions[idx]
            vals = df_phys[col].dropna()

            # Jitter per i punti di sfondo
            import numpy as np
            jitter = np.random.uniform(-0.18, 0.18, size=len(vals))

            fig_strips.add_trace(go.Scatter(
                x=vals, y=[y_val + j for j in jitter],
                mode='markers',
                marker=dict(size=7, color='#c8bfad', opacity=0.6,
                            line=dict(width=0.5, color='#888')),
                showlegend=False,
                hovertemplate=f'<b>{label}</b>: %{{x}} {unit}<extra></extra>',
                name=label,
            ))

            # Mediana
            median_val = vals.median()
            fig_strips.add_shape(type='line',
                x0=median_val, x1=median_val,
                y0=y_val - 0.25, y1=y_val + 0.25,
                line=dict(color='#888', width=2, dash='dot'))

            # Punto del rider selezionato
            if not winner_match.empty and pd.notna(winner_match[col].values[0]):
                rider_val = winner_match[col].values[0]
                fig_strips.add_trace(go.Scatter(
                    x=[rider_val], y=[y_val],
                    mode='markers+text',
                    marker=dict(size=16, color='#FFCC00',
                                line=dict(width=2, color='#1a1a1a'), symbol='diamond'),
                    text=[f'{rider_val:.1f}'], textposition='top center',
                    textfont=dict(size=10, color='#1a1a1a'),
                    showlegend=False,
                    hovertemplate=f'<b>{rider_main.title()}</b><br>{label}: {rider_val:.1f} {unit}<extra></extra>',
                    name=f'{rider_main.title()} — {label}',
                ))

        fig_strips.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=300, margin=dict(l=120, r=20, t=20, b=20),
            xaxis=dict(title='Value', showgrid=True, gridcolor='#e8e4da'),
            yaxis=dict(
                tickmode='array',
                tickvals=y_positions,
                ticktext=[v[0] for v in PHYSICAL_COLS.values()],
                showgrid=False,
            ),
            showlegend=False,
        )

        if winner_match.empty:
            st.markdown(f"""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:12px 16px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;font-style:italic;font-size:12px;">
                    Physical data available only for GC winners. <strong>{rider_main.title()}</strong> is shown in context with all champions.
                </div>
            """, unsafe_allow_html=True)

        st.plotly_chart(fig_strips, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── LONGEVITY vs PEAK ──
        st.markdown("""
            <span class="r-section-label">· Longevity vs Peak ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Career Longevity vs Peak Performance
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                Each dot = a rider with 3+ participations. X = best GC rank ever. Y = total Tours ridden. Selected riders highlighted.
            </p>
        """, unsafe_allow_html=True)

        df_longevity = df_r_norm.groupby('Rider').agg(
            partecipazioni=('Year', 'count'),
            best_rank=('Rank_Num', 'min')
        ).reset_index()
        df_longevity = df_longevity[df_longevity['partecipazioni'] >= 3]
        df_longevity['is_selected'] = df_longevity['Rider'].isin(riders_sel)
        df_longevity['size'] = df_longevity['is_selected'].map({True: 16, False: 6})
        df_longevity['color'] = '#c8bfad'

        for i, rider in enumerate(riders_sel):
            df_longevity.loc[df_longevity['Rider'] == rider, 'color'] = PALETTE[i]

        fig_long = go.Figure()

        # Background dots
        df_bg = df_longevity[~df_longevity['is_selected']]
        fig_long.add_trace(go.Scatter(
            x=df_bg['best_rank'], y=df_bg['partecipazioni'],
            mode='markers',
            marker=dict(size=6, color='#c8bfad', opacity=0.5, line=dict(width=0.5, color='#888')),
            showlegend=False,
            hovertemplate='<b>%{customdata[0]}</b><br>Best: #%{x}<br>Tours: %{y}<extra></extra>',
            customdata=df_bg[['Rider']].values,
        ))

        # Selected riders
        for i, rider in enumerate(riders_sel):
            df_sel = df_longevity[df_longevity['Rider'] == rider]
            if df_sel.empty:
                continue
            fig_long.add_trace(go.Scatter(
                x=df_sel['best_rank'], y=df_sel['partecipazioni'],
                mode='markers+text',
                marker=dict(size=18, color=PALETTE[i], line=dict(width=2, color='white'), symbol='star'),
                text=[rider.title()],
                textposition='top center',
                textfont=dict(size=10, color=PALETTE[i]),
                name=rider.title(),
                hovertemplate=f'<b>{rider.title()}</b><br>Best GC: #%{{x}}<br>Tours ridden: %{{y}}<extra></extra>',
            ))

        fig_long.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(title='Best GC Rank (lower = better)', showgrid=True, gridcolor='#e8e4da'),
            yaxis=dict(title='Total Tour participations', showgrid=True, gridcolor='#e8e4da'),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
        )
        # Quadrant labels
        fig_long.add_annotation(x=2, y=14, text='🏆 Elite Champions', showarrow=False,
                                font=dict(size=10, color='#888', family='Arial'), opacity=0.7)
        fig_long.add_annotation(x=50, y=14, text='🐢 Loyal Domestiques', showarrow=False,
                                font=dict(size=10, color='#888', family='Arial'), opacity=0.7)
        st.plotly_chart(fig_long, use_container_width=True)


    # ══════════════════════════════════════════════════════════
    # TAB 3 — HEAD-TO-HEAD
    # ══════════════════════════════════════════════════════════
    elif st.session_state.riders_tab == "h2h":

        st.markdown("""
            <span class="r-section-label">· The Duel ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Head-to-Head — The Greatest Rivalries
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                Select up to 3 riders. Career normalized: Tour #1 vs Tour #1, regardless of the year.
                <strong>⚠ Max 3 riders.</strong>
            </p>
        """, unsafe_allow_html=True)

        PALETTE_H2H = ['#FFCC00', '#FF6B6B', '#4ECDC4']
        all_riders_h2h = sorted(df_r_norm['Rider'].dropna().unique())

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            h2h_r1 = st.selectbox("Fighter 1:", all_riders_h2h,
                                  index=all_riders_h2h.index('EDDY MERCKX') if 'EDDY MERCKX' in all_riders_h2h else 0,
                                  key='h2h_r1')
        with col_h2:
            others2 = [r for r in all_riders_h2h if r != h2h_r1]
            h2h_r2 = st.selectbox("Fighter 2:", others2,
                                  index=others2.index('BERNARD HINAULT') if 'BERNARD HINAULT' in others2 else 0,
                                  key='h2h_r2')
        with col_h3:
            others3 = [r for r in all_riders_h2h if r not in [h2h_r1, h2h_r2]]
            h2h_add = st.selectbox("Fighter 3 (optional):", ['— None —'] + others3, key='h2h_r3')

        h2h_riders = [h2h_r1, h2h_r2]
        if h2h_add != '— None —':
            h2h_riders.append(h2h_add)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── FIGHTER CARDS (stile mix giornale/videogame) ──
        cols_fighters = st.columns(len(h2h_riders) * 2 - 1)

        for fi, rider in enumerate(h2h_riders):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num'])
            n_tours = len(df_rd)
            best_rank = int(df_rd['Rank_Num'].min()) if n_tours > 0 else 'N/A'
            wins = len(df_w_clean[df_w_clean['Winner'].str.upper().str.strip() == rider.strip()])
            top10 = len(df_rd[df_rd['Rank_Num'] <= 10])
            color = PALETTE_H2H[fi]

            # Country
            wrow = df_w_clean[df_w_clean['Winner'].str.upper().str.strip() == rider.strip()]
            country = wrow['Country_clean'].values[0] if not wrow.empty else '—'
            rider_type = wrow['rt_clean'].values[0].strip().title() if not wrow.empty else '—'

            card_col_idx = fi * 2

            # Calcolo barre (normalizzate su max possibile)
            bar_wins = min(100, (wins / 7) * 100)      # max 7 (Merckx/Armstrong/Indurain)
            bar_top10 = min(100, (top10 / n_tours) * 100) if n_tours > 0 else 0
            bar_tours = min(100, (n_tours / 16) * 100) # max 16

            with cols_fighters[card_col_idx]:
                st.markdown(f"""
                    <div class="fighter-card fighter-card-{fi+1}">
                        <div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;
                                    color:{color};font-family:Arial;margin-bottom:4px;">
                            Fighter {fi+1}
                        </div>
                        <div class="fighter-name">{rider.title()}</div>
                        <div class="fighter-country">{country} · {rider_type}</div>
                        <hr style="border:none;border-top:1px solid #2a2a2a;margin:10px 0;">

                        <div class="fighter-stat-row">
                            <span class="fighter-stat-label">GC Victories</span>
                            <span class="fighter-stat-val" style="color:{color};">{wins}</span>
                        </div>
                        <div class="fighter-bar-wrap">
                            <div class="fighter-bar" style="width:{bar_wins:.0f}%;background:{color};"></div>
                        </div>

                        <div class="fighter-stat-row" style="margin-top:10px;">
                            <span class="fighter-stat-label">Tours Ridden</span>
                            <span class="fighter-stat-val" style="color:{color};">{n_tours}</span>
                        </div>
                        <div class="fighter-bar-wrap">
                            <div class="fighter-bar" style="width:{bar_tours:.0f}%;background:{color};"></div>
                        </div>

                        <div class="fighter-stat-row" style="margin-top:10px;">
                            <span class="fighter-stat-label">Top-10 Rate</span>
                            <span class="fighter-stat-val" style="color:{color};">{bar_top10:.0f}%</span>
                        </div>
                        <div class="fighter-bar-wrap">
                            <div class="fighter-bar" style="width:{bar_top10:.0f}%;background:{color};"></div>
                        </div>

                        <div class="fighter-stat-row" style="margin-top:10px;">
                            <span class="fighter-stat-label">Best GC Result</span>
                            <span class="fighter-stat-val" style="color:{color};">#{best_rank}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # VS badge tra i corridori
            if fi < len(h2h_riders) - 1:
                with cols_fighters[card_col_idx + 1]:
                    st.markdown(f"""
                        <div class="vs-badge"
                             style="font-size:32px;font-weight:900;color:#FFCC00;
                                    text-align:center;padding:60px 0;
                                    font-family:'Merriweather',serif;
                                    text-shadow:0 0 20px rgba(255,204,0,0.3);">
                            VS
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(hr, unsafe_allow_html=True)

        # ── CAREER ARC normalizzato H2H ──
        st.markdown("""
            <span class="r-section-label">· The Race Through Careers ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Career Arc — Side by Side, Tour by Tour
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                X = career participation number. Both start from Tour #1. Year labels shown on each point.
            </p>
        """, unsafe_allow_html=True)

        fig_h2h_arc = go.Figure()
        for i, rider in enumerate(h2h_riders):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num']).sort_values('anno_carriera')
            if df_rd.empty:
                continue
            color = PALETTE_H2H[i]
            fig_h2h_arc.add_trace(go.Scatter(
                x=df_rd['anno_carriera'], y=df_rd['Rank_Num'],
                mode='lines+markers',
                name=rider.title(),
                line=dict(color=color, width=3),
                marker=dict(size=11, color=color, line=dict(width=2, color='white')),
                hovertemplate=(
                    f'<b>{rider.title()}</b><br>'
                    'Tour #%{x} of career (%{customdata[0]})<br>'
                    'GC Rank: #%{y}<extra></extra>'
                ),
                customdata=df_rd[['Year']].values,
            ))
            for _, row in df_rd.iterrows():
                fig_h2h_arc.add_annotation(
                    x=row['anno_carriera'], y=row['Rank_Num'],
                    text=str(int(row['Year'])),
                    showarrow=False,
                    font=dict(size=8, color=color, family='Arial'),
                    yshift=14,
                )

        fig_h2h_arc.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center', font=dict(size=11)),
            xaxis=dict(
                title='Tour participation in career',
                tickmode='linear', dtick=1,
                tickvals=list(range(1, 17)),
                ticktext=[f'Tour #{n}' for n in range(1, 17)],
                showgrid=False, tickfont=dict(size=9),
            ),
            yaxis=dict(title='GC Final Rank', autorange='reversed',
                       showgrid=True, gridcolor='#e8e4da'),
        )
        fig_h2h_arc.add_hrect(y0=1, y1=3, fillcolor='rgba(255,204,0,0.08)',
                              line_width=0, annotation_text='Podium zone',
                              annotation_position='right', annotation_font=dict(size=9, color='#aaa'))
        st.plotly_chart(fig_h2h_arc, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── WIN/LOSS DOTS per anni condivisi ──
        st.markdown("""
            <span class="r-section-label">· Direct Duels ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Head-to-Head Record — Shared Editions
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:16px;">
                Each column = an edition where both competed. Color = who finished higher.
            </p>
        """, unsafe_allow_html=True)

        # Shared years between rider 1 and 2
        years_r1 = set(df_r_norm[df_r_norm['Rider'] == h2h_r1]['Year'].values)
        years_r2 = set(df_r_norm[df_r_norm['Rider'] == h2h_r2]['Year'].values)
        shared_years = sorted(years_r1 & years_r2)

        if shared_years:
            duel_rows = []
            for yr in shared_years:
                row1 = df_r_norm[(df_r_norm['Rider'] == h2h_r1) & (df_r_norm['Year'] == yr)]
                row2 = df_r_norm[(df_r_norm['Rider'] == h2h_r2) & (df_r_norm['Year'] == yr)]
                if row1.empty or row2.empty:
                    continue
                rk1 = row1['Rank_Num'].values[0]
                rk2 = row2['Rank_Num'].values[0]
                if pd.isna(rk1) or pd.isna(rk2):
                    continue
                winner_this_year = h2h_r1 if rk1 < rk2 else h2h_r2
                duel_rows.append({
                    'Year': yr, 'Rank_R1': rk1, 'Rank_R2': rk2,
                    'Winner': winner_this_year, 'Gap': abs(int(rk1) - int(rk2))
                })

            if duel_rows:
                df_duel = pd.DataFrame(duel_rows)
                wins_r1 = (df_duel['Winner'] == h2h_r1).sum()
                wins_r2 = (df_duel['Winner'] == h2h_r2).sum()

                # Scoreboard
                st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:center;gap:32px;
                                margin:16px 0;font-family:'Merriweather',serif;">
                        <div style="text-align:center;">
                            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#888;">{h2h_r1.title()}</div>
                            <div style="font-size:52px;font-weight:900;color:{PALETTE_H2H[0]};line-height:1;">{wins_r1}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:11px;color:#888;">shared<br>editions</div>
                            <div style="font-size:28px;font-weight:700;color:#1a1a1a;">{len(df_duel)}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#888;">{h2h_r2.title()}</div>
                            <div style="font-size:52px;font-weight:900;color:{PALETTE_H2H[1]};line-height:1;">{wins_r2}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Dot chart per anno
                fig_duel = go.Figure()

                for _, row in df_duel.iterrows():
                    color_dot = PALETTE_H2H[0] if row['Winner'] == h2h_r1 else PALETTE_H2H[1]
                    winner_name = h2h_r1.title() if row['Winner'] == h2h_r1 else h2h_r2.title()
                    fig_duel.add_trace(go.Scatter(
                        x=[row['Year']], y=[0],
                        mode='markers+text',
                        marker=dict(size=28, color=color_dot, line=dict(width=2, color='white')),
                        text=[str(int(row['Year']))],
                        textposition='top center',
                        textfont=dict(size=9, color='#1a1a1a', family='Arial'),
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{int(row['Year'])}</b><br>"
                            f"🥇 {winner_name}<br>"
                            f"{h2h_r1.title()}: #{int(row['Rank_R1'])}<br>"
                            f"{h2h_r2.title()}: #{int(row['Rank_R2'])}<br>"
                            f"Gap: {int(row['Gap'])} positions<extra></extra>"
                        ),
                    ))

                fig_duel.update_layout(
                    plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                    height=160, margin=dict(l=0, r=0, t=40, b=20),
                    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
                    yaxis=dict(visible=False, range=[-0.5, 0.8]),
                    showlegend=False,
                )

                # Legend manuale
                for i, (rider, color) in enumerate([(h2h_r1, PALETTE_H2H[0]), (h2h_r2, PALETTE_H2H[1])]):
                    fig_duel.add_annotation(
                        x=0.02 + i * 0.35, y=1.15, xref='paper', yref='paper',
                        text=f'● {rider.title()} wins',
                        showarrow=False, font=dict(size=10, color=color, family='Arial'),
                    )

                st.plotly_chart(fig_duel, use_container_width=True)
            else:
                st.info("No direct duel data available for these riders in shared editions.")
        else:
            st.markdown(f"""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:12px 16px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;font-style:italic;font-size:12px;">
                    {h2h_r1.title()} and {h2h_r2.title()} never raced the Tour in the same year.
                </div>
            """, unsafe_allow_html=True)

        # ── PARALLEL COORDINATES ──
        st.markdown(hr, unsafe_allow_html=True)
        st.markdown("""
            <span class="r-section-label">· Multi-Dimensional Comparison ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Parallel Coordinates — All Dimensions at Once
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                Each line = one Tour edition. Axes: GC Rank · GapSeconds · Career Tour #. Drag axes to reorder.
            </p>
        """, unsafe_allow_html=True)

        df_para_list = []
        for i, rider in enumerate(h2h_riders):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num']).copy()
            df_rd['rider_idx'] = i
            df_rd['rider_name'] = rider.title()
            df_para_list.append(df_rd)

        if df_para_list:
            df_para = pd.concat(df_para_list)
            df_para['GapSeconds_safe'] = df_para['GapSeconds'].fillna(0).clip(upper=20000)

            fig_para = px.parallel_coordinates(
                df_para,
                color='rider_idx',
                dimensions=['anno_carriera', 'Rank_Num', 'GapSeconds_safe'],
                labels={
                    'anno_carriera': 'Career Tour #',
                    'Rank_Num': 'GC Rank',
                    'GapSeconds_safe': 'Gap (sec)',
                    'rider_idx': 'Rider'
                },
                color_continuous_scale=PALETTE_H2H[:len(h2h_riders)],
            )
            fig_para.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
                height=380, margin=dict(l=60, r=60, t=40, b=20),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_para, use_container_width=True)


    # ══════════════════════════════════════════════════════════
    # TAB 4 — NATIONS
    # ══════════════════════════════════════════════════════════
    elif st.session_state.riders_tab == "nations":

        st.markdown("""
            <span class="r-section-label">· Geographic Analysis ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Nations of the Tour — Where Champions Are Born
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                Choropleth map of Tour de France GC victories by country. Hover for details.
            </p>
        """, unsafe_allow_html=True)

        # ── CHOROPLETH ──
        df_choro = df_w_clean.groupby(['Country_clean', 'ISO']).size().reset_index(name='victories')
        # Merge USA
        df_choro.loc[df_choro['Country_clean'] == 'USA', 'ISO'] = 'USA'

        fig_choro = px.choropleth(
            df_choro,
            locations='ISO',
            color='victories',
            hover_name='Country_clean',
            hover_data={'victories': True, 'ISO': False},
            color_continuous_scale=[
                [0, '#F4F1EA'],
                [0.05, '#FFF3CD'],
                [0.2, '#FFDD57'],
                [0.5, '#FFCC00'],
                [0.8, '#FF8C00'],
                [1.0, '#1a1a1a']
            ],
            labels={'victories': 'GC Victories'},
        )
        fig_choro.update_geos(
            showcoastlines=True, coastlinecolor='#c8bfad',
            showland=True, landcolor='#F4F1EA',
            showocean=True, oceancolor='#e8f4f8',
            showframe=False,
            projection_type='natural earth',
            center=dict(lat=48, lon=10),
            lataxis_range=[35, 72],
            lonaxis_range=[-15, 40],
        )
        fig_choro.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=480, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(
                title='Victories', tickfont=dict(size=10),
                len=0.6, thickness=12,
            ),
        )
        st.plotly_chart(fig_choro, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── TREEMAP dominance ──
        st.markdown("""
            <span class="r-section-label">· Victory Share ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Treemap — The Weight of Nations
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                Each rectangle = a country. Size = total GC victories. Color = share (%).
            </p>
        """, unsafe_allow_html=True)

        df_tree = df_w_clean.groupby('Country_clean').size().reset_index(name='victories')
        df_tree = df_tree[df_tree['victories'] > 0]
        df_tree['pct'] = (df_tree['victories'] / df_tree['victories'].sum() * 100).round(1)
        df_tree['label'] = df_tree['Country_clean'] + '<br>' + df_tree['victories'].astype(str) + ' wins'

        fig_tree = px.treemap(
            df_tree,
            path=['Country_clean'],
            values='victories',
            color='pct',
            color_continuous_scale=[
                [0, '#F4F1EA'], [0.1, '#FFF3CD'], [0.4, '#FFCC00'],
                [0.7, '#FF8C00'], [1.0, '#1a1a1a']
            ],
            hover_data={'pct': ':.1f'},
            labels={'pct': '% of all wins', 'victories': 'GC Victories'},
            custom_data=['victories', 'pct'],
        )
        fig_tree.update_traces(
            texttemplate='<b>%{label}</b><br>%{customdata[0]} wins · %{customdata[1]:.1f}%',
            textfont=dict(size=12, family='Merriweather, serif'),
            hovertemplate='<b>%{label}</b><br>GC Victories: %{customdata[0]}<br>Share: %{customdata[1]:.1f}%<extra></extra>',
        )
        fig_tree.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=420, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── DECADE DOMINANCE TABLE ──
        st.markdown("""
            <span class="r-section-label">· Era by Era ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                Who Ruled Each Decade?
            </h4>
        """, unsafe_allow_html=True)

        df_dec = df_w_clean.groupby(['decade', 'Country_clean']).size().reset_index(name='wins')
        df_dec_pivot = df_dec.pivot(index='Country_clean', columns='decade', values='wins').fillna(0).astype(int)
        df_dec_pivot.columns = [f"{int(c)}s" for c in df_dec_pivot.columns]
        df_dec_pivot['TOTAL'] = df_dec_pivot.sum(axis=1)
        df_dec_pivot = df_dec_pivot.sort_values('TOTAL', ascending=False)
        df_dec_pivot.index.name = 'Nation'

        st.dataframe(
            df_dec_pivot.style.background_gradient(cmap='YlOrBr', subset=df_dec_pivot.columns[:-1])
                              .format('{:.0f}')
                              .set_properties(**{'font-family': 'Merriweather, serif', 'font-size': '12px'}),
            use_container_width=True,
        )

        
elif st.session_state.pagina_corrente == "tappe":
    
    # ==========================================
    # 1. INIZIALIZZAZIONE DELLO STATO "ZERO SCROLL"
    # ==========================================
    if "vista_tappe" not in st.session_state:
        st.session_state.vista_tappe = "storico"

    # ==========================================
    # 2. INIEZIONE CSS
    # ==========================================
    st.markdown("""
        <style>
        /* 1. Forza il testo dei Radio Button e delle loro opzioni al NERO */
        div[data-testid="stRadio"] label, 
        div[data-testid="stRadio"] p,
        div[data-testid="stRadio"] span {
            color: #000000 !important;
        }        
        div[data-baseweb="select"] > div {
            background-color: #111111 !important; 
            color: #FFFFFF !important; 
            border-radius: 5px !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] > div > div,
        div[data-baseweb="popover"] ul,
        ul[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #111111 !important;
        }
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] li span,
        ul[data-baseweb="menu"] li {
            color: #FFFFFF !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] li:hover,
        ul[data-baseweb="menu"] li:hover {
            background-color: #333333 !important;
        }
        /* Label selectbox in NERO */
        .stSelectbox label,
        div[data-testid="stSelectbox"] label p {
            color: #000000 !important;
            font-weight: bold !important;
        }
        /* CSS per lo slider */
        [data-testid="stSlider"] {
            background-color: #000000;
            padding: 15px 20px;
            border-radius: 8px;
        }
        [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
        }
        [data-testid="stSliderTickBarMin"], 
        [data-testid="stSliderTickBarMax"], 
        div[data-testid="stSlider"] div {
            color: #ffffff !important;
        }
        
        /* ---> STILE ESCLUSIVO PER I BOTTONI DELLE CARD (type="primary") <--- */
        button[kind="primary"] {
            background-color: #FAFF00 !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 0px !important;
            font-weight: 900 !important;
            font-size: 16px !important;
            padding: 15px !important;
            border-bottom: 0px !important; 
            transition: all 0.2s ease-in-out;
            margin-top: -15px !important; 
            text-transform: uppercase;
        }
        button[kind="primary"]:hover {
            background-color: #000000 !important;
            color: #FAFF00 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # --- PREPARAZIONE DATI ---
    df_stage_h['Year'] = df_stage_h['Year'].fillna(0).astype(int)

    st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🗺️ Stages and Routes Analysis</h2>", unsafe_allow_html=True)

    # ==========================================
    # URL IMMAGINI CARD — modifica qui per cambiare le foto
    # ==========================================
    URL_CARD1 = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9RqpfLR4o-8OqXaHgfkX3i_AQWqHXGhGGkQ&s" 
    URL_CARD2 = "https://cdn.shopify.com/s/files/1/0040/5251/6910/files/GettyImages-1232277_1024x1024.jpg?v=1624033149"  # Maglie Tour
    URL_CARD3 = "https://preview.redd.it/map-of-all-the-stages-in-the-history-of-the-tour-de-france-v0-v1t2yrg7zzyf1.jpeg?width=1080&crop=smart&auto=webp&s=16442894182572aebe679320c02811e74f233f67"
        
    # ==========================================
    # 4. CREAZIONE DELLE 3 CARD FOTOGRAFICHE
    # ==========================================
    def create_image_card(subtitle, title, bg_url):
        return f"""
        <div style="
            position: relative;
            height: 250px;
            background-image: url('{bg_url}');
            background-size: cover;
            background-position: center;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        ">
            <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 70%; background: linear-gradient(to top, rgba(0,0,0,0.95), transparent);"></div>
            <div style="position: absolute; bottom: 15px; left: 15px; right: 15px; z-index: 2; color: white; font-family: 'Arial', sans-serif;">
                <div style="font-size: 14px; font-weight: bold; color: #FAFF00; letter-spacing: 1px; margin-bottom: 5px;">{subtitle}</div>
                <div style="font-size: 22px; font-weight: 900; line-height: 1.1; text-transform: uppercase;">{title}</div>
            </div>
        </div>
        """

    col_card1, col_card2, col_card3 = st.columns(3, gap="medium")

    with col_card1:
        st.markdown(create_image_card("SECTION 1 | DATA", "GENERAL<br>HISTORICAL TRENDS", URL_CARD1), unsafe_allow_html=True)
        if st.button("FIND OUT MORE", key="btn_storico", type="primary", use_container_width=True):
            st.session_state.vista_tappe = "storico"

    with col_card2:
        st.markdown(create_image_card("SECTION 2 | EDITIONS", "DETAILS<br>& JERSEYS", URL_CARD2), unsafe_allow_html=True)
        if st.button("FIND OUT MORE", key="btn_dettaglio", type="primary", use_container_width=True):
            st.session_state.vista_tappe = "dettaglio"

    with col_card3:
        st.markdown(create_image_card("SECTION 3 | GEOGRAPHY", "GEOGRAPHICAL<br>EXPLORATION", URL_CARD3), unsafe_allow_html=True)
        if st.button("FIND OUT MORE", key="btn_mappa", type="primary", use_container_width=True):
            st.session_state.vista_tappe = "mappa"

    st.markdown("<hr style='border: 1px solid #FFCC00; margin-top: 35px; margin-bottom: 30px;'>", unsafe_allow_html=True)


    # ==========================================
    # 5. GESTIONE DEL CONTENUTO "ZERO SCROLL"
    # ==========================================
    vista_corrente = st.session_state.vista_tappe

    # ---------------------------------------------------------
    # VISTA 1: STORICO 
    # ---------------------------------------------------------
    if vista_corrente == "storico":
       
        anno_min_assoluto = int(df_stage_h[df_stage_h['Year'] > 0]['Year'].min())
        anno_max_assoluto = int(df_stage_h['Year'].max())

        anno_min, anno_max = st.slider(
            "Select the historical period to display in the charts below:",
            min_value=anno_min_assoluto,
            max_value=anno_max_assoluto,
            value=(anno_min_assoluto, anno_max_assoluto), 
            step=1
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_dist1, col_dist2 = st.columns(2)

        with col_dist1:
            df_dist_filtered = df_stage_h[(df_stage_h['Year'] >= anno_min) & (df_stage_h['Year'] <= anno_max)]
            df_distanza = df_dist_filtered.groupby('Year')['TotalTDFDistance'].max().reset_index()
            df_distanza = df_distanza.set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()
            
            fig_dist = px.line(df_distanza, x='Year', y='TotalTDFDistance', 
                               labels={'TotalTDFDistance': '', 'Year': 'Year'}, markers=True)
            fig_dist.update_traces(line_color='#FFCC00', line_width=3, marker=dict(size=4, color='white'), connectgaps=False)
            
            fig_dist.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                               annotation_text="World War I", annotation_position="inside bottom left",
                               annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
            fig_dist.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                               annotation_text="World War II", annotation_position="inside bottom left",
                               annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

            fig_dist.update_layout(
                title=dict(text="<b>Total Distance (km)</b>", font=dict(color="white", size=18, family="sans-serif")),
                plot_bgcolor="black", 
                paper_bgcolor="black", 
                font=dict(color="white", family="sans-serif"),
                height=380, margin=dict(l=0, r=0, t=50, b=0), 
                xaxis=dict(range=[anno_min, anno_max])
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        with col_dist2:
            df_dist_avg = df_dist_filtered.groupby('Year').agg({'TotalTDFDistance': 'max', 'Stages': 'count'}).reset_index()
            df_dist_avg['Distanza_Media_Tappa'] = df_dist_avg['TotalTDFDistance'] / df_dist_avg['Stages']
            df_dist_avg = df_dist_avg.set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()
            
            fig_avg_dist = px.area(df_dist_avg, x='Year', y='Distanza_Media_Tappa',
                                   labels={'Distanza_Media_Tappa': '', 'Year': 'Year'})
            fig_avg_dist.update_traces(line_color='#FF6666', fillcolor='rgba(255, 102, 102, 0.3)', connectgaps=False)
            
            fig_avg_dist.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                                   annotation_text="World War I", annotation_position="inside bottom left",
                                   annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
            fig_avg_dist.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                                   annotation_text="World War II", annotation_position="inside bottom left",
                                   annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

            fig_avg_dist.update_layout(
                title=dict(text="<b>Intensity: Average Km per Stage</b>", font=dict(color="white", size=18, family="sans-serif")),
                plot_bgcolor="black", 
                paper_bgcolor="black", 
                font=dict(color="white", family="sans-serif"),
                height=380, margin=dict(l=0, r=0, t=50, b=0),
                xaxis=dict(range=[anno_min, anno_max])
            )
            st.plotly_chart(fig_avg_dist, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        df_vincitori = df_storico[(df_storico['Rank'] == 1) | (df_storico['Rank'] == '1')].copy()
        df_vincitori = df_vincitori[df_vincitori['TotalSeconds'].notna() & (df_vincitori['TotalSeconds'] > 0)]
        df_vincitori['Velocità Media (km/h)'] = df_vincitori['Distance (km)'] / (df_vincitori['TotalSeconds'] / 3600)
        
        df_vincitori_filtered = df_vincitori[(df_vincitori['Year'] >= anno_min) & (df_vincitori['Year'] <= anno_max)]
        df_vincitori_chart = df_vincitori_filtered[['Year', 'Velocità Media (km/h)']].set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()

        fig_vel = px.line(df_vincitori_chart, x='Year', y='Velocità Media (km/h)', 
                          labels={'Velocità Media (km/h)': 'Average Speed (km/h)', 'Year': 'Year'}, markers=True)
        fig_vel.update_traces(line_color='#FFCC00', line_width=3, marker=dict(size=5, color='white'), connectgaps=False)
        
        fig_vel.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                          annotation_text="World War I", annotation_position="inside bottom left",
                          annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
        fig_vel.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                          annotation_text="World War II", annotation_position="inside bottom left",
                          annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

        try:
            y_1998 = df_vincitori[df_vincitori['Year'] == 1998]['Velocità Media (km/h)'].iloc[0]
            y_2006 = df_vincitori[df_vincitori['Year'] == 2006]['Velocità Media (km/h)'].iloc[0]

            fig_vel.add_scatter(x=[1998, 2006], y=[y_1998, y_2006], mode='lines', line=dict(color='#FF3333', width=2, dash='dash'), hoverinfo='skip', showlegend=False)

            anni_buco = list(range(1999, 2006))
            step = (y_2006 - y_1998) / (2006 - 1998)
            y_buco = [y_1998 + step * (anno - 1998) for anno in anni_buco]
            testo_hover = ["<b>Doping Disqualifications</b><br>Titles of L. Armstrong (1999-2005) and F. Landis (2006)<br>were canceled and never reassigned."] * len(anni_buco)

            fig_vel.add_scatter(x=anni_buco, y=y_buco, mode='markers', marker=dict(size=7, color='#FF3333', symbol='x', line=dict(width=2)),
                                hoverinfo='text', hovertext=testo_hover, showlegend=False)
            
            fig_vel.add_vrect(x0=1998.5, x1=2006, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                              annotation_text="Revoked Titles", annotation_position="inside bottom left",
                              annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
        except Exception as e:
            pass 

        fig_vel.update_layout(
            title=dict(text="<b>Evolution of Average Speed</b>", font=dict(color="white", size=20, family="sans-serif")),
            plot_bgcolor="black", 
            paper_bgcolor="black", 
            font=dict(color="white", family="sans-serif"),
            height=450, margin=dict(l=0, r=0, t=60, b=0), 
            xaxis=dict(range=[anno_min, anno_max])
        )
        st.plotly_chart(fig_vel, use_container_width=True)

    # ---------------------------------------------------------
    # VISTA 2: DETTAGLIO 
    # ---------------------------------------------------------
    elif vista_corrente == "dettaglio":
        st.markdown("<p style='font-weight: bold; color: black; font-family: sans-serif; font-size: 1.2rem;'>Route Details and Leaderboard</p>", unsafe_allow_html=True)

        lista_anni = sorted(df_stage_h['Year'].unique(), reverse=True)
        lista_anni = [anno for anno in lista_anni if anno > 0]
        # ✅ label "Select an edition to view details:" in NERO
        anno_scelto = st.selectbox("Select an edition to view details:", lista_anni)

        df_anno = df_stage_h[df_stage_h['Year'] == anno_scelto].sort_values('Stages').copy()

        if not df_anno.empty:
            distanza_tot = df_anno['TotalTDFDistance'].iloc[0] if 'TotalTDFDistance' in df_anno.columns else "N/A"
            num_tappe = len(df_anno)
            
            df_anno['Vincitore_Clean'] = df_anno['Winner of stage'].apply(
                lambda x: str(x).split('(')[0].strip() if pd.notnull(x) else "N/A"
            )
            df_anno['Team'] = df_anno['Winner of stage'].str.extract(r'\((.*?)\)')
            df_anno['Team'] = df_anno['Team'].fillna('Independent/Unknown')

            vittorie_count = df_anno['Vincitore_Clean'].value_counts()
            top_rider = vittorie_count.index[0] if not vittorie_count.empty and vittorie_count.index[0] != "N/A" else "N/A"
            n_vittorie = vittorie_count.iloc[0] if not vittorie_count.empty else 0

            vincitore_finale = "N/A"
            cambi_maglia = "N/A"
            colonna_leader = 'Yellow Jersey' 
            
            if colonna_leader in df_anno.columns:
                leader_validi = df_anno[colonna_leader].dropna()
                if not leader_validi.empty:
                    vincitore_finale = leader_validi.iloc[-1]
                    cambi_maglia = (df_anno[colonna_leader] != df_anno[colonna_leader].shift()).sum() - 1
                    cambi_maglia = max(0, cambi_maglia)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Distance", f"{distanza_tot} km")
            m2.metric("Final Winner", vincitore_finale)
            m3.metric("Cannibal (Stage Wins)", top_rider, f"{n_vittorie} stages")
            m4.metric("Yellow Jersey Changes", cambi_maglia)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"<h3 style='color: black; margin-bottom: 10px;'>Leadership Evolution in {anno_scelto}</h3>", unsafe_allow_html=True)
            
            # Definizione del dizionario di configurazione delle maglie
            maglie_config = {
                "Yellow": {
                    "col": "Yellow Jersey", 
                    "color": "#FFCC00", 
                    "img": "https://www.bobshop.com/media/92/7a/02/1776411535/11346-1_1.png?ts=1776411535",
                    "anno_intro": 1919,
                    "storia": "The Yellow Jersey was introduced in 1919. Before then, the leader was identified only by a green armband. It matches the yellow paper of the historical *L'Auto* newspaper."
                },
                "Green": {
                    "col": "Green jersey", 
                    "color": "#009900", 
                    "img": "https://lh3.googleusercontent.com/d/1d1GLPgO6NHqt4bguSBdXjs8NowirbXAu",
                    "anno_intro": 1953,
                    "storia": "The Green Jersey (points classification) was created in 1953 to celebrate the 50th anniversary of the Tour de France. It rewards the most consistent sprinters."
                },
                "Polka-dot": {
                    "col": "Polka-dot jersey", 
                    "color": "#FF0000", 
                    "img": "https://lh3.googleusercontent.com/d/1sOEebeyDAuhP0Mt6I5L4poKbahfv3xky",
                    "anno_intro": 1975,
                    "storia": "Although the Mountains Classification has existed since 1933, the famous red and white Polka-dot jersey was officially born only in 1975 to reward the King of the Mountains!"
                },
                "White": {
                    "col": "White jersey", 
                    "color": "#CCCCCC", 
                    "img": "https://lh3.googleusercontent.com/d/1DAYUL8bk7eYxd83opOKJCkYT_afuKWdp",
                    "anno_intro": 1975,
                    "storia": "The White Jersey, reserved for the best young rider (currently Under-25) in the General Classification, was established in 1975."
                }
            }

            # Il selettore radio nativo per le maglie
            scelta_maglia = st.radio(
                "Select the jersey:", 
                list(maglie_config.keys()), 
                horizontal=True
            )

            # ==========================================
            # ℹ️ NUOVO POPOVER DINAMICO E CONTESTUALE
            # ==========================================
            colore_testo_popup = maglie_config[scelta_maglia]["color"]
            
            with st.popover(f"ℹ️ Read about the {scelta_maglia} Jersey", use_container_width=True):
                st.markdown(f"### <span style='color: {colore_testo_popup};'>{scelta_maglia} Jersey Classification</span>", unsafe_allow_html=True)
                st.markdown(maglie_config[scelta_maglia]["storia"])

            st.markdown("<br>", unsafe_allow_html=True)

            col_selezionata = maglie_config[scelta_maglia]["col"]
            colore_linea = maglie_config[scelta_maglia]["color"]
            url_immagine = maglie_config[scelta_maglia]["img"]
            anno_introduzione = maglie_config[scelta_maglia]["anno_intro"]

            if anno_scelto < anno_introduzione:
                testo_storia = f"🕰️ <b>A bit of history:</b> In {anno_scelto} this jersey did not exist yet. {maglie_config[scelta_maglia]['storia']}"
                st.markdown(
                    f"""
                    <div style="background-color: #f5f0e6; border-left: 5px solid #FFCC00; padding: 15px; border-radius: 5px; color: black; font-family: sans-serif;">
                        {testo_storia}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            elif col_selezionata in df_anno.columns and not df_anno[col_selezionata].dropna().empty:
                df_leader = df_anno.dropna(subset=[col_selezionata]).copy()
                ordine_cronologico = df_leader[col_selezionata].drop_duplicates().tolist()
                
                fig_leader = px.line(df_leader, x='Stages', y=col_selezionata)
                fig_leader.update_traces(line=dict(color=colore_linea, width=3))
                
                for index, row in df_leader.iterrows():
                    fig_leader.add_layout_image(
                        dict(
                            source=url_immagine, xref="x", yref="y",
                            x=row['Stages'], y=row[col_selezionata],
                            sizex=1.2, sizey=0.9,
                            xanchor="center", yanchor="middle", layer="above"
                        )
                    )
                
                min_tappa = df_leader['Stages'].min() - 1
                max_tappa = df_leader['Stages'].max() + 1
                num_corridori = len(ordine_cronologico)
                
                fig_leader.update_layout(
                    yaxis=dict(
                        title="", categoryorder='array', categoryarray=ordine_cronologico[::-1],
                        range=[-0.5, max(0.5, num_corridori - 0.5)],
                        showgrid=True, gridwidth=1, gridcolor='#333333'
                    ), 
                    xaxis=dict(
                        title="Stage", tickmode='linear', dtick=1,
                        range=[min_tappa, max_tappa],
                        showgrid=True, gridwidth=1, gridcolor='#333333'
                    ),
                    height=max(300, num_corridori * 60), 
                    showlegend=False, 
                    paper_bgcolor="black",   
                    plot_bgcolor="black",    
                    font=dict(color="white"), 
                    margin=dict(l=0, r=0, t=20, b=0)
                )
                st.plotly_chart(fig_leader, use_container_width=True)
                
            else:
                st.warning(f"Data not available for the {scelta_maglia} jersey in the {anno_scelto} edition.")
                
            col_gialla = 'Yellow Jersey'
            col_verde = 'Green' 
            col_pois = 'Polka'  
            col_bianca = 'White'

            maglie_presenti = [col for col in [col_gialla, col_verde, col_pois, col_bianca] if col in df_anno.columns]
            
            if len(maglie_presenti) > 1:
                st.markdown("<h3 style='color: black;'>👕 Jersey holders stage by stage</h3>", unsafe_allow_html=True)
                df_maglie = df_anno[['Stages'] + maglie_presenti].copy()
                st.dataframe(df_maglie, use_container_width=True, hide_index=True)
                
            st.markdown("<br>", unsafe_allow_html=True)

            col_chart1, col_chart2, col_table = st.columns([1, 1, 1.5], gap="medium")

            with col_chart1:
                # ✅ "Multiple Stage Winners" in BIANCO
                st.markdown("<b style='color: white;'>Multiple Stage Winners</b>", unsafe_allow_html=True)
                df_top10 = vittorie_count.reset_index()
                df_top10.columns = ['Athlete', 'Victories']
                df_top10 = df_top10[df_top10['Athlete'] != 'N/A'].head(8) 
                
                fig_vittorie = px.bar(df_top10, y='Athlete', x='Victories', orientation='h', color_discrete_sequence=['#FFCC00'])
                fig_vittorie.update_layout(yaxis={'categoryorder':'total ascending', 'title':''}, xaxis={'title': 'Victories'},
                                           height=350, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_vittorie, use_container_width=True)

            with col_chart2:
                # ✅ "Team Dominance" in BIANCO
                st.markdown("<b style='color: white;'>Team Dominance</b>", unsafe_allow_html=True)
                team_counts = df_anno['Team'].value_counts().reset_index()
                team_counts.columns = ['Team', 'Victories']
                team_counts = team_counts[team_counts['Team'] != 'Independent/Unknown'].head(8) 
                
                fig_team = px.pie(
                    team_counts, 
                    values='Victories', 
                    names='Team', 
                    hole=0.6, 
                    color_discrete_sequence=px.colors.sequential.YlOrBr[::-1] 
                )
                
                fig_team.update_traces(
                    textposition='inside', 
                    textinfo='label+value',
                    hovertemplate='<b>%{label}</b><br>Victories: %{value}<extra></extra>',
                    marker=dict(line=dict(color='#000000', width=2)) 
                )
                fig_team.update_layout(
                    showlegend=False, 
                    height=350, 
                    margin=dict(l=10, r=10, t=20, b=10), 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_team, use_container_width=True)
            
            with col_table:
                # ✅ "Route Details" in BIANCO
                st.markdown("<b style='color: white;'>Route Details</b>", unsafe_allow_html=True)
                cols_to_show = ['Stages', 'Start', 'End', 'Vincitore_Clean']
                df_display = df_anno[cols_to_show].copy()
                st.dataframe(df_display, use_container_width=True, hide_index=True, height=350)
    # ---------------------------------------------------------
    # VISTA 3: MAPPA INTERATTIVA 
    # ---------------------------------------------------------
    elif vista_corrente == "mappa":
        
        url_mappa = "https://preview.redd.it/map-of-all-the-stages-in-the-history-of-the-tour-de-france-v0-v1t2yrg7zzyf1.jpeg?width=1080&crop=smart&auto=webp&s=16442894182572aebe679320c02811e74f233f67"
        
        # --- SOLUZIONE 3: Titolo della sezione in stile Giornalistico ---
        st.markdown("""
            <h3 style='text-align: center; color: #000000; font-family: "Merriweather", Georgia, serif; font-weight: 700; margin-top: 10px; margin-bottom: 25px;'>
                 The Historical Network of Le Tour
            </h3>
        """, unsafe_allow_html=True)
                
        # --- SOLUZIONE 2: Riquadro espositivo d'archivio con didascalia integrata (Centrato senza colonne per rimuovere lo sfondo nero) ---
        st.markdown(f"""
            <div style="
                background-color: #0F172A; 
                padding: 22px; 
                border-radius: 8px; 
                box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
                border: 1px solid #E2E8F0;
                text-align: center;
                max-width: 650px;           /* Blocca la larghezza massima della card */
                margin: 0 auto 30px auto;   /* Centra il blocco nella pagina ed elimina la banda nera */
            ">
                <img src="{url_mappa}" style="width: 100%; border-radius: 4px;">
                <p style='color: #E2E8F0; text-align: center; font-size: 0.95rem; margin-top: 15px; font-style: italic; font-family: "Merriweather", serif; line-height: 1.4;'>
                    The dense network of all stages raced in the history of the Tour de France: a journey through over a century of cycling.
                </p>
            </div>
        """, unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight: bold; color: black; font-family: sans-serif; font-size: 1.2rem;'>Explore Historical Data</p>", unsafe_allow_html=True)

        lista_anni = sorted(df_stage_h['Year'].unique(), reverse=True)
        lista_anni = [anno for anno in lista_anni if anno > 0]
        anno_scelto_mappa = st.selectbox("Select the edition to update the map:", lista_anni, key="select_mappa")

        if not df_coords.empty:
            df_coords_anno = df_coords[df_coords['Year'] == anno_scelto_mappa].copy()
            df_map_plot = df_coords_anno.dropna(subset=['start_lat', 'start_lon', 'end_lat', 'end_lon'])

            if not df_map_plot.empty:
                view_state = pdk.ViewState(
                    latitude=46.2276, 
                    longitude=2.2137, 
                    zoom=5, 
                    pitch=0
                )

                line_layer = pdk.Layer(
                    "LineLayer",
                    df_map_plot,
                    get_source_position="[start_lon, start_lat]",
                    get_target_position="[end_lon, end_lat]",
                    get_color="[255, 204, 0, 200]",
                    get_width=5,
                    pickable=True,
                )

                start_point_layer = pdk.Layer(
                    "ScatterplotLayer",
                    df_map_plot,
                    get_position="[start_lon, start_lat]",
                    get_color="[0, 0, 0, 255]",
                    get_radius=8000,
                    pickable=True,
                )

                end_point_layer = pdk.Layer(
                    "ScatterplotLayer",
                    df_map_plot,
                    get_position="[end_lon, end_lat]",
                    get_color="[0, 0, 0, 255]",
                    get_radius=8000,
                    pickable=True,
                )

                st.pydeck_chart(pdk.Deck(
                    map_style="light", 
                    initial_view_state=view_state,
                    layers=[line_layer, start_point_layer, end_point_layer], 
                    tooltip={
                        "html": "<b>Stage {Stages}</b><br/>From: {Start}<br/>To: {End}",
                        "style": {"color": "white", "backgroundColor": "black"}
                    }
                ))
            else:
                st.info(f"No geographical data found for the year {anno_scelto_mappa}.")

elif st.session_state.pagina_corrente == "teams":
        
        # --- 1. INIEZIONE CSS PER SELECTBOX SCURI E LABEL NERA ---
        css_selectbox_scuro = """
        <style>
            div[data-testid="stSelectbox"] label p {
                color: #000000 !important;
                font-family: 'Georgia', serif !important;
            }
            div[data-baseweb="select"] > div {
                background-color: #111111 !important;
                border: 1px solid #ff0000 !important;
                border-radius: 4px !important;
            }
            div[data-baseweb="select"] span {
                color: #ffffff !important;
                font-family: 'Georgia', serif !important;
                font-size: 16px !important;
            }
            div[data-baseweb="select"] div[data-testid="stSelectbox"] svg,
            div[data-baseweb="select"] svg {
                color: #ffffff !important;
            }
            div[data-baseweb="popover"] div[role="listbox"],
            div[data-baseweb="popover"] ul {
                background-color: #111111 !important;
                border: 1px solid #333333 !important;
            }
            div[data-baseweb="popover"] ul li {
                color: #ffffff !important;
                font-family: 'Georgia', serif !important;
                background-color: #111111 !important;
                padding-top: 10px !important;
                padding-bottom: 10px !important;
            }
            div[data-baseweb="popover"] ul li:hover, 
            div[data-baseweb="popover"] ul li[aria-selected="true"],
            div[data-baseweb="popover"] ul li[aria-selected="true"]:hover {
                background-color: #2b2d30 !important;
                color: #ffffff !important;
            }
        </style>
        """
        st.markdown(css_selectbox_scuro, unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🚴‍♂️ World Tour Teams and Lineups</h2>", unsafe_allow_html=True)
        
        # --- 2. HEADER DELLA PAGINA (Testo Nero) ---
        st.markdown('<h1 class="vintage-title" style="color: #000000;">Team Analysis</h1>', unsafe_allow_html=True)
        st.markdown('<p class="journal-subtitle" style="color: #000000;">Explore the historical performance, roster composition, and palmarès of the teams.</p>', unsafe_allow_html=True)

        # --- 3. GESTIONE DATI STORICI E FILTRI ANOMALIE ---
        anni_revocati = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006]
        
        teams_disponibili = sorted(df_storico['Team'].dropna().unique())
        team_selezionato = st.selectbox("Select a team:", teams_disponibili)
        
        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)

        # Filtraggio dataset principale
        df_team_storico = df_storico[df_storico['Team'] == team_selezionato].copy()
        df_team_storico['Rank_Num'] = pd.to_numeric(df_team_storico['Rank'], errors='coerce')

        
        import unicodedata
        import re

        def pulisci_e_ordina_nome(nome):
            if pd.isna(nome): return ""
            s = str(nome)
            s = re.sub(r'\(.*?\)', '', s) # Rimuove tutto tra parentesi es. (SLO)
            s = re.sub(r'[^a-zA-Z\s]', '', s) # Rimuove asterischi, numeri, punteggiatura
            s = s.lower().strip()
            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            parole = sorted(s.split())
            return " ".join(parole)

        # Puliamo i dataset per il merge
        df_stage_h_clean = df_stage_h.copy()
        df_stage_h_clean['Winner_Clean'] = df_stage_h_clean['Winner of stage'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Yellow_Clean'] = df_stage_h_clean['Yellow Jersey'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Green_Clean'] = df_stage_h_clean['Green jersey'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Pois_Clean'] = df_stage_h_clean['Polka-dot jersey'].apply(pulisci_e_ordina_nome)

        df_storico_clean_all = df_storico[['Year', 'Rider', 'Team']].drop_duplicates().copy()
        df_storico_clean_all['Rider_Clean'] = df_storico_clean_all['Rider'].apply(pulisci_e_ordina_nome)
        
        df_team_storico['Rider_Clean'] = df_team_storico['Rider'].apply(pulisci_e_ordina_nome)

        # Merge tappe vinte individualmente dai corridori
        df_merge_tappe_individuali = pd.merge(
            df_stage_h_clean, 
            df_storico_clean_all, 
            left_on=['Year', 'Winner_Clean'], right_on=['Year', 'Rider_Clean'], how='inner'
        )
        df_tappe_team_individuali = df_merge_tappe_individuali[df_merge_tappe_individuali['Team'] == team_selezionato]

        # Recuperiamo anche le Cronosquadre (TTT) vinte direttamente dal Team
        df_tappe_ttt = df_stage_h_clean[df_stage_h_clean['Winner of stage'].str.contains(str(team_selezionato), case=False, na=False)].copy()
        df_tappe_ttt['Team'] = team_selezionato
        
        # Uniamo le vittorie individuali con quelle di squadra
        df_tappe_team = pd.concat([df_tappe_team_individuali, df_tappe_ttt], ignore_index=True)

        # --- 4. FUNZIONE HELP PER GRAFICI PLOTLY (Testo Bianco Puro) ---
        def applica_tema_vintage(fig):
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Georgia, serif", color="#FFFFFF"), 
                title_font_color="#FFFFFF",
                title_font_size=18,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.15)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.15)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            return fig

        # --- 5. SEZIONE 1: KPI GENERALI DEL TEAM (Versione Sfondo Nero) ---
        vittorie_df = df_team_storico[(df_team_storico['Rank_Num'] == 1) & (~df_team_storico['Year'].isin(anni_revocati))]
        vittorie_totali = len(vittorie_df)
        
        miglior_piazzamento = int(df_team_storico['Rank_Num'].min()) if not df_team_storico['Rank_Num'].isna().all() else "N/A"
        partecipazioni = df_team_storico['Year'].nunique()

        # Nuova iniezione CSS specifica per i KPI Neri
        css_vintage_kpis = """
        <style>
            .vintage-kpi-block-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                margin-bottom: 25px;
            }
            .vintage-kpi-block-title {
                color: #FFFFFF; 
                font-family: 'Georgia', serif !important;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                text-transform: uppercase;
                margin: 0;
            }
            .vintage-card-container-uniform {
                display: flex;
                gap: 15px;
                justify-content: center;
                width: 100%;
            }
            .vintage-card-uniform {
                flex: 1;
                padding: 15px;
                text-align: center;
                /* Background Nero Puro */
                background-color: #000000 !important; 
                /* Bordo Nero */
                border: 2px solid #000000 !important; 
                border-radius: 4px !important;
                /* Ombra leggera per staccarlo dallo sfondo generale (se non è nero) */
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .vintage-card-uniform h4 {
                margin: 0;
                /* Testo Bianco per i titoli interni */
                color: #FFFFFF !important;
                font-family: 'Georgia', serif !important;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .vintage-card-uniform h2 {
                margin: 10px 0 0 0;
                /* Testo Bianco Puro per i numeri */
                color: #FFFFFF !important;
                font-family: 'Georgia', serif !important;
                font-size: 34px;
                font-weight: bold;
            }
        </style>
        """
        st.markdown(css_vintage_kpis, unsafe_allow_html=True)

        # Nuovo HTML dei KPI strutturato e uniformato
        html_kpi_uniformed = f"""
        <div class="vintage-kpi-block-container">
            <h3 class="vintage-kpi-block-title">Team Overview</h3>
            <div class="vintage-card-container-uniform">
                <div class="vintage-card-uniform">
                    <h4>GC Wins</h4>
                    <h2>{vittorie_totali}</h2>
                </div>
                <div class="vintage-card-uniform">
                    <h4>Best Result</h4>
                    <h2>{miglior_piazzamento}</h2>
                </div>
                <div class="vintage-card-uniform">
                    <h4>Total Participations</h4>
                    <h2>{partecipazioni}</h2>
                </div>
            </div>
        </div>
        """
        st.markdown(html_kpi_uniformed, unsafe_allow_html=True)
        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)
        # --- 6. SEZIONE 2: COMPOSIZIONE E STRUTTURA DEL TEAM CORRIDORI ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">Team Roster</h3>', unsafe_allow_html=True)
        
        if not df_team_storico.empty:
            col_comp1, col_comp2 = st.columns(2)

        with col_comp1:
            # Grafico dei plurivincitori di tappe 
            if not df_tappe_team.empty:
                vincitori_tappe = df_tappe_team.groupby('Winner of stage').size().reset_index(name='Tappe Vinte')
                vincitori_tappe = vincitori_tappe.rename(columns={'Winner of stage': 'Corridore'})
                vincitori_tappe = vincitori_tappe.sort_values(by='Tappe Vinte', ascending=False).head(5)
                
                fig_vincitori = px.bar(
                    vincitori_tappe, x='Tappe Vinte', y='Corridore', orientation='h',
                    title="Multiple Stage Winners in the Team",
                    labels={'Corridore': 'Rider', 'Tappe Vinte': 'Number of Stages'}
                )

                fig_vincitori.update_traces(marker_color='#ff6666') 
                
                # 1. Applichiamo prima il tema vintage generale
                fig_vincitori = applica_tema_vintage(fig_vincitori)
                
                # 2. Forziamo il titolo bianco e l'ordinamento alla fine.
                # In questo modo "vince" su qualsiasi configurazione precedente!
                fig_vincitori.update_layout(
                    title_font_color="#FFFFFF",
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_vincitori, use_container_width=True)
            else:
                st.markdown('<p style="color:white ; font-style: italic; text-align: center; padding-top: 30px;">No rider from this lineup has ever won a stage at TDF</p>', unsafe_allow_html=True)
            with col_comp2:
                # Grafico delle presenze storiche del team (I Fedelissimi)
                fedelissimi = df_team_storico['Rider'].value_counts().head(5).reset_index()
                fedelissimi.columns = ['Corridore', 'Partecipazioni']
                
                fig_fedeli = px.bar(
                    fedelissimi, x='Partecipazioni', y='Corridore', orientation='h',
                    title="The Team 'Loyals' (Appearances)",
                    labels={'Corridore': '', 'Partecipazioni': 'Tour Appearances'}
                )
                fig_fedeli.update_traces(marker_color='#d2b48c') 
                fig_fedeli.update_layout(yaxis={'categoryorder':'total ascending'})
                fig_fedeli = applica_tema_vintage(fig_fedeli)
                st.plotly_chart(fig_fedeli, use_container_width=True)

        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)

        # --- 7. SEZIONE 3: PERFORMANCE STORICHE, SELEZIONE ANNO UNICA E STRIP PLOT ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">Historical Performance</h3>', unsafe_allow_html=True)
        if not df_team_storico.empty:
            col_grafico1, col_grafico2 = st.columns(2)
            
            with col_grafico1:
                anni_disponibili_team = sorted(df_team_storico['Year'].unique(), reverse=True)
                anno_selezionato = st.selectbox("Seleziona l'edizione del Tour:", anni_disponibili_team)
                
                roster_anno = df_team_storico[df_team_storico['Year'] == anno_selezionato][['Rider', 'Rank_Num']].sort_values(by='Rank_Num')
                roster_anno['Rank_Num'] = roster_anno['Rank_Num'].apply(lambda x: int(x) if pd.notna(x) else "Ritirato")
                roster_anno.columns = ['Corridore', 'Piazzamento Finale']
                
                st.markdown(f'<p style="color: #000000; font-family: Georgia, serif; margin-top: 10px;"><strong>Formazione e Risultati nel {anno_selezionato}:</strong></p>', unsafe_allow_html=True)
                st.dataframe(roster_anno, use_container_width=True, hide_index=True)
                
            with col_grafico2:
                df_scatter = df_team_storico.dropna(subset=['Rank_Num']).copy()
                df_scatter['Evidenziato'] = df_scatter['Year'] == anno_selezionato
                
                fig_roster = px.strip(
                    df_scatter, x='Year', y='Rank_Num',
                    hover_name='Rider',
                    color='Evidenziato', 
                    color_discrete_map={True: '#ff4b4b', False: 'rgba(143, 188, 143, 0.25)'},
                    title="All-Time Roster Placements",
                    labels={'Rank_Num': 'Ranking', 'Year': 'Year'}
                )
                fig_roster.update_yaxes(autorange="reversed")
                fig_roster.update_traces(
                    marker=dict(size=10, line=dict(width=1, color='rgba(255,255,255,0.8)')),
                    jitter=0.2
                )
                fig_roster.update_layout(showlegend=False)
                fig_roster = applica_tema_vintage(fig_roster)
                st.plotly_chart(fig_roster, use_container_width=True)

        # --- 8. SEZIONE 4: PALMARÈS MAGLIE E VITTORIE TAPPE ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">Palmarès: Stages and Jersey</h3>', unsafe_allow_html=True)
        
        # Calcolo maglie protetto
        corridori_team_clean = df_team_storico[['Year', 'Rider_Clean']].drop_duplicates()
        maglia_gialla = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Yellow_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        maglia_verde = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Green_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        maglia_pois = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Pois_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        
        html_maglie = f"""
        <div class="vintage-card-container" style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #FFD700; background-color: #fffacd;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; font-size: 14px;">Days in Yellow</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; font-size: 24px; font-weight: bold;">{len(maglia_gialla)}</h2>
            </div>
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #228B22; background-color: #f0fff0;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; font-size: 14px;">Days in Green</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; font-size: 24px; font-weight: bold;">{len(maglia_verde)}</h2>
            </div>
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #ff0000; background-image: radial-gradient(#ff0000 15%, transparent 16%), radial-gradient(#ff0000 15%, transparent 16%); background-size: 20px 20px; background-position: 0 0, 10px 10px; background-color: white;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; background-color: rgba(255,255,255,0.85); padding: 5px; font-size: 14px;">Days in Polka dot</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; background-color: rgba(255,255,255,0.85); padding: 5px; display: inline-block; font-size: 24px; font-weight: bold;">{len(maglia_pois)}</h2>
            </div>
        </div>
        """
        st.markdown(html_maglie, unsafe_allow_html=True)
        
        if not df_tappe_team.empty:
            vittorie_per_anno = df_tappe_team.groupby('Year').size().reset_index(name='Vittorie')
            fig_tappe = px.bar(
                vittorie_per_anno, x='Year', y='Vittorie',
                title="Numero di tappe vinte per edizione",
                labels={'Vittorie': 'Tappe Vinte', 'Year': 'Anno'}
            )
            
            # 1. Applichiamo il Giallo Tour de France alle barre
            fig_tappe.update_traces(marker_color='#FFCC00')
            
            # 2. Applichiamo il font di base vintage
            fig_tappe = applica_tema_vintage(fig_tappe)
            
            # 3. Sovrascriviamo lo sfondo trasparente forzando il Nero assoluto per questo specifico grafico
            fig_tappe.update_layout(
                paper_bgcolor='#000000', 
                plot_bgcolor='#000000',
                title_font_color="#FFFFFF",
                font=dict(color="#FFFFFF")
            )
            
            # 4. Assicuriamoci che anche griglie, assi e numerini siano perfettamente bianchi e visibili sul nero
            fig_tappe.update_xaxes(gridcolor='rgba(255,255,255,0.2)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            fig_tappe.update_yaxes(gridcolor='rgba(255,255,255,0.2)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            
            st.plotly_chart(fig_tappe, use_container_width=True)
        else:
            st.markdown('<p class="journal-text" style="color: #000000; font-style: italic; text-align: center;">No stage wins found for this team in the current dataset.</p>', unsafe_allow_html=True)


#============================================
# 6. MENU LATERALE (SIDEBAR)
# ==========================================
#with st.sidebar:
#    st.title("≡ Filtri globali")
#   st.selectbox("Seleziona Nazionalità:", ["Tutte", "Italia", "Francia", "Spagna"])
#    st.checkbox("Mostra solo i team World Tour")