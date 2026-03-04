import streamlit as st
import asyncio
import edge_tts
import PyPDF2
import re
import os

# 1. CONFIGURACIÓN DEL SISTEMA VOXY
st.set_page_config(page_title="VOXY | Matrix Neural Link", page_icon="📟", layout="wide")

if 'paso' not in st.session_state: st.session_state.paso = 1
if 'historial' not in st.session_state: st.session_state.historial = []

# --- MOTOR DE AUDIO ---
async def voxy_engine(texto, voz, archivo, velocidad_std):
    rate_val = int((velocidad_std - 1.0) * 100)
    rate_str = f"{rate_val:+d}%"
    try:
        communicate = edge_tts.Communicate(texto, voz, rate=rate_str)
        await communicate.save(archivo)
        return True
    except: return False

def run_voxy_safe(texto, voz, archivo, velocidad=1.0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: return loop.run_until_complete(voxy_engine(texto, voz, archivo, velocidad))
    finally: loop.close()

# --- INTELIGENCIA DE DATOS ---
def limpiar_texto(texto):
    if not texto: return ""
    limpio = re.sub(r'[\*\-\_/\\#\(\)\[\]]', ' ', texto)
    return " ".join(limpio.split())

def extraer_conceptos(texto):
    if not texto or len(texto) < 10: return [], []
    frases = [f.strip() for f in texto.split('.') if len(f) > 20]
    
    ideas = [f for f in frases if any(p in f.lower() for p in ['es ', 'son ', 'importante', 'clave', 'puesto que'])][:6]
    
    qa = []
    for f in frases:
        if " es " in f.lower() and len(qa) < 4:
            partes = f.split(" es ", 1)
            if len(partes) == 2:
                qa.append({"q": f"¿Qué es {partes[0].strip()}?", "a": f"{partes[1].strip()}"})
    
    if not qa and frases:
        for f in frases[:3]:
            qa.append({"q": "Punto de estudio", "a": f})
            
    return ideas, qa

# --- UI ENGINE: MATRIX STYLE CON CUADRÍCULA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { 
        background-color: #050505; 
        color: #00ff41; 
        font-family: 'Fira Code', monospace;
        /* RESTAURADA LA CUADRÍCULA MATRIX */
        background-image: linear-gradient(rgba(0, 255, 65, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
    }

    .stApp::before {
        content: "101011010101101011010101011010101101011010101101011010101011010";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        font-family: 'VT323'; font-size: 15px; color: rgba(0, 255, 65, 0.03);
        z-index: -1; overflow: hidden; word-break: break-all; pointer-events: none;
    }

    h1, h2, h3 { font-family: 'VT323', monospace !important; color: #00ff41 !important; text-shadow: 0px 0px 8px rgba(0, 255, 65, 0.4); }
    
    .st-emotion-cache-1r6slb0, .st-emotion-cache-ocq8y9 {
        background: rgba(0, 0, 0, 0.8) !important; border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 2px !important; padding: 25px; backdrop-filter: blur(5px);
    }

    .stButton>button {
        background: #111; color: #00ff41; border: 1px solid rgba(0, 255, 65, 0.5);
        font-family: 'VT323', monospace; font-size: 1.5em; width: 100%;
    }
    .stButton>button:hover { background: #00ff41 !important; color: #000 !important; box-shadow: 0px 0px 15px rgba(0, 255, 65, 0.6); }
    
    .log-box { background: #000; border: 1px dashed rgba(0, 255, 65, 0.4); padding: 15px; font-family: 'VT323', monospace; }
    
    /* FLASHCARDS */
    .flip-card { background-color: transparent; width: 100%; height: 180px; perspective: 1000px; margin-bottom: 20px; }
    .flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; border: 1px solid #00ff41; }
    .flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
    .flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; display: flex; align-items: center; justify-content: center; padding: 15px; font-family: 'VT323'; }
    .flip-card-front { background: #000; color: #00ff41; font-size: 1.2em; }
    .flip-card-back { background: #00ff41; color: #000; transform: rotateY(180deg); font-weight: bold; overflow-y: auto; font-size: 1em; }
    
    .idea-item { background: rgba(0, 255, 65, 0.05); border-left: 2px solid #00ff41; padding: 12px; margin-bottom: 10px; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- PANTALLA 1 ---
if st.session_state.paso == 1:
    st.markdown("<br><h1 style='text-align: center; font-size: 4.5em;'>[ VOXY_MATRIX ]</h1>", unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""<div class="log-box">> PENETRANDO EN EL SISTEMA DE ESTUDIO...<br>> FILTRANDO RUIDO BINARIO...<br>> CARGUE MANUSCRITO PDF PARA EXTRACCIÓN...</div>""", unsafe_allow_html=True)
        file = st.file_uploader("", type="pdf", label_visibility="collapsed")
        if file:
            st.session_state.pdf_file = file
            if st.button("ENTRAR EN LA MATRIZ >>"):
                st.session_state.paso = 2
                st.rerun()

# --- PANTALLA 2 ---
elif st.session_state.paso == 2:
    st.sidebar.markdown("### 🕒 ARCHIVOS RECIENTES")
    for item in reversed(st.session_state.historial[-5:]):
        st.sidebar.code(f"ID: {item[:15]}...", language="bash")

    st.markdown("<h2 style='font-size: 3.5em;'>PANEL_DE_CONTROL</h2>", unsafe_allow_html=True)
    
    col_top1, col_top2, col_top3 = st.columns([1.5, 1, 1])
    col_top1.markdown(f"**DATA:** `{st.session_state.pdf_file.name}`")
    total_p = len(PyPDF2.PdfReader(st.session_state.pdf_file).pages)
    col_top2.markdown(f"**PÁGINAS:** {total_p}") # CAMBIADO DE SECTORES A PÁGINAS
    if col_top3.button("REINICIAR"):
        st.session_state.paso = 1
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    rango = st.slider("SELECCIONAR RANGO DE ESTUDIO (PÁGINAS):", 1, total_p, (1, min(2, total_p)))
    
    tab_audio, tab_conceptos = st.tabs(["🔊 DECODIFICADOR AUDIO", "🧠 CONCEPTOS CLAVE"])

    reader = PyPDF2.PdfReader(st.session_state.pdf_file)
    start_p, end_p = rango
    texto_raw = "".join([reader.pages[i].extract_text() for i in range(start_p-1, end_p)])
    texto_ready = limpiar_texto(texto_raw)

    with tab_audio:
        st.markdown("<br>", unsafe_allow_html=True)
        c_audio1, c_audio2 = st.columns(2)
        with c_audio1:
            st.markdown("### SINCRONIZADOR")
            voz_sel = st.selectbox("OPERADOR:", ["es-ES-AlvaroNeural", "es-ES-ElviraNeural"])
            vel_std = st.select_slider("VELOCIDAD:", options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0], value=1.0)
            if st.button("🔊 PROBAR SEÑAL"):
                if run_voxy_safe("Señal verificada.", voz_sel, "test.mp3", vel_std):
                    st.audio("test.mp3")
        
        with c_audio2:
            st.markdown("### PROCESO")
            if st.button(">>> EJECUTAR EXTRACCIÓN DE AUDIO"):
                with st.spinner("DECODIFICANDO..."):
                    if run_voxy_safe(texto_ready, voz_sel, "voxy_final.mp3", vel_std):
                        st.audio("voxy_final.mp3")
                        if st.session_state.pdf_file.name not in st.session_state.historial:
                            st.session_state.historial.append(st.session_state.pdf_file.name)

    with tab_conceptos:
        st.markdown("<br>", unsafe_allow_html=True)
        if not texto_ready.strip():
            st.warning("No se detectó texto en estas páginas.")
        else:
            ideas, qa_list = extraer_conceptos(texto_ready)
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.markdown("### 💡 IDEAS PRINCIPALES")
                for idea in ideas:
                    st.markdown(f'<div class="idea-item">{idea}</div>', unsafe_allow_html=True)
            with c_col2:
                st.markdown("### 🃏 FLASHCARDS")
                for item in qa_list:
                    st.markdown(f"""<div class="flip-card"><div class="flip-card-inner"><div class="flip-card-front">{item['q']}</div><div class="flip-card-back">{item['a']}</div></div></div>""", unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: rgba(0, 255, 65, 0.2);'><p style='text-align: center; font-size: 0.8em; color: #00ff41;'>SARA_CASTRO // CAS_TECH // 2026</p>", unsafe_allow_html=True)
