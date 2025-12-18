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
# 2. CSS MINIMALE (Solo per layout e visibilità SVG)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Stile "Card" pulito che si adatta al tema (Chiaro/Scuro) */
    .glyph-box {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .glyph-box:hover {
        transform: translateY(-5px);
    }
    
    .glyph-name {
        font-size: 1.5em;
        font-weight: bold;
        margin: 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .glyph-cat {
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.7;
    }

    /* IMPORTANTE: Sfondo bianco dietro l'immagine.
       Serve perché i tuoi SVG sono neri. In Dark Mode non si vedrebbero.
       Questo garantisce visibilità sempre.
    */
    .glyph-img-container {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        display: inline-block;
        margin: 15px 0;
    }
    
    .glyph-img {
        width: 120px;
        height: auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DATABASE (DATI INVARIATI)
# -----------------------------------------------------------------------------
GLYPHS = [
    {"id": 1, "nome": "KEMRA", "concetto": "Seme", "cat": "TRASFORMAZIONE", "visual": "Punto al centro di cerchio aperto", "desc": "Potenziale latente, inizio non ancora manifestato, promessa.", "shadow": "Sterilità, incapacità di iniziare."},
    {"id": 2, "nome": "SKIRN", "concetto": "Frattura", "cat": "TRASFORMAZIONE", "visual": "Linea verticale spezzata", "desc": "Rottura necessaria, crisi che apre nuove possibilità.", "shadow": "Distruzione fine a se stessa."},
    {"id": 3, "nome": "LUTHEN", "concetto": "Crisalide", "cat": "TRASFORMAZIONE", "visual": "Ovale chiuso con linea ondulata", "desc": "Processo interno invisibile, transizione protetta.", "shadow": "Isolamento, stagnazione."},
    {"id": 4, "nome": "VRAEL", "concetto": "Emersione", "cat": "TRASFORMAZIONE", "visual": "Triangolo che rompe un cerchio", "desc": "Manifestazione, nascita di nuova forma.", "shadow": "Esposizione prematura, arroganza."},
    {"id": 5, "nome": "ASKOR", "concetto": "Cenere", "cat": "TRASFORMAZIONE", "visual": "Quadrato frammentato", "desc": "Ciclo completato, fine che nutre l'inizio.", "shadow": "Attaccamento al passato, lutto non risolto."},
    
    {"id": 6, "nome": "LIMYR", "concetto": "Soglia", "cat": "RELAZIONE", "visual": "Linee verticali con gap", "desc": "Confine tra sé e altro, spazio liminale.", "shadow": "Muri invalicabili o assenza di confini."},
    {"id": 7, "nome": "MIREN", "concetto": "Specchio", "cat": "RELAZIONE", "visual": "Triangoli opposti", "desc": "Riconoscimento reciproco, proiezione.", "shadow": "Narcisismo, incapacità di vedere l'altro."},
    {"id": 8, "nome": "THEKNA", "concetto": "Nodo", "cat": "RELAZIONE", "visual": "Due cerchi sovrapposti", "desc": "Legame complesso, intreccio che unisce o intrappola.", "shadow": "Dipendenza, soffocamento."},
    {"id": 9, "nome": "SONAL", "concetto": "Risonanza", "cat": "RELAZIONE", "visual": "Cerchi concentrici disallineati", "desc": "Armonia spontanea, sincronicità relazionale.", "shadow": "Eco vuoto, conformismo."},
    {"id": 10, "nome": "VORDEN", "concetto": "Abisso", "cat": "RELAZIONE", "visual": "Linee divergenti", "desc": "Distanza incolmabile, separazione radicale.", "shadow": "Abbandono, alienazione totale."},

    {"id": 11, "nome": "RADHEN", "concetto": "Radice", "cat": "MOVIMENTO", "visual": "Linee verticali discendenti", "desc": "Ancoraggio, stabilità profonda.", "shadow": "Rigidità, incapacità di adattarsi."},
    {"id": 12, "nome": "FLUEN", "concetto": "Corrente", "cat": "MOVIMENTO", "visual": "Linea sinusoidale", "desc": "Flusso naturale, adattamento dinamico.", "shadow": "Passività, mancanza di direzione."},
    {"id": 13, "nome": "SPIREK", "concetto": "Vortice", "cat": "MOVIMENTO", "visual": "Spirale logaritmica", "desc": "Movimento ciclico intenso, essere trascinati.", "shadow": "Ossessione, perdita di controllo."},
    {"id": 14, "nome": "VEKTOR", "concetto": "Sentiero", "cat": "MOVIMENTO", "visual": "Linea retta con freccia", "desc": "Direzione deliberata, progressione consapevole.", "shadow": "Visione a tunnel, fanatismo."},
    {"id": 15, "nome": "KRESH", "concetto": "Salto", "cat": "MOVIMENTO", "visual": "Linea spezzata acuta", "desc": "Discontinuità improvvisa, rischio.", "shadow": "Impulsività sconsiderata, caduta."},

    {"id": 16, "nome": "VELUM", "concetto": "Velo", "cat": "CONOSCENZA", "visual": "Triangolo parzialmente coperto", "desc": "Ciò che nasconde e protegge, mistero necessario.", "shadow": "Inganno, segreti tossici."},
    {"id": 17, "nome": "KLAVEN", "concetto": "Chiave", "cat": "CONOSCENZA", "visual": "Cerchio con linea uscente", "desc": "Comprensione che sblocca, insight risolutivo.", "shadow": "Razionalizzazione eccessiva."},
    {"id": 18, "nome": "MEZEN", "concetto": "Labirinto", "cat": "CONOSCENZA", "visual": "Quadrato labirintico", "desc": "Complessità disorientante, ricerca tortuosa.", "shadow": "Confusione mentale, smarrimento."},
    {"id": 19, "nome": "OKULAR", "concetto": "Testimone", "cat": "CONOSCENZA", "visual": "Cerchio con punto", "desc": "Osservazione neutra, presenza consapevole.", "shadow": "Distacco freddo, voyeurismo."},
    {"id": 20, "nome": "RESON", "concetto": "Echo", "cat": "CONOSCENZA", "visual": "Cerchi concentrici espansivi", "desc": "Conoscenza indiretta, riflesso di verità.", "shadow": "Distorsione dell'informazione, pettegolezzo."},

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
    Versione corretta: HTML generato su singola riga per evitare 
    che Markdown lo interpreti come "blocco di codice" a causa dell'indentazione.
    """
    filename = f"{glyph['nome'].upper()}.svg"
    file_path = os.path.join("assets", "glyphs", filename)
    
    html_visual = ""
    
    # Gestione Immagine
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                # IMPORTANTE: Tutto su una riga senza spazi iniziali
                html_visual = f'<div class="glyph-img-container"><img src="data:image/svg+xml;base64,{encoded}" class="glyph-img"></div>'
        except:
            html_visual = "<div style='color:red'>Errore file</div>"
    else:
        # Fallback testuale
        html_visual = f"<div style='margin: 20px 0; font-style: italic;'>[{glyph['visual']}]</div>"

    # Costruzione Card (Usiamo f-string compatta per evitare spazi indesiderati)
    ombra_html = f'<div style="font-size:0.8em; border-top:1px solid #ccc; padding-top:5px; margin-top:10px; font-style:italic; opacity:0.8;"><b>Ombra:</b> {glyph["shadow"]}</div>' if context == "full" else ""

    card_html = f"""
    <div class="glyph-box">
        <div class="glyph-cat">{glyph['cat']}</div>
        <div class="glyph-name">{glyph['nome']}</div>
        {html_visual}
        <div style="font-weight: bold; margin-bottom: 5px;">{glyph['concetto']}</div>
        <div style="font-size: 0.9em; opacity: 0.9;">{glyph['desc']}</div>
        {ombra_html}
    </div>
    """
    
    # Renderizza interpretando l'HTML
    st.markdown(card_html, unsafe_allow_html=True)
def add_to_history(glyph_list, method):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    names = ", ".join([g['nome'] for g in glyph_list])
    st.session_state['history'].append({"Data": timestamp, "Metodo": method, "Glifi": names})

# -----------------------------------------------------------------------------
# 5. LAYOUT APPLICAZIONE
# -----------------------------------------------------------------------------
st.sidebar.title("SYNKRA")
menu = st.sidebar.radio("Navigazione", 
    ["Archivio", "Oracolo", "Risonanza", "Addestramento", "Diario"])

st.sidebar.divider()
st.sidebar.caption("I 25 Specchi dell'Inconscio")

# --- ARCHIVIO ---
if menu == "Archivio":
    st.title("Archivio")
    search = st.text_input("Cerca glifo", placeholder="Nome, concetto o categoria...")
    
    filtered_glyphs = [g for g in GLYPHS if search.lower() in (g['nome'] + g['concetto'] + g['cat']).lower()]
    
    # Layout responsivo
    cols = st.columns(3)
    for i, glyph in enumerate(filtered_glyphs):
        with cols[i % 3]:
            get_glyph_card(glyph)

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
    
    # Mostra glifo anonimizzato (immagine o visual text)
    fname = f"{curr['nome'].upper()}.svg"
    fpath = os.path.join("assets", "glyphs", fname)
    if os.path.exists(fpath):
        with open(fpath, "rb") as f:
            enc = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="background:white; padding:20px; border-radius:10px; width:fit-content; margin:0 auto;">
            <img src="data:image/svg+xml;base64,{enc}" style="width:100px;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Visual: {curr['visual']}")
        
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