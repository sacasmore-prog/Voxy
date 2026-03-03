import streamlit as st
import asyncio
import edge_tts
import PyPDF2
import re
import os

# 1. CONFIGURACIÓN DEL SISTEMA VOXY
st.set_page_config(page_title="VOXY | Underground Neural Link", page_icon="📟", layout="wide")

if 'paso' not in st.session_state:
    st.session_state.paso = 1

# --- MOTOR DE AUDIO REFORZADO (ANTI-INTERFERENCIAS) ---
async def voxy_engine(texto, voz, archivo):
    for i in range(3): 
        try:
            communicate = edge_tts.Communicate(texto, voz, rate="+12%")
            await communicate.save(archivo)
            return True
        except Exception:
            await asyncio.sleep(1)
    return False

def run_voxy_safe(texto, voz, archivo):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(voxy_engine(texto, voz, archivo))
        return success
    finally:
        loop.close()

# 2. MÓDULOS DE INTELIGENCIA
def limpiar_texto(texto):
    if not texto: return ""
    limpio = re.sub(r'[\*\-\_/\\#\(\)\[\]]', ' ', texto)
    return " ".join(limpio.split())

def generar_resumen(texto):
    if not texto or len(texto) < 150: return texto
    frases = [f.strip() for f in texto.split('.') if len(f) > 25]
    importantes = sorted(frases, key=len, reverse=True)[:6]
    return ". ".join(importantes) + "."

# --- UI ENGINE: HACKER MATRIX EDITION (CSS ACTUALIZADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    
    /* FONDO MATRIX DE CEROS Y UNOS */
    .stApp { 
        background-color: #050505;
        background-image: linear-gradient(rgba(0, 255, 65, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        color: #00ff41; 
        font-family: 'Fira Code', monospace;
    }
    
    /* Capa extra para simular lluvia de código estática */
    .stApp::before {
        content: "101011010101101011010101011010101101011010101101011010101011010";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        font-family: 'VT323';
        font-size: 15px;
        line-height: 15px;
        color: rgba(0, 255, 65, 0.03);
        z-index: -1;
        overflow: hidden;
        word-break: break-all;
        pointer-events: none;
    }

    /* Títulos con Neón Suavizado */
    h1, h2, h3 { 
        font-family: 'VT323', monospace !important; 
        color: #00ff41 !important; 
        text-shadow: 0px 0px 8px rgba(0, 255, 65, 0.4); 
        letter-spacing: 2px;
    }

    /* Tarjetas de Interfaz sutiles */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-ocq8y9 {
        background: rgba(0, 0, 0, 0.8) !important; /* Más opaco para leer mejor */
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        border-radius: 2px !important;
        padding: 25px;
        backdrop-filter: blur(5px);
    }

    /* Botones Estilo Terminal */
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

    /* Caja de Log */
    .log-box {
        background: #000; border: 1px dashed rgba(0, 255, 65, 0.4);
        padding: 15px; font-size: 1.1em; color: #00ff41; 
        margin-bottom: 20px; font-family: 'VT323', monospace;
    }
    
    .stSlider, .stSelectbox { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PANTALLA 1: ACCESO AL SISTEMA ---
if st.session_state.paso == 1:
    st.markdown("<h1 style='text-align: center; font-size: 4.5em;'>[ VOXY_MATRIX ]</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00ff41; opacity: 0.6;'>DECODING ACADEMIC REALITY // CAS_2026</p>", unsafe_allow_html=True)
    
    _, col_c, _ = st.columns([1, 2, 1])
    
    with col_c:
        st.markdown("""
            <div class="log-box">
                > INTRODUCIÉNDOSE EN EL SISTEMA DE ESTUDIO...<br>
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

# --- PANTALLA 2: PANEL DE DECODIFICACIÓN ---
elif st.session_state.paso == 2:
    st.markdown("<h2 style='font-size: 3.5em;'>NÚCLEO_DE_CONTROL</h2>", unsafe_allow_html=True)
    
    if st.button("<< REINICIAR_ENLACE"):
        st.session_state.paso = 1
        st.rerun()
    
    reader = PyPDF2.PdfReader(st.session_state.pdf_file)
    total_pags = len(reader.pages)
    
    st.markdown("<hr style='border-color: rgba(0, 255, 65, 0.3);'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 1])
    
    with c1:
        st.markdown("### SINCRONIZADOR_VOZ")
        voces = {
            "IA-MALE (Alvaro)": "es-ES-AlvaroNeural",
            "IA-FEMALE (Elvira)": "es-ES-ElviraNeural"
        }
        voz_sel = st.selectbox("Elegir Operador:", list(voces.keys()))
        
        if st.button("> TEST_CONEXIÓN"):
            with st.spinner("Ping..."):
                if run_voxy_safe("Conexión establecida en la Matriz.", voces[voz_sel], "test.mp3"):
                    st.audio("test.mp3")
                else:
                    st.error("TIEMPO DE ESPERA AGOTADO.")

    with c2:
        st.markdown("### PARÁMETROS_DATA")
        rango = st.slider("Bloque de páginas:", 1, total_pags, (1, min(2, total_pags)))
        modo = st.radio("Método:", ["Copia_Exacta", "Resumen_Optimizado"])

    with c3:
        st.markdown("### INFO")
        st.info(f"ID: {st.session_state.pdf_file.name[:12]}...")
        st.warning(f"VOL: {total_pags} PÁGS")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(">>> EJECUTAR EXTRACCIÓN BINARIA"):
        with st.spinner("HACKEANDO PDF..."):
            try:
                start, end = rango
                texto_raw = ""
                for p in range(start-1, end):
                    texto_raw += reader.pages[p].extract_text() + " "
                
                texto_final = limpiar_texto(texto_raw)
                
                if not texto_final.strip():
                    st.error("ERROR: SECTOR VACÍO.")
                else:
                    if "Resumen" in modo:
                        texto_final = generar_resumen(texto_final)
                    
                    output_file = "voxy_data.mp3"
                    if run_voxy_safe(texto_final, voces[voz_sel], output_file):
                        st.success("EXTRACCIÓN COMPLETADA CON ÉXITO.")
                        st.audio(output_file)
                        with open(output_file, "rb") as f:
                            st.download_button("DESCARGAR_ARCHIVO_MP3", f, file_name="voxy_matrix.mp3")
                    else:
                        st.error("ERROR CRÍTICO DE TRANSMISIÓN.")
            
            except Exception as e:
                st.error(f"SYSTEM_CRASH: {e}")

st.markdown("<br><hr style='border-color: rgba(0, 255, 65, 0.2);'><p style='text-align: center; font-size: 0.8em; color: #00ff41;'>SARA_CASTRO // CAS_TECH // LIBERANDO TU ESTUDIO</p>", unsafe_allow_html=True)
