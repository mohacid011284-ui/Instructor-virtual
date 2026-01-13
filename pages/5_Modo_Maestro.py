import streamlit as st
import difflib
import re

st.set_page_config(page_title="Modo Maestro", layout="wide")
st.title("Modo Maestro — Alumno vs Mejorado (Instructor virtual)")

st.caption("El Maestro toma tus respuestas actuales y propone una versión mejorada, señalando errores concretos.")

# =============================
# Helpers (análisis)
# =============================
def wc(s: str) -> int:
    return len((s or "").strip().split())

def lc(s: str) -> int:
    return len([ln for ln in (s or "").splitlines() if ln.strip()])

def contains_any(text: str, items) -> bool:
    t = (text or "").lower()
    return any(i in t for i in items)

APLICACION_BANDERAS = [
    "hoy", "mi vida", "en mi", "mi trabajo", "mi familia", "nosotros", "yo",
    "esta semana", "en mi casa", "mi negocio", "mi escuela"
]

CONECTORES = [
    "por tanto", "pero", "porque", "entonces", "sin embargo", "para que",
    "a fin de", "por eso", "así que"
]

VERBOS_APP = ["haz", "busca", "ora", "confiesa", "perdona", "sirve", "lee", "deja", "evita", "practica"]

def diff_md(a: str, b: str) -> str:
    """Devuelve un diff sencillo en markdown (líneas con + / -)"""
    a_lines = (a or "").splitlines()
    b_lines = (b or "").splitlines()
    d = difflib.unified_diff(a_lines, b_lines, fromfile="Alumno", tofile="Mejorado", lineterm="")
    out = "\n".join(d)
    return out if out.strip() else "(Sin cambios sugeridos)"

# =============================
# Generadores "mejorados"
# =============================
def mejorar_audiencia(texto: str) -> tuple[str, list[str]]:
    issues = []
    t = (texto or "").strip()

    if wc(t) < 10:
        issues.append("Audiencia original muy corta: falta autor/audiencia/propósito (mínimo 2–3 frases).")
    if contains_any(t, APLICACION_BANDERAS):
        issues.append("Audiencia original contiene lenguaje de aplicación ('hoy', 'mi vida', etc.). Debe ser histórico-literaria.")

    # Plantilla de mejora (sin inventar datos específicos)
    mejorado = t
    if not t:
        mejorado = "Autor: ____. Audiencia: ____. Propósito: ____ (2–3 frases, sin aplicar todavía)."
        issues.append("No hay respuesta: llena autor/audiencia/propósito.")
    else:
        # Si no menciona componentes típicos, sugiere estructura explícita
        if not re.search(r"(autor|escribe|pablo|juan|mois[eé]s|lucas|mateo|marcos)", t.lower()):
            issues.append("No identificas claramente al autor (si no estás seguro, escribe 'Autor probable' y justifica).")
        if not re.search(r"(a\s+la|a\s+los|a\s+las|iglesia|israel|disc[ií]pulos|corint|rom|g[aá]lat|efes)", t.lower()):
            issues.append("No describes claramente a quién va dirigido (audiencia).")
        if not re.search(r"(para|con el fin|prop[oó]sito|a fin)", t.lower()):
            issues.append("No declaras el propósito ('para…').")

        # Formato sugerido sin cambiar el contenido esencial del alumno
        mejorado = (
            "Autor: " + (t[:120] + ("…" if len(t) > 120 else "")) +
            "\nAudiencia: (describe a quién va dirigido, sin aplicar)\n"
            "Propósito: (explica para qué escribe; 1–2 frases)"
        )

    return mejorado, issues


def mejorar_estructura(texto: str) -> tuple[str, list[str]]:
    issues = []
    t = (texto or "").strip()

    if not t:
        return "1) ____\n2) ____\n3) ____  (2–4 movimientos del texto)", ["No hay estructura: escribe 2–4 movimientos del pasaje."]

    if lc(t) < 2:
        issues.append("Estructura en una sola línea: sepárala en 2–4 movimientos (líneas).")
    if not contains_any(t, CONECTORES) and wc(t) < 25:
        issues.append("Estructura poco anclada al flujo: usa conectores/repeticiones para dividir secciones.")

    # Mejora: si es una sola línea, intenta partir por conectores básicos
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    if len(lines) == 1:
        # Partición simple por conectores (si aparecen)
        raw = lines[0]
        parts = re.split(r"\b(pero|porque|por tanto|entonces|sin embargo|para que|a fin de)\b", raw, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            mejorado = "\n".join([f"{i+1}) {parts[i]}" for i in range(min(4, len(parts)))])
        else:
            mejorado = "1) " + raw + "\n2) (siguiente movimiento del texto)\n3) (siguiente movimiento del texto)"
            issues.append("No se detectan conectores claros: escribe manualmente los movimientos.")
    else:
        # Si ya hay líneas, solo las enumera
        mejorado = "\n".join([f"{i+1}) {ln}" if not re.match(r"^\d+\)", ln) else ln for i, ln in enumerate(lines)])

    return mejorado, issues


def mejorar_enfasis(texto: str) -> tuple[str, list[str]]:
    issues = []
    t = (texto or "").strip()

    if not t:
        return "En una oración: el autor enfatiza ____ (sin aplicación).", ["No hay énfasis: escribe 1 oración (6–14 palabras)."]

    if wc(t) < 6:
        issues.append("Énfasis demasiado corto: debe ser una oración completa (mín. 6 palabras).")
    if contains_any(t, APLICACION_BANDERAS):
        issues.append("Énfasis suena a aplicación (hoy/mi vida/etc.). El énfasis debe describir el punto del texto.")
    if contains_any(t, ["ser mejor", "hacer lo correcto", "portarse bien"]):
        issues.append("Énfasis muy genérico: aterriza en lo que el pasaje realmente afirma/ordena/promete.")

    # Mejora: rehace el énfasis como oración plantilla sin inventar doctrina nueva
    mejorado = t
    if wc(t) < 6 or contains_any(t, APLICACION_BANDERAS):
        mejorado = "El pasaje enfatiza que ____ (acción/verdad del texto) para ____ (propósito del texto)."
    else:
        # “pulido” mínimo: capitalizar + punto final
        mejorado = t[0].upper() + t[1:]
        if not mejorado.endswith("."):
            mejorado += "."

    return mejorado, issues


def mejorar_evangelio(estrategia: str, conexion: str) -> tuple[str, list[str]]:
    issues = []
    e = (estrategia or "").strip()
    c = (conexion or "").strip()

    if e == "— Selecciona —" or not e:
        issues.append("No seleccionaste estrategia texto→evangelio.")
    if wc(c) < 12:
        issues.append("Conexión al evangelio muy corta: explica el puente en 2–4 frases.")
    if not contains_any(c, ["cristo", "jesús", "evangelio", "cruz", "resurrección", "gracia"]):
        issues.append("Conexión sin vocabulario del evangelio (Cristo/gracia/cruz/resurrección).")

    if not c:
        mejorado = (
            "Estrategia: (elige una)\n"
            "Puente: El texto revela ____; esto se cumple/ilumina en Cristo porque ____.\n"
            "Resultado: Por eso ____ (sin borrar el énfasis del pasaje)."
        )
    else:
        mejorado = (
            f"Estrategia: {e if e else '(sin elegir)'}\n"
            f"Puente (2–4 frases): {c}\n"
            "Asegúrate de que este puente NO reemplace el énfasis del pasaje, solo lo ilumine."
        )

    return mejorado, issues


def mejorar_aplicacion(ap_crist: str, ap_no: str) -> tuple[str, str, list[str]]:
    issues = []
    a1 = (ap_crist or "").strip()
    a2 = (ap_no or "").strip()

    if wc(a1) < 15:
        issues.append("Aplicación para cristianos muy corta o general: escribe 2–4 aplicaciones concretas con verbos.")
    if a1 and not contains_any(a1, VERBOS_APP):
        issues.append("Aplicación para cristianos sin verbos de acción (haz/busca/ora/confiesa…).")
    if wc(a2) < 8:
        issues.append("Aplicación para no cristianos muy corta: escribe 1–3 invitaciones concretas (evangelio + respuesta).")

    # Plantillas de mejora
    mejorado_crist = a1 if a1 else (
        "- Haz ____ esta semana (concreto)\n"
        "- Ora ____ (concreto)\n"
        "- Confiesa/ajusta ____ (concreto)"
    )
    mejorado_no = a2 if a2 else (
        "- Considera ____ (verdad del texto)\n"
        "- Responde con ____ (arrepentimiento/fe)\n"
        "- Busca ____ (Cristo/comunidad/palabra)"
    )
    return mejorado_crist, mejorado_no, issues

# =============================
# Leer entradas del alumno (session_state)
# =============================
alumno = {
    "pasaje": st.session_state.get("pasaje", ""),
    "audiencia_original": st.session_state.get("audiencia_original", ""),
    "tipo_texto": st.session_state.get("tipo_texto", ""),
    "estructura": st.session_state.get("estructura", ""),
    "enfasis": st.session_state.get("enfasis", ""),
    "estrategia": st.session_state.get("estrategia", "— Selecciona —"),
    "conexion_evangelio": st.session_state.get("conexion_evangelio", ""),
    "aplicacion_cristianos": st.session_state.get("aplicacion_cristianos", ""),
    "aplicacion_no_cristianos": st.session_state.get("aplicacion_no_cristianos", ""),
}

if not alumno["pasaje"].strip():
    st.warning("Aún no hay pasaje. Ve a **Alumno** y pega un pasaje/referencia.")
    st.stop()

# =============================
# Generar mejorado + issues
# =============================
mej_aud, issues_aud = mejorar_audiencia(alumno["audiencia_original"])
mej_est, issues_est = mejorar_estructura(alumno["estructura"])
mej_enf, issues_enf = mejorar_enfasis(alumno["enfasis"])
mej_eva, issues_eva = mejorar_evangelio(alumno["estrategia"], alumno["conexion_evangelio"])
mej_apc, mej_apn, issues_app = mejorar_aplicacion(alumno["aplicacion_cristianos"], alumno["aplicacion_no_cristianos"])

issues = (
    [("Audiencia original", x) for x in issues_aud] +
    [("Estructura", x) for x in issues_est] +
    [("Énfasis", x) for x in issues_enf] +
    [("Evangelio", x) for x in issues_eva] +
    [("Aplicación", x) for x in issues_app]
)

# =============================
# UI: Errores precisos
# =============================
st.subheader("Errores/ajustes precisos detectados")
if issues:
    for seccion, msg in issues:
        st.write(f"• **{seccion}:** {msg}")
else:
    st.success("No detecté problemas importantes. Tu trabajo va por muy buen camino.")

st.divider()

# =============================
# UI: Comparación Alumno vs Mejorado
# =============================
def comparacion(titulo, alumno_txt, mejorado_txt):
    st.markdown(f"## {titulo}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Alumno")
        st.write(alumno_txt or "—")
    with c2:
        st.markdown("### Mejorado (Maestro)")
        st.write(mejorado_txt or "—")

    with st.expander("Ver diferencias (diff)"):
        st.code(diff_md(alumno_txt, mejorado_txt), language="diff")

comparacion("Audiencia original", alumno["audiencia_original"], mej_aud)
comparacion("Estructura", alumno["estructura"], mej_est)
comparacion("Énfasis", alumno["enfasis"], mej_enf)
comparacion("Conexión al evangelio", alumno["conexion_evangelio"], mej_eva)

st.markdown("## Aplicación")
c1, c2 = st.columns(2)
with c1:
    st.markdown("### Alumno (cristianos)")
    st.write(alumno["aplicacion_cristianos"] or "—")
    st.markdown("### Mejorado (cristianos)")
    st.write(mej_apc or "—")
with c2:
    st.markdown("### Alumno (no cristianos)")
    st.write(alumno["aplicacion_no_cristianos"] or "—")
    st.markdown("### Mejorado (no cristianos)")
    st.write(mej_apn or "—")

with st.expander("Ver diferencias (diff) — Aplicación"):
    st.code(diff_md(alumno["aplicacion_cristianos"], mej_apc), language="diff")
    st.code(diff_md(alumno["aplicacion_no_cristianos"], mej_apn), language="diff")

st.divider()

# =============================
# Botón: Copiar mejorado a Hoja (opcional)
# =============================
st.subheader("Acción rápida (opcional)")
st.caption("Si quieres, puedes reemplazar tus campos por la versión 'Mejorado' para seguir trabajando desde ahí.")
if st.button("📌 Aplicar 'Mejorado' a mis campos (sobrescribe)", key="btn_apply_mejorado"):
    st.session_state.audiencia_original = mej_aud
    st.session_state.estructura = mej_est
    st.session_state.enfasis = mej_enf
    st.session_state.conexion_evangelio = mej_eva
    st.session_state.aplicacion_cristianos = mej_apc
    st.session_state.aplicacion_no_cristianos = mej_apn
    st.success("Listo. Ve a **Hoja de trabajo** para continuar con la versión mejorada.")
