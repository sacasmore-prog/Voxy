import streamlit as st
import asyncio
import edge_tts
import PyPDF2
import re
import os
from datetime import datetime

# 1. CONFIGURACIÓN DEL SISTEMA VOXY
st.set_page_config(page_title="VOXY | Matrix Link", page_icon="📟", layout="wide")

if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- MOTOR DE AUDIO REFORZADO ---
async def voxy_engine(texto, voz, archivo, velocidad_std=1.0):
    rate_val = int((velocidad_std - 1.0) * 100)
    rate_str = f"{rate_val:+d}%"
    try:
        communicate = edge_tts.Communicate(texto, voz, rate=rate_str)
        await communicate.save(archivo)
        return True
    except:
        return False

def run_voxy_safe(texto, voz, archivo, velocidad=1.0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(voxy_engine(texto, voz, archivo, velocidad))
    finally:
        loop.close()

# --- MÓDULOS DE INTELIGENCIA ---
def limpiar_texto_pro(texto):
    if not texto: return ""
    texto = re.sub(r'\b\d{1,3}\b', '', texto)
    return " ".join(re.sub(r'[\*\-_/\\#\(\)\[\]]', ' ', texto).split())

def extraer_data_academica(texto):
    frases = [f.strip() for f in texto.split('.') if len(f) > 35]
    
    # Extraer ideas principales
    ideas = [f for f in frases if any(p in f.lower() for p in ['es ', 'son ', 'clave', 'importante', 'define'])][:6]
    
    # Crear Q&A para Flashcards
    qa = []
    for f in frases:
        # Patrón 1: "X es Y"
        if " es " in f.lower() and len(qa) < 5:
            match = re.search(r'([\w\s]+?)\s+es\s+(.+)', f, re.IGNORECASE)
            if match and len(match.group(2)) > 10:
                qa.append({
                    "q": f"¿Qué es {match.group(1).strip()}?",
                    "a": f"{match.group(2).strip()}"
                })
        # Patrón 2: "X son Y"
        elif " son " in f.lower() and len(qa) < 5:
            match = re.search(r'([\w\s]+?)\s+son\s+(.+)', f, re.IGNORECASE)
            if match and len(match.group(2)) > 10:
                qa.append({
                    "q": f"¿Qué son {match.group(1).strip()}?",
                    "a": f"{match.group(2).strip()}"
                })
    
    return ideas, qa

# --- UI ENGINE: HACKER MATRIX EDITION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { 
        background-color: #050505;
        background-image: linear-gradient(rgba(0, 255, 65, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        color: #00ff41; 
        font-family: 'Fira Code', monospace;
    }
    
    .stApp::before {
        content: "101011010101101011010101011010101101011010101101011010101011010";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        font-family: 'VT323'; font-size: 15px; color: rgba(0, 255, 65, 0.03);
        z-index: -1; overflow: hidden; word-break: break-all; pointer-events: none;
    }

    h1, h2, h3 { 
        font-family: 'VT323', monospace !important; 
        color: #00ff41 !important; 
        text-shadow: 0px 0px 8px rgba(0, 255, 65, 0.4); 
        letter-spacing: 2px;
    }

    .st-emotion-cache-1r6slb0, .st-emotion-cache-ocq8y9 {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 2px !important;
        padding: 25px;
        backdrop-filter: blur(5px);
    }

    .stButton>button {
        background: #111; color: #00ff41; 
        border: 1px solid rgba(0, 255, 65, 0.5);
        font-family: 'VT323', monospace; font-size: 1.5em;
        transition: 0.3s; width: 100%; text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #00ff41 !important; color: #000 !important;
        box-shadow: 0px 0px 15px rgba(0, 255, 65, 0.6);
    }

    .log-box {
        background: #000; border: 1px dashed rgba(0, 255, 65, 0.4);
        padding: 15px; font-size: 1.1em; color: #00ff41; 
        margin-bottom: 20px; font-family: 'VT323', monospace;
    }

    /* FLASHCARDS VOLTEABLES */
    .flip-card { background-color: transparent; width: 100%; height: 160px; perspective: 1000px; margin-bottom: 15px; cursor: pointer; }
    .flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; border: 1px solid #00ff41; }
    .flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
    .flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; display: flex; align-items: center; justify-content: center; padding: 10px; font-family: 'VT323'; font-size: 1.2em; }
    .flip-card-front { background: #000; color: #00ff41; }
    .flip-card-back { background: #00ff41; color: #000; transform: rotateY(180deg); font-weight: bold; }

    .idea-item { background: rgba(0, 255, 65, 0.05); border-left: 2px solid #00ff41; padding: 10px; margin-bottom: 8px; font-size: 0.9em; }
    
    .stSlider, .stSelectbox { color: #00ff41 !important; }
    </style>
    """ , unsafe_allow_html=True)

# --- PANTALLA 1: ACCESO AL SISTEMA ---
if st.session_state.paso == 1:
    st.markdown("<br><h1 style='text-align: center; font-size: 4.5em;'>[ VOXY_MATRIX ]</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00ff41; opacity: 0.6;'>DECODING ACADEMIC REALITY // CAS_2026</p>", unsafe_allow_html=True)
    
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
            <div class="log-box">
                > PENETRANDO EN EL SISTEMA DE ESTUDIO...<br>
                > FILTRANDO RUIDO BINARIO...<br>
                > CARGUE MANUSCRITO PDF PARA EXTRACCIÓN...
            </div>
        """, unsafe_allow_html=True)
        file = st.file_uploader("", type="pdf", label_visibility="collapsed")
        if file:
            st.session_state.pdf_file = file
            st.markdown(f"<p style='color:#00ff41; font-size:16px; text-align:center;'>[!] SECTOR DETECTADO: {file.name.upper()}</p>", unsafe_allow_html=True)
            if st.button("ENTRAR EN LA MATRIZ >>"):
                st.session_state.paso = 2
                st.rerun()

# --- PANTALLA 2: PANEL DE CONTROL ---
elif st.session_state.paso == 2:
    st.sidebar.markdown("### 🕒 HISTORIAL DE SECTORES")
    for item in reversed(st.session_state.historial[-5:]):
        st.sidebar.code(f"📄 {item['archivo']}", language="bash")

    st.markdown("<h2 style='font-size: 3.5em;'>PANEL_DE_CONTROL</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1.5, 1, 1])
    c1.markdown(f"**ARCHIVO:** `{{st.session_state.pdf_file.name}}`")
    c2.markdown(f"**PÁGINAS:** {{len(PyPDF2.PdfReader(st.session_state.pdf_file).pages)}}")
    if c3.button("REINICIAR_SISTEMA"):
        st.session_state.paso = 1
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # TABS PRINCIPALES
    tab_audio, tab_conceptos, tab_demo = st.tabs(["🔊 DECODIFICADOR DE AUDIO", "🧠 EXTRACCIÓN DE CONCEPTOS", "📊 DEMO DE AUDIO"])

    # --- TAB 1: AUDIO ---
    with tab_audio:
        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1.2])
        with col_left:
            st.markdown("### CONFIGURACIÓN")
            voz_sel = st.selectbox("OPERADOR:", ["es-ES-AlvaroNeural", "es-ES-ElviraNeural"])
            vel_val = st.select_slider("VELOCIDAD:", options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0], value=1.0)
            if st.button("🔊 TEST DE SEÑAL (3s)"):
                if run_voxy_safe("Señal de audio verificada en el sector Matrix.", voz_sel, "test.mp3", vel_val):
                    st.audio("test.mp3")

        with col_right:
            st.markdown("### EXTRACCIÓN")
            total_p = len(PyPDF2.PdfReader(st.session_state.pdf_file).pages)
            rango = st.slider("RANGO DE PÁGINAS:", 1, total_p, (1, min(2, total_p)))
            if st.button(">>> EJECUTAR EXTRACCIÓN DE AUDIO"):
                reader = PyPDF2.PdfReader(st.session_state.pdf_file)
                texto = "".join([reader.pages[i].extract_text() for i in range(rango[0]-1, rango[1])])
                texto_limpio = limpiar_texto_pro(texto)
                with st.spinner("PROCESANDO FLUJO..."):
                    if run_voxy_safe(texto_limpio, voz_sel, "voxy_final.mp3", vel_val):
                        st.audio("voxy_final.mp3")
                        st.session_state.historial.append({
                            "archivo": st.session_state.pdf_file.name,
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success("FLUJO COMPLETADO.")
                        with open("voxy_final.mp3", "rb") as f:
                            st.download_button("⬇️ DESCARGAR AUDIO", f, file_name="voxy_matrix.mp3")

    # --- TAB 2: CONCEPTOS Y FLASHCARDS ---
    with tab_conceptos:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(">>> DESPLEGAR DATOS ACADÉMICOS"):
            reader = PyPDF2.PdfReader(st.session_state.pdf_file)
            texto_full = "".join([reader.pages[i].extract_text() for i in range(rango[0]-1, rango[1])])
            ideas, qa_list = extraer_data_academica(limpiar_texto_pro(texto_full))
            
            c_ideas, c_cards = st.columns(2)
            with c_ideas:
                st.markdown("### 💡 IDEAS CLAVE")
                for idea in ideas:
                    st.markdown(f'<div class="idea-item">{{idea}}</div>', unsafe_allow_html=True)
            
            with c_cards:
                st.markdown("### 🃏 FLASHCARDS (PASA EL MOUSE PARA VOLTEAR)")
                for item in qa_list:
                    st.markdown(f"""
                    <div class="flip-card">
                      <div class="flip-card-inner">
                        <div class="flip-card-front">{item['q']}</div>
                        <div class="flip-card-back">{item['a']}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    # --- TAB 3: DEMO DE AUDIOS ---
    with tab_demo:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎙️ MUESTRAS DE AUDIO CON DIFERENTES CONFIGURACIONES")
        
        # Demo 1: Velocidad lenta
        st.markdown("**📍 Muestra 1: Voz masculina lenta (0.75x)**")
        demo_text_1 = "Esto es una prueba de audio a velocidad reducida para mejor comprensión."
        if st.button("▶️ GENERAR DEMO 1"):
            with st.spinner("Generando..."):
                if run_voxy_safe(demo_text_1, "es-ES-AlvaroNeural", "demo_1.mp3", 0.75):
                    st.audio("demo_1.mp3")
                    st.caption("Velocidad: 75% - Ideal para textos densos")
        
        st.markdown("---")
        
        # Demo 2: Velocidad normal
        st.markdown("**📍 Muestra 2: Voz femenina normal (1.0x)**")
        demo_text_2 = "Este es un audio a velocidad estándar, el punto medio entre lentitud y rapidez."
        if st.button("▶️ GENERAR DEMO 2"):
            with st.spinner("Generando..."):
                if run_voxy_safe(demo_text_2, "es-ES-ElviraNeural", "demo_2.mp3", 1.0):
                    st.audio("demo_2.mp3")
                    st.caption("Velocidad: 100% - Velocidad estándar")
        
        st.markdown("---")
        
        # Demo 3: Velocidad rápida
        st.markdown("**📍 Muestra 3: Voz masculina rápida (1.5x)**")
        demo_text_3 = "Este audio se reproduce a una velocidad aumentada para usuarios que prefieren contenido acelerado."
        if st.button("▶️ GENERAR DEMO 3"):
            with st.spinner("Generando..."):
                if run_voxy_safe(demo_text_3, "es-ES-AlvaroNeural", "demo_3.mp3", 1.5):
                    st.audio("demo_3.mp3")
                    st.caption("Velocidad: 150% - Para lectores rápidos")
        
        st.markdown("---")
        
        st.info("💡 Consejo: Prueba diferentes velocidades para encontrar tu ritmo ideal de aprendizaje")

st.markdown("<br><hr style='border-color: rgba(0, 255, 65, 0.2);'><p style='text-align: center; font-size: 0.8em; color: #00ff41;'>SARA_CASTRO // CAS_TECH // LIBERANDO TU ESTUDIO</p>", unsafe_allow_html=True)