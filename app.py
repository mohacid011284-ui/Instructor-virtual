import streamlit as st

st.set_page_config(page_title="Instructor Virtual", layout="wide")
st.title("Instructor Virtual — Interpretación Bíblica")

# -----------------------------
# Estado base
# -----------------------------
if "leccion_completada" not in st.session_state:
    st.session_state.leccion_completada = 0

if "pasaje" not in st.session_state:
    st.session_state.pasaje = ""

# Wizard (pasos del alumno)
if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1  # 1..4
if "audiencia_original" not in st.session_state:
    st.session_state.audiencia_original = ""
if "tipo_texto" not in st.session_state:
    st.session_state.tipo_texto = ""
if "estructura" not in st.session_state:
    st.session_state.estructura = ""
if "enfasis" not in st.session_state:
    st.session_state.enfasis = ""

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Panel")
st.sidebar.write("Lecciones completadas:", st.session_state.leccion_completada)

modo = st.sidebar.radio("Modo", ["Aula", "Alumno", "Maestro", "Hoja de trabajo"])

# -----------------------------
# Helpers
# -----------------------------
def ir_a_paso(n: int):
    st.session_state.paso_actual = n

def puede_avanzar(paso: int) -> bool:
    if paso == 1:
        return bool(st.session_state.pasaje.strip()) and bool(st.session_state.audiencia_original.strip())
    if paso == 2:
        return bool(st.session_state.tipo_texto.strip())
    if paso == 3:
        return bool(st.session_state.estructura.strip())
    if paso == 4:
        return bool(st.session_state.enfasis.strip())
    return False

# -----------------------------
# Modo Aula
# -----------------------------
if modo == "Aula":
    st.subheader("Modo Aula")
    st.write("**Lección 1 (MVP):** Introducción a la Interpretación Bíblica")
    st.info("Regla: primero lección, luego práctica.")

    if st.button("✅ Completar Lección 1"):
        st.session_state.leccion_completada = max(st.session_state.leccion_completada, 1)
        st.success("Lección 1 completada. Ya puedes trabajar con el Alumno y Hoja de trabajo.")

    st.divider()
    st.write("Próximas lecciones (luego):")
    st.write("- Lección 2: Línea Melódica del Libro")
    st.write("- Lección 3: Permanecer en la Línea")

# -----------------------------
# Modo Alumno (wizard)
# -----------------------------
elif modo == "Alumno":
    st.subheader("Modo Alumno (pasos obligatorios)")
    st.caption("Regla del MVP: no puedes saltar pasos. Completa uno y luego avanza.")

    # Progreso visual
    colp = st.columns(4)
    etiquetas = ["1) Audiencia original", "2) Tipo de texto", "3) Estructura", "4) Énfasis"]
    for i in range(4):
        with colp[i]:
            hecho = False
            if i == 0:
                hecho = bool(st.session_state.audiencia_original.strip()) and bool(st.session_state.pasaje.strip())
            elif i == 1:
                hecho = bool(st.session_state.tipo_texto.strip())
            elif i == 2:
                hecho = bool(st.session_state.estructura.strip())
            elif i == 3:
                hecho = bool(st.session_state.enfasis.strip())
            st.metric(etiquetas[i], "✅" if hecho else "—")

    st.divider()

    # Entrada de pasaje siempre visible
    st.session_state.pasaje = st.text_area(
        "Pega tu pasaje o referencia",
        value=st.session_state.pasaje,
        height=130
    )

    # Paso actual
    paso = st.session_state.paso_actual

    if paso == 1:
        st.markdown("### Paso 1 — Audiencia original")
        st.session_state.audiencia_original = st.text_area(
            "¿Quién escribe, a quién y con qué propósito? (2–5 líneas)",
            value=st.session_state.audiencia_original,
            height=120
        )
        if st.button("Siguiente → (Paso 2)"):
            if puede_avanzar(1):
                ir_a_paso(2)
            else:
                st.warning("Completa el pasaje y la audiencia original para avanzar.")

    elif paso == 2:
        st.markdown("### Paso 2 — Tipo de texto")
        st.session_state.tipo_texto = st.text_input(
            "Tipo de texto (ej: narrativo / discurso / poético / epístola / proverbio...)",
            value=st.session_state.tipo_texto
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Volver (Paso 1)"):
                ir_a_paso(1)
        with c2:
            if st.button("Siguiente → (Paso 3)"):
                if puede_avanzar(2):
                    ir_a_paso(3)
                else:
                    st.warning("Escribe el tipo de texto para avanzar.")

    elif paso == 3:
        st.markdown("### Paso 3 — Estructura")
        st.session_state.estructura = st.text_area(
            "Bosquejo breve del pasaje (secciones por conectores/repeticiones)",
            value=st.session_state.estructura,
            height=140
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Volver (Paso 2)"):
                ir_a_paso(2)
        with c2:
            if st.button("Siguiente → (Paso 4)"):
                if puede_avanzar(3):
                    ir_a_paso(4)
                else:
                    st.warning("Escribe una estructura para avanzar.")

    else:
        st.markdown("### Paso 4 — Énfasis")
        st.session_state.enfasis = st.text_input(
            "En una oración: ¿qué enfatiza el pasaje? (sin añadir ideas externas)",
            value=st.session_state.enfasis
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Volver (Paso 3)"):
                ir_a_paso(3)
        with c2:
            if st.button("✅ Terminar (y preparar Hoja de trabajo)"):
                if puede_avanzar(4):
                    st.success("Listo. Ya tienes base para llenar la Hoja de trabajo.")
                else:
                    st.warning("Escribe un énfasis para terminar.")

    st.divider()
    if st.button("🔄 Reiniciar respuestas del Alumno"):
        st.session_state.paso_actual = 1
        st.session_state.audiencia_original = ""
        st.session_state.tipo_texto = ""
        st.session_state.estructura = ""
        st.session_state.enfasis = ""
        st.success("Reiniciado.")

# -----------------------------
# Modo Maestro
# -----------------------------
elif modo == "Maestro":
    st.subheader("Modo Maestro (modelado)")
    st.write("Luego pondremos ejemplos completos y explicados.")

# -----------------------------
# Hoja de trabajo (usa lo capturado)
# -----------------------------
else:
    st.subheader("Hoja de trabajo (MVP)")

    if st.session_state.leccion_completada < 1:
        st.warning("🔒 Bloqueada: completa la Lección 1 en Modo Aula.")
    else:
        # Bloqueo por pasos del alumno
        if not (st.session_state.pasaje.strip() and st.session_state.enfasis.strip() and st.session_state.estructura.strip()):
            st.warning("🔒 Completa en Modo Alumno hasta **Estructura** y **Énfasis** para desbloquear esta hoja.")
        else:
            st.success("Desbloqueada ✅")

            st.caption("Pasaje/referencia:")
            st.code(st.session_state.pasaje)

            st.markdown("### Resumen traído del Modo Alumno")
            st.write("**Audiencia original:**")
            st.write(st.session_state.audiencia_original or "—")
            st.write("**Tipo de texto:**", st.session_state.tipo_texto or "—")
            st.write("**Estructura:**")
            st.write(st.session_state.estructura or "—")
            st.write("**Énfasis:**", st.session_state.enfasis or "—")

            st.divider()
            st.markdown("### Sección extra (notas)")
            notas = st.text_area("Observaciones / conectores / repeticiones", height=120)

            if st.button("Guardar (demo)"):
                st.toast("Guardado ✅ (demo)")
