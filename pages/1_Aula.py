
import streamlit as st

st.set_page_config(page_title="Aula", layout="wide")
st.title("Aula")

if "leccion_completada" not in st.session_state:
    st.session_state.leccion_completada = 0

st.write("**Lección 1 (MVP):** Introducción a la Interpretación Bíblica")
st.info("Regla: primero lección, luego práctica.")

if st.button("✅ Completar Lección 1"):
    st.session_state.leccion_completada = max(st.session_state.leccion_completada, 1)
    st.success("Lección 1 completada. Ya puedes ir a Alumno y Hoja de trabajo.")
