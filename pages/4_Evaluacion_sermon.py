import streamlit as st

st.set_page_config(page_title="Evaluación del Sermón", layout="wide")
st.title("Evaluación del sermón — MVP")

st.caption("Califica 1–5 y agrega comentarios. Luego genera un reporte.")

# Estado
if "eval" not in st.session_state:
    st.session_state.eval = {
        "texto_fiel": 3,
        "estructura_clara": 3,
        "enfasis_claro": 3,
        "cristo_centrico": 3,
        "aplicacion_concreta": 3,
        "claridad": 3,
        "tono_pastoral": 3,
        "comentarios": ""
    }

col1, col2 = st.columns(2)

with col1:
    st.session_state.eval["texto_fiel"] = st.slider("Fidelidad al texto (exégesis)", 1, 5, st.session_state.eval["texto_fiel"])
    st.session_state.eval["estructura_clara"] = st.slider("Estructura clara y lógica", 1, 5, st.session_state.eval["estructura_clara"])
    st.session_state.eval["enfasis_claro"] = st.slider("Énfasis del sermón (una idea dominante)", 1, 5, st.session_state.eval["enfasis_claro"])
    st.session_state.eval["cristo_centrico"] = st.slider("Conexión al evangelio/Cristo (sin forzar)", 1, 5, st.session_state.eval["cristo_centrico"])

with col2:
    st.session_state.eval["aplicacion_concreta"] = st.slider("Aplicación concreta y bíblica", 1, 5, st.session_state.eval["aplicacion_concreta"])
    st.session_state.eval["claridad"] = st.slider("Claridad (lenguaje, ejemplos, ritmo)", 1, 5, st.session_state.eval["claridad"])
    st.session_state.eval["tono_pastoral"] = st.slider("Tono pastoral (verdad + gracia)", 1, 5, st.session_state.eval["tono_pastoral"])

st.session_state.eval["comentarios"] = st.text_area(
    "Comentarios / sugerencias (qué mejorar y cómo)",
    value=st.session_state.eval["comentarios"],
    height=160
)

st.divider()

if st.button("🧾 Generar reporte", key="btn_reporte_eval"):
    e = st.session_state.eval
    promedio = round((e["texto_fiel"] + e["estructura_clara"] + e["enfasis_claro"] + e["cristo_centrico"] +
                      e["aplicacion_concreta"] + e["claridad"] + e["tono_pastoral"]) / 7, 2)

    st.subheader("Reporte (MVP)")
    st.write(f"**Promedio:** {promedio}/5")
    st.markdown("""
**Fortalezas (si 4–5):**
- Fidelidad al texto
- Estructura
- Énfasis
- Conexión al evangelio
- Aplicación
- Claridad
- Tono pastoral

**Siguientes pasos (si 1–3):**
- Aclara el énfasis en una sola oración.
- Revisa si la estructura sale del texto.
- Ajusta aplicaciones: menos general, más concreto.
- Conecta a Cristo sin borrar el punto del pasaje.
""")
    st.write("**Comentarios del evaluador:**")
    st.write(e["comentarios"] or "—")


