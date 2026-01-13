import streamlit as st

st.set_page_config(page_title="Modo Maestro", layout="wide")
st.title("Modo Maestro — Comparación con modelo")

st.caption("Comparación pedagógica: alumno vs modelo (no es para copiar, es para aprender).")

# -----------------------------
# MODELO (ejemplo fijo)
# -----------------------------
MODELO = {
    "audiencia_original": (
        "Pablo escribe a la iglesia en Roma, compuesta por judíos y gentiles, "
        "para explicar el evangelio y unificar a la iglesia bajo la justicia de Dios."
    ),
    "estructura": (
        "1) El problema universal del pecado (1:18–3:20)\n"
        "2) La justificación por la fe (3:21–5:21)\n"
        "3) Vida nueva en Cristo (6–8)"
    ),
    "enfasis": (
        "Dios justifica gratuitamente al pecador por la fe en Cristo, no por obras."
    ),
    "evangelio": (
        "La justicia que el texto exige es la que Dios provee en Cristo, "
        "quien cumple la ley y carga con la condena del pecador."
    ),
}

# -----------------------------
# Leer alumno
# -----------------------------
alumno = {
    "audiencia_original": st.session_state.get("audiencia_original", ""),
    "estructura": st.session_state.get("estructura", ""),
    "enfasis": st.session_state.get("enfasis", ""),
    "evangelio": st.session_state.get("conexion_evangelio", ""),
}

# -----------------------------
# Comparación visual
# -----------------------------
def bloque_comparacion(titulo, alumno_txt, modelo_txt, pista):
    st.markdown(f"## {titulo}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Alumno")
        st.write(alumno_txt or "—")
    with c2:
        st.markdown("### Modelo")
        st.write(modelo_txt)
    st.info("💡 Pista del Maestro: " + pista)

bloque_comparacion(
    "Audiencia original",
    alumno["audiencia_original"],
    MODELO["audiencia_original"],
    "¿Incluyes autor, audiencia y propósito? Evita aplicaciones."
)

bloque_comparacion(
    "Estructura",
    alumno["estructura"],
    MODELO["estructura"],
    "¿Tu estructura sale del flujo del texto o es temática?"
)

bloque_comparacion(
    "Énfasis",
    alumno["enfasis"],
    MODELO["enfasis"],
    "¿Es una sola idea clara y textual?"
)

bloque_comparacion(
    "Conexión al evangelio",
    alumno["evangelio"],
    MODELO["evangelio"],
    "¿El evangelio ilumina el texto sin reemplazarlo?"
)

