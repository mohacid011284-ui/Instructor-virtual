import streamlit as st

st.set_page_config(page_title="Instructor Virtual", layout="wide")

st.title("Instructor Virtual — Inicio")
st.write("Usa el menú de la izquierda para navegar:")
st.markdown("""
- **Aula**: completa lecciones (desbloquea práctica)  
- **Alumno**: pasos obligatorios (audiencia → tipo → estructura → énfasis)  
- **Hoja de trabajo**: formulario oficial + exportar/guardar  
- **Evaluación del sermón**: próximamente  
""")

st.info("Tip: Si no ves el menú, recarga la página. Streamlit lo crea cuando detecta la carpeta `pages/`.")
