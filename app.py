import streamlit as st

st.set_page_config(page_title="Instructor Virtual", layout="wide")
st.title("Instructor Virtual — Interpretación Bíblica")

# -----------------------------
# Estado (progreso)
# -----------------------------
if "leccion_completada" not in st.session_state:
    st.session_state.leccion_completada = 0

if "pasaje" not in st.session_state:
    st.session_state.pasaje = ""

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Panel")
st.sidebar.write("Lecciones completadas:", st.session_state.leccion_completada)

modo = st.sidebar.radio("Modo", ["Aula", "Alumno", "Maestro", "Hoja de trabajo"])

# -----------------------------
# Modo Aula
# -----------------------------
if modo == "Aula":
    st.subheader("Modo Aula")
    st.write("**Lección 1 (MVP):** Introducción a la Interpretación Bíblica")
    st.info("Regla: primero lección, luego práctica/hoja de trabajo.")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("✅ Completar Lección 1"):
            st.session_state.leccion_completada = max(st.session_state.leccion_completada, 1)
            st.success("Lección 1 completada. Ya puedes usar la Hoja de trabajo.")
    with col2:
        st.caption("Tip: esto es un botón demo. Luego lo reemplazamos por un mini-quiz o actividad final.")

    st.divider()
    st.write("Próximas lecciones (bloqueadas en MVP):")
    st.write("- Lección 2: Línea Melódica del Libro")
    st.write("- Lección 3: Permanecer en la Línea")
    st.write("- ...")

# -----------------------------
# Modo Alumno (coach por preguntas)
# -----------------------------
elif modo == "Alumno":
    st.subheader("Modo Alumno (coach por preguntas)")

    st.session_state.pasaje = st.text_area(
        "Pega tu pasaje o referencia",
        value=st.session_state.pasaje,
        height=160
    )

    st.markdown("### Camino (MVP: primeros 4 pasos)")
    pasos = ["Audiencia original", "Tipo de texto", "Estructura", "Énfasis"]
    cols = st.columns(4)
    for i, p in enumerate(pasos):
        with cols[i]:
            st.checkbox(p, key=f"check_{i}")

    if st.button("Iniciar guía"):
        if not st.session_state.pasaje.strip():
            st.warning("Pega un pasaje o referencia primero.")
        else:
            st.success("Empezamos. Responde en orden (sin saltos).")
            st.write("**1) Audiencia original:** ¿quién escribe, a quién, y con qué propósito?")
            st.write("**2) Tipo de texto:** ¿narrativo, discurso, poético u otro?")
            st.write("**3) Estructura:** ¿qué secciones ves por conectores/repeticiones?")
            st.write("**4) Énfasis:** una oración que resuma lo que el texto enfatiza (sin añadir ideas externas).")

# -----------------------------
# Modo Maestro
# -----------------------------
elif modo == "Maestro":
    st.subheader("Modo Maestro (modelado)")
    st.write("Aquí vamos a incluir ejemplos completos y explicados por lección.")
    st.info("MVP: dejaremos un ejemplo más adelante cuando integremos contenido del curso.")

# -----------------------------
# Hoja de trabajo (bloqueada)
# -----------------------------
else:
    st.subheader("Hoja de trabajo (MVP)")
    if st.session_state.leccion_completada < 1:
        st.warning("🔒 Bloqueada: completa la **Lección 1** en Modo Aula para desbloquear esta práctica.")
    else:
        st.success("Desbloqueada ✅")

        if not st.session_state.pasaje.strip():
            st.info("Primero ve a **Modo Alumno** y pega un pasaje/referencia (opcional, pero recomendado).")
        else:
            st.caption(f"Pasaje/referencia actual: {st.session_state.pasaje[:80]}{'...' if len(st.session_state.pasaje)>80 else ''}")

        st.markdown("### Sección 1 — Énfasis y estructura (MVP)")
        enfasis = st.text_input("Énfasis del pasaje (una oración)")
        estructura = st.text_area("Estructura del texto (bosquejo breve)", height=140)

        st.markdown("### Sección 2 — Notas")
        notas = st.text_area("Notas (observaciones, conectores, repeticiones, etc.)", height=120)

        if st.button("Guardar (demo)"):
            st.toast("Guardado ✅ (demo)")
            st.write("**Resumen (demo):**")
            st.write("- Énfasis:", enfasis if enfasis else "—")
            st.write("- Estructura:", estructura if estructura else "—")
            st.write("- Notas:", notas if notas else "—")
