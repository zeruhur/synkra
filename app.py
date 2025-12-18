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
    page_title="SYNKRA",
    page_icon="⚪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CSS AGGIORNATO (STILE SYNKRA + BOX QUADRATI + HOME)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. Stile Base Card */
    .glyph-box {
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 0px; 
        padding: 15px;
        text-align: center;
        background-color: transparent;
        transition: transform 0.2s;
        height: 100%;
        
        /* FIX ORACLE: Limita la larghezza massima della card e la centra */
        max-width: 320px; 
        margin-left: auto;
        margin-right: auto;
    }
    .glyph-box:hover {
        transform: translateY(-3px);
        border-color: #000;
    }

    /* 2. IL QUADRATO VIRTUALE */
    .glyph-img-container {
        width: 100%;             
        aspect-ratio: 1 / 1;     /* Forza proporzione quadrata */
        background-color: #FFFFFF;
        border: 1px solid #eee;
        display: flex;           
        justify-content: center; 
        align-items: center;     
        margin-bottom: 15px;
        overflow: hidden;        
    }
    
    /* 3. L'Immagine dentro il quadrato */
    .glyph-img {
        max-width: 65%;          
        max-height: 65%;         
        width: auto;
        height: auto;
        object-fit: contain;     
    }

    /* Tipografia */
    .glyph-name {
        font-family: 'Space Mono', monospace;
        font-size: 1.1em;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .glyph-cat {
        font-size: 0.7em;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #666;
        margin-bottom: 5px;
    }
    
    /* Stile Home Page */
    .hero-text {
        font-size: 1.2em;
        line-height: 1.6;
        color: #333;
        margin-bottom: 30px;
        border-left: 3px solid #000;
        padding-left: 20px;
    }
    .dimension-box {
        border: 1px solid #000;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DATABASE (DATI)
# -----------------------------------------------------------------------------
GLYPHS = [
    # TRASFORMAZIONE
    {"id": 1, "nome": "KEMRA", "concetto": "Seme", "cat": "TRASFORMAZIONE", "visual": "Punto al centro di cerchio aperto", "desc": "Potenziale latente, inizio non ancora manifestato, promessa.", "shadow": "Sterilità, incapacità di iniziare."},
    {"id": 2, "nome": "SKIRN", "concetto": "Frattura", "cat": "TRASFORMAZIONE", "visual": "Linea verticale spezzata", "desc": "Rottura necessaria, crisi che apre nuove possibilità.", "shadow": "Distruzione fine a se stessa."},
    {"id": 3, "nome": "LUTHEN", "concetto": "Crisalide", "cat": "TRASFORMAZIONE", "visual": "Ovale chiuso con linea ondulata", "desc": "Processo interno invisibile, transizione protetta.", "shadow": "Isolamento, stagnazione."},
    {"id": 4, "nome": "VRAEL", "concetto": "Emersione", "cat": "TRASFORMAZIONE", "visual": "Triangolo che rompe un cerchio", "desc": "Manifestazione, nascita di nuova forma.", "shadow": "Esposizione prematura, arroganza."},
    {"id": 5, "nome": "ASKOR", "concetto": "Cenere", "cat": "TRASFORMAZIONE", "visual": "Quadrato frammentato", "desc": "Ciclo completato, fine che nutre l'inizio.", "shadow": "Attaccamento al passato, lutto non risolto."},
    
    # RELAZIONE
    {"id": 6, "nome": "LIMYR", "concetto": "Soglia", "cat": "RELAZIONE", "visual": "Linee verticali con gap", "desc": "Confine tra sé e altro, spazio liminale.", "shadow": "Muri invalicabili o assenza di confini."},
    {"id": 7, "nome": "MIREN", "concetto": "Specchio", "cat": "RELAZIONE", "visual": "Triangoli opposti", "desc": "Riconoscimento reciproco, proiezione.", "shadow": "Narcisismo, incapacità di vedere l'altro."},
    {"id": 8, "nome": "THEKNA", "concetto": "Nodo", "cat": "RELAZIONE", "visual": "Due cerchi sovrapposti", "desc": "Legame complesso, intreccio che unisce o intrappola.", "shadow": "Dipendenza, soffocamento."},
    {"id": 9, "nome": "SONAL", "concetto": "Risonanza", "cat": "RELAZIONE", "visual": "Cerchi concentrici disallineati", "desc": "Armonia spontanea, sincronicità relazionale.", "shadow": "Eco vuoto, conformismo."},
    {"id": 10, "nome": "VORDEN", "concetto": "Abisso", "cat": "RELAZIONE", "visual": "Linee divergenti", "desc": "Distanza incolmabile, separazione radicale.", "shadow": "Abbandono, alienazione totale."},

    # MOVIMENTO
    {"id": 11, "nome": "RADHEN", "concetto": "Radice", "cat": "MOVIMENTO", "visual": "Linee verticali discendenti", "desc": "Ancoraggio, stabilità profonda.", "shadow": "Rigidità, incapacità di adattarsi."},
    {"id": 12, "nome": "FLUEN", "concetto": "Corrente", "cat": "MOVIMENTO", "visual": "Linea sinusoidale", "desc": "Flusso naturale, adattamento dinamico.", "shadow": "Passività, mancanza di direzione."},
    {"id": 13, "nome": "SPIREK", "concetto": "Vortice", "cat": "MOVIMENTO", "visual": "Spirale logaritmica", "desc": "Movimento ciclico intenso, essere trascinati.", "shadow": "Ossessione, perdita di controllo."},
    {"id": 14, "nome": "VEKTOR", "concetto": "Sentiero", "cat": "MOVIMENTO", "visual": "Linea retta con freccia", "desc": "Direzione deliberata, progressione consapevole.", "shadow": "Visione a tunnel, fanatismo."},
    {"id": 15, "nome": "KRESH", "concetto": "Salto", "cat": "MOVIMENTO", "visual": "Linea spezzata acuta", "desc": "Discontinuità improvvisa, rischio.", "shadow": "Impulsività sconsiderata, caduta."},

    # CONOSCENZA
    {"id": 16, "nome": "VELUM", "concetto": "Velo", "cat": "CONOSCENZA", "visual": "Triangolo parzialmente coperto", "desc": "Ciò che nasconde e protegge, mistero necessario.", "shadow": "Inganno, segreti tossici."},
    {"id": 17, "nome": "KLAVEN", "concetto": "Chiave", "cat": "CONOSCENZA", "visual": "Cerchio con linea uscente", "desc": "Comprensione che sblocca, insight risolutivo.", "shadow": "Razionalizzazione eccessiva."},
    {"id": 18, "nome": "MEZEN", "concetto": "Labirinto", "cat": "CONOSCENZA", "visual": "Quadrato labirintico", "desc": "Complessità disorientante, ricerca tortuosa.", "shadow": "Confusione mentale, smarrimento."},
    {"id": 19, "nome": "OKULAR", "concetto": "Testimone", "cat": "CONOSCENZA", "visual": "Cerchio con punto", "desc": "Osservazione neutra, presenza consapevole.", "shadow": "Distacco freddo, voyeurismo."},
    {"id": 20, "nome": "RESON", "concetto": "Echo", "cat": "CONOSCENZA", "visual": "Cerchi concentrici espansivi", "desc": "Conoscenza indiretta, riflesso di verità.", "shadow": "Distorsione dell'informazione, pettegolezzo."},

    # INTEGRAZIONE
    {"id": 21, "nome": "SHARDEN", "concetto": "Frammento", "cat": "INTEGRAZIONE", "visual": "Triangolo con vertice separato", "desc": "Parte separata dal tutto, incompletezza.", "shadow": "Dissociazione, sentirsi spezzati."},
    {"id": 22, "nome": "NEXAL", "concetto": "Fulcro", "cat": "INTEGRAZIONE", "visual": "Croce bilanciata", "desc": "Punto di equilibrio dinamico.", "shadow": "Paralisi decisionale, stallo."},
    {"id": 23, "nome": "FLODEN", "concetto": "Trabocco", "cat": "INTEGRAZIONE", "visual": "Cerchio che straripa", "desc": "Eccesso che rompe contenimento.", "shadow": "Sopraffazione emotiva, invasione."},
    {"id": 24, "nome": "VAKEN", "concetto": "Vuoto", "cat": "INTEGRAZIONE", "visual": "Quadrato vuoto", "desc": "Assenza produttiva, spazio per il nuovo.", "shadow": "Nichilismo, senso di inutilità."},
    {"id": 25, "nome": "WEVAN", "concetto": "Tessuto", "cat": "INTEGRAZIONE", "visual": "Griglia interconnessa", "desc": "Integrazione riuscita, molteplicità unificata.", "shadow": "Omologazione, perdita di identità."}
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
    Renderizza la card.
    FIX: Reintrodotta la descrizione (desc) e gestione dell'ombra.
    """
    filename = f"{glyph['nome'].upper()}.svg"
    file_path = os.path.join("assets", "glyphs", filename)
    
    # 1. Gestione Immagine
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                img_html = f'<img src="data:image/svg+xml;base64,{encoded}" class="glyph-img">'
        except:
            img_html = "<span style='color:red'>Errore SVG</span>"
    else:
        img_html = f"<div style='font-size:2em; font-family:monospace;'>{glyph['visual'][:1]}</div>"

    # 2. Gestione Contenuti Opzionali (Ombra)
    # Se siamo in Archivio o Focus (context='full'), mostriamo l'ombra.
    ombra_html = ""
    if context == "full":
        ombra_html = f'<div style="font-size:0.75em; border-top:1px solid #eee; padding-top:8px; margin-top:8px; color:#666; font-style:italic;">Ombra: {glyph["shadow"]}</div>'

    # 3. Costruzione HTML
    # REINSERITO {glyph['desc']} che era andato perso
    html = f"""
    <div class="glyph-box">
        <div class="glyph-cat">{glyph['cat']}</div>
        <div class="glyph-img-container">
            {img_html}
        </div>
        <div class="glyph-name">{glyph['nome']}</div>
        <div style="font-weight: bold; font-size: 0.9em; margin-bottom: 6px;">{glyph['concetto']}</div>
        <div style="font-size: 0.8em; line-height: 1.3; color: #333; margin-bottom: 5px;">{glyph['desc']}</div>
        {ombra_html}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def add_to_history(glyph_list, method):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    names = ", ".join([g['nome'] for g in glyph_list])
    st.session_state['history'].append({"Data": timestamp, "Metodo": method, "Glifi": names})

# -----------------------------------------------------------------------------
# 5. LAYOUT APPLICAZIONE E SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("SYNKRA")
menu = st.sidebar.radio("Navigazione", 
    ["Introduzione", "Archivio", "Oracolo", "Risonanza", "Addestramento", "Diario"])

st.sidebar.divider()
st.sidebar.caption("I 25 Specchi dell'Inconscio")

# =============================================================================
# SEZIONE: INTRODUZIONE (HOME PAGE)
# =============================================================================
if menu == "Introduzione":
    st.title("SYNKRA")
    st.subheader("I Venticinque Specchi")
    
    st.markdown("---")
    
    # Colonna unica centrale per il testo manifesto
    st.markdown("""
    <div class="hero-text">
        SYNKRA è un sistema di divinazione psicologica contemporaneo fondato sui principi junghiani 
        di <b>sincronicità</b> e <b>proiezione archetipica</b>. 
        <br><br>
        Nasce con un impegno esplicito all'onestà intellettuale: non rivendica false origini antiche 
        né si appropria di simbolismi culturali altrui. L'estrazione di un simbolo non è una predizione 
        soprannaturale, ma uno <b>specchio per l'inconscio</b> che permette di riconoscere dinamiche 
        interiori altrimenti inaccessibili.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.subheader("Le Cinque Dimensioni")
    st.markdown("La struttura del sistema mappa le dimensioni fondamentali dell'esperienza umana:")
    
    # Griglia delle categorie
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown('<div class="dimension-box">Trasformazione</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="dimension-box">Relazione</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="dimension-box">Movimento</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="dimension-box">Conoscenza</div>', unsafe_allow_html=True)
    with c5: st.markdown('<div class="dimension-box">Integrazione</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 **Inizia dal Menu Laterale**: Esplora l'**Archivio**, consulta l'**Oracolo** o metti alla prova la tua intuizione nell'**Addestramento**.")

# =============================================================================
# ALTRE SEZIONI
# =============================================================================

# --- ARCHIVIO ---
elif menu == "Archivio":
    st.title("Archivio")
    st.markdown("La matrice completa dei 25 specchi.")
    
    search = st.text_input("Cerca glifo", placeholder="Nome, concetto o categoria...")
    
    filtered_glyphs = [g for g in GLYPHS if search.lower() in (g['nome'] + g['concetto'] + g['cat']).lower()]
    
    # Matrice 5x5
    columns_num = 5 
    cols = st.columns(columns_num)
    
    for i, glyph in enumerate(filtered_glyphs):
        with cols[i % columns_num]:
            # FIX: Passiamo context="full" per mostrare anche l'Ombra
            get_glyph_card(glyph, context="full")

# --- ORACOLO ---
elif menu == "Oracolo":
    st.title("Lo Specchio")
    method = st.selectbox("Metodo", ["Focus (1 Glifo)", "Triade (3 Glifi)", "Pentagramma (5 Glifi)"])
    
    if st.button("Estrai", type="primary"):
        if "Focus" in method:
            res = [random.choice(GLYPHS)]
            st.subheader("Il Focus")
            get_glyph_card(res[0], "full")
            
        elif "Triade" in method:
            res = random.sample(GLYPHS, 3)
            c1, c2, c3 = st.columns(3)
            with c1: st.caption("Origine"); get_glyph_card(res[0])
            with c2: st.caption("Situazione"); get_glyph_card(res[1])
            with c3: st.caption("Evoluzione"); get_glyph_card(res[2])
            
        elif "Pentagramma" in method:
            res = random.sample(GLYPHS, 5)
            st.subheader("Mappatura")
            c1, c2, c3 = st.columns([1,1,1])
            with c2: st.caption("Centro"); get_glyph_card(res[0])
            c1, c2 = st.columns(2)
            with c1: st.caption("Sostegno"); get_glyph_card(res[1])
            with c2: st.caption("Ostacolo"); get_glyph_card(res[2])
            c1, c2 = st.columns(2)
            with c1: st.caption("Risorsa"); get_glyph_card(res[3])
            with c2: st.caption("Esito"); get_glyph_card(res[4])
            
        add_to_history(res, method)

# --- RISONANZA ---
elif menu == "Risonanza":
    st.title("Risonanza")
    col1, col2 = st.columns(2)
    with col1: name = st.text_input("Nome / Intento")
    with col2: date = st.date_input("Data Chiave", min_value=datetime.date(1900,1,1))
    
    if st.button("Calcola", type="primary") and name:
        h = hashlib.md5(f"{name}{date}".encode()).hexdigest()
        idx = int(h, 16) % 25
        st.success(f"Risonanza per: {name}")
        get_glyph_card(GLYPHS[idx], "full")

# --- ADDESTRAMENTO ---
elif menu == "Addestramento":
    st.title("Addestramento")
    st.metric("Punteggio", st.session_state['quiz_mode']['score'])
    
    if not st.session_state['quiz_mode']['active']:
        st.session_state['quiz_mode']['current'] = random.choice(GLYPHS)
        st.session_state['quiz_mode']['active'] = True
        st.session_state['quiz_mode']['revealed'] = False
        
    curr = st.session_state['quiz_mode']['current']
    
    # 1. Recupero Immagine
    fname = f"{curr['nome'].upper()}.svg"
    fpath = os.path.join("assets", "glyphs", fname)
    
    img_html_content = ""
    if os.path.exists(fpath):
        with open(fpath, "rb") as f:
            enc = base64.b64encode(f.read()).decode()
            img_html_content = f'<img src="data:image/svg+xml;base64,{enc}" class="glyph-img">'
    else:
        img_html_content = f"<div style='font-size:2em;'>?</div>"

    # 2. Render Quiz usando le STESSE CLASSI CSS
    quiz_html = f"""
    <div style="max-width: 300px; margin: 0 auto;">
        <div class="glyph-img-container">
            {img_html_content}
        </div>
    </div>
    """
    st.markdown(quiz_html, unsafe_allow_html=True)
        
    st.caption(f"Concetto: {curr['concetto']}")
    st.write("---")
    
    opts = random.sample([g['nome'] for g in GLYPHS if g['nome'] != curr['nome']], 3)
    opts.append(curr['nome'])
    random.shuffle(opts)
    
    if not st.session_state['quiz_mode']['revealed']:
        cols = st.columns(4)
        for i, o in enumerate(opts):
            if cols[i].button(o, use_container_width=True):
                if o == curr['nome']:
                    st.toast("Corretto!", icon="✅")
                    st.session_state['quiz_mode']['score'] += 1
                else:
                    st.toast(f"Sbagliato. Era {curr['nome']}", icon="❌")
                st.session_state['quiz_mode']['revealed'] = True
                st.rerun()
    else:
        st.info(f"Risposta: **{curr['nome']}**")
        if st.button("Prossimo"):
            st.session_state['quiz_mode']['active'] = False
            st.rerun()

# --- DIARIO ---
elif menu == "Diario":
    st.title("Diario")
    if st.session_state['history']:
        df = pd.DataFrame(st.session_state['history'])
        st.dataframe(df, use_container_width=True)
        
        all_g = []
        for x in st.session_state['history']:
            all_g.extend([n.strip() for n in x['Glifi'].split(',')])
        
        st.bar_chart(pd.Series(all_g).value_counts())
    else:
        st.info("Il diario è ancora vuoto.")