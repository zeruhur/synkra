import streamlit as st
import pandas as pd
import random
import datetime
import hashlib
import os
import base64

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SYNOPTRA - The 25 Mirrors",
    page_icon="⚪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CSS AGGIORNATO (STILE SYNOPTRA + BOX QUADRATI + HOME)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. Stile Base Card */
    .glyph-box {
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 4px; 
        padding: 15px;
        text-align: center;
        background-color: #FFFFFF;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        max-width: 320px; 
        margin-left: auto;
        margin-right: auto;
    }
    .glyph-box:hover {
        transform: translateY(-3px);
        border-color: #000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* 2. IL QUADRATO VIRTUALE */
    .glyph-img-container {
        width: 100%;             
        aspect-ratio: 1 / 1;     /* Forza proporzione quadrata */
        background-color: #FAFAFA;
        border: 1px solid #EEEEEE;
        border-radius: 2px;
        display: flex;           
        justify-content: center; 
        align-items: center;     
        margin-bottom: 12px;
        overflow: hidden;        
    }
    
    /* 3. L'Immagine dentro il quadrato */
    .glyph-img {
        max-width: 70%;          
        max-height: 70%;         
        width: auto;
        height: auto;
        object-fit: contain;     
    }

    /* Tipografia */
    .glyph-name {
        font-family: 'Space Mono', monospace, sans-serif;
        font-size: 1.15em;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
        color: #111;
    }
    .glyph-cat {
        font-size: 0.7em;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #777;
        margin-bottom: 6px;
        font-weight: 600;
    }
    
    /* Stile Home Page & Manuale */
    .hero-text {
        font-size: 1.15em;
        line-height: 1.65;
        color: #222;
        margin-bottom: 25px;
        border-left: 3px solid #111;
        padding-left: 20px;
        background-color: #F9F9F9;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .dimension-box {
        border: 1px solid #222;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 0.85em;
        letter-spacing: 0.5px;
        background-color: #FFF;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DATABASE (DATI AGGIORNATI DAL HANDBOOK)
# -----------------------------------------------------------------------------
GLYPHS = [
    # TRASFORMAZIONE (T) - Form: Circle
    {
        "id": 1, "code": "T1", "initial": "G", "nome": "GERMA", "concetto": "Seme",
        "cat": "TRASFORMAZIONE", "visual": "Cerchio con un punto al centro",
        "desc": "Potenziale latente, inizio non ancora manifesto, promessa da custodire.",
        "shadow": "Attesa senza fine, potenziale che non diventa mai realtà."
    },
    {
        "id": 2, "code": "T2", "initial": "B", "nome": "BREKA", "concetto": "Frattura",
        "cat": "TRASFORMAZIONE", "visual": "Cerchio con un varco in alto",
        "desc": "Rottura necessaria di una forma di sé, crisi che apre nuove possibilità.",
        "shadow": "Crollo fine a se stesso, distruzione che non apre nulla."
    },
    {
        "id": 3, "code": "T3", "initial": "U", "nome": "UMVEL", "concetto": "Crisalide",
        "cat": "TRASFORMAZIONE", "visual": "Cerchio con una linea ondulata interna",
        "desc": "Trasformazione interna e invisibile, incubazione protetta.",
        "shadow": "Chiusura, il rifugio che diventa guscio o prigione."
    },
    {
        "id": 4, "code": "T4", "initial": "E", "nome": "EMRAL", "concetto": "Emersione",
        "cat": "TRASFORMAZIONE", "visual": "Cerchio con linea dal centro oltre il bordo",
        "desc": "Nuova forma di sé che si manifesta nel mondo e viene alla luce.",
        "shadow": "Esposizione prematura, mostrare qualcosa prima che sia pronto."
    },
    {
        "id": 5, "code": "T5", "initial": "A", "nome": "ASKOR", "concetto": "Cenere",
        "cat": "TRASFORMAZIONE", "visual": "Due cerchi concentrici",
        "desc": "Ciclo completato, la fine che nutre il nuovo inizio.",
        "shadow": "Attaccamento a ciò che è finito, conservare le ceneri anziché concimare."
    },

    # RELAZIONE (R) - Form: Mandorla
    {
        "id": 6, "code": "R1", "initial": "L", "nome": "LIMYR", "concetto": "Soglia",
        "cat": "RELAZIONE", "visual": "Mandorla con un punto al centro",
        "desc": "Confine tra sé e l'altro che diventa invito all'incontro.",
        "shadow": "Barriera difensiva, muro che impedisce ogni contatto."
    },
    {
        "id": 7, "code": "R2", "initial": "D", "nome": "DISTEN", "concetto": "Abisso",
        "cat": "RELAZIONE", "visual": "Mandorla con un varco in alto",
        "desc": "Distanza e differenza che emergono tra sé e l'altro.",
        "shadow": "Separazione rigida, incomprensione che si indurisce."
    },
    {
        "id": 8, "code": "R3", "initial": "M", "nome": "MIREN", "concetto": "Specchio",
        "cat": "RELAZIONE", "visual": "Mandorla con una linea ondulata interna",
        "desc": "Riconoscimento reciproco, vedere parti di sé nell'altro.",
        "shadow": "Proiezione cieca, attribuire all'altro ciò che rifiutiamo in noi."
    },
    {
        "id": 9, "code": "R4", "initial": "T", "nome": "THEKNA", "concetto": "Nodo",
        "cat": "RELAZIONE", "visual": "Mandorla con linea dal centro oltre il bordo",
        "desc": "Legame dichiarato, impegno reciproco reso visibile.",
        "shadow": "Legame che soffoca, dipendenza o trappola."
    },
    {
        "id": 10, "code": "R5", "initial": "S", "nome": "SONAL", "concetto": "Risonanza",
        "cat": "RELAZIONE", "visual": "Due mandorle concentriche",
        "desc": "Armonia matura, due distinte identità in piena sintonia.",
        "shadow": "Fusione simbiotica, perdita della propria voce individuale."
    },

    # MOVIMENTO (M) - Form: Triangle
    {
        "id": 11, "code": "M1", "initial": "R", "nome": "RADHEN", "concetto": "Radice",
        "cat": "MOVIMENTO", "visual": "Triangolo con un punto al centro",
        "desc": "Stabilità scelta, accumulo di forza nel rimanere fermi.",
        "shadow": "Rigidità, ostinazione nel non volersi muovere."
    },
    {
        "id": 12, "code": "M2", "initial": "J", "nome": "JEKTA", "concetto": "Salto",
        "cat": "MOVIMENTO", "visual": "Triangolo con un varco nel vertice",
        "desc": "Rischio consapevole, rottura dal percorso previsto per evolvere.",
        "shadow": "Impulsività sconsiderata, fuga da un problema anziché scelta."
    },
    {
        "id": 13, "code": "M3", "initial": "F", "nome": "FLUEN", "concetto": "Corrente",
        "cat": "MOVIMENTO", "visual": "Triangolo con una linea ondulata interna",
        "desc": "Flusso naturale, adattamento alle forze circostanti.",
        "shadow": "Deriva passiva, lasciarsi trasportare senza direzione o timone."
    },
    {
        "id": 14, "code": "M4", "initial": "V", "nome": "VEKTOR", "concetto": "Sentiero",
        "cat": "MOVIMENTO", "visual": "Triangolo con linea dal centro oltre il vertice",
        "desc": "Direzione deliberata, progressione consapevole verso una meta.",
        "shadow": "Visione a tunnel, percorrere una rotta che ha perso senso."
    },
    {
        "id": 15, "code": "M5", "initial": "C", "nome": "CYRKEL", "concetto": "Ritorno",
        "cat": "MOVIMENTO", "visual": "Due triangoli concentrici",
        "desc": "Ritorno al punto di partenza arricchiti dal viaggio svolto.",
        "shadow": "Movimento circolare sterile, ripercorrere sempre gli stessi errori."
    },

    # CONOSCENZA (K) - Form: Rhombus
    {
        "id": 16, "code": "K1", "initial": "H", "nome": "HULMEN", "concetto": "Velo",
        "cat": "CONOSCENZA", "visual": "Rombo con un punto al centro",
        "desc": "Mistero necessario, ciò che è nascosto e protetto per maturarne la visione.",
        "shadow": "Diniego, mantenere il velo per evitare la verità."
    },
    {
        "id": 17, "code": "K2", "initial": "Q", "nome": "QUERIK", "concetto": "Labirinto",
        "cat": "CONOSCENZA", "visual": "Rombo con un varco in alto",
        "desc": "Perdita della mappa iniziale, disorientamento che attiva la vera ricerca.",
        "shadow": "Confusione mentale sterile, perdersi nei dettagli senza uscire."
    },
    {
        "id": 18, "code": "K3", "initial": "I", "nome": "IKNOR", "concetto": "Traccia",
        "cat": "CONOSCENZA", "visual": "Rombo con una linea ondulata interna",
        "desc": "Comprensione progressiva ricavata da segni e indizi parziali.",
        "shadow": "Tracce false, pettegolezzi o supposizioni prese per certezza."
    },
    {
        "id": 19, "code": "K4", "initial": "K", "nome": "KLAVEN", "concetto": "Chiave",
        "cat": "CONOSCENZA", "visual": "Rombo con linea dal centro oltre il vertice",
        "desc": "Insight illuminante, intuizione che sblocca la comprensione.",
        "shadow": "Presunzione di aver capito tutto, forzare una sola spiegazione ovunque."
    },
    {
        "id": 20, "code": "K5", "initial": "O", "nome": "OKULAR", "concetto": "Testimone",
        "cat": "CONOSCENZA", "visual": "Due rombi concentrici",
        "desc": "Sguardo consapevole, osservazione pura e senza giudizio.",
        "shadow": "Distacco freddo, diventare spettatore passivo della propria vita."
    },

    # INTEGRAZIONE (I) - Form: Square
    {
        "id": 21, "code": "I1", "initial": "Z", "nome": "ZERAN", "concetto": "Vuoto",
        "cat": "INTEGRAZIONE", "visual": "Quadrato con un punto al centro",
        "desc": "Spazio libero ed essenziale che si apre per accogliere il nuovo.",
        "shadow": "Vuoto vissuto come privazione, angoscia da assenza."
    },
    {
        "id": 22, "code": "I2", "initial": "P", "nome": "PARTEN", "concetto": "Frammento",
        "cat": "INTEGRAZIONE", "visual": "Quadrato con un varco in alto",
        "desc": "Separazione di una parte per trovare una sua specifica identità.",
        "shadow": "Frammentazione dolorosa, sentirsi spezzati o scollegati."
    },
    {
        "id": 23, "code": "I3", "initial": "N", "nome": "NEXAL", "concetto": "Fulcro",
        "cat": "INTEGRAZIONE", "visual": "Quadrato con una linea ondulata interna",
        "desc": "Ricerca dinamica di equilibrio tra forze contrapposte.",
        "shadow": "Paralisi decisionale per il timore di sbilanciare l'insieme."
    },
    {
        "id": 24, "code": "I4", "initial": "X", "nome": "XUNDA", "concetto": "Trabocco",
        "cat": "INTEGRAZIONE", "visual": "Quadrato con linea dal centro oltre il bordo",
        "desc": "Pienezza straripante, abbondanza e creatività che chiedono sfogo.",
        "shadow": "Sopraffazione emotiva o eccesso che rompe l'equilibrio."
    },
    {
        "id": 25, "code": "I5", "initial": "W", "nome": "WEVAN", "concetto": "Tessuto",
        "cat": "INTEGRAZIONE", "visual": "Due quadrati concentrici",
        "desc": "Integrazione riuscita, le diverse componenti formano una trama solida.",
        "shadow": "Rete soffocante, trappola di legami che impedisce la libertà."
    }
]

# -----------------------------------------------------------------------------
# 4. STATO E FUNZIONI
# -----------------------------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'quiz_mode' not in st.session_state:
    st.session_state['quiz_mode'] = {'active': False, 'current': None, 'revealed': False, 'score': 0}

def get_glyph_card(glyph, context=""):
    """
    Renderizza la card del glifo verificando la presenza di SVG o PNG nelle cartelle glyphs o assets.
    """
    code_str = glyph.get('code', '')
    name_str = glyph['nome'].upper()

    # Tentativi di caricamento file immagini
    candidate_paths = [
        os.path.join("glyphs", f"{code_str}_{name_str}.svg"),
        os.path.join("glyphs", f"{code_str}_{name_str}.png"),
        os.path.join("assets", "glyphs", f"{name_str}.svg")
    ]

    img_html = ""
    loaded = False
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                ext = "svg+xml" if path.endswith(".svg") else "png"
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                    img_html = f'<img src="data:image/{ext};base64,{encoded}" class="glyph-img">'
                    loaded = True
                    break
            except:
                pass
    
    if not loaded:
        img_html = f"<div style='font-size:2.2em; font-family:monospace; font-weight:bold; color:#444;'>{glyph.get('initial', glyph['nome'][:1])}</div>"

    ombra_html = ""
    if context == "full":
        ombra_html = f'<div style="font-size:0.75em; border-top:1px solid #eee; padding-top:8px; margin-top:8px; color:#666; font-style:italic;"><b>Ombra:</b> {glyph["shadow"]}</div>'

    code_badge = f" • <b>{code_str}</b>" if code_str else ""

    html = f"""
    <div class="glyph-box">
        <div class="glyph-cat">{glyph['cat']}{code_badge}</div>
        <div class="glyph-img-container">
            {img_html}
        </div>
        <div class="glyph-name">{glyph['nome']}</div>
        <div style="font-weight: bold; font-size: 0.9em; margin-bottom: 6px; color:#222;">{glyph['concetto']}</div>
        <div style="font-size: 0.8em; line-height: 1.35; color: #444; margin-bottom: 5px;">{glyph['desc']}</div>
        {ombra_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def add_to_history(glyph_list, method):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    names = ", ".join([f"{g['nome']} ({g['code']})" for g in glyph_list])
    st.session_state['history'].append({"Data": timestamp, "Metodo": method, "Glifi": names})

# -----------------------------------------------------------------------------
# 5. LAYOUT APPLICAZIONE E SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("SYNOPTRA")
st.sidebar.caption("The 25 Mirrors • I Venticinque Specchi")
menu = st.sidebar.radio("Navigazione", 
    ["Introduzione", "Archivio", "Oracolo", "Risonanza", "Addestramento", "Diario", "Manuale"])

st.sidebar.divider()
st.sidebar.caption("Strumento di auto-riflessione simbolica")

# =============================================================================
# SEZIONE: INTRODUZIONE (HOME PAGE)
# =============================================================================
if menu == "Introduzione":
    st.title("SYNOPTRA")
    st.subheader("I Venticinque Specchi • The 25 Mirrors")
    st.markdown("---")
    
    st.markdown("""
    <div class="hero-text">
        SYNOPTRA è un sistema di auto-riflessione simbolica fondato sui principi junghiani 
        di <b>proiezione archetipica</b> e <b>sincronicità</b>. 
        <br><br>
        Nasce con un impegno esplicito all'onestà intellettuale: non dichiara false origini antiche 
        né si appropria di simbolismi culturali altrui. L'estrazione di un simbolo non è una predizione 
        futura, ma uno <b>specchio per l'inconscio</b> che permette di riconoscere dinamiche 
        interiori altrimenti inaccessibili.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.subheader("La Matrice 5×5")
    st.markdown("Il sistema organizza 25 glifi geometrici nell'intersezione tra **5 Dimensioni dell'esperienza** e **5 Fasi del cambiamento**:")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown('<div class="dimension-box">T • Trasformazione<br><small style="text-transform:none;font-weight:normal;">Cerchio</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="dimension-box">R • Relazione<br><small style="text-transform:none;font-weight:normal;">Mandorla</small></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="dimension-box">M • Movimento<br><small style="text-transform:none;font-weight:normal;">Triangolo</small></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="dimension-box">K • Conoscenza<br><small style="text-transform:none;font-weight:normal;">Rombo</small></div>', unsafe_allow_html=True)
    with c5: st.markdown('<div class="dimension-box">I • Integrazione<br><small style="text-transform:none;font-weight:normal;">Quadrato</small></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    | Fase | Nome | Segno sulla forma base | Senso del processo |
    | :--- | :--- | :--- | :--- |
    | **1** | **Latenza** | Punto al centro | Potenziale presente ma non ancora attivo |
    | **2** | **Crisi** | Varco nel contorno in alto | Rottura o apertura necessaria |
    | **3** | **Processo** | Linea ondulata interna | Lavoro profondo, invisibile dall'esterno |
    | **4** | **Manifestazione** | Linea che esce dal centro | Emersione nella luce, forma resa visibile |
    | **5** | **Compimento** | Copia concentrica | Chiusura del ciclo e integrazione |
    """)

    st.markdown("---")
    st.info("👈 **Come iniziare**: Consulta l'**Archivio** per studiare la matrice completa, usa **Oracolo** per condurre una lettura con gli stesi ufficiali, o esplora il **Manuale** completo.")

# =============================================================================
# SEZIONE: ARCHIVIO
# =============================================================================
elif menu == "Archivio":
    st.title("Archivio")
    st.markdown("La matrice completa dei 25 specchi.")
    
    col_search, col_cat, col_phase = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input("Cerca glifo", placeholder="Nome, codice, concetto o descrizione...")
    with col_cat:
        cat_filter = st.selectbox("Dimensione", ["Tutte", "TRASFORMAZIONE", "RELAZIONE", "MOVIMENTO", "CONOSCENZA", "INTEGRAZIONE"])
    with col_phase:
        phase_filter = st.selectbox("Fase", ["Tutte", "1 - Latenza", "2 - Crisi", "3 - Processo", "4 - Manifestazione", "5 - Compimento"])

    filtered_glyphs = GLYPHS.copy()

    if cat_filter != "Tutte":
        filtered_glyphs = [g for g in filtered_glyphs if g['cat'] == cat_filter]

    if phase_filter != "Tutte":
        p_num = phase_filter.split(" ")[0]
        filtered_glyphs = [g for g in filtered_glyphs if g['code'].endswith(p_num)]

    if search:
        s = search.lower()
        filtered_glyphs = [
            g for g in filtered_glyphs 
            if s in g['nome'].lower() or s in g['concetto'].lower() or s in g['cat'].lower() or s in g['code'].lower() or s in g['desc'].lower() or s in g['shadow'].lower()
        ]

    st.caption(f"Visualizzati: {len(filtered_glyphs)} di 25 glifi")
    
    # Matrice
    columns_num = 5 
    cols = st.columns(columns_num)
    
    for i, glyph in enumerate(filtered_glyphs):
        with cols[i % columns_num]:
            get_glyph_card(glyph, context="full")

# =============================================================================
# SEZIONE: ORACOLO (LO SPECCHIO)
# =============================================================================
elif menu == "Oracolo":
    st.title("Lo Specchio (Oracolo)")
    st.markdown("Formula una domanda aperta e focalizzata prima di estrarre i glifi.")
    
    stedi_options = [
        "Focus (1 Glifo)", 
        "Triade del Tempo (3 Glifi: Passato, Presente, Tendenza)", 
        "Triade del Nodo (3 Glifi: Situazione, Ostacolo, Risorsa)", 
        "Quincunx (5 Glifi: Centro, Sopra, Sotto, Sinistra, Destra)", 
        "Due Percorsi (3 Glifi: Opzione A, Elemento Comune, Opzione B)",
        "Il Ciclo (5 Glifi: Latenza -> Compimento)"
    ]
    
    method = st.selectbox("Seleziona lo Steso (Spread)", stedi_options)
    question = st.text_input("La tua domanda (opzionale):", placeholder="Es. Su cosa devo porre attenzione nel progetto attuale?")
    
    if st.button("Estrai Glifi", type="primary"):
        if question:
            st.markdown(f"> **Domanda:** *{question}*")
            
        if "Focus" in method:
            res = [random.choice(GLYPHS)]
            st.subheader("Il Focus")
            get_glyph_card(res[0], "full")
            
        elif "Triade del Tempo" in method:
            res = random.sample(GLYPHS, 3)
            st.subheader("Triade del Tempo")
            c1, c2, c3 = st.columns(3)
            with c1: st.caption("1. Passato (Origine)"); get_glyph_card(res[0], "full")
            with c2: st.caption("2. Presente (Attuale)"); get_glyph_card(res[1], "full")
            with c3: st.caption("3. Tendenza (Evoluzione)"); get_glyph_card(res[2], "full")
            
        elif "Triade del Nodo" in method:
            res = random.sample(GLYPHS, 3)
            st.subheader("Triade del Nodo")
            c1, c2, c3 = st.columns(3)
            with c1: st.caption("1. Situazione"); get_glyph_card(res[0], "full")
            with c2: st.caption("2. Ostacolo"); get_glyph_card(res[1], "full")
            with c3: st.caption("3. Risorsa"); get_glyph_card(res[2], "full")
            
        elif "Quincunx" in method:
            res = random.sample(GLYPHS, 5)
            st.subheader("Mappatura Quincunx")
            
            # Sopra
            _, c_top, _ = st.columns([1,1,1])
            with c_top: st.caption("Sopra (Ciò che si conosce)"); get_glyph_card(res[1], "full")
            
            # Sinistra, Centro, Destra
            c_left, c_mid, c_right = st.columns(3)
            with c_left: st.caption("Sinistra (Ciò che trattiene)"); get_glyph_card(res[3], "full")
            with c_mid: st.caption("Centro (Cuore della questione)"); get_glyph_card(res[0], "full")
            with c_right: st.caption("Destra (Ciò che spinge avanti)"); get_glyph_card(res[4], "full")
            
            # Sotto
            _, c_bot, _ = st.columns([1,1,1])
            with c_bot: st.caption("Sotto (Ciò che rimane nell'ombra)"); get_glyph_card(res[2], "full")
            
        elif "Due Percorsi" in method:
            res = random.sample(GLYPHS, 3)
            st.subheader("Steso Due Percorsi")
            c1, c2, c3 = st.columns(3)
            with c1: st.caption("Percorso A"); get_glyph_card(res[0], "full")
            with c2: st.caption("Elemento Comune"); get_glyph_card(res[1], "full")
            with c3: st.caption("Percorso B"); get_glyph_card(res[2], "full")

        elif "Il Ciclo" in method:
            res = random.sample(GLYPHS, 5)
            st.subheader("Steso Il Ciclo")
            cols = st.columns(5)
            labels = ["1. Latenza", "2. Crisi", "3. Processo", "4. Manifestazione", "5. Compimento"]
            for i in range(5):
                with cols[i]:
                    st.caption(labels[i])
                    get_glyph_card(res[i], "full")

        add_to_history(res, method)

# =============================================================================
# SEZIONE: RISONANZA
# =============================================================================
elif menu == "Risonanza":
    st.title("Risonanza")
    st.markdown("Calcola il glifo di risonanza derivato in modo deterministico dal tuo intento e da una data chiave.")
    
    col1, col2 = st.columns(2)
    with col1: name = st.text_input("Nome / Intento / Domanda")
    with col2: date = st.date_input("Data Chiave", min_value=datetime.date(1900,1,1))
    
    if st.button("Calcola Risonanza", type="primary") and name:
        h = hashlib.md5(f"{name.strip().lower()}{date}".encode()).hexdigest()
        idx = int(h, 16) % 25
        res_glyph = GLYPHS[idx]
        st.success(f"Glifo di Risonanza per: **{name}** ({date})")
        get_glyph_card(res_glyph, "full")

# =============================================================================
# SEZIONE: ADDESTRAMENTO
# =============================================================================
elif menu == "Addestramento":
    st.title("Addestramento Intuizione")
    st.markdown("Metti alla prova la tua memoria e intuizione sui 25 specchi.")
    
    st.metric("Punteggio Corretto", st.session_state['quiz_mode']['score'])
    
    if not st.session_state['quiz_mode']['active']:
        st.session_state['quiz_mode']['current'] = random.choice(GLYPHS)
        st.session_state['quiz_mode']['active'] = True
        st.session_state['quiz_mode']['revealed'] = False
        
    curr = st.session_state['quiz_mode']['current']
    
    # Renderizza il test del glifo
    code_str = curr.get('code', '')
    name_str = curr['nome'].upper()
    candidate_paths = [
        os.path.join("glyphs", f"{code_str}_{name_str}.svg"),
        os.path.join("glyphs", f"{code_str}_{name_str}.png"),
        os.path.join("assets", "glyphs", f"{name_str}.svg")
    ]

    img_html_content = ""
    loaded = False
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                ext = "svg+xml" if path.endswith(".svg") else "png"
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                    img_html_content = f'<img src="data:image/{ext};base64,{encoded}" class="glyph-img">'
                    loaded = True
                    break
            except:
                pass
                
    if not loaded:
        img_html_content = f"<div style='font-size:3em; font-family:monospace;'>?</div>"

    quiz_html = f"""
    <div style="max-width: 280px; margin: 0 auto; text-align:center;">
        <div class="glyph-img-container">
            {img_html_content}
        </div>
    </div>
    """
    st.markdown(quiz_html, unsafe_allow_html=True)
        
    st.caption(f"Dimensione: **{curr['cat']}** • Concetto: **{curr['concetto']}**")
    st.write("---")
    
    opts = random.sample([g['nome'] for g in GLYPHS if g['nome'] != curr['nome']], 3)
    opts.append(curr['nome'])
    random.shuffle(opts)
    
    if not st.session_state['quiz_mode']['revealed']:
        cols = st.columns(4)
        for i, o in enumerate(opts):
            if cols[i].button(o, use_container_width=True):
                if o == curr['nome']:
                    st.toast("Esatto! ✅", icon="✅")
                    st.session_state['quiz_mode']['score'] += 1
                else:
                    st.toast(f"Errato! Era {curr['nome']} ({curr['code']})", icon="❌")
                st.session_state['quiz_mode']['revealed'] = True
                st.rerun()
    else:
        st.info(f"Risposta Corretta: **{curr['nome']}** [{curr['code']}] - {curr['visual']}")
        if st.button("Prossimo Glifo"):
            st.session_state['quiz_mode']['active'] = False
            st.rerun()

# =============================================================================
# SEZIONE: DIARIO
# =============================================================================
elif menu == "Diario":
    st.title("Diario delle Letture")
    if st.session_state['history']:
        df = pd.DataFrame(st.session_state['history'])
        st.dataframe(df, use_container_width=True)
        
        all_g = []
        for x in st.session_state['history']:
            all_g.extend([n.strip() for n in x['Glifi'].split(',')])
        
        st.subheader("Frequenza Glifi Estratti")
        st.bar_chart(pd.Series(all_g).value_counts())
    else:
        st.info("Il diario delle letture è ancora vuoto. Effettua una consultazione nell'Oracolo per iniziare a registrarle.")

# =============================================================================
# SEZIONE: MANUALE (HANDBOOK REFERENCE)
# =============================================================================
elif menu == "Manuale":
    st.title("The SYNOPTRA Handbook")
    st.subheader("Guida Completa ai 25 Specchi")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["I Principi", "La Matrice 5x5", "Procedura di Lettura"])
    
    with tab1:
        st.markdown("""
        ### I Tre Principi Fondativi
        1. **Onestà Intellettuale**: Il glifo estratto non ha conoscenze soprannaturali e non predice il futuro. Offre un'immagine aperta alla proiezione del consultante.
        2. **Struttura a Matrice**: Ogni glifo nasce dall'intersezione di 1 Dimensione dell'esperienza (riga) e 1 Fase del cambiamento (colonna).
        3. **Doppio Volto (Luce e Ombra)**: Ogni simbolo possiede un polo generativo (Significato) e un ostacolo potenziale (Ombra). Nessun glifo è solo positivo o negativo.
        
        ### Le 5 Dimensioni
        - **TRASFORMAZIONE (Circle)**: L'identità che cambia, cicli di fine e inizio.
        - **RELAZIONE (Mandorla)**: Lo spazio condiviso tra sé e l'altro.
        - **MOVIMENTO (Triangle)**: L'azione, la direzione e la scelta di rotta.
        - **CONOSCENZA (Rhombus)**: La comprensione, l'osservazione e i misteri.
        - **INTEGRAZIONE (Square)**: La struttura e la relazione tra le parti e il tutto.
        """)
        
    with tab2:
        st.markdown("### Tabella di Riferimento Rapido dei 25 Glifi")
        df_glyphs = pd.DataFrame([{
            "Codice": g["code"],
            "Iniziale": g["initial"],
            "Nome": g["nome"],
            "Concetto": g["concetto"],
            "Dimensione": g["cat"],
            "Significato": g["desc"],
            "Ombra": g["shadow"]
        } for g in GLYPHS])
        st.dataframe(df_glyphs, use_container_width=True, height=500)

    with tab3:
        st.markdown("""
        ### La Procedura in 6 Passi
        1. **Formulare una domanda aperta** e annotarla sul diario con la data.
        2. **Estrarre i glifi** e posizionarli nello steso prescelto senza consultarli subito.
        3. **Osservare l'immagine** di ogni glifo e annotare la prima reazione d'istinto.
        4. **Valutare Significato e Ombra** per ciascun glifo e scegliere il polo attivo.
        5. **Analizzare la forma dello steso**: quali righe e fasi si ripetono o mancano.
        6. **Sintetizzare il messaggio** in una frase conclusiva e definire una piccola azione concreta.
        """)