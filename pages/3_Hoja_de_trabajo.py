import streamlit as st
import os
import json
from datetime import datetime

st.set_page_config(page_title="Hoja de trabajo", layout="wide")
st.title("Hoja de trabajo (oficial — MVP)")

# Estado mínimo
if "leccion_completada" not in st.session_state:
    st.session_state.leccion_completada = 0
if "pasaje" not in st.session_state:
    st.session_state.pasaje = ""
if "audiencia_original" not in st.session_state:
    st.session_state.audiencia_original = ""
if "tipo_texto" not in st.session_state:
    st.session_state.tipo_texto = ""
if "estructura" not in st.session_state:
    st.session_state.estructura = ""
if "enfasis" not in st.session_state:
    st.session_state.enfasis = ""

# Defaults hoja
hoja_defaults = {
    "contexto_literario": "",
    "contexto_cultural": "",
    "contexto_biblico": "",
    "contexto_circunstancial": "",
    "linea_melodica": "",
    "argumento_autor": "",
    "estrategia": "— Selecciona —",
    "conexion_evangelio": "",
    "aplicacion_cristianos": "",
    "aplicacion_no_cristianos": "",
}
for k, v in hoja_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Guardar/cargar persistente
SAVE_PATH = "ultima_hoja.json"

def snapshot_hoja() -> dict:
    return {
        "pasaje": st.session_state.pasaje,
        "audiencia_original": st.session_state.audiencia_original,
        "tipo_texto": st.session_state.tipo_texto,
        "estructura": st.session_state.estructura,
        "enfasis": st.session_state.enfasis,
        "contexto_literario": st.session_state.contexto_literario,
        "contexto_cultural": st.session_state.contexto_cultural,
        "contexto_biblico": st.session_state.contexto_biblico,
        "contexto_circunstancial": st.session_state.contexto_circunstancial,
        "linea_melodica": st.session_state.linea_melodica,
        "argumento_autor": st.session_state.argumento_autor,
        "estrategia": st.session_state.estrategia,
        "conexion_evangelio": st.session_state.conexion_evangelio,
        "aplicacion_cristianos": st.session_state.aplicacion_cristianos,
        "aplicacion_no_cristianos": st.session_state.aplicacion_no_cristianos,
    }

def guardar_ultima_hoja():
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot_hoja(), f, ensure_ascii=False, indent=2)

def cargar_ultima_hoja() -> bool:
    if not os.path.exists(SAVE_PATH):
        return False
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for k, v in data.items():
        st.session_state[k] = v
    return True

# Autocarga una sola vez
if "autocarga_hecha" not in st.session_state:
    st.session_state.autocarga_hecha = True
    cargar_ultima_hoja()

# Bloqueos
if st.session_state.leccion_completada < 1:
    st.warning("🔒 Bloqueada: completa la Lección 1 en **Aula**.")
    st.stop()

if not (st.session_state.pasaje.strip() and st.session_state.estructura.strip() and st.session_state.enfasis.strip()):
    st.warning("🔒 Completa en **Alumno** hasta Estructura y Énfasis para desbloquear esta hoja.")
    st.stop()

st.success("Desbloqueada ✅")

st.caption("Pasaje/referencia:")
st.code(st.session_state.pasaje)

st.markdown("### Resumen traído del Alumno")
st.write("**Audiencia original:**")
st.write(st.session_state.audiencia_original or "—")
st.write("**Tipo de texto:**", st.session_state.tipo_texto or "—")
st.write("**Estructura:**")
st.write(st.session_state.estructura or "—")
st.write("**Énfasis:**", st.session_state.enfasis or "—")

st.divider()

# 1) Contexto
st.markdown("## 1) Contexto e hilos contextuales")
col1, col2 = st.columns(2)
with col1:
    st.session_state.contexto_literario = st.text_area(
        "Contexto literario (¿qué pasa antes/después?)",
        value=st.session_state.contexto_literario,
        height=110,
        key="hoja_contexto_literario"
    )
    st.session_state.contexto_cultural = st.text_area(
        "Contexto cultural (solo si el texto lo exige)",
        value=st.session_state.contexto_cultural,
        height=110,
        key="hoja_contexto_cultural"
    )
with col2:
    st.session_state.contexto_biblico = st.text_area(
        "Contexto bíblico (citas/alusiones; relación con otros textos)",
        value=st.session_state.contexto_biblico,
        height=110,
        key="hoja_contexto_biblico"
    )
    st.session_state.contexto_circunstancial = st.text_area(
        "Contexto circunstancial (situación del autor/audiencia)",
        value=st.session_state.contexto_circunstancial,
        height=110,
        key="hoja_contexto_circunstancial"
    )

# 2) Línea melódica
st.markdown("## 2) Línea melódica del libro")
st.session_state.linea_melodica = st.text_input(
    "En una frase: ¿cuál es la línea melódica del libro?",
    value=st.session_state.linea_melodica,
    key="hoja_linea_melodica"
)

# 3) Argumento
st.markdown("## 3) Argumento del autor (flujo)")
st.session_state.argumento_autor = st.text_area(
    "Resume el argumento en 3–6 líneas (qué está haciendo el autor y cómo llega al énfasis)",
    value=st.session_state.argumento_autor,
    height=140,
    key="hoja_argumento_autor"
)

# 4) Texto → Evangelio
st.markdown("## 4) Del texto al evangelio")
opciones = [
    "— Selecciona —", "Tipología", "Promesa-Cumplimiento", "Tema bíblico",
    "Contraste ley/evangelio", "Necesidad humana/solución en Cristo", "Otro"
]
idx = opciones.index(st.session_state.estrategia) if st.session_state.estrategia in opciones else 0
st.session_state.estrategia = st.selectbox(
    "Estrategia principal",
    opciones,
    index=idx,
    key="hoja_estrategia"
)
st.session_state.conexion_evangelio = st.text_area(
    "Explica la conexión con el evangelio (sin opacar el énfasis del texto)",
    value=st.session_state.conexion_evangelio,
    height=120,
    key="hoja_conexion_evangelio"
)

# 5) Aplicación
st.markdown("## 5) Del significado a la vida")
st.session_state.aplicacion_cristianos = st.text_area(
    "Aplicación para cristianos (concretas, 2–4)",
    value=st.session_state.aplicacion_cristianos,
    height=110,
    key="hoja_aplicacion_cristianos"
)
st.session_state.aplicacion_no_cristianos = st.text_area(
    "Aplicación para no cristianos (concretas, 1–3)",
    value=st.session_state.aplicacion_no_cristianos,
    height=110,
    key="hoja_aplicacion_no_cristianos"
)

st.divider()

# Validación mínima
faltantes = []
if not st.session_state.linea_melodica.strip():
    faltantes.append("Línea melódica")
if st.session_state.estrategia == "— Selecciona —":
    faltantes.append("Estrategia (texto→evangelio)")
if not st.session_state.conexion_evangelio.strip():
    faltantes.append("Conexión con el evangelio")
if not st.session_state.aplicacion_cristianos.strip():
    faltantes.append("Aplicación (cristianos)")
if faltantes:
    st.info("Para completar el MVP, te faltan: " + ", ".join(faltantes))

# Exportar JSON
st.markdown("## Exportar (JSON)")
hoja_export = {
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "pasaje": st.session_state.pasaje,
    "audiencia_original": st.session_state.audiencia_original,
    "tipo_texto": st.session_state.tipo_texto,
    "estructura": st.session_state.estructura,
    "enfasis": st.session_state.enfasis,
    "contexto": {
        "literario": st.session_state.contexto_literario,
        "cultural": st.session_state.contexto_cultural,
        "biblico": st.session_state.contexto_biblico,
        "circunstancial": st.session_state.contexto_circunstancial,
    },
    "linea_melodica": st.session_state.linea_melodica,
    "argumento_autor": st.session_state.argumento_autor,
    "texto_a_evangelio": {
        "estrategia": st.session_state.estrategia,
        "conexion": st.session_state.conexion_evangelio,
    },
    "aplicacion": {
        "cristianos": st.session_state.aplicacion_cristianos,
        "no_cristianos": st.session_state.aplicacion_no_cristianos,
    }
}

st.download_button(
    label="⬇️ Descargar hoja (JSON)",
    data=json.dumps(hoja_export, ensure_ascii=False, indent=2),
    file_name="hoja_trabajo.json",
    mime="application/json",
    key="btn_download_json"
)

st.divider()
st.markdown("## Guardado local (MVP)")
c1, c2 = st.columns(2)
with c1:
    if st.button("💾 Guardar como última hoja", key="btn_save_last"):
        guardar_ultima_hoja()
        st.success("Guardado en ultima_hoja.json ✅")
with c2:
    if st.button("📥 Cargar última hoja", key="btn_load_last"):
        ok = cargar_ultima_hoja()
        st.success("Cargado ✅" if ok else "No existe ultima_hoja.json todavía.")

