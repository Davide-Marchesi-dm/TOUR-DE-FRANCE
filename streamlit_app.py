import streamlit as st
import pandas as pd
import altair as alt


# ==========================================
# FUNZIONE PER CARICARE I DATI
# ==========================================
# ==========================================
# FUNZIONE PER CARICARE I DATI (3 LINK)
# ==========================================
# ==========================================
# FUNZIONE PER CARICARE I DATI (LINK CORRETTI)
# ==========================================
@st.cache_data
def load_all_datasets():
    # Link convertiti in formato 'export'
    url_storico = "https://docs.google.com/spreadsheets/d/1hI6y5tDpw176v0DhJN-P5hzsmXrtRSB0/export?format=xlsx"
    url_stage_h = "https://docs.google.com/spreadsheets/d/1bYnt9BfbKk-HMYR8bekqQfaKH02eZBWq/export?format=xlsx" 
    url_tour_w = "https://docs.google.com/spreadsheets/d/1GrXwBG2Cda93AvOsWa-oDT19gwWCaF-2/export?format=xlsx"

    # Caricamento con gestione errori per ogni file
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
    
    return df_storico, df_stage_h, df_tour_w

# 1. Carichiamo i tre dataframe (CHIAMATA UNICA)
df_storico, df_stage_h, df_tour_w = load_all_datasets()

# 2. RIMUOVI la riga "df_storico = load_data()" perché è un doppione che causa l'errore!
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
    .contenuto-pagina {
        padding: 2rem 4rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. COSTRUZIONE DELLA BARRA DI NAVIGAZIONE
# ==========================================
col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5], vertical_alignment="center")

with col1:
    # Se clicchi, lo stato cambia in "2025"
    if st.button("CLASSIFICA", use_container_width=True):
        st.session_state.pagina_corrente = "classifica"
with col2:
    if st.button("CORRIDORI", use_container_width=True):
        st.session_state.pagina_corrente = "corridori"

with col3:
    url_logo = "https://www.brandforum.it/wp-content/uploads/2019/03/38020191021104459.png"
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; transform: translateY(-8px);">
            <a href="?nav=home" target="_self" title="Torna alla Home">
                <img src="{url_logo}" 
                     style="width: 100%; max-width: 140px; background-color: white; padding: 2px 8px; border-radius: 8px; cursor: pointer;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    if st.button("TAPPE", use_container_width=True):
        st.session_state.pagina_corrente = "tappe"

with col5:
    if st.button("TEAMS", use_container_width=True):
        st.session_state.pagina_corrente = "teams"


# ==========================================
# 5. CONTENUTO DELLE PAGINE
# ==========================================
st.markdown('<div class="contenuto-pagina">', unsafe_allow_html=True)


if st.session_state.pagina_corrente == "home":
    
    # 1. IL "TITOLONE" DA PRIMA PAGINA
    st.markdown("""
        <h1 style='text-align: center; font-size: 3.5rem; text-transform: uppercase; border-bottom: 3px solid black; padding-bottom: 10px; margin-bottom: 10px; color: #000000;'>
            Le Tour de France
        </h1>
        <h3 style='text-align: center; font-style: italic; color: #000000; margin-bottom: 40px;'>
            Tutti i numeri, i segreti e i protagonisti della Grande Boucle
        </h3>
    """, unsafe_allow_html=True)

    # 2. LAYOUT A COLONNE (Stile articolo)
    col_sx, col_dx = st.columns([1.5, 1], gap="large")
    
    with col_sx:
        # Testo dell'articolo introduttivo
        st.markdown("""
        **PARIGI** — Il Tour de France non è semplicemente una corsa ciclistica; è un monumento nazionale itinerante, una prova di resistenza sovrumana e il palcoscenico dove, da oltre un secolo, si forgiano le leggende dello sport. 
        
        Sulle strade di Francia, i giganti del pedale si sfidano attraverso pianure spazzate dal vento, colline insidiose e le vette massacranti di Alpi e Pirenei. Questo portale nasce per dissezionare ogni singolo aspetto della corsa a tappe più famosa del mondo.
        
        **Esplora i dati:** Usa la barra di navigazione superiore per immergerti nelle statistiche. Dalle planimetrie dettagliate di ogni singola tappa, fino ai profili biometrici dei ciclisti e alle squadre World Tour.
        """)
        
        # Una linea di separazione elegante
        st.markdown("<hr style='border: 1px solid #555; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # ---> LE STATISTICHE SPOSTATE SOPRA (Senza catenella link) <---
        st.markdown("<h3 style='margin-top: 20px; margin-bottom: 15px; color: #FFFFFF;'>I Numeri della Corsa</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Edizioni", "111")
        c2.metric("Chilometri", "~3.500")
        c3.metric("Tappe", "21")
        
        # Un po' di spazio
        st.markdown("<br>", unsafe_allow_html=True)

        # ---> BOX CURIOSITÀ SPOSTATO SOTTO <---
        st.markdown("""
            <div style='background-color: #E6E1CF; color: #000000; padding: 15px; border-left: 5px solid #FFCC00; margin-top: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
            <h4 style='margin-top: 0; margin-bottom: 10px; font-style: italic; border-bottom: 1px solid #999; padding-bottom: 5px; color: #000000;'>📰 Dietro le quinte del Tour</h4>
                
            <p style='font-size: 0.95rem; margin-top: 10px;'><strong>Le origini commerciali:</strong> Il Tour fu fondato nel 1903 da Henri Desgrange, direttore del giornale sportivo francese <em>L'Auto</em> (il predecessore de L'Équipe), con un obiettivo molto pratico: sbaragliare la concorrenza e vendere più copie del suo quotidiano.</p>
                
            <p style='font-size: 0.95rem; margin-bottom: 0;'><strong>Il segreto del Giallo:</strong> La celebre maglia gialla, introdotta nel 1919 per rendere il leader della corsa facilmente riconoscibile in gruppo, deve il suo colore proprio alla carta su cui veniva stampato il giornale <em>L'Auto</em>.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_dx:
        # Foto "in prima pagina" (Senza icona espandi schermo)
        foto_hero = "https://cdn.artphotolimited.com/images/5c2e191bd96b2e012e7a7fc5/1000x1000/tour-de-france-1937.jpg"
        st.markdown(f"<img src='{foto_hero}' style='width: 100%; border-radius: 3px;'>", unsafe_allow_html=True)
        
        # Didascalia della foto in piccolo (Margine sistemato per l'HTML)
        st.markdown("""
            <p style='font-size: 0.85rem; text-align: right; font-style: italic; color: #FFFFFF; margin-top: 5px;'>
                Guy Lapébie il vincitore dell'edizione del 1937. (Foto: Archivi Storici)
            </p>
        """, unsafe_allow_html=True)
    
    # ---> SEZIONE CITAZIONI CELEBRI (3 Colonne) <---
    # Una linea per separare la parte alta della pagina
    st.markdown("<hr style='border: 1px solid #555; margin-top: 50px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    
    # Titolo della sezione citazioni
    st.markdown("<h3 style='text-align: center; font-style: italic; color: #333; margin-bottom: 40px;'> Voci dalla Grande Boucle</h3>", unsafe_allow_html=True)

    # Creiamo tre colonne per affiancare le tue tre citazioni
    cit1, cit2, cit3 = st.columns(3, gap="large")

    with cit1:
        # Henri Desgrange
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBrNDQ34YGwB6cNLr1TaGGmkzQtqPAjpaB8g&s" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il Tour de France ideale sarebbe quello in cui un solo corridore riuscisse ad arrivare a Parigi.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Henri Desgrange</strong></p>
            <p style='font-size: 0.8rem; color: #FFFFFF; line-height: 1.3; margin-top: 5px;'>Fondatore del Tour.</p>
        </div>
        """, unsafe_allow_html=True)

    with cit2:
        # Lance Armstrong
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://cdn.mos.cms.futurecdn.net/WAu4qwBuYVmi4qtQ6W8F4K.jpg" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il Tour non è solo una gara di ciclismo, nient'affatto. È una prova. Ti prova fisicamente, ti prova mentalmente e ti prova persino moralmente.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Lance Armstrong</strong></p>
            </div>
            """, unsafe_allow_html=True)

    with cit3:
        # Mark Cavendish
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://imgresizer.eurosport.com/unsafe/1200x0/filters:format(jpeg)/origin-imgresizer.eurosport.com/2021/06/29/3163795-64831628-2560-1440.jpg" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il ciclismo non è un gioco, è uno sport in cui si soffre. Ma il Tour de France è un livello di sofferenza completamente diverso.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Mark Cavendish</strong></p>
        </div>
        """, unsafe_allow_html=True)

        
elif st.session_state.pagina_corrente == "classifica":
    
    st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🏆 Classifica e Albo d'Oro</h2>", unsafe_allow_html=True)
    
    if not df_storico.empty:
        
        # ==========================================
        # 1. CSS PER LA TENDINA NERA
        # ==========================================
        st.markdown("""
            <style>
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
            .stSelectbox label {
                color: #000000 !important;
                font-weight: bold !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # ==========================================
        # 2. FILTRO ANNO E DATI
        # ==========================================
        anni_disponibili = sorted(df_storico['Year'].dropna().unique(), reverse=True)
        
        col_filtro, _ = st.columns([1, 3])
        with col_filtro:
            anno_selezionato = st.selectbox("Seleziona l'edizione:", anni_disponibili)
            
        st.markdown("<hr style='border: 1px solid #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)

        df_anno = df_storico[df_storico['Year'] == anno_selezionato].reset_index(drop=True)
        
        # ==========================================
        # 3. IL PODIO
        # ==========================================
        st.markdown(f"<h3 style='color: #000000; margin-bottom: 20px;'>Il Podio dell'edizione {int(anno_selezionato)}</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        try:
            with col1:
                st.metric(label="🥇 1° Classificato", 
                          value=df_anno.iloc[0].get("Rider", "N/D"), 
                          delta=df_anno.iloc[0].get("Time", "N/D"), 
                          delta_color="off")
            with col2:
                st.metric(label="🥈 2° Classificato", 
                          value=df_anno.iloc[1].get("Rider", "N/D"), 
                          delta=f"+ {df_anno.iloc[1].get('Gap', 'N/D')}", 
                          delta_color="inverse")
            with col3:
                st.metric(label="🥉 3° Classificato", 
                          value=df_anno.iloc[2].get("Rider", "N/D"), 
                          delta=f"+ {df_anno.iloc[2].get('Gap', 'N/D')}", 
                          delta_color="inverse")
        except Exception as e:
            st.warning("Dati del podio incompleti per questa edizione.")

        st.markdown("<br><hr style='border: 1px dashed #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)

        # ==========================================
        # 4. GRAFICI E METRICHE
        # ==========================================
        st.markdown("<h4 style='color: #000000;'>Dinamiche e Performance</h4>", unsafe_allow_html=True)
        col_stat1, col_stat2 = st.columns(2, gap="large")
        
        vincitore_anno = df_anno.iloc[0]
        # Check di sicurezza sui tempi
        tempi_validi = pd.notna(vincitore_anno.get('TotalSeconds')) and vincitore_anno.get('TotalSeconds', 0) > 0
        
        with col_stat1:
            # Titolo impostato su bianco (#FFFFFF)
            st.markdown("<p style='font-weight: bold; color: #FFFFFF;'>I distacchi della Top 10 (in minuti)</p>", unsafe_allow_html=True)
            
            if tempi_validi:
                df_top10 = df_anno.head(10).copy()
                
                # --- CONVERSIONE IN MINUTI ---
                df_top10['Gap (Minuti)'] = df_top10['GapSeconds'] / 60
                
                # --- TRUCCO PER L'ORDINAMENTO ---
                # 1. Ci assicuriamo che il Rank sia un numero intero pulito
                df_top10['Rank_Int'] = pd.to_numeric(df_top10['Rank'], errors='coerce').fillna(0).astype(int)
                
                # 2. Creiamo una nuova etichetta combinando Posizione (con zfill a 2 cifre) e Nome
                df_top10['Rider_Label'] = df_top10['Rank_Int'].astype(str).str.zfill(2) + "° " + df_top10['Rider']
                
                # 3. Impostiamo questa nuova colonna come indice per il grafico
                df_top10.set_index('Rider_Label', inplace=True)
                
                # Ora il grafico li ordinerà da 01° a 10° usando la colonna in minuti
                # AGGIUNTA: color="#FFCC00" per fare le barre gialle!
                st.bar_chart(df_top10['Gap (Minuti)'].fillna(0), color="#FFCC00")
            else:
                st.info("ℹ️ I dati sui distacchi cronometrici non sono disponibili per questa edizione.")
        with col_stat2:
            # 1. Titolo bianco (#FFFFFF)
            st.markdown("<p style='font-weight: bold; color: #FFFFFF;'>Storico del distacco tra 1° e 10° Classificato</p>", unsafe_allow_html=True)
            
            # --- CSS PER LO SLIDER GIALLO ---
            # Andiamo a "colorare" la barra e i pallini dello slider
            st.markdown("""
                <style>
                /* Colore del pallino dello slider */
                .stSlider [data-baseweb="slider"] [role="slider"] {
                    background-color: #FFCC00 !important;
                }
                /* Colore della barra riempita */
                .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] > div > div > div {
                    background-color: #FFCC00 !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Preparazione dei dati base
            df_gap_storico = df_storico.copy()
            df_gap_storico['Rank_Int'] = pd.to_numeric(df_gap_storico['Rank'], errors='coerce')
            df_decimi = df_gap_storico[df_gap_storico['Rank_Int'] == 10].copy()
            
            df_decimi = df_decimi[df_decimi['GapSeconds'].notna()]
            df_decimi = df_decimi[df_decimi['GapSeconds'] > 0]
            df_decimi['Gap (Minuti)'] = df_decimi['GapSeconds'] / 60
            
            df_chart = df_decimi[['Year', 'Gap (Minuti)']].dropna()
            
            # SLIDER PER IL RANGE DI ANNI
            min_year_disp = int(df_chart['Year'].min())
            max_year_disp = int(df_chart['Year'].max())
            
            range_anni = st.slider(
                "Seleziona il periodo storico da visualizzare:",
                min_value=min_year_disp,
                max_value=max_year_disp,
                value=(min_year_disp, max_year_disp) 
            )
            
            # Filtriamo il dataframe in base agli anni scelti con lo slider
            df_chart_filtered = df_chart[(df_chart['Year'] >= range_anni[0]) & (df_chart['Year'] <= range_anni[1])]
            
            # 4. Creiamo il grafico base con Altair (Linea GIALLA: #FFCC00)
            linea_storico = alt.Chart(df_chart_filtered).mark_line(color='#FFCC00', strokeWidth=2).encode(
                x=alt.X('Year:Q', 
                        title='Anno', 
                        axis=alt.Axis(format='d'), 
                        scale=alt.Scale(domain=[range_anni[0], range_anni[1]])),
                y=alt.Y('Gap (Minuti):Q', title='Gap (Minuti)')
            )
            
            # 4.1 Punti interattivi su tutta la linea (Punti GIALLI: #FFCC00)
            punti_storico = alt.Chart(df_chart_filtered).mark_circle(color='#FFCC00', size=50).encode(
                x=alt.X('Year:Q', scale=alt.Scale(domain=[range_anni[0], range_anni[1]])),
                y=alt.Y('Gap (Minuti):Q'),
                tooltip=[
                    alt.Tooltip('Year:Q', title='Anno', format='d'),
                    alt.Tooltip('Gap (Minuti):Q', title='Distacco (min)', format='.1f')
                ]
            )
            
            # 5. Punto rosso e linea tratteggiata per l'anno selezionato
            df_anno_sel = df_chart[df_chart['Year'] == int(anno_selezionato)]
            
            punto_rosso = alt.Chart(df_anno_sel).mark_circle(color='red', size=120, opacity=1).encode(
                x='Year:Q',
                y='Gap (Minuti):Q',
                tooltip=[
                    alt.Tooltip('Year:Q', title='Anno Selezionato', format='d'),
                    alt.Tooltip('Gap (Minuti):Q', title='Distacco (min)', format='.1f')
                ]
            )
            
            linea_vert_rossa = alt.Chart(df_anno_sel).mark_rule(color='red', strokeDash=[5, 5]).encode(
                x='Year:Q'
            )
            
            # 6. Sovrapposizione finale
            grafico_completo = alt.layer(linea_storico, punti_storico, linea_vert_rossa, punto_rosso).configure_view(strokeWidth=0)
            
            # Mostriamo il grafico
            st.altair_chart(grafico_completo, use_container_width=True)
        st.markdown("<hr style='border: 1px dashed #ccc; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        c_met1, c_met2, c_met3 = st.columns(3)
        c_met1.metric("Distanza Totale", f"{vincitore_anno.get('Distance (km)', 'N/D')} km")
        c_met2.metric("Numero di Tappe", vincitore_anno.get('Number of stages', 'N/D'))
        
        if tempi_validi:
            ore_totali = vincitore_anno['TotalSeconds'] / 3600
            vel_media = vincitore_anno['Distance (km)'] / ore_totali
            c_met3.metric("Velocità Media Vincitore", f"{vel_media:.1f} km/h")
        else:
            c_met3.metric("Velocità Media Vincitore", "N/D")

        # ==========================================
        # 5. TABELLA DATI COMPLETI
        # ==========================================
        st.markdown("<h4 style='color: #000000; margin-top: 30px;'>Dati Completi dell'Edizione</h4>", unsafe_allow_html=True)
        st.dataframe(df_anno, use_container_width=True, hide_index=True)

    else:
        st.warning("Impossibile caricare i dati. Assicurati che il link sia corretto e il file accessibile.")


elif st.session_state.pagina_corrente == "corridori":
    # ==========================================
    # 1. CSS PER LA TENDINA NERA (COERENZA UI)
    # ==========================================
    st.markdown("""
        <style>
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
        .stSelectbox label {
            color: #000000 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🏆 I Campioni della Grande Boucle</h2>", unsafe_allow_html=True)

    # ==========================================
    # 2. SELEZIONE ATLETA DA DF_TOUR_W
    # ==========================================
    if not df_tour_w.empty:
        # Creiamo la lista dalla colonna Winner
        lista_campioni = sorted(df_tour_w['Winner'].dropna().unique())
        
        col_sel, _ = st.columns([1.5, 2])
        with col_sel:
            vincitore_scelto = st.selectbox("Seleziona un vincitore:", lista_campioni)
        
        st.markdown("<hr style='border: 1px solid #ccc; margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)

        # ==========================================
        # 3. FILTRAGGIO DATI VITTORIE
        # ==========================================
        # Filtriamo TUTTE le righe del vincitore per contare gli anni
        storico_vittorie = df_tour_w[df_tour_w['Winner'] == vincitore_scelto].sort_values('Year')
        
        numero_vittorie = len(storico_vittorie)
        anni_vittoria = ", ".join(storico_vittorie['Year'].astype(str).tolist())
        
        # Per i dati biometrici prendiamo l'ultima riga (la vittoria più recente)
        dati_vincitore = storico_vittorie.iloc[-1]

        # ==========================================
        # 4. VISUALIZZAZIONE DATI TECNICI (COLONNE)
        # ==========================================
        col_bio, col_pps = st.columns([1.2, 2], gap="large")

        with col_bio:
            # Box Carta d'Identità (ora include il numero di vittorie e gli anni)
            st.markdown(f"""
                <div style="background-color: #000000; padding: 20px; border-radius: 10px; border-left: 8px solid #FFCC00;">
                    <h3 style="color: #FFCC00; margin-bottom: 5px;">{vincitore_scelto}</h3>
                    <p style="color: #ffffff; font-size: 1.1rem; margin-bottom: 2px;"><b>Paese:</b> {dati_vincitore.get('Country', 'N/D')}</p>
                    <p style="color: #ffffff; font-size: 0.9rem; font-style: italic;">{dati_vincitore.get('Team', 'Team N/D')}</p>
                    
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- PARAMETRI BIOMETRICI ---
            st.markdown("<h4 style='color: #000;'>Dati Antropometrici</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)

            # 1. Gestione Altezza (Correzione virgola e precisione a 2 decimali)
            raw_h = str(dati_vincitore.get('height_(m)', '0')).replace(',', '.')

            try:
                val_h = float(raw_h)
                
                if val_h > 10: 
                    s_h = str(int(val_h))
                    txt_altezza = f"{s_h[0]}.{s_h[1:3]} m" 
                else:
                    txt_altezza = f"{val_h:.2f} m"
            except:
                txt_altezza = "N/D"

            # 2. Gestione Peso
            try:
                val_peso = float(str(dati_vincitore.get('weight_(Kg)', '0')).replace(',', '.'))
                txt_peso = f"{val_peso:.1f} kg" 
            except:
                txt_peso = "N/D"

            # Visualizzazione nelle colonne
            c1.metric("Altezza", txt_altezza)
            c1.metric("Peso", txt_peso)

            # 3. Età e BMI
            try:
                eta = int(dati_vincitore.get('age', 0))
                c2.metric("Età", f"{eta} anni")
            except:
                c2.metric("Età", "N/D")

            try:
                bmi_val = float(str(dati_vincitore.get('BMI', 0)).replace(',', '.'))
                c2.metric("BMI", f"{bmi_val:.1f}")
            except:
                c2.metric("BMI", "N/D")
                    
        with col_pps:
            # --- PROFILO DI POTENZA (PPS) ---
            st.markdown("<h4 style='color: #000;'>Analisi Tecnica (PPS)</h4>", unsafe_allow_html=True)
            tipo_pps = dati_vincitore.get('rider_type_(PPS)', 'N/D')
            simile_pps = dati_vincitore.get('close_rider_type_(PPS)', 'N/D')

            st.markdown(f"""
                <div style="background-color: #E6E1CF; padding: 20px; border-radius: 5px; color: #000; border: 1px solid #999;">
                    <p style="margin-bottom: 10px;"><b> Rider Type:</b><br><span style="font-size: 1.3rem; font-weight: bold; color: #d4af37;">{tipo_pps}</span></p>
                    <p style="margin-bottom: 0;"><b>Close Rider Type:</b><br><span>{simile_pps}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # 5. CARRIERA COMPLETA IN FONDO (Larghezza intera)
        # ==========================================
        # ==========================================
        # 5. CARRIERA COMPLETA E CONFRONTO (Grafico Interattivo)
        # ==========================================
        st.markdown("<hr style='border: 1px dashed #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #000; font-weight: bold;'>Analisi Comparativa della Carriera</h4>", unsafe_allow_html=True)
        
        # 1. Normalizziamo il nome del ciclista principale
        nome_principale = str(vincitore_scelto).strip().upper()
        
        # 2. Creiamo una lista pulita di tutti i corridori per il menu a tendina
        df_storico['Rider_Norm'] = df_storico['Rider'].astype(str).str.strip().str.upper()
        tutti_i_corridori = sorted(df_storico['Rider'].astype(str).str.strip().unique())
        
        # 3. Selezione sfidanti (Multi-selezione)
        st.markdown("""
            <style>
            div[data-testid="stMultiSelect"] label p {
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 1.1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        sfidanti = st.multiselect(
            "Aggiungi altri ciclisti al grafico per un confronto testa a testa:", 
            options=[c for c in tutti_i_corridori if str(c).strip().upper() != nome_principale],
            help="Seleziona uno o più nomi dall'archivio storico"
        )
        
        # 4. Prepariamo la lista di tutti i nomi da cercare (Principale + Sfidanti)
        nomi_da_cercare = [nome_principale] + [str(s).strip().upper() for s in sfidanti]
        
        # 5. Funzione di ricerca elastica per più nomi contemporaneamente
        def match_multiplo(nome_db):
            for nome in nomi_da_cercare:
                if nome in nome_db or nome_db in nome:
                    return True
            return False
            
        # Filtriamo il database storico
        maschera_ricerca = df_storico['Rider_Norm'].apply(match_multiplo)
        df_plot = df_storico[maschera_ricerca].copy()
        
        if not df_plot.empty:
            # Convertiamo il Rank in formato numerico (fondamentale per l'asse Y)
            # errors='coerce' trasforma eventuali testi come "DNF" (Ritirato) in NaN
            df_plot['Rank_Num'] = pd.to_numeric(df_plot['Rank'], errors='coerce')
            
            # Filtriamo le righe valide per il grafico
            df_grafico = df_plot.dropna(subset=['Rank_Num'])
            
            # --- CREAZIONE GRAFICO ALTAIR ---
            grafico_carriera = alt.Chart(df_grafico).mark_line(
                point=alt.OverlayMarkDef(size=80, opacity=1, filled=True), 
                strokeWidth=3
            ).encode(
                x=alt.X('Year:O', title='Anno', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Rank_Num:Q', title='Posizione Finale', scale=alt.Scale(reverse=True, domainMin=1)),
                color=alt.Color('Rider:N', title='Atleta', scale=alt.Scale(scheme='set1')),
                # Il Tooltip genera la finestra riassuntiva al passaggio del mouse
                tooltip=[
                    alt.Tooltip('Rider:N', title='Ciclista'),
                    alt.Tooltip('Year:O', title='Anno'),
                    alt.Tooltip('Rank:N', title='Classifica Generale'),
                    alt.Tooltip('Team:N', title='Squadra'),
                    alt.Tooltip('Times:N', title='Tempo') # Se la tua colonna si chiama 'Times', correggi qui
                ]
            ).properties(
                height=450
            ).interactive() # Permette di zoomare e spostarsi nel grafico
            
            # Mostriamo il grafico
            st.altair_chart(grafico_carriera, use_container_width=True)
            
            
    else:
        st.warning("Caricamento del dataset vincitori non riuscito.")


elif st.session_state.pagina_corrente == "tappe":
    st.title("🗺️ Tappe del Tour")
    st.write("Pagina in costruzione...")
    
    st.markdown("<p style='font-weight: bold; color: #333;'>L'evoluzione della Velocità Media (Storico)</p>", unsafe_allow_html=True)
    df_vincitori = df_storico[(df_storico['Rank'] == 1) | (df_storico['Rank'] == '1')].copy()
            
            # Filtro globale per eliminare gli anni con dati difettosi sul tempo
    df_vincitori = df_vincitori[df_vincitori['TotalSeconds'].notna()]
    df_vincitori = df_vincitori[df_vincitori['TotalSeconds'] > 0]
            
    df_vincitori['Velocità Media (km/h)'] = df_vincitori['Distance (km)'] / (df_vincitori['TotalSeconds'] / 3600)
    df_vincitori.set_index('Year', inplace=True)
    df_vincitori.sort_index(inplace=True)
            
    st.line_chart(df_vincitori['Velocità Media (km/h)'])

elif st.session_state.pagina_corrente == "teams":
    st.title("👥 Squadre Partecipanti")
    st.write("Pagina in costruzione...")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. MENU LATERALE (SIDEBAR)
# ==========================================
#with st.sidebar:
#    st.title("≡ Filtri globali")
#   st.selectbox("Seleziona Nazionalità:", ["Tutte", "Italia", "Francia", "Spagna"])
#    st.checkbox("Mostra solo i team World Tour")