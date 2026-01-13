import streamlit as st

st.set_page_config(page_title="Alumno", layout="wide")
st.title("Alumno (pasos obligatorios)")

if "pasaje" not in st.session_state:
    st.session_state.pasaje = ""
if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1
if "audiencia_original" not in st.session_state:
    st.session_state.audiencia_original = ""
if "tipo_texto" not in st.session_state:
    st.session_state.tipo_texto = ""
if "estructura" not in st.session_state:
    st.session_state.estructura = ""
if "enfasis" not in st.session_state:
    st.session_state.enfasis = ""

def ir_a_paso(n):
    st.session_state.paso_actual = n

def puede_avanzar(paso):
    if paso == 1:
        return bool(st.session_state.pasaje.strip()) and bool(st.session_state.audiencia_original.strip())
    if paso == 2:
        return bool(st.session_state.tipo_texto.strip())
    if paso == 3:
        return bool(st.session_state.estructura.strip())
    if paso == 4:
        return bool(st.session_state.enfasis.strip())
    return False

st.session_state.pasaje = st.text_area(
    "Pega tu pasaje o referencia",
    value=st.session_state.pasaje,
    height=130
)

paso = st.session_state.paso_actual

if paso == 1:
    st.session_state.audiencia_original = st.text_area(
        "Audiencia original: ¿quién escribe, a quién y por qué?",
        value=st.session_state.audiencia_original
    )
    if st.button("Siguiente"):
        if puede_avanzar(1):
            ir_a_paso(2)

elif paso == 2:
    st.session_state.tipo_texto = st.text_input(
        "Tipo de texto",
        value=st.session_state.tipo_texto
    )
    if st.button("Siguiente"):
        if puede_avanzar(2):
            ir_a_paso(3)

elif paso == 3:
    st.session_state.estructura = st.text_area(
        "Estructura del texto",
        value=st.session_state.estructura
    )
    if st.button("Siguiente"):
        if puede_avanzar(3):
            ir_a_paso(4)

else:
    st.session_state.enfasis = st.text_input(
        "Énfasis (una oración)",
        value=st.session_state.enfasis
    )
    if st.button("Terminar"):
        if puede_avanzar(4):
            st.success("Listo. Ve a Hoja de trabajo.")

