import random
import os
import time
import hmac
import unicodedata
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURACIÓN GENERAL Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Instructor Bíblico AI",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
    }
    .stInfo {
        background-color: #e2e3e5;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTES Y TEMARIO
# ==========================================
TEMARIO_OFICIAL = [
    "1. Bienvenida", 
    "2. Parcelación", 
    "3. Indicaciones", 
    "4. Introducción al género",
    "5. Tipos de géneros y Rasgos literarios", 
    "6. Permaneciendo en la línea", 
    "7. Énfasis",
    "8. Estructura", 
    "9. Estrategias", 
    "10. Contexto (General)", 
    "11. Argumento A/Original",
    "12. Reflexión Teológica (General)", 
    "13. Persuasión", 
    "14. Arreglo"
]

# === BASE DE DATOS DE LIBROS Y PASAJES ===
DB_BIBLIA = {
    "Discurso": {
        "2 Timoteo": [
            "2 Timoteo 1:1-5", "2 Timoteo 1:6-12", "2 Timoteo 2:1-7", 
            "2 Timoteo 2:8-13", "2 Timoteo 2:14-19", "2 Timoteo 2:20-26",
            "2 Timoteo 3:10-17", "2 Timoteo 4:1-8", "2 Timoteo 4:9-18"
        ]
    },
    "Narrativa": {
        "Éxodo": [
            "Éxodo 1:1-22", "Éxodo 2:11-22", "Éxodo 3:1-10", "Éxodo 10:21-29", 
            "Éxodo 12:1-28", "Éxodo 13:17-15:21", "Éxodo 17:8-18:27", 
            "Éxodo 19:1-20:21", "Éxodo 32:1-35", "Éxodo 33:1-23", 
            "Éxodo 37:1-9", "Éxodo 40:1-38"
        ],
        "Hechos": [
            "Hechos 1:1-11", "Hechos 2:1-47", "Hechos 3:1-4:4", "Hechos 4:32-5:11", 
            "Hechos 8:1-40", "Hechos 9:1-31", "Hechos 10:1-11:18", "Hechos 11:19-30", 
            "Hechos 13:1-52", "Hechos 15:1-35", "Hechos 18:24-19:22", "Hechos 24:1-26:32"
        ]
    },
    "Poético": {
        "Oseas": [
            "Oseas 2:2-3:5", "Oseas 4:1-10", "Oseas 4:11-19", "Oseas 5:1-6:3", 
            "Oseas 6:4-7:16", "Oseas 8:1-14", "Oseas 9:1-9", "Oseas 9:10-10:15", 
            "Oseas 11:1-11", "Oseas 11:12-12:4", "Oseas 13:1-16", "Oseas 14:1-9"
        ]
    }
}

# === VIDEOTECA DE LECCIONES ===
DB_VIDEOS = {
    "1. Bienvenida": "https://youtu.be/TU_ENLACE_LECCION_1",
    "2. Parcelación": "https://youtu.be/TU_ENLACE_LECCION_2",
    "3. Indicaciones": "https://youtu.be/TU_ENLACE_LECCION_3",
    "4. Introducción al género": {
        "Narrativa": "https://youtu.be/VIDEO_NARRATIVA",
        "Poético": "https://youtu.be/VIDEO_POETICO",
        "Discurso": "https://youtu.be/VIDEO_DISCURSO"
    },
    "5. Tipos de géneros y Rasgos literarios": "https://youtu.be/TU_ENLACE_LECCION_5",
    "6. Permaneciendo en la línea": "https://youtu.be/TU_ENLACE_LECCION_6",
    "7. Énfasis": "https://youtu.be/TU_ENLACE_LECCION_7",
    "8. Estructura": "https://youtu.be/TU_ENLACE_LECCION_8",
    "9. Estrategias": "https://youtu.be/TU_ENLACE_LECCION_9",
    "10. Contexto (General)": "https://youtu.be/TU_ENLACE_LECCION_10",
    "11. Argumento A/Original": "https://youtu.be/TU_ENLACE_LECCION_11",
    "12. Reflexión Teológica (General)": "https://youtu.be/TU_ENLACE_LECCION_12",
    "13. Persuasión": "https://youtu.be/TU_ENLACE_LECCION_13",
    "14. Arreglo": "https://youtu.be/TU_ENLACE_LECCION_14"
}

# ==========================================
# 3. GESTIÓN DE SECRETOS Y CONEXIONES
# ==========================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    maestro_pass = st.secrets.get("MAESTRO_PASSWORD", "12345")
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"⚠️ Error Crítico de Configuración: {e}")
    st.stop()

# ==========================================
# 4. CEREBROS DE LA IA (PROMPTS)
# ==========================================

# --- CEREBRO 1: EL TUTOR (Para el Alumno) ---
INSTRUCCIONES_BASE = """
Eres un GPT personalizado que funciona como INSTRUCTOR DE INTERPRETACIÓN BÍBLICA (Paideia AI).
Tu tono es pastoral, firme pero amable, como el Pastor Mohacid Leal.

TU COMPORTAMIENTO CAMBIA SEGÚN LA LECCIÓN:

MODO 1: FASE INFORMATIVA (Lecciones 1, 2 y 3)
- OBJETIVO: Entregar información pura.
- COMPORTAMIENTO: Eres un EXPOSITOR.
- REGLA DE ORO: NO HAGAS PREGUNTAS. NO PIDAS INTERACCIÓN.
- FLUJO: Escribe todo el contenido de la sección de forma continua. NO hagas pausas tipo "¿Seguimos?".
- FORMATO: Bloques de texto claros y explicativos.

MODO 2: FASE DE ESTUDIO (Lección 4 en adelante)
- OBJETIVO: Enseñar y asegurar comprensión.
- COMPORTAMIENTO: Eres un TUTOR SOCRÁTICO.
- REGLA: Explica un concepto y HAZ UNA PREGUNTA para verificar.

TU FUENTE DE VERDAD:
Usa EXCLUSIVAMENTE el contenido proporcionado en los archivos de conocimiento.
"""

# --- CEREBRO 2: EL MAESTRO EXPERTO (Para Revisión y Admin) ---
INSTRUCCIONES_MAESTRO = """
Actúa como un INSTRUCTOR VIRTUAL AVANZADO DE INTERPRETACIÓN BÍBLICA Y TEOLÓGICA, con enfoque expositivo, pastoral, pedagógico y fiel a las Escrituras.
Tu función principal es enseñar, explicar e interpretar la Biblia de manera responsable, profunda y clara.

────────────────────────
🧠 ENFOQUE GENERAL
────────────────────────
Prioriza siempre la fidelidad bíblica por encima de opiniones personales.
Evita sacar textos de su contexto inmediato o canónico.
Diferencia claramente entre interpretación, doctrina, aplicación y opinión.
No espiritualices ni alegorices sin base textual.

────────────────────────
✅ ESTRUCTURA OBLIGATORIA (3 FASES)
────────────────────────
FASE 1: EXÉGESIS (El Qué)
- Texto, Audiencia, Tipo de Texto.
- Estructura y Argumento.
- Énfasis: una Idea Central Única (ICU).

FASE 2: REFLEXIÓN TEOLÓGICA (La Conexión)
- Conecta con Cristo SOLO por vías legítimas (Observación, Ley->Gracia, Tipología, Promesa/Cumplimiento).

FASE 3: PERSUASIÓN (El Para Qué)
- Argumentos, Aplicación específica y Arreglo (Bosquejo).

────────────────────────
⬛ RECTÁNGULO DE CLOWNEY (Obligatorio)
────────────────────────
Usa este esquema para moverte correctamente desde el pasaje hasta Cristo:
1. 📍 El texto en su contexto (significado original).
2. ⬆️ Conexión con la historia redentora.
3. ➡️ Cristo (cumplimiento).
4. ⬇️ Aplicación para nosotros (en Cristo).

🎯 Objetivo: Evitar moralismo sin evangelio y alegoría forzada.
"""

def get_full_prompt_alumno():
    prompt = INSTRUCCIONES_BASE
    prompt += "\n\n=== BIBLIOTECA DE CONOCIMIENTO (ALUMNO) ===\n"
    if os.path.exists("knowledge"):
        archivos = sorted([f for f in os.listdir("knowledge") if f.endswith(".md")])
        for f in archivos:
            try:
                path = os.path.join("knowledge", f)
                with open(path, "r", encoding="utf-8") as file:
                    prompt += f"\n--- ARCHIVO: {f} ---\n{file.read()}\n"
            except Exception: pass
    return prompt

# Inicialización de Clientes Gemini
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=get_full_prompt_alumno(),
            temperature=0.3
        )
    )

# ==========================================
# 5. VARIABLES DE ESTADO
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "usuario_validado" not in st.session_state: st.session_state.usuario_validado = False
if "datos_usuario" not in st.session_state: st.session_state.datos_usuario = {}
if "maestro_unlocked" not in st.session_state: st.session_state.maestro_unlocked = False
if "ultimo_tema_visto" not in st.session_state: st.session_state.ultimo_tema_visto = ""
if "modo_maestro_view" not in st.session_state: st.session_state.modo_maestro_view = False

# ==========================================
# 6. FUNCIONES AUXILIARES
# ==========================================
def buscar_usuario(email):
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        usuario = df[df['Email'] == email]
        if not usuario.empty: return usuario.iloc[0].to_dict()
        return None
    except Exception: return None

def registrar_nuevo_usuario(datos):
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        nuevo_df = pd.DataFrame([datos])
        df_actualizado = pd.concat([df, nuevo_df], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_actualizado)
        return True
    except Exception as e:
        if "200" in str(e): return True
        st.error(f"Error BD: {e}")
        return False

def actualizar_progreso(email, nuevo_nivel):
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        idx = df.index[df['Email'] == email].tolist()
        if idx:
            df.at[idx[0], 'Progreso'] = nuevo_nivel
            conn.update(worksheet="Hoja 1", data=df)
    except Exception: pass

def normalizar_nombre(texto):
    if not texto: return ""
    texto = texto.lower()
    texto = ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
    return texto.replace(" ", "_")

def mostrar_video_leccion(leccion_actual):
    video_url = None
    if "4." in leccion_actual and leccion_actual in DB_VIDEOS:
        genero = st.session_state.datos_usuario.get('Genero')
        if genero in DB_VIDEOS[leccion_actual]:
            video_url = DB_VIDEOS[leccion_actual][genero]
    elif leccion_actual in DB_VIDEOS and isinstance(DB_VIDEOS[leccion_actual], str):
        video_url = DB_VIDEOS[leccion_actual]
    if video_url:
        st.info("🎥 **Video Explicativo:** Antes de continuar, mira este breve video.")
        with st.expander("▶️ Ver Video de la Clase", expanded=True):
            st.video(video_url)

def contenido_interactivo_leccion_3():
    st.markdown("---")
    st.subheader("5. Materiales y Asignación de Proyecto")
    st.write("Selecciona tu proyecto para habilitar las descargas.")

    with st.expander("📄 Documentos de Apoyo (Descargar primero)", expanded=False):
        c1, c2 = st.columns(2)
        ruta_guia = "materiales/guia_elaboracion.docx"
        ruta_faq = "materiales/preguntas_frecuentes.docx" 
        
        if os.path.exists(ruta_guia):
            with open(ruta_guia, "rb") as f:
                c1.download_button("📥 Guía de Elaboración", f, "guia_elaboracion.docx")
        else: c1.warning("Falta: guia_elaboracion.docx")
            
        if os.path.exists(ruta_faq):
            with open(ruta_faq, "rb") as f:
                c2.download_button("📥 Preguntas Frecuentes", f, "preguntas_frecuentes.docx")
        else: c2.warning("Falta: preguntas_frecuentes.docx")

    st.divider()

    if "libro_seleccionado" not in st.session_state.datos_usuario:
        st.info("🎯 **Configura tu estudio:** Selecciona Género y Libro.")
        col1, col2 = st.columns(2)
        genero = col1.selectbox("1. Género:", ["Seleccionar...", "Narrativa", "Poético", "Discurso"])
        
        libros = []
        if genero != "Seleccionar...":
            libros = list(DB_BIBLIA[genero].keys())
        libro = col2.selectbox("2. Libro:", ["Seleccionar..."] + libros)
        
        if libro != "Seleccionar..." and st.button("🎲 CONFIRMAR Y ASIGNAR PASAJE"):
            with st.spinner("Asignando pasaje aleatorio..."):
                time.sleep(1.0)
                pasaje = random.choice(DB_BIBLIA[genero][libro])
                st.session_state.datos_usuario['Genero'] = genero
                st.session_state.datos_usuario['libro_seleccionado'] = libro
                st.session_state.datos_usuario['Pasaje'] = pasaje
                st.balloons()
                st.rerun()
    else:
        datos = st.session_state.datos_usuario
        st.success(f"✅ PROYECTO: **{datos['libro_seleccionado']}** ({datos['Genero']})")
        st.info(f"📖 TU PASAJE: **{datos['Pasaje']}**")
        st.markdown("#### 📥 Descarga tus Hojas de Trabajo:")
        col_d1, col_d2 = st.columns(2)
        ruta_linea = "materiales/linea_melodica_estandar.docx"
        ruta_trabajo = "materiales/hoja_trabajo_estandar.docx"
        
        if os.path.exists(ruta_linea):
            with open(ruta_linea, "rb") as f:
                col_d1.download_button("📥 Línea Melódica (Plantilla)", f, "linea_melodica_estandar.docx")
        else: col_d1.error("Falta archivo: linea_melodica_estandar.docx")
            
        if os.path.exists(ruta_trabajo):
            with open(ruta_trabajo, "rb") as f:
                col_d2.download_button("📥 Hoja de Trabajo (Plantilla)", f, "hoja_trabajo_estandar.docx")
        else: col_d2.error("Falta archivo: hoja_trabajo_estandar.docx")
        
        if st.checkbox("🔄 Cambiar selección (Solo pruebas)"):
            del st.session_state.datos_usuario['libro_seleccionado']
            st.rerun()

def contenido_vista_maestro():
    """Interfaz exclusiva para el Maestro: Centro de Comando"""
    
    st.markdown("""
    <div style="background-color:#461b7e;padding:15px;border-radius:10px;margin-bottom:20px;">
        <h2 style="color:white;margin:0;">👨‍🏫 Centro de Comando del Maestro</h2>
        <p style="color:#e0e0e0;margin:0;">Panel de Supervisión y Evaluación (Fidelidad Expositiva)</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Revisión de Tareas", "📚 Recursos y Solucionarios", "⚙️ Admin Alumno"])

    # --- PESTAÑA 1: REVISIÓN CON CEREBRO EXPERTO ---
    with tab1:
        st.info("Pega aquí el trabajo del alumno. La IA evaluará usando el Rectángulo de Clowney y las 3 Fases Expositivas.")
        
        c1, c2 = st.columns(2)
        tipo_trabajo = c1.selectbox("Tipo de Tarea", ["Línea Melódica", "Hoja de Trabajo (Exégesis)", "Reflexión Teológica", "Bosquejo Final"])
        libro_contexto = c2.text_input("Libro Bíblico (Contexto)", value=st.session_state.datos_usuario.get('libro_seleccionado', 'General'))
        
        texto_alumno = st.text_area("Pegar contenido del alumno:", height=200, placeholder="Pega aquí lo que escribió el alumno...")
        
        if st.button("🔍 ANALIZAR Y CALIFICAR (MODO EXPERTO)", type="primary"):
            if texto_alumno:
                # AQUÍ INYECTAMOS EL CEREBRO MAESTRO
                prompt_maestro_evaluacion = (
                    f"{INSTRUCCIONES_MAESTRO}\n\n"
                    f"--- SOLICITUD DE EVALUACIÓN ---\n"
                    f"Estás evaluando una tarea de tipo: '{tipo_trabajo}' sobre el libro de '{libro_contexto}'.\n"
                    f"CONTENIDO DEL ALUMNO:\n{texto_alumno}\n\n"
                    "TU TAREA:\n"
                    "1. Analiza si identificó la Idea Central Única (ICU).\n"
                    "2. Verifica si pasó por el Rectángulo de Clowney (Evitar moralismo/alegoría).\n"
                    "3. Evalúa la conexión con Cristo (¿Es legítima o forzada?).\n"
                    "4. Señala fortalezas y correcciones teológicas necesarias.\n"
                    "5. Dale una calificación del 1 al 10."
                )
                
                with st.spinner("Analizando con rigor exegético y teológico..."):
                    try:
                        # Usamos 'generate_content' directo para no afectar el chat del alumno
                        res = st.session_state.client.models.generate_content(
                            model="gemini-2.0-flash", contents=prompt_maestro_evaluacion
                        )
                        st.success("Evaluación Generada:")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"Error al conectar con el cerebro del maestro: {e}")
            else:
                st.warning("El campo de texto está vacío.")

    # --- PESTAÑA 2: RECURSOS ---
    with tab2:
        st.write("Descargas de referencia para el maestro.")
        c1, c2 = st.columns(2)
        ruta_linea = "materiales/linea_melodica_estandar.docx"
        ruta_trabajo = "materiales/hoja_trabajo_estandar.docx"
        
        if os.path.exists(ruta_linea):
            with open(ruta_linea, "rb") as f:
                c1.download_button("📥 Línea Melódica (Plantilla)", f, "plantilla_linea.docx")
        
        if os.path.exists(ruta_trabajo):
            with open(ruta_trabajo, "rb") as f:
                c2.download_button("📥 Hoja de Trabajo (Plantilla)", f, "plantilla_trabajo.docx")

    # --- PESTAÑA 3: ADMINISTRACIÓN ---
    with tab3:
        st.warning("⚠️ Zona de Peligro: Modificar el estado del alumno.")
        st.write(f"**Alumno:** {st.session_state.datos_usuario.get('Nombre')}")
        st.write(f"**Nivel Actual:** {st.session_state.datos_usuario.get('Progreso')} ({st.session_state.leccion_actual_visual})")
        
        c_reset, c_skip = st.columns(2)
        if c_reset.button("🔄 REINICIAR ALUMNO A LECCIÓN 1"):
            st.session_state.datos_usuario['Progreso'] = 0
            st.session_state.leccion_actual_visual = TEMARIO_OFICIAL[0]
            st.session_state.messages = []
            if 'libro_seleccionado' in st.session_state.datos_usuario:
                del st.session_state.datos_usuario['libro_seleccionado']
            actualizar_progreso(st.session_state.datos_usuario['Email'], 0)
            st.success("Alumno reiniciado.")
            time.sleep(1)
            st.rerun()
            
        if c_skip.button("⏩ SALTAR AL SIGUIENTE NIVEL"):
            avanzar_nivel()

    st.divider()
    if st.button("🔙 SALIR DEL MODO MAESTRO (Volver a Clase)"):
        st.session_state.modo_maestro_view = False
        st.rerun()

def avanzar_nivel():
    """Avanza al siguiente nivel de forma segura"""
    nivel_actual = int(st.session_state.datos_usuario['Progreso'])
    if nivel_actual < len(TEMARIO_OFICIAL) - 1:
        nuevo_nivel = nivel_actual + 1
        st.session_state.datos_usuario['Progreso'] = nuevo_nivel
        st.session_state.leccion_actual_visual = TEMARIO_OFICIAL[nuevo_nivel]
        st.session_state.ultimo_tema_visto = TEMARIO_OFICIAL[nuevo_nivel]
        st.session_state.messages = [] 
        actualizar_progreso(st.session_state.datos_usuario['Email'], nuevo_nivel)
        time.sleep(0.5)
        st.rerun()
    else:
        st.balloons()
        st.success("¡CURSO COMPLETADO!")

# ==========================================
# 7. CHAT IA (CEREBRO ALUMNO)
# ==========================================
def stream_gemini_response(texto_usuario):
    try:
        if "COMANDO INTERNO" not in texto_usuario:
            st.session_state.messages.append({"role": "user", "content": texto_usuario})
        
        response_stream = st.session_state.chat.send_message_stream(texto_usuario)
        full_response = ""
        placeholder = st.empty()
        
        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
                time.sleep(0.01)
        
        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "model", "content": full_response})
    except Exception as e:
        st.error(f"Error AI: {e}")

def trigger_leccion_seleccionada(nombre_leccion):
    datos = st.session_state.datos_usuario
    nombre = datos['Nombre']
    instruccion_extra = ""
    
    if "4." in nombre_leccion:
        genero = datos.get('Genero', 'General')
        libro = datos.get('libro_seleccionado', 'la Biblia')
        instruccion_extra = (
            f"\n\nCONTEXTO CRÍTICO: El alumno eligió el género '{genero}' y está estudiando el libro de '{libro}'. "
            f"Tu explicación de 'Introducción al género' debe enfocarse 100% en el género {genero}. "
            f"Usa ejemplos específicos de {libro} para ilustrar los conceptos. "
            "No expliques detalladamente los otros géneros, céntrate en el suyo."
        )

    if nombre_leccion.startswith(("1.", "2.", "3.")):
        modo_instruccion = "Actúa en MODO EXPOSITOR: Entrega la información de forma continua, clara y sin hacer preguntas al final."
    else:
        modo_instruccion = "Actúa en MODO TUTOR SOCRÁTICO: Explica el concepto adaptado a su libro y termina con UNA pregunta reflexiva para verificar comprensión."

    prompt = (
        f"COMANDO INTERNO: El alumno {nombre} ha entrado a la lección '{nombre_leccion}'. "
        f"{instruccion_extra} "
        f"\n\n{modo_instruccion} Salúdalo y comienza."
    )
    stream_gemini_response(prompt)

def trigger_maestro_accion():
    prompt = "COMANDO INTERNO: Activa 'Modo Maestro'. Interrumpe para corregir o modelar un ejercicio."
    stream_gemini_response(prompt)

# ==========================================
# 8. INTERFAZ PRINCIPAL
# ==========================================

# A. LOGIN
if not st.session_state.usuario_validado:
    st.title("🔐 Acceso al Aula Virtual")
    tab1, tab2 = st.tabs(["Ingresar", "Registrarme"])
    
    with tab1:
        email = st.text_input("Correo Electrónico", key="login_email").strip()
        if st.button("Entrar"):
            user = buscar_usuario(email)
            if user:
                st.session_state.datos_usuario = user
                st.session_state.usuario_validado = True
                st.rerun()
            else: st.error("Correo no encontrado.")
            
    with tab2:
        with st.form("registro"):
            nom = st.text_input("Nombre")
            mail = st.text_input("Correo").strip()
            minis = st.selectbox("Ministerio", ["Pastor", "Líder", "Estudiante"])
            iglesia = st.text_input("Iglesia")
            tel = st.text_input("Teléfono")
            if st.form_submit_button("Registrar"):
                if buscar_usuario(mail): st.warning("Ya existe.")
                else:
                    new_user = {"Email": mail, "Nombre": nom, "Progreso": 0, "Ministerio": minis, "Iglesia": iglesia, "Telefono": tel}
                    if registrar_nuevo_usuario(new_user):
                        st.session_state.datos_usuario = new_user
                        st.session_state.usuario_validado = True
                        st.success("¡Bienvenido!")
                        time.sleep(1)
                        st.rerun()

# B. AULA VIRTUAL
else:
    user = st.session_state.datos_usuario
    nivel_real_idx = int(user['Progreso'])
    
    if nivel_real_idx >= len(TEMARIO_OFICIAL): nivel_real_idx = len(TEMARIO_OFICIAL) - 1
    leccion_maxima = TEMARIO_OFICIAL[nivel_real_idx]

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image("https://cfmpaideia.com/wp-content/uploads/2023/05/logo-paideia-blanco.png", width=200)
        st.markdown(f"### 👤 {user['Nombre']}")
        st.caption(f"Nivel: {nivel_real_idx + 1} / {len(TEMARIO_OFICIAL)}")
        st.divider()
        
        if not st.session_state.modo_maestro_view:
            st.subheader("📍 Navegación")
            lecciones_dispo = TEMARIO_OFICIAL[:nivel_real_idx + 1]
            if "leccion_actual_visual" not in st.session_state:
                st.session_state.leccion_actual_visual = leccion_maxima
            try:
                idx_visual = lecciones_dispo.index(st.session_state.leccion_actual_visual)
            except ValueError:
                idx_visual = len(lecciones_dispo) - 1
            leccion_actual = st.selectbox("Ir a lección:", lecciones_dispo, index=idx_visual, key="nav_selector")
            
            if leccion_actual != st.session_state.leccion_actual_visual:
                st.session_state.leccion_actual_visual = leccion_actual
                st.session_state.messages = []
                st.rerun()
            st.progress((nivel_real_idx + 1) / len(TEMARIO_OFICIAL))
            st.divider()
            st.subheader("📂 Tareas")
            up = st.file_uploader("Subir archivo", key="tarea_up")
            if up: st.success("Enviado.")
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("Limpiar"):
                st.session_state.messages = []
                st.rerun()
            if c2.button("Salir"):
                st.session_state.clear()
                st.rerun()

        st.divider()
        if not st.session_state.maestro_unlocked:
            with st.expander("🔐 Maestro"):
                if st.button("Desbloquear") and hmac.compare_digest(st.text_input("Pass", type="password"), maestro_pass):
                    st.session_state.maestro_unlocked = True
                    st.rerun()
        else:
            if st.session_state.modo_maestro_view:
                st.info("🎓 MODO MAESTRO ACTIVO")
            else:
                if st.button("👨‍🏫 ABRIR PANEL MAESTRO"): 
                    st.session_state.modo_maestro_view = True
                    st.session_state.messages = [] 
                    st.rerun()

    # --- AREA PRINCIPAL (DECISIÓN DE VISTA) ---
    if st.session_state.modo_maestro_view:
        contenido_vista_maestro()
    else:
        st.title(f"📖 {leccion_actual}")
        mostrar_video_leccion(leccion_actual)
        
        for m in st.session_state.messages:
            if "COMANDO INTERNO" not in m["content"]:
                with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"]=="user" else "📖"):
                    st.markdown(m["content"])

        if leccion_actual == "3. Indicaciones":
            contenido_interactivo_leccion_3()

        if len(st.session_state.messages) == 0:
            trigger_leccion_seleccionada(leccion_actual)

        if p := st.chat_input("Tu respuesta..."):
            with st.chat_message("user"): st.markdown(p)
            with st.chat_message("model"): stream_gemini_response(p)

        if leccion_actual == leccion_maxima:
            st.markdown("---")
            c1, c2, c3 = st.columns([1,2,1])
            bloqueado = (leccion_actual == "3. Indicaciones" and "libro_seleccionado" not in user)
            if bloqueado:
                c2.warning("⚠️ Debes seleccionar un libro arriba para avanzar.")
            else:
                if c2.button("✅ TERMINAR LECCIÓN Y AVANZAR", use_container_width=True):
                    avanzar_nivel()
        else:
            st.divider()
            st.info(f"Estás repasando **{leccion_actual}**. Ve a **{leccion_maxima}** para avanzar.")