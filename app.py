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
# 4. CONFIGURACIÓN DEL CEREBRO IA
# ==========================================

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

def get_full_prompt():
    prompt = INSTRUCCIONES_BASE
    prompt += "\n\n=== BIBLIOTECA DE CONOCIMIENTO ===\n"
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
            system_instruction=get_full_prompt(),
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
    """Limpia nombres para archivos (útil aunque sean genéricos)"""
    if not texto: return ""
    texto = texto.lower()
    texto = ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
    return texto.replace(" ", "_")

def contenido_interactivo_leccion_3():
    """Maneja la selección de proyecto y descarga de materiales ESTÁNDAR"""
    
    st.markdown("---")
    st.subheader("5. Materiales y Asignación de Proyecto")
    st.write("Selecciona tu proyecto para habilitar las descargas.")

    # A. MATERIALES GENERALES (Guía + Preguntas Frecuentes)
    with st.expander("📄 Documentos de Apoyo (Descargar primero)", expanded=False):
        c1, c2 = st.columns(2)
        
        # Rutas de archivos
        ruta_guia = "materiales/guia_elaboracion.docx"
        ruta_faq = "materiales/preguntas_frecuentes.docx" 
        
        # Botón 1: Guía
        if os.path.exists(ruta_guia):
            with open(ruta_guia, "rb") as f:
                c1.download_button("📥 Guía de Elaboración", f, "guia_elaboracion.docx")
        else: c1.warning("Falta: guia_elaboracion.docx")
            
        # Botón 2: Preguntas Frecuentes
        if os.path.exists(ruta_faq):
            with open(ruta_faq, "rb") as f:
                c2.download_button("📥 Preguntas Frecuentes", f, "preguntas_frecuentes.docx")
        else: c2.warning("Falta: preguntas_frecuentes.docx")

    st.divider()

    # B. LÓGICA DE SELECCIÓN (Si no ha elegido, muestra selectores)
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
                
                # Guardamos la selección
                st.session_state.datos_usuario['Genero'] = genero
                st.session_state.datos_usuario['libro_seleccionado'] = libro
                st.session_state.datos_usuario['Pasaje'] = pasaje
                st.balloons()
                st.rerun()

    # C. SI YA ELIGIÓ (Muestra descargas estándar)
    else:
        datos = st.session_state.datos_usuario
        st.success(f"✅ PROYECTO: **{datos['libro_seleccionado']}** ({datos['Genero']})")
        st.info(f"📖 TU PASAJE: **{datos['Pasaje']}**")
        
        st.markdown("#### 📥 Descarga tus Hojas de Trabajo:")
        st.write("Estas hojas son el formato estándar para tu análisis.")
        
        col_d1, col_d2 = st.columns(2)
        
        # Archivos ESTÁNDAR
        archivo_linea = "materiales/linea_melodica_estandar.docx"
        archivo_trabajo = "materiales/hoja_trabajo_estandar.docx"
        
        if os.path.exists(archivo_linea):
            with open(archivo_linea, "rb") as f:
                col_d1.download_button("📥 Línea Melódica (Plantilla)", f, "linea_melodica_estandar.docx")
        else: col_d1.error("Falta archivo: linea_melodica_estandar.docx")
            
        if os.path.exists(archivo_trabajo):
            with open(archivo_trabajo, "rb") as f:
                col_d2.download_button("📥 Hoja de Trabajo (Plantilla)", f, "hoja_trabajo_estandar.docx")
        else: col_d2.error("Falta archivo: hoja_trabajo_estandar.docx")
        
        # Checkbox para pruebas (al final)
        if st.checkbox("🔄 Cambiar selección (Solo pruebas)"):
            del st.session_state.datos_usuario['libro_seleccionado']
            st.rerun()

def avanzar_nivel():
    """Avanza al siguiente nivel de forma segura"""
    nivel_actual = int(st.session_state.datos_usuario['Progreso'])
    
    if nivel_actual < len(TEMARIO_OFICIAL) - 1:
        nuevo_nivel = nivel_actual + 1
        st.session_state.datos_usuario['Progreso'] = nuevo_nivel
        # Forzamos la actualización de la variable visual
        st.session_state.leccion_actual_visual = TEMARIO_OFICIAL[nuevo_nivel]
        st.session_state.ultimo_tema_visto = TEMARIO_OFICIAL[nuevo_nivel]
        st.session_state.messages = [] 
        actualizar_progreso(st.session_state.datos_usuario['Email'], nuevo_nivel)
        time.sleep(0.5)
        st.rerun()
    else:
        st.balloons()
        st.success("¡CURSO COMPLETADO!")

    def contenido_vista_maestro():
    """Interfaz exclusiva para el Maestro: Descargas y Revisión"""
    st.markdown("## 👨‍🏫 Panel de Maestro: Revisión y Herramientas")
    st.info("Estás en el modo de supervisión. Aquí puedes descargar las plantillas de referencia y corregir el trabajo del alumno.")

    # 1. ZONA DE DESCARGAS (REFERENCIA)
    st.subheader("1. Plantillas de Referencia")
    c1, c2 = st.columns(2)
    
    ruta_linea = "materiales/linea_melodica_estandar.docx"
    ruta_trabajo = "materiales/hoja_trabajo_estandar.docx"
    
    if os.path.exists(ruta_linea):
        with open(ruta_linea, "rb") as f:
            c1.download_button("📥 Descargar Línea Melódica", f, "linea_melodica_estandar.docx")
    
    if os.path.exists(ruta_trabajo):
        with open(ruta_trabajo, "rb") as f:
            c2.download_button("📥 Descargar Hoja de Trabajo", f, "hoja_trabajo_estandar.docx")

    st.divider()

    # 2. ZONA DE REVISIÓN
    st.subheader("2. Revisión de Tarea")
    st.write("Copia y pega aquí el contenido que el alumno escribió en su hoja para evaluarlo.")
    
    # Selector de tipo de tarea
    tipo_tarea = st.radio("¿Qué estás revisando?", ["Línea Melódica", "Hoja de Trabajo / Texto"], horizontal=True)
    
    # Área de texto para pegar el contenido del alumno
    contenido_alumno = st.text_area("Pegar contenido del alumno aquí:", height=200)
    
    if st.button("📝 REVISAR TAREA AHORA"):
        if contenido_alumno:
            with st.spinner("Analizando teológicamente y estructuralmente..."):
                # Prompt específico para que la IA actúe como EXAMINADOR
                prompt_revision = (
                    f"ACTÚA COMO UN PROFESOR DE HERMENÉUTICA EXPERTO EN PREDICACIÓN EXPOSITIVA. "
                    f"Tarea a revisar: {tipo_tarea}. "
                    f"Contexto: El alumno está analizando el libro de {st.session_state.datos_usuario.get('libro_seleccionado', 'la Biblia')}. "
                    f"Contenido del alumno: '{contenido_alumno}'. "
                    "INSTRUCCIONES: Evalúa si el alumno ha identificado correctamente la idea central. "
                    "Señala aciertos y errores. Sé constructivo pero riguroso teológicamente. "
                    "Si es Línea Melódica, verifica si captó el flujo del pensamiento del autor."
                )
                stream_gemini_response(prompt_revision)
        else:
            st.warning("⚠️ Por favor pega el contenido del alumno para poder revisarlo.")

    st.divider()
    
    # 3. BOTÓN PARA SALIR
    if st.button("🔙 VOLVER AL AULA (Salir del Modo Maestro)"):
        st.session_state.modo_maestro_view = False
        st.rerun()

# ==========================================
# 7. CHAT IA
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
    nombre = st.session_state.datos_usuario['Nombre']
    prompt = f"COMANDO INTERNO: El alumno {nombre} está en '{nombre_leccion}'. Salúdalo y expón el tema SIN hacer preguntas finales."
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
    
    # Blindaje de índice
    if nivel_real_idx >= len(TEMARIO_OFICIAL): nivel_real_idx = len(TEMARIO_OFICIAL) - 1
    leccion_maxima = TEMARIO_OFICIAL[nivel_real_idx]

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image("https://cfmpaideia.com/wp-content/uploads/2023/05/logo-paideia-blanco.png", width=200)
        st.markdown(f"### 👤 {user['Nombre']}")
        st.caption(f"Nivel: {nivel_real_idx + 1} / {len(TEMARIO_OFICIAL)}")
        st.divider()
        
        # Si NO estamos en modo maestro, mostramos navegación normal
        if not st.session_state.modo_maestro_view:
            st.subheader("📍 Navegación")
            lecciones_dispo = TEMARIO_OFICIAL[:nivel_real_idx + 1]
            
            if "leccion_actual_visual" not in st.session_state:
                st.session_state.leccion_actual_visual = leccion_maxima
            
            try:
                idx_visual = lecciones_dispo.index(st.session_state.leccion_actual_visual)
            except ValueError:
                idx_visual = len(lecciones_dispo) - 1
                
            leccion_actual = st.selectbox(
                "Ir a lección:", lecciones_dispo, index=idx_visual, key="nav_selector"
            )
            
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

        # --- BOTÓN MAESTRO (LÓGICA ACTUALIZADA) ---
        st.divider()
        if not st.session_state.maestro_unlocked:
            with st.expander("🔐 Maestro"):
                if st.button("Desbloquear") and hmac.compare_digest(st.text_input("Pass", type="password"), maestro_pass):
                    st.session_state.maestro_unlocked = True
                    st.rerun()
        else:
            # Si ya está desbloqueado, mostramos el botón de entrar/salir
            if st.session_state.modo_maestro_view:
                st.info("🎓 MODO MAESTRO ACTIVO")
            else:
                if st.button("👨‍🏫 ABRIR PANEL MAESTRO"): 
                    st.session_state.modo_maestro_view = True
                    st.session_state.messages = [] # Limpiamos chat visualmente
                    st.rerun()

    # --- AREA PRINCIPAL (DECISIÓN DE VISTA) ---
    
    # CASO 1: VISTA DE MAESTRO (Pantalla Limpia + Herramientas)
    if st.session_state.modo_maestro_view:
        contenido_vista_maestro()
        
        # Mostramos la respuesta de la IA (La corrección) aquí abajo
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="👨‍🏫" if m["role"]=="user" else "🤖"):
                st.markdown(m["content"])

    # CASO 2: VISTA DE ALUMNO (Clase Normal)
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

        # --- BOTÓN AVANZAR ---
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