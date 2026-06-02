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
import numpy as np


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
            /* ---> STATO ATTIVO REALE: Mantiene fissa la linea gialla per i tab selezionati <--- */
    div.stButton > button[kind="primary"] {
        color: #FFCC00 !important;
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
    if st.button("STANDINGS", use_container_width=True, type="primary" if st.session_state.pagina_corrente == "classifica" else "secondary"):
        st.session_state.pagina_corrente = "classifica"
        st.rerun()

with col2:
    if st.button("RIDERS", use_container_width=True, type="primary" if st.session_state.pagina_corrente == "corridori" else "secondary"):
        st.session_state.pagina_corrente = "corridori"
        st.rerun()

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
    if st.button("STAGES", use_container_width=True, type="primary" if st.session_state.pagina_corrente == "tappe" else "secondary"):
        st.session_state.pagina_corrente = "tappe"
        st.rerun()

with col5:
    if st.button("TEAMS", use_container_width=True, type="primary" if st.session_state.pagina_corrente == "teams" else "secondary"):
        st.session_state.pagina_corrente = "teams"
        st.rerun()

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
            background: #0d0d0d; border: 1px solid #2a2a2a; border-radius: 4px;
            padding: 20px; font-family: 'Merriweather', Georgia, serif; position: relative; overflow: hidden;
        }
        .fighter-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
        .fighter-card-1::before { background: #FFCC00; }
        .fighter-card-2::before { background: #FF6B6B; }
        .fighter-card-3::before { background: #4ECDC4; }

        .fighter-name {
            font-size: 22px; font-weight: 900; color: #f0ece4; line-height: 1.1; margin-bottom: 6px;
            text-transform: uppercase; letter-spacing: -0.5px;
        }
        .fighter-country { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #888; margin-bottom: 14px; }

        /* ── VS badge ── */
        .vs-badge {
            display: flex; align-items: center; justify-content: center;
            font-family: 'Merriweather', serif; font-size: 28px; font-weight: 900;
            color: #FFCC00; text-shadow: 0 0 20px rgba(255,204,0,0.4); height: 100%;
        }

        /* ── BOTTONI TAB NAVIGATION (FIX) ── */
        button[kind="primary"], button[data-testid="baseButton-primary"] {
            background-color: #1a1a1a !important;
            color: #FFCC00 !important;
            border: none !important;
            border-radius: 0 !important;
            /* Ombra interna per evitare il taglio del bordo */
            box-shadow: inset 0 -4px 0 0 #FFCC00 !important;
            font-family: 'Merriweather', serif !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            padding: 12px !important;
        }
        button[kind="secondary"], button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            color: #888 !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: inset 0 -3px 0 0 #c8bfad !important;
            font-family: 'Merriweather', serif !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            padding: 12px !important;
        }
        button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {
            color: #1a1a1a !important;
            box-shadow: inset 0 -3px 0 0 #888 !important;
            background-color: transparent !important;
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
    # 🪄 FIX STATO INIZIALE: Impostiamo a None (nessun tab attivo) alla prima apertura della pagina
    if "riders_tab" not in st.session_state:
        st.session_state.riders_tab = None

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        if st.button("🏆  THE CHAMPIONS", use_container_width=True, type="primary" if st.session_state.riders_tab == "champions" else "secondary"):
            st.session_state.riders_tab = "champions"
            st.rerun()
    with col_t2:
        if st.button("📈  CAREER EXPLORER", use_container_width=True, type="primary" if st.session_state.riders_tab == "career" else "secondary"):
            st.session_state.riders_tab = "career"
            st.rerun()
    with col_t3:
        if st.button("⚔️  HEAD-TO-HEAD", use_container_width=True, type="primary" if st.session_state.riders_tab == "h2h" else "secondary"):
            st.session_state.riders_tab = "h2h"
            st.rerun()
    with col_t4:
        if st.button("🌍  GEOGRAPHY", use_container_width=True, type="primary" if st.session_state.riders_tab == "nations" else "secondary"):
            st.session_state.riders_tab = "nations"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    hr = "<hr class='r-rule'>"

# ══════════════════════════════════════════════════════════
    # TAB 1 — THE CHAMPIONS
    # ══════════════════════════════════════════════════════════
    if st.session_state.riders_tab == "champions":

        # Margini di respiro per i testi e i titoli
        st.markdown("""
            <div style="padding: 0 2rem;">
                <span class="r-section-label">· The Golden Age ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Age of Glory — When Champions Conquered the Tour
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;">
                    Each dot is a Tour winner. Position on Y-axis = age at victory. Color = nation. Hover to explore.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ── BEESWARM: età vincitori per anno ──
        df_bee = df_w_clean.dropna(subset=['age']).copy()
        
        # Normalizzazione delle stringhe delle nazioni per evitare sdoppiamenti in legenda
        df_bee['Country_clean'] = df_bee['Country_clean'].astype(str).str.strip().str.title()
        df_bee['Country_clean'] = df_bee['Country_clean'].replace({
            'United Kingdom': 'Great Britain',
            'Great Britain': 'Great Britain',
            'Usa': 'USA',
            'United States': 'USA'
        })

        df_bee['Winner_display'] = df_bee['Winner'].str.title()
        df_bee['rt_display'] = df_bee['rt_clean'].str.title()

        # 🪄 FIX TAVOLOZZA: Un colore unico ed esclusivo per CIASCUNA nazione (niente più doppioni)
        COLORI_NAZIONI_UNICI = {
            'France': '#0055A4',         # Blu Reale
            'Belgium': '#E5A93C',        # Oro Antico (staccato dal giallo brillante della Colombia)
            'Italy': '#009246',          # Verde prato
            'Spain': '#AA151B',          # Rosso scuro
            'USA': '#7A1E44',            # Amaranto / Vinaccia (staccato dai rossi europei)
            'Great Britain': '#4A90E2',  # Celeste / Carta da zucchero
            'Luxembourg': '#44DBFF',     # Turchese acceso
            'Denmark': '#C60C30',        # Rosso bandiera
            'Slovenia': '#3F51B5',       # Indaco / Blu scuro
            'Netherlands': '#FF6600',    # Arancione accesa
            'Switzerland': '#E63946',    # Rosso corallo vibrante
            'Colombia': '#FFD700',       # Giallo brillante ed esclusivo
            'Australia': '#1B5E20',      # Verde foresta scuro (staccato dal verde Italia)
            'Germany': '#1A1A1A',        # Nero grafite
            'Ireland': '#81C784'         # Verde menta chiaro
        }

        fig_bee = px.strip(
            df_bee, x='Year', y='age',
            color='Country_clean',
            hover_name='Winner_display',
            hover_data={'Country_clean': True, 'rt_display': True, 'age': True, 'Year': True},
            labels={'age': 'Age at Victory', 'Year': 'Edition', 'Country_clean': 'Nation', 'rt_display': 'Rider Type'},
            color_discrete_map=COLORI_NAZIONI_UNICI,
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
            height=420, 
            margin=dict(l=40, r=40, t=10, b=0),
            legend=dict(
                title='Nation', orientation='v', x=1.01, y=1,
                font=dict(size=10), bgcolor='rgba(244,241,234,0.9)',
                bordercolor='#c8bfad', borderwidth=1
            ),
            xaxis=dict(title='Edition', showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(title='Age', showgrid=True, gridcolor='#e8e4da', gridwidth=1),
        )

        # Margini esterni per incapsulare il grafico
        st.markdown('<div style="padding: 0 2rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_bee, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(hr, unsafe_allow_html=True)

       # ── BUMP CHART: dominanza nazioni per decade ──
        # ---> AGGIUNTA MARGINI: Blocco di respiro per i testi e i titoli <---
        st.markdown("""
            <div style="padding: 0 2rem;">
                <span class="r-section-label">· National Dynasties ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    The Rise & Fall of Nations — A Century of Dominance
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:8px;">
                    Victories per decade for the top 8 nations. Hover each line to track the shift of power.
                </p>
            </div>
        """, unsafe_allow_html=True)

        TOP_NATIONS = ['France', 'Belgium', 'Spain', 'Italy', 'USA', 'United Kingdom', 'Luxembourg', 'Denmark']
        
        # Allineiamo i nomi del dataset per far combaciare perfettamente le chiavi colore
        df_w_clean['Country_bump'] = df_w_clean['Country_clean'].astype(str).str.strip().str.title()
        df_w_clean['Country_bump'] = df_w_clean['Country_bump'].replace({
            'United Kingdom': 'Great Britain',
            'Great Britain': 'Great Britain',
            'Usa': 'USA',
            'United States': 'USA'
        })
        
        # Ri-mappiamo TOP_NATIONS per coerenza con le stringhe normalizzate
        TOP_NATIONS_NORM = ['France', 'Belgium', 'Spain', 'Italy', 'USA', 'Great Britain', 'Luxembourg', 'Denmark']

        df_bump = df_w_clean[df_w_clean['Country_bump'].isin(TOP_NATIONS_NORM)].groupby(['decade', 'Country_bump']).size().reset_index(name='wins')

        # Tavolozza coerente identica al grafico superiore
        COLORI_BUMP_COERENTI = {
            'France': '#0055A4',         # Blu Reale
            'Belgium': '#E5A93C',        # Oro Antico
            'Italy': '#009246',          # Verde prato
            'Spain': '#AA151B',          # Rosso scuro
            'USA': '#7A1E44',            # Amaranto / Vinaccia
            'Great Britain': '#4A90E2',  # Celeste (ex United Kingdom)
            'Luxembourg': '#44DBFF',     # Turchese acceso
            'Denmark': '#C60C30'         # Rosso bandiera
        }

        fig_bump = go.Figure()
        for nation in TOP_NATIONS_NORM:
            df_n = df_bump[df_bump['Country_bump'] == nation].sort_values('decade')
            if df_n.empty:
                continue
            color = COLORI_BUMP_COERENTI.get(nation, '#888')
            
            # Label corretta per la legenda
            legend_name = "Great Britain" if nation == "Great Britain" else nation
            
            fig_bump.add_trace(go.Scatter(
                x=df_n['decade'], y=df_n['wins'],
                mode='lines+markers+text',
                name=legend_name,
                line=dict(color=color, width=2.5),
                marker=dict(size=8, color=color, line=dict(width=1.5, color='white')),
                text=df_n['wins'].astype(str),
                textposition='top center',
                textfont=dict(size=9, color=color),
                hovertemplate=f'<b>{legend_name}</b><br>Decade: %{{x}}s<br>Victories: %{{y}}<extra></extra>'
            ))
            
        fig_bump.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=400, 
            # Margini interni del grafico coordinati
            margin=dict(l=40, r=40, t=10, b=0),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(size=10)),
            xaxis=dict(title='Decade', tickvals=list(range(1900, 2030, 10)),
                       ticktext=[f"{d}s" for d in range(1900, 2030, 10)],
                       showgrid=False),
            yaxis=dict(title='Victories', showgrid=True, gridcolor='#e8e4da'),
        )
        
       # Annotazioni ere storiche (WWI, WWII) + Era Doping allineate sul pavimento dell'asse X
        for x0, x1, label in [(1914, 1918, 'WWI'), (1939, 1947, 'WWII'), (1995, 2005, 'Doping Era (1999-2005)')]:
            is_doping = 'Doping' in label
            
            # Disegniamo la banda verticale colorata di sfondo
            fig_bump.add_vrect(
                x0=x0, x1=x1, 
                fillcolor='#cc0000' if is_doping else '#888', 
                opacity=0.07 if is_doping else 0.12, 
                line_width=0
            )
            
            # Colore e peso del font differenziati per l'era del doping
            testo_colore = '#cc0000' if is_doping else '#666'
            testo_peso = 'bold' if is_doping else 'normal'
            
            # Inseriamo il testo ancorato sul fondo del grafico (quota 0 dell'asse Y)
            fig_bump.add_annotation(
                x=(x0 + x1) / 2, y=0,         # Centrato nella banda, ancorato a quota 0 sull'asse Y (il pavimento)
                xref="x", yref="y",           # Usiamo il riferimento reale dell'asse Y per evitare sovrapposizioni
                text=label,
                showarrow=False,
                xanchor="center",
                yanchor="bottom",             # Appoggia la base del testo sopra la linea dello 0
                yshift=4,                     # Distanza di sicurezza dalla linea dell'asse X
                font=dict(size=9, color=testo_colore, weight=testo_peso, family='Arial'),
                bgcolor='#F4F1EA',            # Maschera le linee piatte di nazioni a zero vittorie
                borderpad=2
            )
            
        # Margini esterni per incapsulare il grafico
        st.markdown('<div style="padding: 0 2rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_bump, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(hr, unsafe_allow_html=True)
        
      # ── RIDER TYPE HEATMAP per decade ──
        st.markdown("""
            <div style="padding: 0 2rem;">
                <span class="r-section-label">· Tactical Evolution ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Who Wins the Tour? — The Rider Type Revolution
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:8px;">
                    Heatmap of winning rider types per decade. From the early sprinters to the modern pure climbers.
                </p>
            </div>
        """, unsafe_allow_html=True)

        df_heat = df_w_clean.groupby(['decade', 'rt_clean']).size().reset_index(name='count')
        df_heat = df_heat.sort_values('decade')
        df_heat_pivot = df_heat.pivot(index='rt_clean', columns='decade', values='count').fillna(0)

        # Normalizza a Title Case
        df_heat_pivot.index = df_heat_pivot.index.str.strip().str.title()

        ordine_fissato = ['Climber', 'Sprinter', 'Time Trial']
        righe_presenti = [r for r in ordine_fissato if r in df_heat_pivot.index]
        righe_extra = [r for r in df_heat_pivot.index if r not in ordine_fissato]
        df_heat_pivot = df_heat_pivot.reindex(righe_presenti + righe_extra)

        if df_heat_pivot.empty or df_heat_pivot.values.size == 0:
            st.warning("Nessun dato disponibile per la heatmap dei rider type.")
        else:
            RIDER_COLORS_HEX = {
                'climber':     (198, 40,  40),   # rosso
                'sprinter':    (46,  125, 50),   # verde
                'time trial':  (21,  101, 192),  # blu
                'all rounder': (106, 27,  154),  # viola
            }
            DEFAULT_RGB = (84, 110, 122)

            def get_rider_rgb(rider_type: str):
                key = rider_type.lower().strip()
                for k, v in RIDER_COLORS_HEX.items():
                    if k in key:
                        return v
                return DEFAULT_RGB

            max_val = df_heat_pivot.values.max() or 1

            # ── Costruiamo matrici di colori e testi ──
            color_matrix = []   # ogni cella: colore rgba stringa
            text_matrix  = []
            z_matrix     = []   # valori numerici per hover

            riders = list(df_heat_pivot.index)
            decades = list(df_heat_pivot.columns)

            for rider in riders:
                rgb = get_rider_rgb(rider)
                row_colors = []
                row_text   = []
                row_z      = []
                for decade in decades:
                    v = df_heat_pivot.loc[rider, decade]
                    if v == 0:
                        row_colors.append('rgba(244,241,234,1)')  # beige neutro
                    else:
                        alpha = 0.20 + 0.80 * (v / max_val)
                        row_colors.append(f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha:.2f})')
                    row_text.append(str(int(v)) if v > 0 else '0')
                    row_z.append(int(v))
                color_matrix.append(row_colors)
                text_matrix.append(row_text)
                z_matrix.append(row_z)

            # ── Usiamo go.Figure con shapes + annotations invece di Heatmap ──
            # per avere controllo totale sui colori cella per cella
            fig_heat = go.Figure()

            n_rows = len(riders)
            n_cols = len(decades)
            cell_h = 1.0 / n_rows  # altezza normalizzata per cella

            decade_labels = [f"{int(d)}s" for d in decades]

            for ri, rider in enumerate(riders):
                rgb = get_rider_rgb(rider)
                for ci, decade in enumerate(decades):
                    v = df_heat_pivot.loc[rider, decade]
                    if v == 0:
                        fill = 'rgba(244,241,234,1)'
                    else:
                        alpha = 0.20 + 0.80 * (v / max_val)
                        fill = f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha:.2f})'

                    # Shape per la cella
                    fig_heat.add_shape(
                        type='rect',
                        x0=ci - 0.5, x1=ci + 0.5,
                        y0=ri - 0.5, y1=ri + 0.5,
                        fillcolor=fill,
                        line=dict(color='#F4F1EA', width=2),
                    )
                    # Testo dentro la cella
                    fig_heat.add_annotation(
                        x=ci, y=ri,
                        text=str(int(v)),
                        showarrow=False,
                        font=dict(size=13, family='Merriweather, serif', color='#1a1a1a'),
                        xref='x', yref='y',
                    )

            # Asse X: decadi
            fig_heat.update_xaxes(
                tickmode='array',
                tickvals=list(range(n_cols)),
                ticktext=decade_labels,
                side='bottom',
                tickfont=dict(size=10, family='Merriweather, serif'),
                showgrid=False, zeroline=False,
                range=[-0.5, n_cols - 0.5],
            )

            # Asse Y: rider con colore
            def rider_color_hex(rider):
                rgb = get_rider_rgb(rider)
                return '#{:02x}{:02x}{:02x}'.format(*rgb)

            fig_heat.update_yaxes(
                tickmode='array',
                tickvals=list(range(n_rows)),
                ticktext=[
                    f'<span style="color:{rider_color_hex(r)};font-weight:bold">{r}</span>'
                    for r in riders
                ],
                tickfont=dict(size=11, family='Merriweather, serif'),
                showgrid=False, zeroline=False,
                range=[-0.5, n_rows - 0.5],
            )

            fig_heat.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
                height=220,
                margin=dict(l=90, r=40, t=10, b=30),
            )

            st.markdown('<div style="padding: 0 2rem;">', unsafe_allow_html=True)
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── RIDER TYPE EXPLAINER CARDS ──
            rider_cards_html = """
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:0 2rem 1.5rem;font-family:'Merriweather',Georgia,serif;">

            <!-- CLIMBER -->
            <div style="background:#fff8f8;border:1.5px solid #C62828;border-radius:10px;padding:14px 16px;cursor:pointer;"
                onclick="toggleCard(this,'climber')">
                <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:11px;height:11px;border-radius:50%;background:#C62828;flex-shrink:0"></div>
                <div style="flex:1">
                    <p style="margin:0;font-size:14px;font-weight:700;color:#C62828;">Climber</p>
                    <p style="margin:2px 0 0;font-size:11px;color:#666;font-style:italic;line-height:1.4;">Light, powerful, relentless uphill</p>
                </div>
                <span id="chev-climber" style="font-size:13px;color:#999;transition:transform 0.2s;display:inline-block;">▼</span>
                </div>
                <div id="body-climber" style="max-height:0;overflow:hidden;transition:max-height 0.3s ease;">
                <div style="border-top:1px solid #f5c6c6;margin-top:10px;padding-top:10px;">
                    <p style="margin:0;font-size:12px;color:#444;line-height:1.7;">
                    A climber excels due to an exceptional power-to-weight ratio — high watts per kilogram of body mass,
                    typically under 65 kg. They dominate Alpine and Pyrenean stages where gravity penalises every extra gram,
                    and are the primary GC contenders on summit finishes. Their relative weakness is flat terrain and time trials.
                    </p>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;">
                    <span style="background:#FFEBEE;color:#C62828;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">Low body weight</span>
                    <span style="background:#FFEBEE;color:#C62828;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">High W/kg</span>
                    <span style="background:#FFEBEE;color:#C62828;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">GC contender</span>
                    </div>
                    <p style="font-size:10px;color:#999;margin:10px 0 2px;text-transform:uppercase;letter-spacing:0.05em;">Iconic riders</p>
                    <p style="font-size:12px;color:#1a1a1a;font-weight:600;margin:0;">Pantani · Gaul · Pogačar · Sastre</p>
                </div>
                </div>
            </div>

            <!-- SPRINTER -->
            <div style="background:#f6faf6;border:1.5px solid #2E7D32;border-radius:10px;padding:14px 16px;cursor:pointer;"
                onclick="toggleCard(this,'sprinter')">
                <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:11px;height:11px;border-radius:50%;background:#2E7D32;flex-shrink:0"></div>
                <div style="flex:1">
                    <p style="margin:0;font-size:14px;font-weight:700;color:#2E7D32;">Sprinter</p>
                    <p style="margin:2px 0 0;font-size:11px;color:#666;font-style:italic;line-height:1.4;">Explosive speed in the final 200 metres</p>
                </div>
                <span id="chev-sprinter" style="font-size:13px;color:#999;transition:transform 0.2s;display:inline-block;">▼</span>
                </div>
                <div id="body-sprinter" style="max-height:0;overflow:hidden;transition:max-height 0.3s ease;">
                <div style="border-top:1px solid #c8e6c9;margin-top:10px;padding-top:10px;">
                    <p style="margin:0;font-size:12px;color:#444;line-height:1.7;">
                    A sprinter produces a massive surge of power — often over 1,500 watts — for a short window at the end
                    of a flat stage. Heavier and more muscular than climbers, with fast-twitch fibres built for explosive output.
                    They survive mountain stages by staying sheltered in the peloton, then unleash their acceleration in the
                    chaotic final sprint for stage glory.
                    </p>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;">
                    <span style="background:#E8F5E9;color:#2E7D32;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">Explosive power</span>
                    <span style="background:#E8F5E9;color:#2E7D32;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">Fast-twitch muscles</span>
                    <span style="background:#E8F5E9;color:#2E7D32;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">Green jersey</span>
                    </div>
                    <p style="font-size:10px;color:#999;margin:10px 0 2px;text-transform:uppercase;letter-spacing:0.05em;">Iconic riders</p>
                    <p style="font-size:12px;color:#1a1a1a;font-weight:600;margin:0;">Cavendish · Cipollini · Greipel · Kittel</p>
                </div>
                </div>
            </div>

            <!-- TIME TRIALIST -->
            <div style="background:#f5f8ff;border:1.5px solid #1565C0;border-radius:10px;padding:14px 16px;cursor:pointer;"
                onclick="toggleCard(this,'tt')">
                <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:11px;height:11px;border-radius:50%;background:#1565C0;flex-shrink:0"></div>
                <div style="flex:1">
                    <p style="margin:0;font-size:14px;font-weight:700;color:#1565C0;">Time trialist</p>
                    <p style="margin:2px 0 0;font-size:11px;color:#666;font-style:italic;line-height:1.4;">Alone against the clock</p>
                </div>
                <span id="chev-tt" style="font-size:13px;color:#999;transition:transform 0.2s;display:inline-block;">▼</span>
                </div>
                <div id="body-tt" style="max-height:0;overflow:hidden;transition:max-height 0.3s ease;">
                <div style="border-top:1px solid #bbdefb;margin-top:10px;padding-top:10px;">
                    <p style="margin:0;font-size:12px;color:#444;line-height:1.7;">
                    A time trialist excels when each rider races alone against the clock — no drafting, no tactics, pure effort.
                    They have very high sustained power output (FTP) and an aerodynamic position on the bike. Larger and more
                    powerful than climbers, they can swing the GC by minutes on flat TT stages. The most complete GC champions
                    often combine this with climbing ability.
                    </p>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;">
                    <span style="background:#E3F2FD;color:#1565C0;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">High sustained power</span>
                    <span style="background:#E3F2FD;color:#1565C0;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">Aerodynamic</span>
                    <span style="background:#E3F2FD;color:#1565C0;font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600;">GC time gains</span>
                    </div>
                    <p style="font-size:10px;color:#999;margin:10px 0 2px;text-transform:uppercase;letter-spacing:0.05em;">Iconic riders</p>
                    <p style="font-size:12px;color:#1a1a1a;font-weight:600;margin:0;">Induráin · Cancellara · Froome · Ullrich</p>
                </div>
                </div>
            </div>

            </div>

            <script>
            function toggleCard(card, id) {
            var body = document.getElementById('body-' + id);
            var chev = document.getElementById('chev-' + id);
            var isOpen = body.style.maxHeight && body.style.maxHeight !== '0px';
            var allIds = ['climber','sprinter','tt'];
            allIds.forEach(function(i) {
                document.getElementById('body-' + i).style.maxHeight = '0px';
                document.getElementById('chev-' + i).style.transform = 'rotate(0deg)';
            });
            if (!isOpen) {
                body.style.maxHeight = '400px';
                chev.style.transform = 'rotate(180deg)';
            }
            }
            </script>
            """

            st.components.v1.html(rider_cards_html, height=130, scrolling=False)

        st.markdown(hr, unsafe_allow_html=True) 


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

    
        # ── PHYSICAL OUTLIER STRIP (Confronto Multiplo Vincitori) ──
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Physical Profile ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Physical Outlier Detector - Are These Champions Atypical?
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                    Distribution of all Tour winners (grey). Colored markers = selected riders. Only available for GC winners.
                </p>
            </div>
        """, unsafe_allow_html=True)

        PHYSICAL_COLS = {
            'age': ('Age at Victory', 'years'),
            'BMI': ('BMI', 'kg/m²'),
            'weight_(Kg)': ('Weight', 'kg'),
        }

        df_phys = df_w_clean.dropna(subset=['age', 'BMI', 'weight_(Kg)'])

        fig_strips = go.Figure()
        metrics_list = list(PHYSICAL_COLS.items())
        y_positions = [3, 2, 1]

        # Liste per tenere traccia di chi ha i dati e chi no
        not_winners = []
        winners_found = []

        # Primo ciclo di controllo sui rider selezionati
        for rider in riders_sel:
            rider_norm = rider.title().lower().strip()
            winner_match = df_phys[df_phys['Winner'].str.lower().str.strip() == rider_norm]
            
            if winner_match.empty:
                # Tentativo con ricerca parziale
                winner_match = df_phys[df_phys['Winner'].str.lower().str.contains(rider.split()[0].lower())]
            
            if winner_match.empty:
                not_winners.append(rider.title())
            else:
                winners_found.append((rider.title(), winner_match.iloc[0]))

        # Disegno lo sfondo e i punti dei vincitori validi
        for idx, (col, (label, unit)) in enumerate(metrics_list):
            y_val = y_positions[idx]
            vals = df_phys[col].dropna()

            # Jitter per i punti di sfondo
            jitter = np.random.uniform(-0.18, 0.18, size=len(vals))

            # Background (tutti i vincitori storici)
            fig_strips.add_trace(go.Scatter(
                x=vals, y=[y_val + j for j in jitter],
                mode='markers',
                marker=dict(size=7, color='#c8bfad', opacity=0.4,
                            line=dict(width=0.5, color='#888')),
                showlegend=False,
                hovertemplate=f'<b>{label}</b>: %{{x}} {unit}<extra></extra>',
                name=label,
            ))

            # Mediana storica
            median_val = vals.median()
            fig_strips.add_shape(type='line',
                x0=median_val, x1=median_val,
                y0=y_val - 0.25, y1=y_val + 0.25,
                line=dict(color='#888', width=2, dash='dot'))

            # Aggiungo i punti colorati per ciascun rider selezionato che ha vinto il Tour
            for i, (rider_title, row_data) in enumerate(winners_found):
                if pd.notna(row_data[col]):
                    rider_val = row_data[col]
                    
                    # Usiamo la PALETTE globale per differenziare i ciclisti selezionati
                    rider_color = PALETTE[i % len(PALETTE)]
                    
                    fig_strips.add_trace(go.Scatter(
                        x=[rider_val], y=[y_val],
                        mode='markers+text',
                        marker=dict(size=14, color=rider_color,
                                    line=dict(width=1.5, color='#1a1a1a'), symbol='diamond'),
                        text=[f'{rider_val:.1f}'], textposition='top center',
                        textfont=dict(size=9, color='#1a1a1a', family='Arial'),
                        showlegend=(idx == 0), # Mostra in legenda solo al primo ciclo per non duplicare
                        name=rider_title,
                        hovertemplate=f'<b>{rider_title}</b><br>{label}: {rider_val:.1f} {unit}<extra></extra>',
                    ))

        fig_strips.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=320, margin=dict(l=120, r=20, t=20, b=20),
            xaxis=dict(title='Value', showgrid=True, gridcolor='#e8e4da'),
            yaxis=dict(
                tickmode='array',
                tickvals=y_positions,
                ticktext=[v[0] for v in PHYSICAL_COLS.values()],
                showgrid=False,
            ),
            legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center'),
            showlegend=True if winners_found else False
        )

        st.plotly_chart(fig_strips, use_container_width=True)

        # Messaggio dinamico per chi non ha mai vinto il Tour
        if not_winners:
            riders_str = ", ".join([f"<strong>{r}</strong>" for r in not_winners])
            st.markdown(f"""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:12px 16px; margin: 0 16px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;font-style:italic;font-size:12px;margin-bottom:15px;">
                    Physical data available only for GC winners. {riders_str} did not win the Tour de France GC and cannot be highlighted.
                </div>
            """, unsafe_allow_html=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── LONGEVITY vs PEAK ──
        st.markdown(hr, unsafe_allow_html=True)
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Longevity vs Peak ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Career Longevity vs Peak Performance
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;line-height:1.5;">
                    Each dot represents a rider (with at least 3 participations). The X-axis shows their all-time best career result, while the Y-axis represents their total Tours ridden. Selected riders are highlighted.
                </p>
            </div>
        """, unsafe_allow_html=True)

        df_longevity = df_r_norm.groupby('Rider').agg(
            partecipazioni=('Year', 'count'),
            best_rank=('Rank_Num', 'min')
        ).reset_index()

        # Teniamo traccia di chi escludiamo perché ha meno di 3 partecipazioni
        low_participations = []
        for rider in riders_sel:
            rider_row = df_longevity[df_longevity['Rider'].str.lower().str.strip() == rider.lower().strip()]
            if rider_row.empty or rider_row['partecipazioni'].values[0] < 3:
                low_participations.append(rider.title())

        # Filtro del dataset principale per la visualizzazione dello sfondo
        df_longevity_filtered = df_longevity[df_longevity['partecipazioni'] >= 3].copy()
        df_longevity_filtered['is_selected'] = df_longevity_filtered['Rider'].isin(riders_sel)

        fig_long = go.Figure()

        # Background dots
        df_bg = df_longevity_filtered[~df_longevity_filtered['is_selected']]
        fig_long.add_trace(go.Scatter(
            x=df_bg['best_rank'], y=df_bg['partecipazioni'],
            mode='markers',
            marker=dict(size=6, color='#c8bfad', opacity=0.5, line=dict(width=0.5, color='#888')),
            showlegend=False,
            hovertemplate='<b>%{customdata[0]}</b><br>Best: #%{x}<br>Tours: %{y}<extra></extra>',
            customdata=df_bg[['Rider']].values,
        ))

        # Selected riders (Evidenziati come stelle)
        for i, rider in enumerate(riders_sel):
            df_sel = df_longevity_filtered[df_longevity_filtered['Rider'].str.lower().str.strip() == rider.lower().strip()]
            if df_sel.empty:
                continue
            fig_long.add_trace(go.Scatter(
                x=df_sel['best_rank'], y=df_sel['partecipazioni'],
                mode='markers+text',
                marker=dict(size=18, color=PALETTE[i % len(PALETTE)], line=dict(width=2, color='white'), symbol='star'),
                text=[rider.title()],
                textposition='top center',
                textfont=dict(size=10, color=PALETTE[i % len(PALETTE)]),
                name=rider.title(),
                hovertemplate=f'<b>{rider.title()}</b><br>Best GC: #%{{x}}<br>Tours ridden: %{{y}}<extra></extra>',
            ))

        fig_long.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=380, margin=dict(l=40, r=20, t=20, b=20),
            xaxis=dict(title='Best GC Rank (lower = better)', showgrid=True, gridcolor='#e8e4da'),
            yaxis=dict(title='Total Tour participations', showgrid=True, gridcolor='#e8e4da'),
            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
            showlegend=True
        )

        # Quadrant labels 
        fig_long.add_annotation(x=2, y=14, text='🏆 Legends & Long Careers', showarrow=False,
                                font=dict(size=10, color='#888', family='Arial', weight='bold'), opacity=0.8)
        fig_long.add_annotation(x=50, y=14, text='🐢 Loyal Domestiques', showarrow=False,
                                font=dict(size=10, color='#888', family='Arial'), opacity=0.7)

        st.plotly_chart(fig_long, use_container_width=True)

        # Messaggio dinamico per chi ha meno di 3 partecipazioni nel secondo grafico
        if low_participations:
            low_riders_str = ", ".join([f"<strong>{r}</strong>" for r in low_participations])
            st.markdown(f"""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:12px 16px;margin: 0 16px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;font-style:italic;font-size:12px;">
                    Longevity criteria notice: {low_riders_str} has/have fewer than 3 total Tour de France participations and cannot be plotted.
                </div>
            """, unsafe_allow_html=True)


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

        # ── FIGHTER CARDS via components.html (fix rendering) ──
        fighter_cards_data = []
        for fi, rider in enumerate(h2h_riders):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num'])
            n_tours = len(df_rd)
            best_rank = int(df_rd['Rank_Num'].min()) if n_tours > 0 else 0
            wins = len(df_w_clean[df_w_clean['Winner'].str.upper().str.strip() == rider.strip()])
            top10 = len(df_rd[df_rd['Rank_Num'] <= 10])
            wrow = df_w_clean[df_w_clean['Winner'].str.upper().str.strip() == rider.strip()]
            country = wrow['Country_clean'].values[0] if not wrow.empty else '—'
            rider_type = wrow['rt_clean'].values[0].strip().title() if not wrow.empty else '—'
            bar_wins  = min(100, (wins / 7) * 100)
            bar_top10 = min(100, (top10 / n_tours) * 100) if n_tours > 0 else 0
            bar_tours = min(100, (n_tours / 16) * 100)
            fighter_cards_data.append({
                'rider': rider.title(), 'country': country, 'type': rider_type,
                'wins': wins, 'n_tours': n_tours, 'top10_pct': round(bar_top10),
                'best_rank': best_rank, 'bar_wins': round(bar_wins),
                'bar_tours': round(bar_tours), 'bar_top10': round(bar_top10),
                'color': PALETTE_H2H[fi], 'fi': fi + 1,
            })

        # Build cards HTML as single block
        cards_cols = []
        for i, d in enumerate(fighter_cards_data):
            c = d['color']
            card_html = f"""
            <div style="flex:1;background:#0d0d0d;border:1px solid #2a2a2a;border-radius:4px;
                        padding:22px 20px;font-family:'Merriweather',Georgia,serif;
                        position:relative;overflow:hidden;border-top:3px solid {c};">
                <div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;
                            color:{c};font-family:Arial;margin-bottom:6px;">Fighter {d['fi']}</div>
                <div style="font-size:20px;font-weight:900;color:#f0ece4;line-height:1.1;
                            margin-bottom:4px;text-transform:uppercase;letter-spacing:-0.5px;">
                    {d['rider']}</div>
                <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                            color:#888;margin-bottom:16px;">{d['country']} · {d['type']}</div>
                <hr style="border:none;border-top:1px solid #2a2a2a;margin:0 0 14px;">
                <!-- GC Victories -->
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                    <span style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#666;font-family:Arial;">GC Victories</span>
                    <span style="font-size:18px;font-weight:900;color:{c};">{d['wins']}</span>
                </div>
                <div style="width:100%;height:4px;background:#1e1e1e;border-radius:2px;margin-bottom:12px;">
                    <div style="width:{d['bar_wins']}%;height:100%;background:{c};border-radius:2px;transition:width 0.8s;"></div>
                </div>
                <!-- Tours Ridden -->
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                    <span style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#666;font-family:Arial;">Tours Ridden</span>
                    <span style="font-size:18px;font-weight:900;color:{c};">{d['n_tours']}</span>
                </div>
                <div style="width:100%;height:4px;background:#1e1e1e;border-radius:2px;margin-bottom:12px;">
                    <div style="width:{d['bar_tours']}%;height:100%;background:{c};border-radius:2px;transition:width 0.8s;"></div>
                </div>
                <!-- Top-10 Rate -->
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                    <span style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#666;font-family:Arial;">Top-10 Rate</span>
                    <span style="font-size:18px;font-weight:900;color:{c};">{d['top10_pct']}%</span>
                </div>
                <div style="width:100%;height:4px;background:#1e1e1e;border-radius:2px;margin-bottom:12px;">
                    <div style="width:{d['bar_top10']}%;height:100%;background:{c};border-radius:2px;transition:width 0.8s;"></div>
                </div>
                <!-- Best GC -->
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#666;font-family:Arial;">Best GC Result</span>
                    <span style="font-size:18px;font-weight:900;color:{c};">#{d['best_rank']}</span>
                </div>
            </div>"""
            cards_cols.append(card_html)

        # VS separators
        n = len(fighter_cards_data)
        all_parts = []
        for i, card in enumerate(cards_cols):
            all_parts.append(card)
            if i < n - 1:
                all_parts.append("""
                <div style="display:flex;align-items:center;justify-content:center;
                            padding:0 12px;min-width:60px;">
                    <span style="font-size:30px;font-weight:900;color:#FFCC00;
                                 font-family:'Merriweather',serif;
                                 text-shadow:0 0 16px rgba(255,204,0,0.35);">VS</span>
                </div>""")

        fighter_html = f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&display=swap" rel="stylesheet">
        <style>body{{margin:0;background:transparent;padding:4px 0;}}</style>
        </head><body>
        <div style="display:flex;align-items:stretch;gap:0;">
            {''.join(all_parts)}
        </div>
        </body></html>"""

        card_height = 320 + (60 * (len(fighter_cards_data) > 2))
        components.html(fighter_html, height=card_height)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(hr, unsafe_allow_html=True)

        # ── CAREER ARC normalizzato H2H ──
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· The Race Through Careers ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Career Arc - Side by Side, Tour by Tour
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;line-height:1.5;">
                    X = career participation number. Both start from Tour #1. Year labels shown on each point.
                </p>
            </div>
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
            height=400, 
            # 🪄 FIX: Margini interni calibrati per far respirare i numeri dell'asse Y e allinearli
            margin=dict(l=40, r=16, t=20, b=20), 
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
        
        # 🪄 FIX: Avvolgiamo il grafico nello stesso allineamento del titolo
        st.markdown('<div style="margin: 0 16px;">', unsafe_allow_html=True)
        st.plotly_chart(fig_h2h_arc, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── WIN/LOSS DOTS per anni condivisi ──
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Direct Duels ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Head-to-Head Record - Shared Editions
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:16px;line-height:1.5;">
                    Each column = an edition where both competed. Color = who finished higher.
                </p>
            </div>
        """, unsafe_allow_html=True)

       # ── WIN/LOSS DOTS per anni condivisi ──
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

                # 1. Scoreboard Principale
                st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:center;gap:32px;
                                margin:16px 0 0 0;font-family:'Merriweather',serif;">
                        <div style="text-align:center; min-width: 150px;">
                            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#888;">{h2h_r1.title()}</div>
                            <div style="font-size:52px;font-weight:900;color:{PALETTE_H2H[0]};line-height:1;">{wins_r1}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:11px;color:#888;line-height:1.2;">shared<br>editions</div>
                            <div style="font-size:28px;font-weight:700;color:#1a1a1a;margin-top:4px;">{len(df_duel)}</div>
                        </div>
                        <div style="text-align:center; min-width: 150px;">
                            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#888;">{h2h_r2.title()}</div>
                            <div style="font-size:52px;font-weight:900;color:{PALETTE_H2H[1]};line-height:1;">{wins_r2}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # 2. Nuova Legenda Originale Centrata in mezzo
                st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:center;gap:24px;
                                margin:10px 0 16px 0;font-family:Arial,sans-serif;font-size:12px;">
                        <span style="color:{PALETTE_H2H[0]};font-weight:bold;">● {h2h_r1.title()} wins</span>
                        <span style="color:{PALETTE_H2H[1]};font-weight:bold;">● {h2h_r2.title()} wins</span>
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
                    height=130, margin=dict(l=40, r=40, t=10, b=20),
                    xaxis=dict(
                        showgrid=False, 
                        zeroline=False, 
                        tickfont=dict(size=10, family='Arial'),
                        # 🪄 FIX: Forza l'asse a non mostrare i decimali ed evita la virgola delle migliaia (es. 2,024 -> 2024)
                        tickmode='array',
                        tickvals=shared_years,
                        tickformat='d'
                    ),
                    yaxis=dict(visible=False, range=[-0.5, 0.6]),
                    showlegend=False, # Disattiva la legenda nativa decentrata di Plotly
                )

                st.markdown('<div style="margin: 0 16px;">', unsafe_allow_html=True)
                st.plotly_chart(fig_duel, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No direct duel data available for these riders in shared editions.")
        else:
            st.markdown(f"""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:12px 16px; margin: 0 16px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;font-style:italic;font-size:12px;">
                    {h2h_r1.title()} and {h2h_r2.title()} never raced the Tour in the same year.
                </div>
            """, unsafe_allow_html=True)

        # ── BEST RANK COMPARISON BAR CHART ──
        st.markdown(hr, unsafe_allow_html=True)
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Career Stats Breakdown ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Career Breakdown — Rank Distribution by Zone
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;">
                    For each rider: how many Tours ended in the Win / Podium / Top-10 / Rest zone.
                </p>
            </div>
        """, unsafe_allow_html=True)

        breakdown_rows = []
        zones = ['Win', 'Podium (2-3)', 'Top 10 (4-10)', 'Rest (11+)']
        for i, rider in enumerate(h2h_riders):
            df_rd = df_r_norm[df_r_norm['Rider'] == rider].dropna(subset=['Rank_Num'])
            total = len(df_rd)
            if total == 0:
                continue
            counts = {
                'Win':            len(df_rd[df_rd['Rank_Num'] == 1]),
                'Podium (2-3)':   len(df_rd[df_rd['Rank_Num'].between(2, 3)]),
                'Top 10 (4-10)':  len(df_rd[df_rd['Rank_Num'].between(4, 10)]),
                'Rest (11+)':     len(df_rd[df_rd['Rank_Num'] > 10]),
            }
            for zone, cnt in counts.items():
                breakdown_rows.append({
                    'Rider': rider.title(), 'Zone': zone,
                    'Count': cnt, 'Pct': round(cnt / total * 100, 1),
                    'Color': PALETTE_H2H[i],
                })

        if breakdown_rows:
            df_breakdown = pd.DataFrame(breakdown_rows)
            ZONE_OPACITY = {'Win': 1.0, 'Podium (2-3)': 0.82, 'Top 10 (4-10)': 0.55, 'Rest (11+)': 0.28}
            fig_bkd = go.Figure()
            
            # Cicliamo prima per corridore in modo da creare una serie di colonne unica per atleta
            for i, rider in enumerate(h2h_riders):
                rider_title = rider.title()
                df_rider = df_breakdown[df_breakdown['Rider'] == rider_title]
                
                if df_rider.empty:
                    continue
                
                base_color = PALETTE_H2H[i]
                r_hex = base_color.lstrip('#')
                r, g, b = int(r_hex[0:2], 16), int(r_hex[2:4], 16), int(r_hex[4:6], 16)
                
                # Creiamo le liste ordinate per le 4 zone per questo specifico corridore
                y_counts = []
                text_labels = []
                marker_colors = []
                
                for zone in zones:
                    row_zone = df_rider[df_rider['Zone'] == zone]
                    if not row_zone.empty:
                        cnt = int(row_zone['Count'].values[0])
                        pct = row_zone['Pct'].values[0]
                        alpha = ZONE_OPACITY[zone]
                        
                        y_counts.append(cnt)
                        text_labels.append(f"{cnt}<br>({pct}%)" if cnt > 0 else "")
                        marker_colors.append(f"rgba({r},{g},{b},{alpha})")
                    else:
                        y_counts.append(0)
                        text_labels.append("")
                        marker_colors.append(f"rgba({r},{g},{b},0.1)")
                
                # Aggiungiamo la traccia per il corridore attuale
                fig_bkd.add_trace(go.Bar(
                    name=rider_title,
                    x=zones,
                    y=y_counts,
                    text=text_labels,
                    textposition='outside',
                    marker_color=marker_colors,
                    marker_line=dict(width=0),
                    hovertemplate=f"<b>{rider_title}</b><br>%{{x}}: %{{y}} Tours<extra></extra>",
                ))

            fig_bkd.update_layout(
                barmode='group',
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
                height=380, margin=dict(l=40, r=20, t=30, b=20),
                showlegend=True,
                legend=dict(
                    orientation='h', y=-0.15, x=0.5, xanchor='center',
                    font=dict(size=10),
                ),
                xaxis=dict(title='', tickfont=dict(size=12, family='Merriweather, serif')),
                yaxis=dict(title='Number of Tours', showgrid=True, gridcolor='#e8e4da'),
            )

            st.plotly_chart(fig_bkd, use_container_width=True)


    # ══════════════════════════════════════════════════════════
    # TAB 4 — NATIONS
    # ══════════════════════════════════════════════════════════
    elif st.session_state.riders_tab == "nations":

        st.markdown("""
    <div style="padding: 0 16px;">
        <span class="r-section-label">· Geographic Analysis ·</span>
        <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
            Nations of the Tour - Where Champions Are Born
        </h3>
        <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;font-style:italic;margin-bottom:16px;line-height:1.5;">
            Choropleth map of Tour de France GC victories by country. Hover for details.
        </p>
    </div>
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
            # 🪄 FIX: Scala di soli gialli (dal crema chiaro al giallo saturo/ocra intenso)
            color_continuous_scale=[
                [0.0, '#FFF3CD'],   # 1 vittoria (giallo crema, ben visibile sul fondo carta)
                [0.2, '#FFE066'],   # Giallo tenue
                [0.5, '#FFCC00'],   # Giallo classico Tour de France
                [0.8, '#E6B800'],   # Giallo scuro / dorato
                [1.0, '#B38F00']    # Giallo ocra intenso per il picco massimo (Francia)
            ],
            labels={'victories': 'GC Victories'},
        )
        fig_choro.update_geos(
            showcoastlines=True, coastlinecolor='#c8bfad',
            showland=True, landcolor='#F4F1EA', # I paesi a zero vittorie rimangono neutri del colore dello sfondo
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
        
        st.markdown('<div style="margin: 0 16px;">', unsafe_allow_html=True)
        st.plotly_chart(fig_choro, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── SUNBURST: Continente → Nazione ──
        # ── SUNBURST: Continente → Nazione ──
# ── SUNBURST: Continente → Nazione ──
# ── SUNBURST: Continente → Nazione ──
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Victory Share ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    The Geography of Glory — Victory Share by Region
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;font-style:italic;margin-bottom:8px;line-height:1.5;">
                    Inner ring = continent region. Outer ring = specific nation. Segment size represents the volume of GC victories. Click on a region to zoom.
                </p>
            </div>
        """, unsafe_allow_html=True)

        CONTINENT_MAP = {
            'France': 'Western Europe', 'Belgium': 'Western Europe',
            'Netherlands': 'Western Europe', 'Luxembourg': 'Western Europe',
            'Switzerland': 'Western Europe', 'Germany': 'Western Europe',
            'Spain': 'Southern Europe', 'Italy': 'Southern Europe',
            'Portugal': 'Southern Europe',
            'United Kingdom': 'British Isles', 'Ireland': 'British Isles',
            'Denmark': 'Northern Europe', 'Norway': 'Northern Europe',
            'Slovenia': 'Central Europe', 'Austria': 'Central Europe',
            'USA': 'Americas', 'Colombia': 'Americas',
            'Australia': 'Oceania',
        }
        CONTINENT_COLORS = {
            'Western Europe': '#FFCC00', 'Southern Europe': '#FF8C00',
            'British Isles': '#CF142B', 'Northern Europe': '#4ECDC4',
            'Central Europe': '#7B68EE', 'Americas': '#B22234',
            'Oceania': '#00843D',
        }

        df_sun = df_w_clean.groupby('Country_clean').size().reset_index(name='victories')
        df_sun['continent'] = df_sun['Country_clean'].map(CONTINENT_MAP).fillna('Other')
        df_sun['pct'] = (df_sun['victories'] / df_sun['victories'].sum() * 100).round(1)
        df_sun['cont_color'] = df_sun['continent'].map(CONTINENT_COLORS).fillna('#888')

        # Sunburst con Plotly
        # Livelli: root → continent → country
        labels = ['Tour de France']
        parents = ['']
        values = [df_sun['victories'].sum()]
        colors = ['#1a1a1a']
        customdata_sun = [(110, 100.0)]

        # Continenti
        for cont in df_sun['continent'].unique():
            df_c = df_sun[df_sun['continent'] == cont]
            total_c = df_c['victories'].sum()
            pct_c = round(total_c / df_sun['victories'].sum() * 100, 1)
            labels.append(cont)
            parents.append('Tour de France')
            values.append(total_c)
            colors.append(CONTINENT_COLORS.get(cont, '#888'))
            customdata_sun.append((total_c, pct_c))

        # Nazioni
        for _, row in df_sun.iterrows():
            labels.append(row['Country_clean'])
            parents.append(row['continent'])
            values.append(row['victories'])
            colors.append(row['cont_color'])
            customdata_sun.append((row['victories'], row['pct']))

        fig_sun = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors, line=dict(color='#F4F1EA', width=2)),
            hovertemplate='<b>%{label}</b><br>Victories: %{customdata[0]}<br>Share: %{customdata[1]:.1f}%<extra></extra>',
            customdata=customdata_sun,
            texttemplate='<b>%{label}</b><br>%{value}',
            textfont=dict(size=11, family='Arial'),
            insidetextorientation='radial',
            branchvalues='total',
            rotation=90,
        ))
        fig_sun.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, Georgia, serif', color='#1a1a1a'),
            height=500, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_sun, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)                
        # ── DECADE DOMINANCE TABLE ──
        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="r-section-label">· Era by Era ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;color:#1a1a1a;margin:4px 0 4px;">
                    Who Ruled Each Decade?
                </h4>
            </div>
        """, unsafe_allow_html=True)

        df_dec = df_w_clean.groupby(['decade', 'Country_clean']).size().reset_index(name='wins')
        df_dec_pivot = df_dec.pivot(index='Country_clean', columns='decade', values='wins').fillna(0).astype(int)
        df_dec_pivot.columns = [f"{int(c)}s" for c in df_dec_pivot.columns]
        df_dec_pivot['TOTAL'] = df_dec_pivot.sum(axis=1)
        df_dec_pivot = df_dec_pivot.sort_values('TOTAL', ascending=False)
        df_dec_pivot.index.name = 'Nation'

        # Heatmap manuale senza matplotlib
        max_val = df_dec_pivot.iloc[:, :-1].max().max()

        def cell_bg(val, is_total=False):
            if is_total:
                return "#1a1a1a", "#FFCC00"  # Colore fisso distintivo per la colonna TOTAL
            if val == 0:
                return "#F4F1EA", "#bbb"     # Sfondo neutro per i valori a zero
            
            # Calcolo intensità normalizzata (0 a 1)
            intensity = val / max_val if max_val > 0 else 0
            
            # Scala lineare di soli gialli (RGB di #FFF3CD -> RGB di #B38F00)
            r = int(255 - (intensity * (255 - 179)))
            g = int(243 - (intensity * (243 - 143)))
            b = int(205 - (intensity * (205 - 0)))
            
            # Contrasto dinamico del testo basato sull'intensità del giallo
            txt = "#ffffff" if intensity > 0.75 else "#1a1a1a"
            return f"rgb({r},{g},{b})", txt

        cols_decade = ["Nation"] + list(df_dec_pivot.columns)
        header_cells = "".join(
            f'<th style="padding:8px 12px;font-size:10px;letter-spacing:1px;text-transform:uppercase;'
            f'font-family:Arial;color:#888;border-bottom:2px solid #1a1a1a;white-space:nowrap;">{c}</th>'
            for c in cols_decade
        )

        body_rows = ""
        for nation, row in df_dec_pivot.iterrows():
            cells = f'<td style="padding:8px 12px;font-weight:700;font-size:12px;'
            cells += f'font-family:Merriweather,serif;color:#1a1a1a;border-right:1px solid #e8e4da;'
            cells += f'white-space:nowrap;">{nation}</td>'
            for ci, col in enumerate(df_dec_pivot.columns):
                val = row[col]
                is_total = col == "TOTAL"
                bg, fg = cell_bg(val, is_total)
                fw = "900" if is_total else ("700" if val > 0 else "400")
                cells += (
                    f'<td style="padding:8px 12px;text-align:center;background:{bg};'
                    f'color:{fg};font-weight:{fw};font-size:{"13" if is_total else "12"}px;'
                    f'font-family:{"Arial" if is_total else "Merriweather,serif"};'
                    f'border-right:1px solid #e8e4da;">'
                    f'{"" if val == 0 and not is_total else int(val)}</td>'
                )
            body_rows += f'<tr style="border-bottom:1px solid #e8e4da;">{cells}</tr>'

        # ── COSTRUZIONE DELLA LEGENDA CROMATICA ──
        # Una barra sfumata orizzontale con indicatori per il valore minimo (1 win) e massimo
        legend_html = f"""
        <div style="margin: 12px 16px 0 16px; font-family: Arial, sans-serif; font-size: 11px; color: #666; display: flex; align-items: center; gap: 10px;">
            <span style="white-space: nowrap;">0 wins: <span style="display:inline-block; width:12px; height:12px; background:#F4F1EA; border:1px solid #c8bfad; vertical-align:middle; margin-left:2px; border-radius:2px;"></span></span>
            <span style="margin-left: 8px;">1 win</span>
            <div style="flex-grow: 1; max-width: 180px; height: 10px; background: linear-gradient(to right, #FFF3CD, #FFE066, #FFCC00, #E6B800, #B38F00); border-radius: 2px;"></div>
            <span>{max_val} wins (Max)</span>
        </div>
        """

        decade_table_html = f"""
        <div style="overflow-x:auto; margin: 8px 16px 0 16px;">
        <table style="width:100%;border-collapse:collapse;font-family:'Merriweather',serif;
                      background:#F4F1EA;border:1px solid #c8bfad;border-radius:4px;overflow:hidden;">
            <thead><tr style="background:#1a1a1a;">{header_cells}</tr></thead>
            <tbody>{body_rows}</tbody>
        </table>
        </div>
        {legend_html}
        """
        st.markdown(decade_table_html, unsafe_allow_html=True)

        

elif st.session_state.pagina_corrente == "tappe":

    # ----------------------------------------------------------
    # 0. PREPARAZIONE DATI GLOBALI
    # ----------------------------------------------------------
    df_stage_h['Year'] = df_stage_h['Year'].fillna(0).astype(int)
    df_stage_h_filtered = df_stage_h[df_stage_h['Year'] >= 1903].copy()

# df_coords = stages_TDF.xlsx
    df_coords_all = df_coords.copy()
    
    # 1. Pulizia preventiva
    df_coords_all.columns = df_coords_all.columns.str.strip()

    if 'Year' not in df_coords_all.columns:
        df_coords_all['Year'] = pd.to_datetime(df_coords_all['Date'], errors='coerce').dt.year

    # 2. Allineamento nomi colonne per la mappa (Start/End -> Origin/Destination)
    if 'Start' in df_coords_all.columns and 'Origin' not in df_coords_all.columns:
        df_coords_all = df_coords_all.rename(columns={'Start': 'Origin'})
    if 'End' in df_coords_all.columns and 'Destination' not in df_coords_all.columns:
        df_coords_all = df_coords_all.rename(columns={'End': 'Destination'})

    # 3. Gestione Tipo di Tappa a prova di crash
    col_type = next((col for col in ['Type', 'Stage Type', 'Type of stage', 'Type of route', 'Stage_Type'] if col in df_coords_all.columns), None)

    if col_type is None:
        # Se nel file Excel non c'è il tipo, assegniamo 'Other' a tutte le tappe per non far bloccare l'app
        df_coords_all['Type_group'] = 'Other'
    else:
        TYPE_MAP = {
            'Plain stage': 'Flat', 'Flat stage': 'Flat', 'Flat Stage': 'Flat',
            'Flat cobblestone stage': 'Flat', 'Plain stage with cobblestones': 'Flat',
            'Stage with mountain(s)': 'Mountain', 'High mountain stage': 'Mountain',
            'Mountain stage': 'Mountain', 'Mountain Stage': 'Mountain',
            'Medium mountain stage': 'Mountain', 'Stage with mountain': 'Mountain',
            'Hilly stage': 'Hilly',
            'Individual time trial': 'Time Trial', 'Mountain time trial': 'Time Trial',
            'Team time trial': 'Team TT',
            'Half Stage': 'Other', 'Transition stage': 'Other',
            'Intermediate stage': 'Other',
        }
        df_coords_all['Type_group'] = df_coords_all[col_type].astype(str).str.strip().map(TYPE_MAP).fillna('Other')
    
    df_coords_all['decade'] = (df_coords_all['Year'] // 10) * 10

    TYPE_COLORS = {
        'Flat': '#4ECDC4', 'Mountain': '#FF6B6B',
        'Hilly': '#FFCC00', 'Time Trial': '#A29BFE',
        'Team TT': '#FD79A8', 'Other': '#888',
    }

    # Coordinate hardcoded per le città più frequenti del Tour
    CITY_COORDS = {
        'Paris': (48.8566, 2.3522), 'Bordeaux': (44.8378, -0.5792),
        'Pau': (43.2951, -0.3708), 'Luchon': (42.7911, 0.5936),
        'Metz': (49.1193, 6.1757), 'Grenoble': (45.1885, 5.7245),
        'Nice': (43.7102, 7.2620), 'Perpignan': (42.6887, 2.8948),
        'Marseille': (43.2965, 5.3698), 'Caen': (49.1829, -0.3707),
        'Bayonne': (43.4929, -1.4748), 'Montpellier': (43.6108, 3.8767),
        'Brest': (48.3904, -4.4861), 'Nantes': (47.2184, -1.5536),
        'Belfort': (47.6370, 6.8632), 'Toulouse': (43.6047, 1.4442),
        'Roubaix': (50.6942, 3.1746), 'Gap': (44.5594, 6.0773),
        'Strasbourg': (48.5734, 7.7521), 'Aix-les-Bains': (45.6888, 5.9141),
        'La Rochelle': (46.1591, -1.1520), 'Angers': (47.4784, -0.5632),
        'Le Havre': (49.4938, 0.1077), 'Rouen': (49.4432, 1.0993),
        'Lyon': (45.7640, 4.8357), 'Cherbourg': (49.6337, -1.6225),
        'Lille': (50.6292, 3.0573), 'Morzine': (46.1792, 6.7108),
        'Dijon': (47.3220, 5.0415), "Alpe d'Huez": (45.0919, 6.0706),
        'Versailles': (48.8014, 2.1301), 'Nancy': (48.6921, 6.1844),
        'Rennes': (48.1173, -1.6778), 'Dunkerque': (51.0343, 2.3767),
        'Limoges': (45.8336, 1.2611), 'Mulhouse': (47.7508, 7.3359),
        'Cannes': (43.5528, 7.0174), 'Toulon': (43.1242, 5.9280),
        'Vannes': (47.6559, -2.7603), 'Amiens': (49.8942, 2.2957),
        'Albi': (43.9279, 2.1480), 'Reims': (49.2583, 4.0317),
        'Geneva': (46.2044, 6.1432), 'Dieppe': (49.9218, 1.0798),
        'Brussels': (50.8503, 4.3517), 'Liège': (50.6326, 5.5797),
        'Amsterdam': (52.3676, 4.9041), 'Rotterdam': (51.9244, 4.4777),
        'London': (51.5074, -0.1278), 'Dublin': (53.3498, -6.2603),
        'Frankfurt': (50.1109, 8.6821), 'Berlin': (52.5200, 13.4050),
        'Luxembourg': (49.6116, 6.1319), 'Lausanne': (46.5197, 6.6323),
        'Berne': (46.9480, 7.4474), 'Zurich': (47.3769, 8.5417),
        'Milan': (45.4654, 9.1859), 'Turin': (45.0703, 7.6869),
        'San Sebastián': (43.3183, -1.9812), 'Bilbao': (43.2630, -2.9350),
        'Barcelona': (41.3851, 2.1734), 'Madrid': (40.4168, -3.7038),
        'Briançon': (44.8956, 6.6415), 'Besançon': (47.2378, 6.0241),
        'Saint-Étienne': (45.4397, 4.3872), 'Évian': (46.3890, 6.5890),
        'Mâcon': (46.3069, 4.8281), 'Lons-le-Saunier': (46.6750, 5.5556),
        'Pontarlier': (46.9057, 6.3556), 'Chamonix': (45.9237, 6.8694),
        'Megève': (45.8572, 6.6194), 'Courchevel': (45.4154, 6.6344),
        'L\'Alpe-d\'Huez': (45.0919, 6.0706), 'Alpe d\'Huez': (45.0919, 6.0706),
        'Luz-Ardiden': (42.8889, -0.0300), 'Superbagnères': (42.7917, 0.5822),
        'Pla-d\'Adet': (42.8181, 0.3178), 'La Mongie': (42.9142, 0.1672),
        'Hautacam': (43.0397, -0.0506), 'Peyragudes': (42.8253, 0.3833),
        'Le Bourg-d\'Oisans': (45.0560, 6.0261), 'Saint-Gaudens': (43.1058, 0.7236),
        'Dax': (43.7101, -1.0520), 'Agen': (44.2009, 0.6219),
        'Issoire': (45.5447, 3.2494), 'Vichy': (46.1278, 3.4267),
        'Clermont-Ferrand': (45.7772, 3.0870), 'Aurillac': (44.9283, 2.4419),
        'Mende': (44.5194, 3.4986), 'Millau': (44.0996, 3.0778),
        'Rodez': (44.3500, 2.5750), 'Nîmes': (43.8367, 4.3601),
        'Montélimar': (44.5567, 4.7522), 'Valence': (44.9334, 4.8924),
        'Carpentras': (44.0561, 5.0528), 'Avignon': (43.9493, 4.8055),
        'Aix-en-Provence': (43.5298, 5.4474), 'Antibes': (43.5804, 7.1283),
        'Monaco': (43.7384, 7.4246), 'Menton': (43.7765, 7.5024),
        'Charleville': (49.7657, 4.7180), 'Épernay': (49.0399, 3.9598),
        'Laval': (48.0740, -0.7709), 'Le Mans': (47.9960, 0.1966),
        'Tours': (47.3941, 0.6848), 'Orléans': (47.9029, 1.9093),
        'Chartres': (48.4469, 1.4889), 'Évreux': (49.0266, 1.1511),
        'Chateauroux': (46.8130, 1.6919), 'Guéret': (46.1717, 1.8716),
        'Saintes': (45.7461, -0.6333), 'Cognac': (45.6944, -0.3289),
        'Angoulême': (45.6497, 0.1563), 'Périgueux': (45.1851, 0.7210),
        'Brive-la-Gaillarde': (45.1589, 1.5347), 'Tulle': (45.2676, 1.7727),
        'Figeac': (44.6085, 2.0328), 'Cahors': (44.4486, 1.4420),
        'Tarbes': (43.2329, 0.0780), 'Foix': (42.9649, 1.6058),
        'Ax-les-Thermes': (42.7198, 1.8367), 'Carcassonne': (43.2130, 2.3491),
        'Sète': (43.4072, 3.6968), 'Béziers': (43.3444, 3.2150),
        'Pézenas': (43.4617, 3.4233), 'Lodève': (43.7311, 3.3194),
        'Mâcon': (46.3069, 4.8281), 'Bourg-en-Bresse': (46.2050, 5.2257),
        'Thonon-les-Bains': (46.3731, 6.4778), 'Annecy': (45.8992, 6.1294),
        'Albertville': (45.6753, 6.3942), 'Bourg-Saint-Maurice': (45.6186, 6.7697),
        'Val-d\'Isère': (45.4481, 6.9770), 'Tignes': (45.4688, 6.9086),
        'Isola 2000': (44.1892, 7.1711), 'Auron': (44.2033, 6.9258),
        'Sestrières': (44.9583, 6.8772), 'Turin': (45.0703, 7.6869),
        'Alessandria': (44.9119, 8.6148), 'Cuneo': (44.3842, 7.5420),
        'Embrun': (44.5639, 6.4978), 'Sisteron': (44.2004, 5.9434),
        'Digne-les-Bains': (44.0920, 6.2361), 'Castellane': (43.8494, 6.5133),
        'Draguignan': (43.5353, 6.4647), 'Fréjus': (43.4297, 6.7370),
        'Saint-Raphaël': (43.4250, 6.7694), 'Hyères': (43.1203, 6.1286),
        'Dunkerque': (51.0343, 2.3767), 'Calais': (50.9513, 1.8587),
        'Boulogne-sur-Mer': (50.7264, 1.6141), 'Amiens': (49.8942, 2.2957),
        'Compiègne': (49.4183, 2.8268), 'Soissons': (49.3817, 3.3232),
        'Laon': (49.5636, 3.6245), 'Épinal': (48.1726, 6.4506),
        'Colmar': (48.0793, 7.3585), 'Ribeauvillé': (48.1938, 7.3202),
        'Thann': (47.8122, 7.1025), 'Gerardmer': (48.0726, 6.8773),
        'Remiremont': (48.0168, 6.5905), 'Vittel': (48.2006, 5.9533),
        'Bar-le-Duc': (48.7731, 5.1622), 'Verdun': (49.1611, 5.3875),
        'Sedan': (49.7016, 4.9400), 'Charleville-Mézières': (49.7657, 4.7180),
    }

    # ----------------------------------------------------------
    # 1. CSS GLOBALE SEZIONE STAGES
    # ----------------------------------------------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

        /* ── Masthead ── */
        .stages-masthead {
            border-top: 5px solid #1a1a1a;
            border-bottom: 2px solid #1a1a1a;
            padding: 12px 0 8px;
            text-align: center;
            margin-bottom: 24px;
        }
        .st-section-label-s {
            font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
            color: #888; font-family: Arial, sans-serif;
            display: block; margin-bottom: 4px;
        }
        .s-rule { border: none; border-top: 1px solid #c8bfad; margin: 28px 0; }

        /* ── Card fotografiche ── */
        .stage-card-wrap {
            position: relative; height: 260px;
            background-size: cover; background-position: center;
            border-radius: 4px 4px 0 0; overflow: hidden; cursor: pointer;
        }
        .stage-card-overlay {
            position: absolute; inset: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.3) 60%, transparent 100%);
        }
        .stage-card-text {
            position: absolute; bottom: 0; left: 0; right: 0;
            padding: 16px; color: white;
        }
        .stage-card-subtitle {
            font-size: 10px; font-weight: 700; color: #FFCC00;
            letter-spacing: 2px; text-transform: uppercase;
            font-family: Arial, sans-serif; margin-bottom: 6px;
        }
        .stage-card-title {
            font-size: 20px; font-weight: 900; line-height: 1.1;
            text-transform: uppercase; font-family: 'Merriweather', serif;
        }

        /* ── Selectbox scura ── */
        div[data-testid="stSelectbox"] label p { color: #1a1a1a !important; font-family: 'Merriweather', serif !important; font-weight: 700 !important; }
        div[data-baseweb="select"] > div { background-color: #111 !important; color: #fff !important; border: 1px solid #444 !important; border-radius: 3px !important; }
        div[data-baseweb="popover"] ul, ul[data-baseweb="menu"], ul[role="listbox"] { background-color: #111 !important; }
        div[data-baseweb="popover"] li, ul[data-baseweb="menu"] li, ul[role="listbox"] li { color: #fff !important; background-color: #111 !important; }
        div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover { background-color: #2a2a2a !important; }
        ul[role="listbox"] li[aria-selected="true"] { color: #FFCC00 !important; }

        /* ── Radio buttons ── */
        div[data-testid="stRadio"] label, div[data-testid="stRadio"] p,
        div[data-testid="stRadio"] span { color: #1a1a1a !important; }

/* ── Bottoni card ── */
        button[kind="primary"], button[data-testid="baseButton-primary"] {
            background-color: #1a1a1a !important; 
            color: #FFCC00 !important;
            border: none !important; 
            border-radius: 0 !important;
            box-shadow: inset 0 -4px 0 0 #FFCC00 !important;
            font-family: 'Merriweather', serif !important; 
            font-size: 11px !important;
            font-weight: 700 !important; 
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important; 
            padding: 14px !important;
        }
        button[kind="secondary"] {
            background-color: #F4F1EA !important; color: #888 !important;
            border: 1px solid #c8bfad !important; border-radius: 0 !important;
            font-family: 'Merriweather', serif !important; font-size: 11px !important;
            font-weight: 700 !important; letter-spacing: 1.5px !important;
            text-transform: uppercase !important; padding: 14px !important;
        }
        button[kind="secondary"]:hover {
            color: #1a1a1a !important; border-color: #888 !important;
            background-color: #ece8e0 !important;
        }

        /* ── Slider ── */
        [data-testid="stSlider"] {
            background-color: #111; padding: 14px 18px; border-radius: 4px;
            border-bottom: 2px solid #FFCC00;
        }
        [data-testid="stWidgetLabel"] p { color: #f0ece4 !important; font-family: 'Merriweather', serif !important; font-size: 11px !important; letter-spacing: 1px !important; }
        [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] { color: #888 !important; }
        </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 2. TESTATA GIORNALISTICA
    # ----------------------------------------------------------
    st.markdown("""
        <div class="stages-masthead">
            <span style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#888;font-family:Arial,sans-serif;">
                Stages Archive · 1903 to Today · 2,400+ Stages
            </span>
            <h1 style="font-family:'Merriweather',Georgia,serif;font-size:42px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 2px;letter-spacing:-1px;">
                The Road Unfolds
            </h1>
            <div style="font-size:10px;letter-spacing:2px;color:#888;font-family:Arial,sans-serif;
                        border-top:1px solid #c8bfad;padding-top:6px;margin-top:6px;">
                Historical Trends · Edition Details · Geography of Le Tour
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 3. STATE
    # ----------------------------------------------------------
    if "vista_tappe" not in st.session_state:
        st.session_state.vista_tappe = None

    # ----------------------------------------------------------
    # 4. CARD FOTOGRAFICHE
    # ----------------------------------------------------------
    URL_CARD1 = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9RqpfLR4o-8OqXaHgfkX3i_AQWqHXGhGGkQ&s"
    URL_CARD2 = "https://cdn.shopify.com/s/files/1/0040/5251/6910/files/GettyImages-1232277_1024x1024.jpg?v=1624033149"
    URL_CARD3 = "https://preview.redd.it/map-of-all-the-stages-in-the-history-of-the-tour-de-france-v0-v1t2yrg7zzyf1.jpeg?width=1080&crop=smart&auto=webp&s=16442894182572aebe679320c02811e74f233f67"

    cards_data = [
        ("storico",  "SECTION 1 · DATA",      "HISTORICAL<br>TRENDS",        URL_CARD1),
        ("dettaglio","SECTION 2 · EDITIONS",   "DETAILS &<br>JERSEYS",        URL_CARD2),
        ("mappa",    "SECTION 3 · GEOGRAPHY",  "GEOGRAPHIC<br>EXPLORATION",   URL_CARD3),
    ]

    col_c1, col_c2, col_c3 = st.columns(3, gap="small")
    cols_cards = [col_c1, col_c2, col_c3]

    for idx, (vista_key, subtitle, title, img_url) in enumerate(cards_data):
        is_active = st.session_state.vista_tappe == vista_key
        with cols_cards[idx]:
            st.markdown(f"""
                <div style="position:relative;height:220px;
                            background-image:url('{img_url}');
                            background-size:cover;background-position:center;
                            border-radius:4px 4px 0 0;overflow:hidden;">
                    <div style="position:absolute;inset:0;
                                background:linear-gradient(to top,rgba(0,0,0,{'0.92' if is_active else '0.75'}) 0%,
                                rgba(0,0,0,0.2) 70%,transparent 100%);"></div>
                    <div style="position:absolute;bottom:0;left:0;right:0;padding:14px;">
                        <div style="font-size:9px;font-weight:700;color:#FFCC00;letter-spacing:2px;
                                    text-transform:uppercase;font-family:Arial;margin-bottom:4px;">
                            {subtitle}</div>
                        <div style="font-size:17px;font-weight:900;line-height:1.1;
                                    text-transform:uppercase;font-family:'Merriweather',serif;color:white;">
                            {title}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            btn_type = "primary" if is_active else "secondary"
            if st.button("EXPLORE →", key=f"btn_{vista_key}",
                         type=btn_type, use_container_width=True):
                st.session_state.vista_tappe = vista_key
                st.rerun()

    st.markdown("<hr class='s-rule'>", unsafe_allow_html=True)

    hr = "<hr class='s-rule'>"
    vista_corrente = st.session_state.vista_tappe

    # ══════════════════════════════════════════════════════════
    # VISTA 1 — HISTORICAL TRENDS (rinnovata)
    # ══════════════════════════════════════════════════════════
    if vista_corrente == "storico":

        st.markdown("""
            <span class="st-section-label-s">· Historical Overview ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 4px;">
                A Century of Racing — Distance, Intensity & Composition
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;
                      font-style:italic;margin-bottom:16px;">
                Drag the slider to filter the historical window. All charts update simultaneously.
            </p>
        """, unsafe_allow_html=True)

        # Slider
        anno_min_abs = int(df_stage_h_filtered['Year'].min())
        anno_max_abs = int(df_stage_h_filtered['Year'].max())
        anno_min, anno_max = st.slider(
            "Historical window:", min_value=anno_min_abs, max_value=anno_max_abs,
            value=(anno_min_abs, anno_max_abs), step=1, key="slider_storico"
        )

        df_filt = df_stage_h_filtered[(df_stage_h_filtered['Year'] >= anno_min) &
                                       (df_stage_h_filtered['Year'] <= anno_max)]
        df_coords_filt = df_coords_all[(df_coords_all['Year'] >= anno_min) &
                                        (df_coords_all['Year'] <= anno_max)]

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 1: Distance + Avg Stage Distance ──
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("""
                <span class="st-section-label-s">· Total Race Distance ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                           color:#1a1a1a;font-size:16px;margin:2px 0 8px;">
                    Total km per Edition
                </h4>
            """, unsafe_allow_html=True)

            df_dist = df_filt.groupby('Year')['TotalTDFDistance'].max().reset_index()
            df_dist = df_dist.set_index('Year').reindex(range(anno_min, anno_max+1)).reset_index()
            df_dist.columns = ['Year', 'TotalTDFDistance']

            fig_dist = go.Figure()
            fig_dist.add_trace(go.Scatter(
                x=df_dist['Year'], y=df_dist['TotalTDFDistance'],
                mode='lines', fill='tozeroy',
                line=dict(color='#FFCC00', width=2.5),
                fillcolor='rgba(255,204,0,0.12)',
                hovertemplate='<b>%{x}</b><br>%{y:,.0f} km<extra></extra>',
                connectgaps=False,
            ))
            # Record annotation
            max_row = df_dist.dropna().loc[df_dist['TotalTDFDistance'].idxmax()]
            fig_dist.add_annotation(
                x=max_row['Year'], y=max_row['TotalTDFDistance'],
                text=f"Record<br>{int(max_row['TotalTDFDistance']):,} km",
                showarrow=True, arrowhead=2, arrowcolor='#888',
                font=dict(size=9, color='#1a1a1a', family='Arial'),
                bgcolor='rgba(255,204,0,0.8)', borderpad=4, ax=30, ay=-30,
            )
            for x0, x1, lbl in [(1914,1918,'WWI'),(1939,1947,'WWII')]:
                if x0 >= anno_min and x1 <= anno_max:
                    fig_dist.add_vrect(x0=x0, x1=x1, fillcolor='#888', opacity=0.15,
                                       line_width=0, annotation_text=lbl,
                                       annotation_font=dict(size=9, color='#888'))
            fig_dist.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=300, margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(showgrid=False, range=[anno_min, anno_max]),
                yaxis=dict(showgrid=True, gridcolor='#e8e4da', title='km'),
                showlegend=False,
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        with col2:
            st.markdown("""
                <span class="st-section-label-s">· Stage Intensity ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                           color:#1a1a1a;font-size:16px;margin:2px 0 8px;">
                    Average km per Stage
                </h4>
            """, unsafe_allow_html=True)

            df_avg = df_filt.groupby('Year').agg(
                total=('TotalTDFDistance','max'), n=('Stages','count')
            ).reset_index()
            df_avg['avg_stage'] = df_avg['total'] / df_avg['n']
            df_avg = df_avg.set_index('Year').reindex(range(anno_min, anno_max+1)).reset_index()

            fig_avg = go.Figure()
            fig_avg.add_trace(go.Scatter(
                x=df_avg['Year'], y=df_avg['avg_stage'],
                mode='lines', fill='tozeroy',
                line=dict(color='#FF6B6B', width=2.5),
                fillcolor='rgba(255,107,107,0.10)',
                hovertemplate='<b>%{x}</b><br>%{y:.1f} km/stage<extra></extra>',
                connectgaps=False,
            ))
            for x0, x1, lbl in [(1914,1918,'WWI'),(1939,1947,'WWII')]:
                if x0 >= anno_min and x1 <= anno_max:
                    fig_avg.add_vrect(x0=x0, x1=x1, fillcolor='#888', opacity=0.15,
                                      line_width=0, annotation_text=lbl,
                                      annotation_font=dict(size=9, color='#888'))
            fig_avg.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=300, margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(showgrid=False, range=[anno_min, anno_max]),
                yaxis=dict(showgrid=True, gridcolor='#e8e4da', title='km/stage'),
                showlegend=False,
            )
            st.plotly_chart(fig_avg, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── STACKED AREA: composizione tappe per decade ──
        st.markdown("""
            <span class="st-section-label-s">· Stage DNA ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                       color:#1a1a1a;font-size:18px;margin:2px 0 4px;">
                The Changing DNA of the Tour — Stage Types Over Decades
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                      font-style:italic;margin-bottom:8px;">
                Stacked area: how the mix of flat, mountain, time trial stages evolved. 
                More mountains, fewer epic flat stages.
            </p>
        """, unsafe_allow_html=True)

        df_type_dec = df_coords_filt.groupby(['decade', 'Type_group']).size().reset_index(name='count')
        TYPE_ORDER = ['Flat', 'Mountain', 'Hilly', 'Time Trial', 'Team TT', 'Other']
        df_type_dec['Type_group'] = pd.Categorical(df_type_dec['Type_group'], categories=TYPE_ORDER, ordered=True)
        df_type_dec = df_type_dec.sort_values(['decade', 'Type_group'])

        fig_area = go.Figure()
        for ttype in TYPE_ORDER:
            df_t = df_type_dec[df_type_dec['Type_group'] == ttype]
            if df_t.empty:
                continue
            fig_area.add_trace(go.Scatter(
                x=df_t['decade'], y=df_t['count'],
                name=ttype,
                mode='lines',
                stackgroup='one',
                line=dict(width=0.5, color=TYPE_COLORS.get(ttype, '#888')),
                fillcolor=TYPE_COLORS.get(ttype, '#888'),
                opacity=0.85,
                hovertemplate=f'<b>{ttype}</b><br>%{{x}}s: %{{y}} stages<extra></extra>',
            ))
        fig_area.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, serif', color='#1a1a1a'),
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center', font=dict(size=10)),
            xaxis=dict(title='Decade', showgrid=False,
                       tickvals=list(range(1900,2030,10)),
                       ticktext=[f"{d}s" for d in range(1900,2030,10)]),
            yaxis=dict(title='Number of stages', showgrid=True, gridcolor='#e8e4da'),
        )
        st.plotly_chart(fig_area, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

        # ── SPEED EVOLUTION ──
        st.markdown("""
            <span class="st-section-label-s">· Speed of Champions ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                       color:#1a1a1a;font-size:18px;margin:2px 0 4px;">
                Evolution of Average Winning Speed
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                      font-style:italic;margin-bottom:8px;">
                Dotted segment = doping era (1999–2005), titles revoked, no official winners.
            </p>
        """, unsafe_allow_html=True)

        df_winners_speed = df_storico.copy()
        df_winners_speed['Rank_Num'] = pd.to_numeric(df_winners_speed['Rank'], errors='coerce')
        df_winners_speed = df_winners_speed[
            (df_winners_speed['Rank_Num'] == 1) &
            df_winners_speed['TotalSeconds'].notna() &
            (df_winners_speed['TotalSeconds'] > 0) &
            (df_winners_speed['Year'] >= anno_min) &
            (df_winners_speed['Year'] <= anno_max)
        ].copy()
        df_winners_speed['avg_speed'] = df_winners_speed['Distance (km)'] / (df_winners_speed['TotalSeconds'] / 3600)

        # Split: clean vs doping era
        df_clean = df_winners_speed[~df_winners_speed['Year'].isin(range(1999,2006))]
        df_doping = df_winners_speed[df_winners_speed['Year'].isin(range(1999,2006))]

        fig_speed = go.Figure()
        fig_speed.add_trace(go.Scatter(
            x=df_clean['Year'], y=df_clean['avg_speed'],
            mode='lines+markers',
            line=dict(color='#1a1a1a', width=2.5),
            marker=dict(size=5, color='#FFCC00', line=dict(width=1, color='#1a1a1a')),
            hovertemplate='<b>%{x}</b><br>%{y:.2f} km/h<extra></extra>',
            name='Official speed', showlegend=False,
            connectgaps=False,
        ))
        if not df_doping.empty:
            fig_speed.add_trace(go.Scatter(
                x=df_doping['Year'], y=df_doping['avg_speed'],
                mode='markers',
                marker=dict(size=8, color='#FF6B6B', symbol='x', line=dict(width=2)),
                hovertemplate='<b>%{x}</b> — Title subsequently revoked<br>%{y:.2f} km/h (unofficial)<extra></extra>',
                name='Revoked title', showlegend=True,
            ))
            # Doping era vrect
            if 1999 >= anno_min and 2005 <= anno_max:
                fig_speed.add_vrect(x0=1998.5, x1=2005.5, fillcolor='#888', opacity=0.1,
                                    line_width=0, annotation_text='Revoked era',
                                    annotation_font=dict(size=9, color='#888'))
        for x0, x1, lbl in [(1914,1918,'WWI'),(1939,1947,'WWII')]:
            if x0 >= anno_min and x1 <= anno_max:
                fig_speed.add_vrect(x0=x0, x1=x1, fillcolor='#888', opacity=0.15,
                                    line_width=0, annotation_text=lbl,
                                    annotation_font=dict(size=9, color='#888'))
        fig_speed.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, serif', color='#1a1a1a'),
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, range=[anno_min, anno_max]),
            yaxis=dict(title='Average speed (km/h)', showgrid=True, gridcolor='#e8e4da'),
            legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center'),
        )
        st.plotly_chart(fig_speed, use_container_width=True)

        st.markdown(hr, unsafe_allow_html=True)

# ── SCATTER: ogni singola tappa come punto ──
        st.markdown("""
            <span class="st-section-label-s">· All Stages Ever ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                       color:#1a1a1a;font-size:18px;margin:2px 0 4px;">
                Every Stage in History — Distance by Type
            </h4>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                      font-style:italic;margin-bottom:8px;">
                Each dot = one stage. Color = type. The early Tour's epic 400+ km stages stand out dramatically.
            </p>
        """, unsafe_allow_html=True)

        df_scatter_all = df_coords_filt.copy()
        st.write("Colonne trovate nel dataset:", df_scatter_all.columns.tolist())        
       
        # 🪄 FIX: Trova automaticamente il nome corretto della colonna distanza
        dist_col = next((col for col in ['Distance', 'Distance (km)', 'distance', 'Distance '] if col in df_scatter_all.columns), None)
        
        if dist_col is None:
            st.warning("⚠️ Impossibile trovare la colonna della distanza nel dataset. Verifica che si chiami 'Distance' o 'Distance (km)'.")
        else:
            # Assicuriamoci che sia numerica per evitare altri errori
            df_scatter_all[dist_col] = pd.to_numeric(df_scatter_all[dist_col], errors='coerce')
            
            fig_scatter = go.Figure()
            for ttype in TYPE_ORDER:
                df_t = df_scatter_all[df_scatter_all['Type_group'] == ttype]
                if df_t.empty:
                    continue
                fig_scatter.add_trace(go.Scatter(
                    x=df_t['Year'], y=df_t[dist_col],
                    mode='markers',
                    name=ttype,
                    marker=dict(size=5, color=TYPE_COLORS.get(ttype,'#888'),
                                opacity=0.65, line=dict(width=0.3, color='white')),
                    hovertemplate=(
                        f'<b>{ttype}</b><br>'
                        'Year: %{x}<br>'
                        f'Distance: %{{y}} km<br>'
                        '%{customdata}<extra></extra>'
                    ),
                    customdata=df_t['Origin'].astype(str) + ' → ' + df_t['Destination'].astype(str),
                ))
            fig_scatter.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=380, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation='h', y=-0.12, x=0.5, xanchor='center', font=dict(size=10)),
                xaxis=dict(title='Year', showgrid=False, range=[anno_min, anno_max]),
                yaxis=dict(title='Stage distance (km)', showgrid=True, gridcolor='#e8e4da'),
            )
            # Annotazione tappe epiche
            epic = df_scatter_all[df_scatter_all[dist_col] > 450]
            if not epic.empty:
                top_epic = epic.nlargest(1, dist_col).iloc[0]
                fig_scatter.add_annotation(
                    x=top_epic['Year'], y=top_epic[dist_col],
                    text=f"{top_epic['Origin']} → {top_epic['Destination']}<br>{top_epic[dist_col]:.0f} km",
                    showarrow=True, arrowhead=2, arrowcolor='#888',
                    font=dict(size=9, color='#1a1a1a', family='Arial'),
                    bgcolor='rgba(255,204,0,0.85)', borderpad=4, ax=-60, ay=-20,
                )
            st.plotly_chart(fig_scatter, use_container_width=True)
    # ══════════════════════════════════════════════════════════
    # VISTA 2 — EDITION DETAILS (rinnovata, maglie preservate)
    # ══════════════════════════════════════════════════════════
    elif vista_corrente == "dettaglio":

        st.markdown("""
            <span class="st-section-label-s">· Edition Details ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 4px;">
                Route & Jerseys — Stage by Stage
            </h3>
        """, unsafe_allow_html=True)

        lista_anni = sorted([a for a in df_stage_h_filtered['Year'].unique() if a > 0], reverse=True)
        anno_scelto = st.selectbox("📅 Select an edition:", lista_anni)
        df_anno = df_stage_h_filtered[df_stage_h_filtered['Year'] == anno_scelto].sort_values('Stages').copy()

        if df_anno.empty:
            st.warning("No data for this edition.")
        else:
            # Winner parse
            df_anno['Vincitore_Clean'] = df_anno['Winner of stage'].apply(
                lambda x: str(x).split('(')[0].strip() if pd.notnull(x) else "N/A"
            )
            df_anno['Team_Stage'] = df_anno['Winner of stage'].str.extract(r'\((.*?)\)')
            df_anno['Team_Stage'] = df_anno['Team_Stage'].fillna('—')

            distanza_tot = df_anno['TotalTDFDistance'].iloc[0] if 'TotalTDFDistance' in df_anno.columns else "N/A"
            num_tappe = len(df_anno)
            vittorie_count = df_anno['Vincitore_Clean'].value_counts()
            top_rider = vittorie_count.index[0] if not vittorie_count.empty else "N/A"
            n_vittorie_top = vittorie_count.iloc[0] if not vittorie_count.empty else 0
            vincitore_finale = df_anno['Yellow Jersey'].dropna().iloc[-1] if df_anno['Yellow Jersey'].notna().any() else "N/A"
            cambi_maglia = max(0, (df_anno['Yellow Jersey'] != df_anno['Yellow Jersey'].shift()).sum() - 1) if df_anno['Yellow Jersey'].notna().any() else "N/A"

            # ── KPI HTML ──
            kpi_html = f"""
            <div style="display:flex;gap:12px;margin:16px 0 24px;flex-wrap:wrap;">
                <div style="flex:1;min-width:120px;background:#0d0d0d;border:1px solid #222;
                            border-top:3px solid #FFCC00;border-radius:4px;padding:14px 16px;
                            font-family:'Merriweather',serif;">
                    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                                color:#888;font-family:Arial;margin-bottom:6px;">Total Distance</div>
                    <div style="font-size:26px;font-weight:900;color:#f0ece4;">{distanza_tot} <span style="font-size:14px;color:#666;">km</span></div>
                </div>
                <div style="flex:1;min-width:120px;background:#0d0d0d;border:1px solid #222;
                            border-top:3px solid #FFCC00;border-radius:4px;padding:14px 16px;
                            font-family:'Merriweather',serif;">
                    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                                color:#888;font-family:Arial;margin-bottom:6px;">Stages</div>
                    <div style="font-size:26px;font-weight:900;color:#f0ece4;">{num_tappe}</div>
                </div>
                <div style="flex:1;min-width:120px;background:#0d0d0d;border:1px solid #222;
                            border-top:3px solid #4ECDC4;border-radius:4px;padding:14px 16px;
                            font-family:'Merriweather',serif;">
                    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                                color:#888;font-family:Arial;margin-bottom:6px;">Stage Cannibal</div>
                    <div style="font-size:16px;font-weight:900;color:#f0ece4;line-height:1.2;">{top_rider}</div>
                    <div style="font-size:11px;color:#4ECDC4;margin-top:2px;">{n_vittorie_top} wins</div>
                </div>
                <div style="flex:1;min-width:120px;background:#0d0d0d;border:1px solid #222;
                            border-top:3px solid #FFCC00;border-radius:4px;padding:14px 16px;
                            font-family:'Merriweather',serif;">
                    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                                color:#888;font-family:Arial;margin-bottom:6px;">Yellow Jersey Changes</div>
                    <div style="font-size:26px;font-weight:900;color:#FFCC00;">{cambi_maglia}</div>
                </div>
                <div style="flex:1;min-width:140px;background:#0d0d0d;border:1px solid #222;
                            border-top:3px solid #FFD700;border-radius:4px;padding:14px 16px;
                            font-family:'Merriweather',serif;">
                    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                                color:#888;font-family:Arial;margin-bottom:6px;">Final Winner</div>
                    <div style="font-size:15px;font-weight:900;color:#FFD700;line-height:1.2;">{vincitore_finale}</div>
                </div>
            </div>
            """
            st.markdown(kpi_html, unsafe_allow_html=True)
            st.markdown(hr, unsafe_allow_html=True)

            # ── JERSEY EVOLUTION (conservata e migliorata) ──
            st.markdown("""
                <span class="st-section-label-s">· Leadership Race ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                           color:#1a1a1a;font-size:18px;margin:4px 0 4px;">
                    Jersey Evolution — Stage by Stage
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                          font-style:italic;margin-bottom:12px;">
                    Select a jersey to see who led the race at each stage. 
                    Each icon marks a leadership change.
                </p>
            """, unsafe_allow_html=True)

            MAGLIE_CONFIG = {
                "🟡 Yellow": {
                    "col": "Yellow Jersey", "color": "#FFD700",
                    "img": "https://www.bobshop.com/media/92/7a/02/1776411535/11346-1_1.png?ts=1776411535",
                    "anno_intro": 1919,
                    "storia": "Introduced in 1919 to reward the overall GC leader. The color matches *L'Auto* newspaper's yellow paper stock — a living advertisement.",
                },
                "🟢 Green": {
                    "col": "Green jersey", "color": "#22c55e",
                    "img": "https://lh3.googleusercontent.com/d/1d1GLPgO6NHqt4bguSBdXjs8NowirbXAu",
                    "anno_intro": 1953,
                    "storia": "Created in 1953 for the 50th anniversary. It rewards the points classification — the sprinters' championship.",
                },
                "🔴 Polka-dot": {
                    "col": "Polka-dot jersey", "color": "#ef4444",
                    "img": "https://lh3.googleusercontent.com/d/1sOEebeyDAuhP0Mt6I5L4poKbahfv3xky",
                    "anno_intro": 1975,
                    "storia": "Mountains classification since 1933, but the iconic jersey only appeared in 1975 — introduced by Chocolat Poulain, whose packaging had a similar pattern.",
                },
                "⚪ White": {
                    "col": "White jersey", "color": "#d1d5db",
                    "img": "https://lh3.googleusercontent.com/d/1DAYUL8bk7eYxd83opOKJCkYT_afuKWdp",
                    "anno_intro": 1975,
                    "storia": "Best young rider (under 25) in the GC. Established in 1975.",
                },
            }

            scelta_maglia = st.radio("Select jersey:", list(MAGLIE_CONFIG.keys()), horizontal=True)
            cfg = MAGLIE_CONFIG[scelta_maglia]

            with st.expander(f"ℹ️ History of the {scelta_maglia.split()[-1]} Jersey"):
                st.markdown(cfg['storia'])

            st.markdown("<br>", unsafe_allow_html=True)

            col_sel = cfg['col']
            colore = cfg['color']
            img_maglia = cfg['img']
            anno_intro = cfg['anno_intro']

            if anno_scelto < anno_intro:
                st.markdown(f"""
                    <div style="background:#f5f0e6;border-left:4px solid #FFCC00;
                                padding:14px 18px;border-radius:3px;
                                font-family:'Merriweather',serif;color:#666;
                                font-style:italic;font-size:12px;">
                        🕰️ In <strong>{anno_scelto}</strong> this jersey did not exist yet.
                        {cfg['storia']}
                    </div>
                """, unsafe_allow_html=True)

            elif col_sel in df_anno.columns and df_anno[col_sel].notna().any():
                df_leader = df_anno.dropna(subset=[col_sel]).copy()
                ordine = df_leader[col_sel].drop_duplicates().tolist()

                fig_jersey = px.line(df_leader, x='Stages', y=col_sel)
                fig_jersey.update_traces(
                    line=dict(color=colore, width=4),
                    mode='lines+markers',
                    marker=dict(size=10, color=colore, line=dict(width=2, color='white')),
                )

                # Icona maglia su ogni cambio di leader
                prev = None
                
               # ── ICONE MAGLIA SU OGNI SINGOLO PALLINO ──
                for _, row in df_leader.iterrows():
                    # Rimosso il controllo del resto (%), ora inserisce l'immagine per ogni riga
                    fig_jersey.add_layout_image(dict(
                        source=img_maglia, xref="x", yref="y",
                        x=row['Stages'], y=row[col_sel],
                        sizex=1.4, sizey=0.85, 
                        xanchor="center", yanchor="middle", layer="above"
                    ))
                prev = row[col_sel]

                fig_jersey.update_layout(
                    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
                    font=dict(family='Merriweather, serif', color='#f0ece4'),
                    height=max(280, len(ordine) * 55 + 60),
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(title='Stage', tickmode='linear', dtick=1,
                               showgrid=True, gridcolor='#1e1e1e',
                               range=[df_leader['Stages'].min()-0.5, df_leader['Stages'].max()+0.5]),
                    yaxis=dict(title='', categoryorder='array',
                               categoryarray=ordine[::-1],
                               showgrid=True, gridcolor='#1e1e1e',
                               range=[-0.6, max(0.6, len(ordine)-0.4)]),
                    showlegend=False,
                )
                st.plotly_chart(fig_jersey, use_container_width=True)
            else:
                st.info(f"No data for the {scelta_maglia} jersey in {anno_scelto}.")

            st.markdown(hr, unsafe_allow_html=True)

            # ── BOTTOM ROW: stage wins bar + team donut + route table ──
            col_b1, col_b2, col_b3 = st.columns([1.1, 1, 1.4], gap="medium")

            with col_b1:
                st.markdown("""
                    <span class="st-section-label-s">· Stage Winners ·</span>
                    <h5 style="font-family:'Merriweather',serif;font-weight:900;
                               color:#1a1a1a;font-size:14px;margin:2px 0 6px;">
                        Most Wins This Edition
                    </h5>
                """, unsafe_allow_html=True)
                df_top_wins = vittorie_count.reset_index()
                df_top_wins.columns = ['Rider', 'Wins']
                df_top_wins = df_top_wins[df_top_wins['Rider'] != 'N/A'].head(8)

                fig_wins = px.bar(df_top_wins, y='Rider', x='Wins', orientation='h',
                                  color_discrete_sequence=['#FFCC00'])
                fig_wins.update_layout(
                    yaxis=dict(categoryorder='total ascending', title=''),
                    xaxis=dict(title='Stage wins', showgrid=True, gridcolor='#e8e4da'),
                    plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                    font=dict(family='Merriweather, serif', color='#1a1a1a'),
                    height=280, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                )
                st.plotly_chart(fig_wins, use_container_width=True)

            with col_b2:
                st.markdown("""
                    <span class="st-section-label-s">· Team Dominance ·</span>
                    <h5 style="font-family:'Merriweather',serif;font-weight:900;
                               color:#1a1a1a;font-size:14px;margin:2px 0 6px;">
                        Wins by Team
                    </h5>
                """, unsafe_allow_html=True)
                team_counts = df_anno['Team_Stage'].value_counts().reset_index()
                team_counts.columns = ['Team', 'Wins']
                team_counts = team_counts[team_counts['Team'] != '—'].head(8)

                fig_teams = px.pie(team_counts, values='Wins', names='Team', hole=0.55,
                                   color_discrete_sequence=['#FFCC00','#FF6B6B','#4ECDC4',
                                                            '#A29BFE','#FD79A8','#FDCB6E',
                                                            '#55efc4','#e17055'])
                fig_teams.update_traces(
                    textposition='inside', textinfo='label+value',
                    hovertemplate='<b>%{label}</b><br>%{value} stages<extra></extra>',
                    marker=dict(line=dict(color='#F4F1EA', width=2)),
                )
                fig_teams.update_layout(
                    showlegend=False, plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                    font=dict(family='Merriweather, serif', color='#1a1a1a'),
                    height=280, margin=dict(l=0, r=0, t=0, b=0),
                )
                st.plotly_chart(fig_teams, use_container_width=True)

            with col_b3:
                st.markdown("""
                    <span class="st-section-label-s">· Route ·</span>
                    <h5 style="font-family:'Merriweather',serif;font-weight:900;
                               color:#1a1a1a;font-size:14px;margin:2px 0 6px;">
                        Stage-by-Stage Itinerary
                    </h5>
                """, unsafe_allow_html=True)
                df_route = df_anno[['Stages','Start','End','Vincitore_Clean']].copy()
                df_route.columns = ['#','Start','Finish','Stage Winner']
                df_route['#'] = df_route['#'].apply(lambda x: int(x) if pd.notna(x) else '?')
                st.dataframe(df_route, use_container_width=True, hide_index=True, height=280)

    # ══════════════════════════════════════════════════════════
    # VISTA 3 — GEOGRAPHIC MAP (completamente rinnovata)
    # ══════════════════════════════════════════════════════════
    elif vista_corrente == "mappa":

        st.markdown("""
            <span class="st-section-label-s">· Geographic Archive ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:24px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 4px;">
                The Geography of Le Tour
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:12px;color:#666;
                      font-style:italic;margin-bottom:16px;">
                Select an edition to visualize its route. Cities are geocoded from a curated dictionary
                of the ~200 most historic Tour locations.
            </p>
        """, unsafe_allow_html=True)

        lista_anni_mappa = sorted([a for a in df_coords_all['Year'].dropna().unique()
                                   if a > 0], reverse=True)
        anno_mappa = st.selectbox("📅 Select edition:", lista_anni_mappa, key="select_mappa")

        df_mappa_anno = df_coords_all[df_coords_all['Year'] == anno_mappa].copy()

        # Geocoding con dizionario hardcoded
        def get_coords(city_name):
            if pd.isna(city_name):
                return None
            city_clean = str(city_name).strip()
            # Fix encoding
            city_clean = city_clean.replace('Ã©','é').replace('Ã¨','è').replace('Ã\xaa','ê')
            city_clean = city_clean.replace('Ã§','ç').replace('Ã®','î').replace('Ã´','ô')
            city_clean = city_clean.replace('Ã»','û').replace('Ã ','à').replace('Ã¹','ù')
            city_clean = city_clean.replace('Ã«','ë').replace('Ã¯','ï').replace('DÃ¼sseldorf','Düsseldorf')
            # Lookup
            if city_clean in CITY_COORDS:
                return CITY_COORDS[city_clean]
            # Partial match
            for k, v in CITY_COORDS.items():
                if city_clean.lower() in k.lower() or k.lower() in city_clean.lower():
                    return v
            return None

        # Aggiungi coordinate
        df_mappa_anno['start_coords'] = df_mappa_anno['Origin'].apply(get_coords)
        df_mappa_anno['end_coords'] = df_mappa_anno['Destination'].apply(get_coords)
        df_mappa_anno = df_mappa_anno.dropna(subset=['start_coords','end_coords'])
        df_mappa_anno['start_lat'] = df_mappa_anno['start_coords'].apply(lambda x: x[0])
        df_mappa_anno['start_lon'] = df_mappa_anno['start_coords'].apply(lambda x: x[1])
        df_mappa_anno['end_lat']   = df_mappa_anno['end_coords'].apply(lambda x: x[0])
        df_mappa_anno['end_lon']   = df_mappa_anno['end_coords'].apply(lambda x: x[1])

        n_stages_found = len(df_mappa_anno)
        n_stages_total = len(df_coords_all[df_coords_all['Year'] == anno_mappa])

        coverage = int(n_stages_found / max(n_stages_total, 1) * 100)

        # Banner copertura
        banner_color = '#22c55e' if coverage >= 70 else '#FFCC00' if coverage >= 40 else '#FF6B6B'
        st.markdown(f"""
            <div style="background:#111;border:1px solid #2a2a2a;border-left:4px solid {banner_color};
                        padding:10px 16px;border-radius:3px;margin-bottom:16px;
                        font-family:'Merriweather',serif;display:flex;align-items:center;gap:12px;">
                <span style="font-size:18px;font-weight:900;color:{banner_color};">{coverage}%</span>
                <span style="font-size:11px;color:#888;">
                    {n_stages_found} of {n_stages_total} stages geocoded from the Tour's 
                    historic city dictionary · {int(anno_mappa)} edition
                </span>
            </div>
        """, unsafe_allow_html=True)

        if n_stages_found == 0:
            st.markdown("""
                <div style="background:#f5f0e6;border-left:4px solid #c8bfad;padding:14px 18px;
                            border-radius:3px;font-family:'Merriweather',serif;color:#666;
                            font-style:italic;font-size:12px;">
                    No stages could be geocoded for this edition. The cities may use historical
                    spellings not yet in the dictionary.
                </div>
            """, unsafe_allow_html=True)
        else:
            # Mappa Plotly con linee tappa
            fig_map = go.Figure()

            # Linee di percorso colorate per tipo tappa
            for _, row in df_mappa_anno.iterrows():
                ttype = TYPE_MAP.get(row.get('Type','').strip(), 'Other')
                color = TYPE_COLORS.get(ttype, '#888')
                stage_num = row.get('Stage', '?')
                origin = row.get('Origin','?')
                dest = row.get('Destination','?')
                dist = row.get('Distance', '?')
                winner = row.get('Winner','?')

                fig_map.add_trace(go.Scattergeo(
                    lon=[row['start_lon'], row['end_lon']],
                    lat=[row['start_lat'], row['end_lat']],
                    mode='lines',
                    line=dict(width=3, color=color),
                    opacity=0.85,
                    showlegend=False,
                    hovertemplate=(
                        f"<b>Stage {stage_num}</b> — {ttype}<br>"
                        f"{origin} → {dest}<br>"
                        f"Distance: {dist} km<br>"
                        f"Winner: {winner}<extra></extra>"
                    ),
                ))

            # Punti di partenza (cerchi)
            starts = df_mappa_anno.drop_duplicates(subset=['start_lat','start_lon'])
            fig_map.add_trace(go.Scattergeo(
                lon=starts['start_lon'], lat=starts['start_lat'],
                mode='markers',
                marker=dict(size=7, color='#1a1a1a', opacity=0.7,
                            line=dict(width=1.5, color='white')),
                showlegend=False,
                hovertemplate='<b>%{customdata}</b><extra></extra>',
                customdata=starts['Origin'],
            ))

            # Punto finale (stella) — ultimo arrivo
            last = df_mappa_anno.iloc[-1]
            fig_map.add_trace(go.Scattergeo(
                lon=[last['end_lon']], lat=[last['end_lat']],
                mode='markers+text',
                marker=dict(size=16, color='#FFCC00', symbol='star',
                            line=dict(width=2, color='#1a1a1a')),
                text=[last['Destination']],
                textposition='top center',
                textfont=dict(size=10, color='#1a1a1a', family='Arial'),
                showlegend=False,
                hovertemplate=f"<b>Final Stage Finish</b><br>{last['Destination']}<extra></extra>",
            ))

            # Legenda manuale per tipo tappa
            for ttype, color in TYPE_COLORS.items():
                if ttype == 'Other':
                    continue
                df_t = df_mappa_anno[df_mappa_anno['Type_group'] == ttype]
                if df_t.empty:
                    continue
                fig_map.add_trace(go.Scattergeo(
                    lon=[None], lat=[None],
                    mode='lines',
                    line=dict(width=3, color=color),
                    name=f"{ttype} ({len(df_t)})",
                    showlegend=True,
                ))

            fig_map.update_geos(
                showcoastlines=True, coastlinecolor='#c8bfad', coastlinewidth=1,
                showland=True, landcolor='#F4F1EA',
                showocean=True, oceancolor='#ddeeff',
                showframe=False,
                showborder=True, bordercolor='#e8e4da',
                showcountries=True, countrycolor='#e8e4da',
                projection_type='mercator',
                center=dict(lat=46.5, lon=4.0),
                lataxis_range=[40, 55],
                lonaxis_range=[-6, 18],
            )
            fig_map.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=560, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(
                    orientation='v', x=0.01, y=0.99,
                    bgcolor='rgba(244,241,234,0.92)',
                    bordercolor='#c8bfad', borderwidth=1,
                    font=dict(size=10),
                ),
                title=dict(
                    text=f"<b>{int(anno_mappa)} Tour de France</b> — {n_stages_found} stages mapped",
                    font=dict(size=13, family='Merriweather, serif', color='#1a1a1a'),
                    x=0.01, xanchor='left',
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)

            st.markdown(hr, unsafe_allow_html=True)

            # ── HEATMAP CITTÀ più visitate nella storia ──
            st.markdown("""
                <span class="st-section-label-s">· Most Historic Cities ·</span>
                <h4 style="font-family:'Merriweather',Georgia,serif;font-weight:900;
                           color:#1a1a1a;font-size:18px;margin:4px 0 4px;">
                    The Tour's Most Visited Cities — All Time
                </h4>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                          font-style:italic;margin-bottom:8px;">
                    Combined count of starts and finishes in each city across all editions.
                </p>
            """, unsafe_allow_html=True)

            all_cities_hist = pd.concat([
                df_coords_all[['Origin']].rename(columns={'Origin':'city'}),
                df_coords_all[['Destination']].rename(columns={'Destination':'city'}),
            ])
            # Normalizza encoding
            all_cities_hist['city'] = all_cities_hist['city'].str.strip()
            city_counts = all_cities_hist['city'].value_counts().head(20).reset_index()
            city_counts.columns = ['City','Appearances']

            fig_cities = px.bar(
                city_counts, y='City', x='Appearances', orientation='h',
                color='Appearances',
                color_continuous_scale=[[0,'#FFF3CD'],[0.4,'#FFCC00'],[1,'#1a1a1a']],
                labels={'Appearances': 'Starts + Finishes'},
            )
            fig_cities.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=480, margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(categoryorder='total ascending', title=''),
                xaxis=dict(showgrid=True, gridcolor='#e8e4da'),
                coloraxis_showscale=False,
                showlegend=False,
            )
            # Annotazione Parigi
            paris_row = city_counts[city_counts['City']=='Paris']
            if not paris_row.empty:
                fig_cities.add_annotation(
                    x=paris_row['Appearances'].values[0], y='Paris',
                    text="The eternal finish line",
                    showarrow=True, arrowhead=2, arrowcolor='#888',
                    font=dict(size=9, color='#1a1a1a', family='Arial'),
                    bgcolor='rgba(255,204,0,0.85)', borderpad=4, ax=-80, ay=0,
                )
            st.plotly_chart(fig_cities, use_container_width=True)

# ==========================================
# SEZIONE TEAMS — CODICE COMPLETO RIDISEGNATO
# Sostituisce: elif st.session_state.pagina_corrente == "teams":
# ==========================================

elif st.session_state.pagina_corrente == "teams":

    import unicodedata, re

    # ──────────────────────────────────────────────────────────
    # 0. DIZIONARIO RAGGRUPPAMENTO SQUADRE
    # ──────────────────────────────────────────────────────────
    TEAM_GROUPS = {
        # ── MODERN WORLDTOUR ──
        "AG2R (2000–present)": ['AG2R PREVOYANCE','AG2R LA MONDIALE','AG2R-LA MONDIALE','AG2R CITROEN TEAM','DECATHLON AG2R LA MONDIALE TEAM'],
        "Astana (2006–present)": ['ASTANA','PRO TEAM ASTANA','ASTANA PRO TEAM','ASTANA - PREMIER TECH','ASTANA - QAZAQSTAN TEAM','ASTANA QAZAQSTAN TEAM','XDS ASTANA TEAM'],
        "Bahrain (2017–present)": ['BAHRAIN - MERIDA','BAHRAIN - MCLAREN','BAHRAIN VICTORIOUS'],
        "Bora – Hansgrohe (2015–present)": ['BORA-ARGON 18','BORA - HANSGROHE','RED BULL - BORA - HANSGROHE'],
        "Bouygues Telecom (2000–2010)": ['BOUYGUES TELECOM','BBOX BOUYGUES TELECOM'],
        "Cofidis (1997–present)": ['COFIDIS','COFIDIS . CREDIT PAR TELEPHONE','COFIDIS . LE CREDIT PAR TELEPHONE','COFIDIS CREDIT PAR TELEPHONE','COFIDIS LE CREDIT EN LIGNE','COFIDIS, SOLUTIONS CREDITS','COFIDIS, SOLUTIONS CRÉDITS','COFIDIS.LE CREDIT PAR TELEPHONE'],
        "DSM / Sunweb (2015–present)": ['TEAM SUNWEB','TEAM DSM','TEAM DSM - FIRMENICH','TEAM DSM-FIRMENICH POSTNL','TEAM PICNIC POSTNL'],
        "EF Education (2012–present)": ['GARMIN CHIPOTLE','GARMIN - SLIPSTREAM','GARMIN - TRANSITIONS','GARMIN - SHARP','GARMIN-SHARP','TEAM GARMIN - CERVELO','CANNONDALE','CANNONDALE DRAPAC TEAM','CANNONDALE DRAPAC PROFESSIONAL CYCLING TEAM','TEAM CANNONDALE-GARMIN','EF PRO CYCLING','EF EDUCATION FIRST','EF EDUCATION - NIPPO','EF EDUCATION - EASYPOST','TEAM EF EDUCATION FIRST - DRAPAC P/B CANNONDALE'],
        "Euskaltel-Euskadi (1994–2013)": ['EUSKALTEL - EUSKADI'],
        "Groupama–FDJ (1997–present)": ['FRANCAISE DES JEUX','LA FRANCAISE DES JEUX','FDJ','FDJ.FR','FDJEUX.COM','FDJeux.com','FDJ-BIGMAT','GROUPAMA - FDJ','GROUPAMA-FDJ'],
        "Ineos / Sky (2010–present)": ['SKY PRO CYCLING','SKY PROCYCLING','TEAM SKY','TEAM INEOS','INEOS GRENADIERS'],
        "Intermarché–Wanty (2013–present)": ['WANTY - GROUPE GOBERT','WANTY - GOBERT CYCLING TEAM','INTERMARCHÉ - WANTY','INTERMARCHÉ - WANTY - GOBERT MATERIAUX','INTERMARCHÉ - CIRCUS - WANTY','INTERMARCHE - WANTY - GOBERT MATERIAUX'],
        "Israel Premier Tech (2020–present)": ['ISRAEL START-UP NATION','ISRAEL - PREMIER TECH','ISRAEL-PREMIER TECH'],
        "Jumbo-Visma / Visma (2016–present)": ['TEAM LOTTO NL - JUMBO','TEAM JUMBO - VISMA','JUMBO - VISMA','JUMBO-VISMA','TEAM VISMA | LEASE A BIKE'],
        "Katusha (2009–2018)": ['KATUSHA TEAM','TEAM KATUSHA','TEAM KATUSHA ALPECIN'],
        "Lidl-Trek (2012–present)": ['TREK FACTORY RACING','TREK - SEGAFREDO','LIDL - TREK','LIDL-TREK'],
        "Lotto (1985–present)": ['LOTTO','LOTTO - ADECCO','LOTTO - DOMO','LOTTO - MOBISTAR','LOTTO-MOBISTAR-ISOGLASS','LOTTO-ISOGLASS','LOTTO-BELGACOM','LOTTO-BELISOL','LOTTO-BELISOL TEAM','LOTTO-SUPERCLUB','LOTTO-SUPERCLUB-MBK','LOTTO-EDDY MERCKX-CAMPAGNOLO','LOTTO-VETTA-CALÒ','DAVITAMON - LOTTO','PREDICTOR - LOTTO','SILENCE - LOTTO','OMEGA PHARMA - LOTTO','LOTTO SOUDAL','LOTTO-SOUDAL','LOTTO DSTNY'],
        "Mitchelton-Scott / Jayco (2012–present)": ['ORICA GREENEDGE','ORICA - SCOTT','ORICA-BIKEEXCHANGE','MITCHELTON - SCOTT','TEAM BIKEEXCHANGE','TEAM BIKEEXCHANGE-JAYCO','TEAM JAYCO ALULA'],
        "Movistar (1980–present)": ['REYNOLDS','REYNOLDS-BANESTO','REYNOLDS-PAPEL ALUMINIO','REYNOLDS-SEUR-SADA','REYNOLDS-TS BATTERIES','BANESTO','IBANESTO.COM','ILLES BALEARS-CAISSE D EPARGNE',"CAISSE D'EPARGNE-ILLES BALEARS","CAISSE D'EPARGNE","CAISSE Dâ€™EPARGNE",'ILLES BALEARS - B. SANTANDER','MOVISTAR TEAM'],
        "NTT / Dimension Data (2015–2021)": ['TEAM DIMENSION DATA','MTN-QHUBEKA','TEAM QHUBEKA NEXTHASH','NTT PRO CYCLING TEAM'],
        "ONCE (1989–2003)": ['ONCE','ONCE - EROSKI','O.N.C.E - DEUTSCHE BANK','O.N.C.E. - EROSKI'],
        "Quick-Step (1999–present)": ['MAPEI - QUICK STEP','MAPEI-CLAS','MAPEI-GB','MAPEI - BRICOBI','QUICK STEP','QUICK STEP - DAVITAMON','QUICK STEP - INNERGETIC','QUICK STEP CYCLING TEAM','OMEGA PHARMA-QUICK STEP','ETIXX-QUICK STEP','DECEUNINCK - QUICK - STEP','QUICK - STEP FLOORS','QUICK-STEP ALPHA VINYL TEAM','SOUDAL QUICK-STEP'],
        "Rabobank / Blanco (1996–2013)": ['RABOBANK','RABOBANK CYCLING TEAM','BELKIN PRO CYCLING'],
        "T-Mobile / HTC (1999–2011)": ['TEAM DEUTSCHE TELEKOM','T-MOBILE TEAM','TEAM TELEKOM','TEAM COLUMBIA','TEAM COLUMBIA - HTC','TEAM HTC - COLUMBIA','HTC - HIGHROAD'],
        "Tinkoff / Saxo (2008–2016)": ['TEAM SAXO BANK','TEAM CSC SAXO BANK','SAXO BANK SUNGARD','TEAM SAXO BANK-TINKOFF BANK','TEAM SAXO-TINKOFF','TINKOFF-SAXO','TINKOFF'],
        "TotalEnergies (2004–present)": ['BONJOUR','BRIOCHES LA BOULANGERE','AGRITUBEL','BRETAGNE - SECHE ENVIRONNEMENT','SAUR-SOJASUN','SOJASUN','DIRECT ENERGIE','TOTAL DIRECT ENERGIE','TOTALENERGIES'],
        "UAE Team Emirates (2017–present)": ['UAE TEAM EMIRATES','UAE TEAM EMIRATES XRG'],
        "Uno-X (2021–present)": ['UNO-X PRO CYCLING TEAM','UNO-X MOBILITY'],
        "US Postal / Discovery (1996–2007)": ['U.S POSTAL SERVICE','US POSTAL SERVICE','US POSTAL - BERRY FLOOR','DISCOVERY CHANNEL TEAM'],
        # ── SQUADRE STORICHE ──
        "Alcyon (1906–1931)": ['ALCYON','ALCYON-DUNLOP','ALCYON-SOLY'],
        "Alpecin (2014–present)": ['TEAM GIANT-SHIMANO','TEAM GIANT-ALPECIN','TEAM ARGOS-SHIMANO','ALPECIN - FENIX','ALPECIN - DECEUNINCK','ALPECIN-DECEUNINCK'],
        "Automoto (1920–1932)": ['AUTOMOTO','AUTOMOTO-CONTINENTAL','AUTOMOTO-HUTCHINSON'],
        "B&B Hotels / Arkéa (2016–present)": ['FORTUNEO - VITAL CONCEPT','TEAM FORTUNEO - SAMSIC','TEAM FORTUNEO - OSCARO','B&B HOTELS - VITAL CONCEPT P / B KTM','B&B HOTELS - KTM','B&B HOTELS P/B KTM','ARKEA-B&B HOTELS','TEAM ARKEA - SAMSIC'],
        "Bianchi (1949–2005)": ['BIANCHI','BIANCHI-CAMPAGNOLO','BIANCHI-FAEMA','TEAM BIANCHI'],
        "BMC Racing (2007–2018)": ['BMC RACING TEAM'],
        "Carrera (1984–1995)": ['CARRERA JEANS','CARRERA JEANS-INOXPRAN','CARRERA JEANS-TASSONI','CARRERA JEANS-VAGABOND','CARRERA-INOXPRAN','CARRERA-TASSONI','CARRERA BLUE JEANS-LONGONI'],
        "Castorama (1990–1994)": ['CASTORAMA','CASTORAMA-RALEIGH'],
        "CSC / Riis (2000–2007)": ['TEAM CSC','CSC - TISCALI','TEAM CSC TISCALI'],
        "Faema (1956–1970)": ['FAEMA','FAEMA-FAEMINO','FAEMA-FLANDRIA','FAEMA-FLANDRIA-CLEMENT'],
        "Fassa Bortolo (1997–2005)": ['FASSA BORTOLO'],
        "Festina (1990–2001)": ['FESTINA','FESTINA WATCHES','FESTINA Watches','FESTINA-ANDORRA'],
        "Flandria (1959–1979)": ['FLANDRIA-CA VA SEUL','FLANDRIA-CARPENTER-CONFORTLUXE','FLANDRIA-DE CLERCK-KRUGER','FLANDRIA-ROMEO','FLANDRIA-SHIMANO-MERLIN PLAGE','FLANDRIA-VELDA-VLEESBDRIJF','MARS-FLANDRIA','BEAULIEU-FLANDRIA'],
        "Gan / Crédit Agricole (1989–2008)": ['GAN','GAN-MERCIER','GAN-MERCIER-HUTCHINSON','CREDIT AGRICOLE'],
        "Gerolsteiner (2000–2008)": ['GEROLSTEINER'],
        "Gitane / Renault (1955–1986)": ['GITANE','GITANE-CAMPAGNOLO','GITANE-FRIGECREME','FORD-FRANCE-GITANE-DUNLOP','RENAULT-GITANE','RENAULT-ELF-GITANE','RENAULT-ELF'],
        "KAS (1960–1988)": ['KAS','KAS-CAMPAGNOLO','KAS-MAVIC','KAS-KASKOL','KAS-MIKO-MAVIC','KAS-CANAL 10-MAVIC'],
        "Kelme (1984–2003)": ['KELME','KELME - COSTA BLANCA','KELME-ARTIACH-COSTA BLANCA','KELME-AVIANCA','KELME-COSTA BLANCA-EUROSPORT'],
        "La Vie Claire (1984–1987)": ['LA VIE CLAIRE-TERRAILLON','LA VIE CLAIRE-WONDER-RADAR','TOSHIBA-LOOK-LA VIE CLAIRE','TOSHIBA'],
        "La Redoute (1977–1988)": ['LA REDOUTE','LA REDOUTE-MOTOBECANE'],
        "Lampre (1995–2016)": ['LAMPRE','LAMPRE - CAFFITA','LAMPRE - DAIKIN','LAMPRE - FARNESE','LAMPRE - ISD','LAMPRE - MERIDA','LAMPRE - N.G.C','LAMPRE-FONDITAL','LAMPRE-PANARIA','LAMPRE-POLTI'],
        "Legnano (1908–1956)": ['LEGNANO','LEGNANO-PIRELLI'],
        "Liberty Seguros / Würth (2003–2006)": ['LIBERTY SEGUROS','LIBERTY SEGUROS - WÜRTH TEAM'],
        "Liquigas (2005–2012)": ['LIQUIGAS','LIQUIGAS - BIANCHI','LIQUIGAS-CANNONDALE','LIQUIGAS-DOIMO'],
        "Mapei (1994–2002)": ['MAPEI-CLAS','MAPEI-GB','MAPEI - BRICOBI'],
        "Mercatone Uno (1994–2002)": ['MERCATONE UNO-MEDEGHINI','MERCATONE UNO-SAECO','MERCATONE UNO - BIANCHI','MERCATONE UNO - ALBACOM','MERCATONE-UNO'],
        "Mercier (1935–1984)": ['MERCIER-BP-HUTCHINSON','GAN-MERCIER','GAN-MERCIER-HUTCHINSON','FAGOR-MERCIER','FAGOR-MERCIER-HUTCHINSON','MIKO-MERCIER','MIKO-MERCIER-VIVAGEL'],
        "Molteni (1958–1976)": ['MOLTENI','MOLTENI-IGNIS','I.B.A.C-MOLTENI'],
        "Motorola / 7-Eleven (1985–1996)": ['MOTOROLA','SEVEN ELEVEN-AMERICAN AIRLINES','SEVEN ELEVEN-HOONVED'],
        "Panasonic / PDM (1984–1992)": ['PANASONIC','PANASONIC-ISOSTAR','PANASONIC-RALEIGH','PANASONIC-SPORTLIFE','PDM','PDM-CONCORDE','P.D.M'],
        "Pelforth / Sauvage (1960–1971)": ['PELFORTH-SAUVAGE-LEJEUNE','PELFORTH-SAUVAGE-LEJEUNE-WOLBER'],
        "Peugeot (1954–1991)": ['PEUGEOT','PEUGEOT-BP','PEUGEOT-BP-DUNLOP','PEUGEOT-BP-ENGLEBERT','PEUGEOT-BP-MICHELIN','PEUGEOT-ESSO','PEUGEOT-ESSO-MICHELIN','PEUGEOT-SHELL','PEUGEOT-SHELL-MICHELIN','PEUGEOT-WOLBER','Z-PEUGEOT','Z'],
        "Phonak (2002–2006)": ['PHONAK HEARING SYSTEMS'],
        "RadioShack / Trek (2010–2015)": ['TEAM RADIOSHACK','RADIOSHACK-NISSAN','RADIOSHACK LEOPARD','TEAM LEOPARD-TREK'],
        "RMO (1986–1993)": ['RMO- MAVIC-LIBERIA','RMO-LIBERIA-MAVIC','RMO-MAVIC','RMO-MERAL-MAVIC'],
        "Saeco (1990–2003)": ['SAECO','SAECO - CANNONDALE','SAECO - MACCHINE PER CAFFE','SAECO MACCHINE DA CAFFE - CANNONDALE','SAECO - VALLI & VALLI','SAECO-ESTRO'],
        "Salvarani (1961–1972)": ['SALVARANI'],
        "Saunier Duval (2000–2008)": ['SAUNIER DUVAL - PRODIR'],
        "Système U / Castorama (1986–1994)": ['SYSTEME U','SUPER U','CASTORAMA','CASTORAMA-RALEIGH'],
        "Team Europcar (2011–2015)": ['TEAM EUROPCAR'],
        "Team Milram (2006–2010)": ['TEAM MILRAM'],
        "Team Polti (1993–1999)": ['TEAM POLTI','Team POLTI'],
        "Teka (1977–1988)": ['TEKA'],
        "TI-Raleigh (1973–1983)": ['TI-RALEIGH','TI-RALEIGH-CAMPAGNOLO','TI-RALEIGH-CREDA','TI-RALEIGH-McGREGOR'],
        "TVM (1987–1999)": ['TVM','TVM-BISON','TVM-POLIS DIRECT'],
        # ── NAZIONALI / REGIONALI ──
        "France (national team)": ['FRANCE','FRANCE A','FRANCE B','FRANCE C','France'],
        "Belgique (national team)": ['BELGIQUE','BELGIQUE A','BELGIQUE B','Belgique'],
        "Italie (national team)": ['ITALIE','ITALIA','ITALIE B','Italie'],
        "Espagne (national team)": ['ESPAGNE','ESPAGNE-LUXEMBOURG','ESPANA','Espagne'],
        "Suisse (national team)": ['SUISSE','SUISSE-ALLEMAGNE','SUISSE-ESPAGNE','SUISSE-LUXEMBOURG','SUISSE/LUXEMBOURG','Suisse','HELVETIA','HELVETIA-COMMODORE','HELVETIA-LA SUISSE'],
        "Pays-Bas (national team)": ['PAYS-BAS','PAYS BAS','PAYS BAS-LUXEMBOURG','NEDERLAND','PAYS-BAS/LUXEMBOURG','PAYS-BAS/ETRANGERS DE FRANCE','Hollande'],
        "Allemagne (national team)": ['ALLEMAGNE','ALLEMAGNE-AUTRICHE','DEUTSCHLAND'],
        "Touristes-Routiers (1924–1937)": ['TOURISTES ROUTIERS','TOURISTES-ROUTIERS'],
        "Régions françaises": ['OUEST','OUEST-NORD','OUEST-SUD OUEST','Ouest','NORD','NORD EST-CENTRE','NORD-EST','SUD-EST','Sud-Est','SUD-OUEST','Sud-Ouest','ILE DE FRANCE','ILE DE FRANCE-NORD EST','Ile de France','CENTRE-MIDI','CENTRE-SUD OUEST','NORMANDIE','CHAMPAGNE','PARIS','PARIS-NORD','PARIS-NORD EST'],
        "Isolés / Inconnus": ['ISOLES','INCONNU','INCOGNUE','INTERNATIONAUX','INTERNATIONONS'],
    }

    # Inverso: alias -> group name
    ALIAS_TO_GROUP = {}
    for gname, aliases in TEAM_GROUPS.items():
        for alias in aliases:
            ALIAS_TO_GROUP[alias] = gname

    def get_group(team_name):
        return ALIAS_TO_GROUP.get(str(team_name).strip(), str(team_name).strip())

    # ──────────────────────────────────────────────────────────
    # 1. PREPARAZIONE DATI
    # ──────────────────────────────────────────────────────────
    df_storico['Rank_Num'] = pd.to_numeric(df_storico['Rank'], errors='coerce')
    df_storico['Team_Group'] = df_storico['Team'].apply(get_group)

    anni_revocati = list(range(1999, 2006)) + [2006]

    def pulisci_nome(nome):
        if pd.isna(nome): return ""
        s = re.sub(r'\(.*?\)', '', str(nome))
        s = re.sub(r'[^a-zA-Z\s]', '', s).lower().strip()
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return " ".join(sorted(s.split()))

    df_stage_h_c = df_stage_h.copy()
    df_stage_h_c['Winner_Clean']  = df_stage_h_c['Winner of stage'].apply(pulisci_nome)
    df_stage_h_c['Yellow_Clean']  = df_stage_h_c['Yellow Jersey'].apply(pulisci_nome)
    df_stage_h_c['Green_Clean']   = df_stage_h_c['Green jersey'].apply(pulisci_nome)
    df_stage_h_c['Pois_Clean']    = df_stage_h_c['Polka-dot jersey'].apply(pulisci_nome)

    df_storico_clean = df_storico[['Year','Rider','Team','Team_Group']].drop_duplicates().copy()
    df_storico_clean['Rider_Clean'] = df_storico_clean['Rider'].apply(pulisci_nome)

    # ──────────────────────────────────────────────────────────
    # 2. CSS
    # ──────────────────────────────────────────────────────────
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

        .teams-masthead {
            border-top: 5px solid #1a1a1a; border-bottom: 2px solid #1a1a1a;
            padding: 12px 0 8px; text-align: center; margin-bottom: 24px;
        }
        .t-rule { border: none; border-top: 1px solid #c8bfad; margin: 26px 0; }
        .t-section-label {
            font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
            color: #888; font-family: Arial, sans-serif; display: block; margin-bottom: 4px;
        }
        div[data-testid="stSelectbox"] {
            background-color: transparent !important;
        }
        div[data-testid="stSelectbox"] label p {
            color: #1a1a1a !important; font-family: 'Merriweather', serif !important; font-weight: 700 !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #F4F1EA !important; color: #1a1a1a !important;
            border: 1px solid #c8bfad !important; border-radius: 3px !important;
        }
        div[data-baseweb="popover"] ul, ul[data-baseweb="menu"], ul[role="listbox"] { background-color: #111 !important; }
        div[data-baseweb="popover"] li, ul[data-baseweb="menu"] li, ul[role="listbox"] li { color: #fff !important; background-color: #111 !important; }
        div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover { background-color: #2a2a2a !important; }
        ul[role="listbox"] li[aria-selected="true"] { color: #FFCC00 !important; }
        div[data-testid="stPlotlyChart"] > div {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        div[data-testid="column"],
        div[data-testid="stVerticalBlock"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # ──────────────────────────────────────────────────────────
    # 3. TESTATA
    # ──────────────────────────────────────────────────────────
    st.markdown("""
        <div class="teams-masthead">
            <span style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#888;font-family:Arial,sans-serif;">
                Teams Archive · 1903 to Today · 100+ Franchises
            </span>
            <h1 style="font-family:'Merriweather',Georgia,serif;font-size:42px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 2px;letter-spacing:-1px;">
                The Teams of Le Tour
            </h1>
            <div style="font-size:10px;letter-spacing:2px;color:#888;font-family:Arial,sans-serif;
                        border-top:1px solid #c8bfad;padding-top:6px;margin-top:6px;">
                Dynasties · Rosters · Palmarès · Stage Wins
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # 4. SELECTBOX GRUPPI
    # ──────────────────────────────────────────────────────────
    all_groups_in_data = sorted(df_storico['Team_Group'].dropna().unique())
    # Aggiungi anche le famiglie del dizionario che hanno alias nel dataset
    groups_with_data = [g for g in TEAM_GROUPS.keys()
                        if df_storico['Team'].isin(TEAM_GROUPS[g]).any()]
    # Unisci squadre singole (non mappate) che hanno dati
    all_selectable = sorted(set(groups_with_data) | set(all_groups_in_data))

    default_idx = all_selectable.index("Ineos / Sky (2010–present)") if "Ineos / Sky (2010–present)" in all_selectable else 0
    team_scelto = st.selectbox("🚴 Select a team or franchise:", all_selectable, index=default_idx)

    # Recupera alias per il gruppo selezionato
    aliases_gruppo = TEAM_GROUPS.get(team_scelto, [team_scelto])
    df_team = df_storico[df_storico['Team'].isin(aliases_gruppo)].copy()
    df_team['Rank_Num'] = pd.to_numeric(df_team['Rank'], errors='coerce')

    # Banner alias
    if len(aliases_gruppo) > 1:
        alias_list = " · ".join([f"<em>{a.title()}</em>" for a in aliases_gruppo if df_storico['Team'].eq(a).any()])
        st.markdown(f"""
            <div style="background:#111;border:1px solid #2a2a2a;border-left:4px solid #FFCC00;
                        padding:10px 16px;border-radius:3px;margin-bottom:20px;
                        font-family:'Merriweather',serif;font-size:11px;color:#888;">
                <strong style="color:#FFCC00;">Franchise includes:</strong> {alias_list}
            </div>
        """, unsafe_allow_html=True)

    if df_team.empty:
        st.warning("No data available for this selection.")
    else:
        hr = "<hr class='t-rule'>"

        # ── KPI ──
        vittorie_gc = len(df_team[(df_team['Rank_Num'] == 1) & (~df_team['Year'].isin(anni_revocati))])
        miglior_rank = int(df_team['Rank_Num'].min()) if not df_team['Rank_Num'].isna().all() else "N/A"
        partecipazioni = df_team['Year'].nunique()
        anno_debutto = int(df_team['Year'].min())
        anno_ultimo  = int(df_team['Year'].max())
        top10_count  = len(df_team[df_team['Rank_Num'] <= 10])

        kpi_html = f"""
        <div style="display:flex;gap:12px;margin:16px 0 24px;flex-wrap:wrap;">
            <div style="flex:1;min-width:110px;background:#0d0d0d;border:1px solid #222;
                        border-top:3px solid #FFCC00;border-radius:4px;padding:14px 16px;
                        font-family:'Merriweather',serif;">
                <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial;margin-bottom:6px;">GC Wins</div>
                <div style="font-size:30px;font-weight:900;color:#FFCC00;">{vittorie_gc}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#0d0d0d;border:1px solid #222;
                        border-top:3px solid #f0ece4;border-radius:4px;padding:14px 16px;
                        font-family:'Merriweather',serif;">
                <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial;margin-bottom:6px;">Best GC Result</div>
                <div style="font-size:30px;font-weight:900;color:#f0ece4;">#{miglior_rank}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#0d0d0d;border:1px solid #222;
                        border-top:3px solid #4ECDC4;border-radius:4px;padding:14px 16px;
                        font-family:'Merriweather',serif;">
                <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial;margin-bottom:6px;">Editions</div>
                <div style="font-size:30px;font-weight:900;color:#4ECDC4;">{partecipazioni}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#0d0d0d;border:1px solid #222;
                        border-top:3px solid #FF6B6B;border-radius:4px;padding:14px 16px;
                        font-family:'Merriweather',serif;">
                <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial;margin-bottom:6px;">Top-10 Finishes</div>
                <div style="font-size:30px;font-weight:900;color:#FF6B6B;">{top10_count}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#0d0d0d;border:1px solid #222;
                        border-top:3px solid #888;border-radius:4px;padding:14px 16px;
                        font-family:'Merriweather',serif;">
                <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;font-family:Arial;margin-bottom:6px;">Active Period</div>
                <div style="font-size:20px;font-weight:900;color:#f0ece4;">{anno_debutto}–{anno_ultimo}</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        st.markdown(hr, unsafe_allow_html=True)

        # ──────────────────────────────────────────────────────
        # SEZIONE A: DYNASTY TIMELINE
        # ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 0 16px;">
            <span class="t-section-label">· Season by Season ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:22px;font-weight:900;
                    color:#1a1a1a;margin:4px 0 4px;">
                Dynasty Timeline — Every Edition at a Glance
            </h3>
            <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                    font-style:italic;margin-bottom:8px;line-height:1.5;">
                Each dot = one edition. Color = best GC result that year. Hover for details.
            </p>
        </div>
    """, unsafe_allow_html=True)

        df_by_year = df_team.dropna(subset=['Rank_Num']).groupby('Year').agg(
            best_rank=('Rank_Num','min'),
            n_riders=('Rider','count'),
            top_rider=('Rider', lambda x: x[df_team.loc[x.index,'Rank_Num'].idxmin()] if len(x)>0 else ''),
        ).reset_index()

        def rank_color(r):
            if r == 1:   return '#FFD700'
            if r <= 3:   return '#C0C0C0'
            if r <= 10:  return '#CD7F32'
            if r <= 20:  return '#4ECDC4'
            return '#555'

        def rank_label(r):
            if r == 1:   return '🏆 GC Victory'
            if r <= 3:   return '🥈 Podium'
            if r <= 10:  return 'Top 10'
            if r <= 20:  return 'Top 20'
            return 'Participant'

        df_by_year['color']      = df_by_year['best_rank'].apply(rank_color)
        df_by_year['result_lbl'] = df_by_year['best_rank'].apply(rank_label)
        df_by_year['size']       = df_by_year['best_rank'].apply(lambda r: 22 if r==1 else 16 if r<=3 else 13 if r<=10 else 10)

        fig_timeline = go.Figure()

        # Linea di sfondo
        fig_timeline.add_trace(go.Scatter(
            x=df_by_year['Year'], y=[0]*len(df_by_year),
            mode='lines', line=dict(color='#c8bfad', width=1.5),
            showlegend=False, hoverinfo='skip',
        ))

        # Dot per categoria
        for lbl, color in [('🏆 GC Victory','#FFD700'),('🥈 Podium','#C0C0C0'),
                            ('Top 10','#CD7F32'),('Top 20','#4ECDC4'),('Participant','#555')]:
            df_cat = df_by_year[df_by_year['result_lbl'] == lbl]
            if df_cat.empty: continue
            fig_timeline.add_trace(go.Scatter(
                x=df_cat['Year'], y=[0]*len(df_cat),
                mode='markers',
                marker=dict(
                    size=df_cat['size'], color=color,
                    line=dict(width=2, color='white'), symbol='circle',
                ),
                name=lbl,
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>'
                    'Best GC: #%{customdata[1]}<br>'
                    'Leader: %{customdata[2]}<br>'
                    'Riders: %{customdata[3]}<extra></extra>'
                ),
                customdata=list(zip(
                    df_cat['Year'].astype(int),
                    df_cat['best_rank'].astype(int),
                    df_cat['top_rider'].str.title(),
                    df_cat['n_riders'].astype(int),
                )),
            ))

        # Linee verticali per vittorie GC
        for _, row in df_by_year[df_by_year['best_rank']==1].iterrows():
            fig_timeline.add_annotation(
                x=row['Year'], y=0,
                text=f"🏆 {int(row['Year'])}",
                showarrow=True, arrowhead=0, arrowcolor='#FFD700',
                font=dict(size=9, color='#FFD700', family='Arial'),
                ay=-36, ax=0, bgcolor='rgba(0,0,0,0.0)',
            )

        fig_timeline.update_layout(
            plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
            font=dict(family='Merriweather, serif', color='#1a1a1a'),
            height=200, margin=dict(l=0, r=0, t=30, b=10),
            xaxis=dict(title='', showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(visible=False, range=[-0.5, 0.6]),
            legend=dict(orientation='h', y=-0.3, x=0.5, xanchor='center', font=dict(size=10)),
            showlegend=True,
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown(hr, unsafe_allow_html=True)

   # ── TEAM ROLES EXPLAINER ──
# ── TEAM ROLES EXPLAINER ──
# ── TEAM ROLES EXPLAINER ──
        if 'roles_open' not in st.session_state:
            st.session_state.roles_open = False

        arrow = "▲" if st.session_state.roles_open else "▼"

        st.markdown(f"""
            <style>
            div[data-testid="stButton"]:has(button[kind="secondary"]#roles_toggle_btn) button,
            div[data-testid="stBaseButton-secondary"]:has(#roles_toggle_btn) {{
                background: #F4F1EA !important;
                border-top: 2px solid #1a1a1a !important;
                border-bottom: 1px solid #c8bfad !important;
                border-left: none !important;
                border-right: none !important;
                border-radius: 0 !important;
                padding: 9px 20px !important;
                box-shadow: none !important;
                width: 100% !important;
                color: #1a1a1a !important;
                font-family: 'Merriweather', Georgia, serif !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                letter-spacing: 0px !important;
                text-transform: none !important;
            }}
            
            /* 🪄 FIX: Forza in nero qualsiasi testo interno (paragrafi/span) generato da Streamlit nel bottone */
            div[data-testid="stButton"] button[kind="secondary"]#roles_toggle_btn p,
            div[data-testid="stButton"] button[kind="secondary"]#roles_toggle_btn div,
            div[data-testid="stButton"] button[kind="secondary"]#roles_toggle_btn span {{
                color: #1a1a1a !important;
            }}

            /* Selettore più largo come fallback */
            div[data-testid="stButton"] button[kind="secondary"] {{
                background: #F4F1EA !important;
                border-top: 2px solid #1a1a1a !important;
                border-bottom: 1px solid #c8bfad !important;
                border-left: none !important;
                border-right: none !important;
                border-radius: 0 !important;
                padding: 9px 20px !important;
                box-shadow: none !important;
                color: #1a1a1a !important;
                font-family: 'Merriweather', Georgia, serif !important;
                font-size: 12px !important;
                font-weight: 700 !important;
            }}
            
            div[data-testid="stButton"] button[kind="secondary"] p {{
                color: #1a1a1a !important;
            }}

            div[data-testid="stButton"] button[kind="secondary"]:hover {{
                background: #ede9e0 !important;
                border-top: 2px solid #1a1a1a !important;
                border-bottom: 1px solid #c8bfad !important;
                border-left: none !important;
                border-right: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        # Testo pulito senza tag HTML che confondono Streamlit
        if st.button(
            f"· Team Roles ·   Who does what inside a Tour de France squad?   {arrow}",
            key="roles_toggle_btn",
            use_container_width=True
        ):
            st.session_state.roles_open = not st.session_state.roles_open
            st.rerun()

        if st.session_state.roles_open:
            roles_content_html = """
            <div style="background:#F4F1EA;border-bottom:1px solid #c8bfad;padding:16px 20px;
                        font-family:'Merriweather',Georgia,serif;margin-top:-8px;">
            <p style="font-size:12px;color:#555;line-height:1.7;margin:0 0 14px">
                A professional cycling team is not a collection of solo athletes — it is a precisely structured unit
                where every rider has a defined function. Understanding these roles transforms how you read the roster heatmap below.
            </p>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#FFCC00;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Team captain</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">The designated GC leader. The entire team rides in service of this rider on key mountain stages and time trials. All tactical decisions revolve around protecting and advancing the captain's result.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#FFF8DC;color:#854F0B;">GC leader</span>
                </div>

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#4ECDC4;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Domestique</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">The backbone of any team. Domestiques sacrifice their own race to serve the captain — fetching water bottles, chasing attacks, setting tempo on climbs, and shielding the leader from wind. Rarely in results, but indispensable.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#e0f7f5;color:#0a6b65;">selfless worker</span>
                </div>

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#FF6B6B;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Climbing domestique</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">A specialist capable of maintaining pace on steep mountain passes. Sets a relentless rhythm that cracks rival teams, then peels off deep in the climb to let the captain race alone to the summit.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#FFEBEE;color:#A32D2D;">mountain worker</span>
                </div>

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#aaa;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Lead-out man</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">Critical for sprinter teams. Drives at maximum speed in the final kilometres directly in front of the sprinter, clearing a path and delivering them to the perfect launch point. One of cycling's most technically demanding roles.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#f0ece4;color:#555;">sprint train</span>
                </div>

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#7F77DD;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Super-domestique</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">Talented enough to be a captain elsewhere, but supports a stronger teammate. Takes secondary leadership if the captain abandons, and can be unleashed on breakaways to secure bonus time or stage wins.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#EEEDFE;color:#3C3489;">versatile asset</span>
                </div>

                <div style="border-radius:6px;padding:12px 14px;border:0.5px solid #c8bfad;background:#fff;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="width:9px;height:9px;border-radius:50%;background:#D85A30;flex-shrink:0"></div>
                    <span style="font-size:13px;font-weight:700;color:#1a1a1a;">Breakaway specialist</span>
                </div>
                <p style="font-size:11px;color:#444;line-height:1.65;margin:0;">Given freedom to join early escapes. Since they don't threaten the GC, rivals let them go. This earns the team stage wins, polka-dot points, and crucial television exposure for sponsors throughout the race.</p>
                <span style="display:inline-block;font-size:10px;padding:2px 8px;border-radius:20px;margin-top:7px;font-weight:600;background:#FAECE7;color:#712B13;">stage hunter</span>
                </div>

            </div>
            <p style="font-size:11px;color:#888;margin:14px 0 0;line-height:1.6;font-style:italic;">
                In the roster heatmap below, brighter cells often indicate captains or super-domestiques. Long streaks of dark cells are the hallmark of a loyal domestique who rode in the shadows of the team's success.
            </p>
            </div>
            """
            st.components.v1.html(roles_content_html, height=420, scrolling=False)
        # ──────────────────────────────────────────────────────
        # SEZIONE B: ROSTER HEATMAP "WHO RODE WHEN"
        # ──────────────────────────────────────────────────────

        st.markdown("""
            <div style="padding: 0 16px;">
                <span class="t-section-label">· Roster DNA ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:22px;font-weight:900;
                        color:#1a1a1a;margin:4px 0 4px;">
                    Who Rode When — The Full Team Roster
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                        font-style:italic;margin-bottom:8px;line-height:1.5;">
                    Each cell = one Tour. Color intensity = GC rank (brighter = better). 
                    Reveals captains, loyal domestiques, and transitions.
                </p>
            </div>
        """, unsafe_allow_html=True)

        df_heatmap = df_team.dropna(subset=['Rank_Num']).copy()
        rider_years = df_heatmap.groupby('Rider')['Year'].count()
        # Mostra solo corridori con 2+ presenze o rank ≤ 20
        top_riders_hm = rider_years[rider_years >= 2].index.tolist()
        elite_riders  = df_heatmap[df_heatmap['Rank_Num'] <= 20]['Rider'].unique().tolist()
        riders_to_show = list(set(top_riders_hm) | set(elite_riders))
        df_hm = df_heatmap[df_heatmap['Rider'].isin(riders_to_show)].copy()

        if not df_hm.empty:
            pivot = df_hm.pivot_table(index='Rider', columns='Year', values='Rank_Num', aggfunc='min')
            
            # Ordina al contrario (ascending=False) per contrastare l'inversione dell'asse Y di Plotly. 
            pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]
            
            # Limita a 30 corridori max
            pivot = pivot.head(30)
            
            # Inverti scala: rank 1 = valore alto (appare luminoso)
            pivot_inv = pivot.copy()
            for col in pivot_inv.columns:
                pivot_inv[col] = pivot_inv[col].apply(lambda x: max(0, 180-x) if pd.notna(x) else None)

            # Creiamo una matrice di testi formattata a mano per eliminare la scritta 'NaN' dalle celle vuote
            text_matrix = []
            for rider_idx in pivot.index:
                row_text = []
                for year_col in pivot.columns:
                    val = pivot.loc[rider_idx, year_col]
                    if pd.isna(val):
                        row_text.append("") 
                    else:
                        row_text.append(f"{int(val)}")
                text_matrix.append(row_text)

            fig_hm = go.Figure(data=go.Heatmap(
                z=pivot_inv.values,
                x=[int(c) for c in pivot_inv.columns],
                y=[r.title() for r in pivot_inv.index],
                # 🪄 FIX COLORS: Ricalibrata la distribuzione per isolare il picco di luce (1.0) solo per la vittoria
                colorscale=[
                    [0.0, '#F4F1EA'],    # Assente (colore sfondo app)
                    [0.01, '#0d0d0d'],   # Fondo classifica (>100) -> Nero profondo
                    [0.4, '#193326'],    # Gruppo (Rank 50-100) -> Verde scuro opaco
                    [0.75, '#D4A373'],   # Top 20-30 -> Ocra / Bronzo spento
                    [0.88, '#FF9F1C'],   # Top 10 (Rank 4-10) -> Arancione/Giallo caldo intenso
                    [0.96, '#FFCC00'],   # Podio (Rank 2-3) -> Giallo iconico Tour
                    [1.0, '#FFFFFF']     # Vittoria (#1 Win) -> Oro bianco / Luce purissima per staccare al massimo
                ],
                text=text_matrix, 
                texttemplate='%{text}',
                textfont=dict(size=9, family='Arial', weight='bold'), # Messo in bold per leggere meglio i numeri chiari
                hovertemplate='<b>%{y}</b><br>%{x}<br>GC Rank: #%{text}<extra></extra>',
                showscale=False,
                zmin=0, 
                zmax=180, 
                xgap=2,
                ygap=2,
            ))
            fig_hm.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=max(300, len(pivot)*22 + 60),
                margin=dict(l=40, r=20, t=10, b=20), 
                xaxis=dict(title='', tickmode='linear', dtick=max(1,len(pivot.columns)//15),
                        tickfont=dict(size=9), side='bottom'),
                yaxis=dict(title='', tickfont=dict(size=10)),
            )
            
            st.markdown('<div style="margin: 0 16px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_hm, use_container_width=True)
            
            # ── LEGENDA AGGIORNATA CON I NUOVI LIVELLI ──
            legend_hm_html = """
            <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
                        margin-top: 8px; padding: 8px 12px; background: #F4F1EA; border: 1px solid #c8bfad; border-radius: 4px; font-family: Arial, sans-serif; font-size: 11px; color: #555;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 12px; height: 12px; background: #FFFFFF; border-radius: 2px; border: 1px solid #c8bfad;"></span>
                        <strong>#1 Win</strong>
                    </span>
                    <span style="display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 12px; height: 12px; background: #FFCC00; border-radius: 2px; border: 1px solid #c8bfad;"></span>
                        Podium (2-3)
                    </span>
                    <span style="display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 12px; height: 12px; background: #FF9F1C; border-radius: 2px;"></span>
                        Top 10
                    </span>
                    <span style="display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 12px; height: 12px; background: #193326; border-radius: 2px;"></span>
                        Mid Pack
                    </span>
                    <span style="display: flex; align-items: center; gap: 5px;">
                        <span style="display: inline-block; width: 12px; height: 12px; background: #0d0d0d; border-radius: 2px;"></span>
                        Back Pack / DNF
                    </span>
                </div>
                <div style="color: #888; font-style: italic;">
                    Numbers = GC rank · Brighter = better result · Only riders with 2+ appearances or top-20 finish shown
                </div>
            </div>
            </div>
            """
            st.markdown(legend_hm_html, unsafe_allow_html=True)
        else:
            st.info("Not enough data to build the roster heatmap.")

        st.markdown(hr, unsafe_allow_html=True)        
        
        # ──────────────────────────────────────────────────────
        # SEZIONE C: HISTORICAL PERFORMANCE
        # ──────────────────────────────────────────────────────
        # ──────────────────────────────────────────────────────
        # SEZIONE C: HISTORICAL PERFORMANCE
        # ──────────────────────────────────────────────────────
        # ──────────────────────────────────────────────────────
        # SEZIONE C: HISTORICAL PERFORMANCE
        # ──────────────────────────────────────────────────────
        st.markdown("""
            <style>
            /* 1. Forza lo sfondo chiaro su TUTTO il blocco delle colonne di questa sezione */
            div[data-testid="stHorizontalBlock"] {
                background-color: #F4F1EA !important;
            }
            div[data-testid="column"] {
                background-color: #F4F1EA !important;
            }
            
            /* 2. Selectbox chiara */
            div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                background-color: #F4F1EA !important;
                border: 1px solid #c8bfad !important;
                color: #1a1a1a !important;
            }
            div[data-testid="stSelectbox"] label p {
                color: #1a1a1a !important;
                font-family: 'Merriweather', serif !important;
                font-size: 12px !important;
                font-weight: 700 !important;
            }
            
            /* 3. Dropdown menu chiaro e 🪄 FIX: Testo degli anni forzato in NERO */
            div[data-baseweb="popover"] ul, ul[role="listbox"] {
                background-color: #F4F1EA !important;
            }
            div[data-baseweb="popover"] li, ul[role="listbox"] li, div[role="option"] {
                color: #1a1a1a !important;
                background-color: #F4F1EA !important;
            }
            /* Colpisce i singoli span di testo annidati dentro la tendina per sovrascrivere il bianco */
            div[data-baseweb="popover"] span, ul[role="listbox"] span, div[role="option"] span {
                color: #1a1a1a !important;
            }
            div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover, div[role="option"]:hover {
                background-color: #ede9e0 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="padding: 0 16px 8px;">
                <span class="t-section-label">· Historical Performance ·</span>
                <h3 style="font-family:'Merriweather',Georgia,serif;font-size:22px;font-weight:900;
                            color:#1a1a1a;margin:4px 0 4px;">
                    All-Time Placements & Edition Spotlight
                </h3>
                <p style="font-family:'Merriweather',serif;font-size:11px;color:#666;
                        font-style:italic;margin-bottom:8px;line-height:1.5;">
                    Select an edition on the left to spotlight that year in the scatter plot.
                    Each dot = one rider. Yellow = selected year. The red dotted line tracks the team's average GC rank over time.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_p1, col_p2 = st.columns([1.2, 1], gap="medium")

        with col_p1:
            st.markdown('<div style="padding-left: 16px; background:#F4F1EA;">', unsafe_allow_html=True)
            anni_team = sorted(df_team['Year'].dropna().unique(), reverse=True)
            anno_sel = st.selectbox("📅 Focus on edition:", [int(a) for a in anni_team], key="team_anno")

            df_anno_team = df_team[df_team['Year'] == anno_sel][['Rider', 'Rank_Num']].sort_values('Rank_Num').copy()
            df_anno_team['Rank_Num'] = df_anno_team['Rank_Num'].apply(
                lambda x: int(x) if pd.notna(x) else "DNF"
            )
            df_anno_team.columns = ['Rider', 'Final GC']
            df_anno_team['Rider'] = df_anno_team['Rider'].str.title()

            best_yr_row = df_by_year.loc[df_by_year['best_rank'].idxmin()] if not df_by_year.empty else None
            if best_yr_row is not None and int(best_yr_row['Year']) == anno_sel:
                st.markdown(
                    '<div style="background:rgba(255,215,0,0.08);border:1px solid #FFD700;'
                    'border-radius:4px;padding:8px 12px;margin-bottom:8px;'
                    'font-family:Merriweather,serif;font-size:11px;color:#1a1a1a;">'
                    '⭐ <strong>Best edition in franchise history</strong></div>',
                    unsafe_allow_html=True
                )

            rows_html = ""
            for _, row in df_anno_team.iterrows():
                gc = row['Final GC']
                if gc == "DNF":
                    bg, col, pre = "#FFEBEE", "#A32D2D", ""
                else:
                    n = int(gc)
                    if n == 1:
                        bg, col, pre = "#FFF8DC", "#854F0B", "🏆 "
                    elif n <= 3:
                        bg, col, pre = "#f0ece4", "#444444", ""
                    elif n <= 10:
                        bg, col, pre = "#e0f7f5", "#0a6b65", ""
                    else:
                        bg, col, pre = "#F4F1EA", "#888888", ""

                rows_html += (
                    '<tr style="border-bottom:1px solid #c8bfad;">'
                    '<td style="padding:8px 12px;font-family:Merriweather,serif;'
                    'font-size:12px;color:#1a1a1a;">' + str(row['Rider']) + '</td>'
                    '<td style="padding:8px 12px;text-align:center;">'
                    '<span style="background:' + bg + ';color:' + col + ';font-size:11px;'
                    'font-weight:700;padding:2px 10px;border-radius:20px;'
                    'font-family:Arial,sans-serif;">' + pre + str(gc) + '</span>'
                    '</td></tr>'
                )

            table_html = (
                '<div style="background:#F4F1EA;border:1px solid #c8bfad;border-radius:4px;'
                'overflow:hidden;margin-top:4px;max-height:320px;overflow-y:auto;">'
                '<table style="width:100%;border-collapse:collapse;background:#F4F1EA;">'
                '<thead>'
                '<tr style="background:#F4F1EA;border-bottom:2px solid #1a1a1a;">'
                '<th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;'
                'font-size:10px;letter-spacing:2px;text-transform:uppercase;'
                'color:#1a1a1a;font-weight:700;">Rider</th>'
                '<th style="padding:10px 12px;text-align:center;font-family:Arial,sans-serif;'
                'font-size:10px;letter-spacing:2px;text-transform:uppercase;'
                'color:#1a1a1a;font-weight:700;">Final GC</th>'
                '</tr>'
                '</thead>'
                '<tbody>' + rows_html + '</tbody>'
                '</table>'
                '</div>'
            )

            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p2:
            st.markdown('<div style="padding-right: 16px; background:#F4F1EA;">', unsafe_allow_html=True)
            df_strip = df_team.dropna(subset=['Rank_Num']).copy()
            df_strip['Selected'] = df_strip['Year'] == anno_sel

            fig_strip = go.Figure()

            # Tutti gli altri anni — grigio
            df_other = df_strip[~df_strip['Selected']]
            if not df_other.empty:
                jitter = np.random.uniform(-0.18, 0.18, size=len(df_other))
                fig_strip.add_trace(go.Scatter(
                    x=df_other['Year'] + jitter,
                    y=df_other['Rank_Num'],
                    mode='markers',
                    name='Other editions',
                    marker=dict(size=6, color='#c8bfad', opacity=0.5,
                                line=dict(width=0)),
                    hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>GC rank: #%{y:.0f}<extra></extra>',
                    customdata=list(zip(
                        df_other['Rider'].str.title(),
                        df_other['Year'].astype(int),
                    )),
                ))

            # Anno selezionato — giallo evidenziato
            df_sel = df_strip[df_strip['Selected']]
            if not df_sel.empty:
                jitter_sel = np.random.uniform(-0.18, 0.18, size=len(df_sel))
                fig_strip.add_trace(go.Scatter(
                    x=df_sel['Year'] + jitter_sel,
                    y=df_sel['Rank_Num'],
                    mode='markers',
                    name=f'{anno_sel} edition',
                    marker=dict(size=11, color='#FFCC00', opacity=1.0,
                                line=dict(width=1.5, color='#1a1a1a')),
                    hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>GC rank: #%{y:.0f}<extra></extra>',
                    customdata=list(zip(
                        df_sel['Rider'].str.title(),
                        df_sel['Year'].astype(int),
                    )),
                ))

            # Linea media per anno
            avg_by_year = df_strip.groupby('Year')['Rank_Num'].mean().reset_index()
            fig_strip.add_trace(go.Scatter(
                x=avg_by_year['Year'],
                y=avg_by_year['Rank_Num'],
                mode='lines',
                name='Team avg rank',
                line=dict(color='#FF6B6B', width=1.5, dash='dot'),
                hovertemplate='<b>%{x}</b><br>Avg GC rank: #%{y:.1f}<extra></extra>',
            ))

            fig_strip.update_layout(
                plot_bgcolor='#F4F1EA',
                paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=360,
                margin=dict(l=50, r=20, t=10, b=50),
                xaxis=dict(
                    title='Year',
                    showgrid=False,
                    tickmode='linear',
                    dtick=max(1, (df_strip['Year'].max() - df_strip['Year'].min()) // 8),
                    tickfont=dict(size=10),
                    title_font=dict(size=11),
                ),
                yaxis=dict(
                    title='GC rank (lower = better)',
                    autorange='reversed',
                    showgrid=True,
                    gridcolor='#e8e4da',
                    tickfont=dict(size=10),
                    title_font=dict(size=11),
                ),
                legend=dict(
                    orientation='h',
                    y=-0.22, x=0.5, xanchor='center',
                    font=dict(size=10, family='Arial'),
                    bgcolor='rgba(0,0,0,0)',
                ),
                showlegend=True,
            )

            # Fascia top 10 ricalibrata
            fig_strip.add_hrect(
                y0=0.5, y1=10.5,
                fillcolor='rgba(255,204,0,0.06)',
                line_width=0,
                annotation_text='Top 10 zone',
                annotation_font=dict(size=9, color='#854F0B', family='Arial', weight='bold'),
                annotation_position='top right',
            )

            st.plotly_chart(fig_strip, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(hr, unsafe_allow_html=True)
        # ──────────────────────────────────────────────────────
        # SEZIONE D: PALMARÈS
        # ──────────────────────────────────────────────────────
        st.markdown("""
            <span class="t-section-label">· Palmarès ·</span>
            <h3 style="font-family:'Merriweather',Georgia,serif;font-size:22px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 4px;">
                Stage Wins & Jersey Days
            </h3>
        """, unsafe_allow_html=True)

        # Calcola tappe vinte
        df_team_riders = df_storico_clean[df_storico_clean['Team'].isin(aliases_gruppo)]
        df_merge_stages = pd.merge(
            df_stage_h_c, df_team_riders,
            left_on=['Year','Winner_Clean'], right_on=['Year','Rider_Clean'], how='inner'
        )
        df_tappe_ttt = df_stage_h_c[
            df_stage_h_c['Winner of stage'].apply(
                lambda x: any(a.lower() in str(x).lower() for a in aliases_gruppo)
            )
        ].copy()
        df_tappe = pd.concat([df_merge_stages, df_tappe_ttt], ignore_index=True).drop_duplicates(
            subset=['Year','Stages']
        )

        # Maglie
        corridori_set = df_team_riders[['Year','Rider_Clean']].drop_duplicates()
        maglia_gialla = pd.merge(df_stage_h_c, corridori_set, left_on=['Year','Yellow_Clean'], right_on=['Year','Rider_Clean'], how='inner')
        maglia_verde  = pd.merge(df_stage_h_c, corridori_set, left_on=['Year','Green_Clean'],  right_on=['Year','Rider_Clean'], how='inner')
        maglia_pois   = pd.merge(df_stage_h_c, corridori_set, left_on=['Year','Pois_Clean'],   right_on=['Year','Rider_Clean'], how='inner')

        n_yellow = len(maglia_gialla)
        n_green  = len(maglia_verde)
        n_pois   = len(maglia_pois)
        n_stages_won = len(df_tappe)

        # ── JERSEY RADIAL GAUGE ──
        col_gauge, col_stagewin = st.columns([1, 1.6], gap="medium")

        with col_gauge:
            st.markdown("""
                <span class="t-section-label">· Jersey Days ·</span>
                <h5 style="font-family:'Merriweather',serif;font-weight:900;color:#1a1a1a;
                           font-size:14px;margin:2px 0 8px;">
                    Days Wearing Each Jersey
                </h5>
            """, unsafe_allow_html=True)

            max_days = max(n_yellow, n_green, n_pois, 1)
            gauge_items = [
                ('Yellow', n_yellow, '#FFD700', 'GC Leader'),
                ('Green',  n_green,  '#22c55e', 'Points Leader'),
                ('Polka-dot', n_pois, '#ef4444', 'KOM Leader'),
            ]
            fig_gauge = go.Figure()
            for i, (name, val, color, label) in enumerate(gauge_items):
                pct = val / max_days
                # Arco pieno (sfondo)
                fig_gauge.add_trace(go.Barpolar(
                    r=[1], theta=[i*120 + 60], width=[80],
                    marker_color='#e8e4da', opacity=0.4,
                    showlegend=False, hoverinfo='skip',
                ))
                # Arco valore
                if val > 0:
                    fig_gauge.add_trace(go.Barpolar(
                        r=[pct], theta=[i*120 + 60], width=[80],
                        marker_color=color, opacity=0.9,
                        name=f'{name}: {val} days',
                        hovertemplate=f'<b>{label}</b><br>{val} days<extra></extra>',
                    ))
            fig_gauge.update_layout(
                polar=dict(
                    radialaxis=dict(visible=False, range=[0,1.1]),
                    angularaxis=dict(visible=False),
                    bgcolor='#F4F1EA',
                ),
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                height=280, margin=dict(l=20,r=20,t=20,b=20),
                legend=dict(orientation='h', y=-0.08, x=0.5, xanchor='center', font=dict(size=10)),
                showlegend=True,
            )
            # Numero al centro come annotation
            fig_gauge.add_annotation(
                x=0.5, y=0.5, xref='paper', yref='paper',
                text=f'<b>{n_yellow+n_green+n_pois}</b><br><span style="font-size:10px">total jersey<br>days</span>',
                showarrow=False, font=dict(size=14, color='#1a1a1a', family='Merriweather, serif'),
                align='center',
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_stagewin:
            st.markdown("""
                <span class="t-section-label">· Stage Wins per Edition ·</span>
                <h5 style="font-family:'Merriweather',serif;font-weight:900;color:#1a1a1a;
                           font-size:14px;margin:2px 0 8px;">
                    Stage Wins Timeline
                </h5>
            """, unsafe_allow_html=True)

            if not df_tappe.empty and 'Year' in df_tappe.columns:
                vittorie_anno = df_tappe.groupby('Year').size().reset_index(name='wins')

                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=vittorie_anno['Year'], y=vittorie_anno['wins'],
                    marker=dict(
                        color=vittorie_anno['wins'],
                        colorscale=[[0,'#FFF3CD'],[0.4,'#FFCC00'],[1,'#1a1a1a']],
                        line=dict(width=0),
                    ),
                    hovertemplate='<b>%{x}</b><br>Stage wins: %{y}<extra></extra>',
                ))
                fig_bar.update_layout(
                    plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                    font=dict(family='Merriweather, serif', color='#1a1a1a'),
                    height=280, margin=dict(l=0,r=0,t=10,b=0),
                    xaxis=dict(title='', showgrid=False, tickfont=dict(size=9)),
                    yaxis=dict(title='Stage Wins', showgrid=True, gridcolor='#e8e4da'),
                    showlegend=False,
                    title=dict(text=f'Total stage wins: <b>{n_stages_won}</b>',
                               font=dict(size=12, color='#1a1a1a')),
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No stage win data found for this team.")

        st.markdown(hr, unsafe_allow_html=True)

        # ── TOP STAGE WINNERS del team ──
        st.markdown("""
            <span class="t-section-label">· Franchise Heroes ·</span>
            <h4 style="font-family:'Merriweather',Georgia,serif;font-size:18px;font-weight:900;
                       color:#1a1a1a;margin:4px 0 4px;">
                The Franchise's Greatest Stage Winners
            </h4>
        """, unsafe_allow_html=True)

        col_sw1, col_sw2 = st.columns(2, gap="medium")

        with col_sw1:
            if not df_tappe.empty and 'Winner of stage' in df_tappe.columns:
                top_sw = df_tappe.groupby('Winner of stage').size().reset_index(name='Wins')
                top_sw = top_sw.sort_values('Wins', ascending=False).head(10)
                top_sw['Winner of stage'] = top_sw['Winner of stage'].str.title()

                fig_sw = px.bar(top_sw, y='Winner of stage', x='Wins', orientation='h',
                                color='Wins',
                                color_continuous_scale=[[0,'#FFF3CD'],[0.5,'#FFCC00'],[1,'#FF6B6B']],
                                labels={'Winner of stage':'', 'Wins':'Stage Wins'})
                fig_sw.update_layout(
                    plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                    font=dict(family='Merriweather, serif', color='#1a1a1a'),
                    height=320, margin=dict(l=0,r=0,t=10,b=0),
                    yaxis=dict(categoryorder='total ascending', title=''),
                    xaxis=dict(showgrid=True, gridcolor='#e8e4da'),
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_sw, use_container_width=True)

        with col_sw2:
            # "Loyals": corridori con più presenze
            loyals = df_team['Rider'].value_counts().reset_index()
            loyals.columns = ['Rider','Tours']
            loyals['Rider'] = loyals['Rider'].str.title()
            loyals = loyals.head(10)

            fig_loyals = px.bar(loyals, y='Rider', x='Tours', orientation='h',
                                color='Tours',
                                color_continuous_scale=[[0,'#e8e4da'],[0.5,'#4ECDC4'],[1,'#1a1a1a']],
                                labels={'Rider':'', 'Tours':'Tour Appearances with Franchise'})
            fig_loyals.update_layout(
                plot_bgcolor='#F4F1EA', paper_bgcolor='#F4F1EA',
                font=dict(family='Merriweather, serif', color='#1a1a1a'),
                height=320, margin=dict(l=0,r=0,t=10,b=0),
                yaxis=dict(categoryorder='total ascending', title=''),
                xaxis=dict(showgrid=True, gridcolor='#e8e4da'),
                coloraxis_showscale=False,
                title=dict(text='The Franchise Loyals', font=dict(size=13, color='#1a1a1a')),
            )
            st.plotly_chart(fig_loyals, use_container_width=True)