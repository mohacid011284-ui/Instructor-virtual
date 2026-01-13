import streamlit as st

st.set_page_config(page_title="Instructor Virtual", layout="wide")

st.title("Instructor Virtual — Interpretación Bíblica")
st.write("✅ Si ves esto, Streamlit ya está funcionando.")

st.divider()

st.header("MVP: Tres modos")
modo = st.radio("Elige modo", ["Aula", "Alumno", "Maestro"], horizontal=True)

if modo == "Aula":
    st.subheader("Modo Aula")
    st.write("Aquí irán las lecciones secuenciales.")
elif modo == "Alumno":
    st.subheader("Modo Alumno")
    pasaje = st.text_area("Pega tu pasaje o referencia", height=150)
    if st.button("Iniciar guía"):
        if not pasaje.strip():
            st.warning("Pega un pasaje o referencia primero.")
        else:
            st.success("Perfecto. Empezamos por la audiencia original.")
            st.write("1) ¿Quién escribe, a quién, y por qué?")
            st.write("2) ¿Qué tipo de texto es (narrativo/discurso/poético)?")
else:
    st.subheader("Modo Maestro")
    st.write("Aquí se mostrarán ejemplos completos modelados.")
