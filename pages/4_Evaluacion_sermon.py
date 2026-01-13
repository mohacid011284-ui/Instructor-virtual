import streamlit as st

st.set_page_config(page_title="Evaluación del Sermón", layout="wide")
st.title("Evaluación del sermón — Automática (Instructor virtual)")

# -----------------------------
# Helpers (heurísticas simples)
# -----------------------------
def clamp(n, lo=1, hi=5):
    return max(lo, min(hi, n))

def word_count(s: str) -> int:
    return len((s or "").strip().split())

def line_count(s: str) -> int:
    return len([ln for ln in (s or "").splitlines() if ln.strip()])

def contains_any(text: str, items) -> bool:
    t = (text or "").lower()
    return any(i in t for i in items)

def score_text_fidelity(pasaje: str, estructura: str, enfasis: str) -> int:
    # Heurística: si hay pasaje + estructura y énfasis suficientemente explicados, sube
    score = 1
    if (pasaje or "").strip():
        score += 1
    if word_count(estructura) >= 15 or line_count(estructura) >= 2:
        score += 1
    if word_count(enfasis) >= 6:
        score += 1
    # Penaliza si énfasis suena a aplicación (“hoy”, “mi vida”…)
    if contains_any(enfasis, ["hoy", "mi vida", "en mi", "mi trabajo", "mi familia", "yo", "nosotros"]):
        score -= 1
    return clamp(score)

def score_structure(estructura: str) -> int:
    score = 1
    if line_count(estructura) >= 2:
        score += 2
    if line_count(estructura) >= 4:
        score += 1
    if contains_any(estructura, ["por tanto", "pero", "porque", "entonces", "sin embargo", "para que", "a fin de"]):
        score += 1
    return clamp(score)

def score_emphasis(enfasis: str) -> int:
    score = 1
    wc = word_count(enfasis)
    if wc >= 6:
        score += 2
    if wc >= 10:
        score += 1
    # Penaliza si está muy corto o es vago
    if wc < 6:
        score -= 1
    if contains_any(enfasis, ["ser mejor", "hacer lo correcto", "portarse bien", "tener fe"]):
        score -= 1
    return clamp(score)

def score_christ_centered(estrategia: str, conexion: str) -> int:
    score = 1
    if (estrategia or "") != "— Selecciona —" and (estrategia or "").strip():
        score += 2
    if word_count(conexion) >= 20:
        score += 1
    if contains_any(conexion, ["cristo", "jesús", "evangelio", "cruz", "resurrección", "gracia"]):
        score += 1
    return clamp(score)

def score_application(ap_crist: str, ap_no: str) -> int:
    score = 1
    total_words = word_count(ap_crist) + word_count(ap_no)
    if total_words >= 25:
        score += 2
    if total_words >= 45:
        score += 1
    # Concreción: verbos
    if contains_any(ap_crist + " " + ap_no, ["haz", "busca", "ora", "confiesa", "perdona", "sirve", "lee", "deja", "evita", "practica"]):
        score += 1
    return clamp(score)

def score_clarity(estructura: str, argumento: str, conexion: str) -> int:
    score = 2
    if line_count(estructura) >= 2:
        score += 1
    if word_count(argumento) >= 20:
        score += 1
    if word_count(conexion) >= 20:
        score += 1
    return clamp(score)

def score_pastoral_tone(ap_crist: str, ap_no: str, conexion: str) -> int:
    # Heurística: presencia de gracia/evangelio + evitar puro regaño
    score = 2
    if contains_any(conexion, ["gracia", "misericordia", "perdón", "adopción", "justificación"]):
        score += 2
    if contains_any(ap_crist + " " + ap_no, ["arrep", "confiesa", "perdona", "paciencia", "humildad", "amor"]):
        score += 1
    # Penaliza tono duro
    if contains_any(ap_crist + " " + ap_no, ["deberías", "tienes que", "si no", "castigo"]):
        score -= 1
    return clamp(score)

def build_feedback(scores: dict) -> str:
    # Comentarios automáticos breves
    fuertes = [k for k, v in scores.items() if v >= 4]
    debiles = [k for k, v in scores.items() if v <= 3]

    etiquetas = {
        "texto_fiel": "Fidelidad al texto",
        "estructura_clara": "Estructura",
        "enfasis_claro": "Énfasis",
        "cristo_centrico": "Conexión al evangelio",
        "aplicacion_concreta": "Aplicación",
        "claridad": "Claridad",
        "tono_pastoral": "Tono pastoral",
    }

    out = []
    if fuertes:
        out.append("**Fortalezas:** " + ", ".join(etiquetas[x] for x in fuertes))
    if debiles:
        out.append("**Ajustes prioritarios:** " + ", ".join(etiquetas[x] for x in debiles))

    tips = []
    if scores["enfasis_claro"] <= 3:
        tips.append("Reescribe el énfasis en **una oración completa** (6–12 palabras mínimo) sin aplicar todavía.")
    if scores["estructura_clara"] <= 3:
        tips.append("Divide la estructura en **2–4 movimientos** (líneas) siguiendo conectores/repeticiones.")
    if scores["cristo_centrico"] <= 3:
        tips.append("Elige una **estrategia texto→evangelio** y explica el puente en 2–4 frases.")
    if scores["aplicacion_concreta"] <= 3:
        tips.append("Haz aplicaciones **concretas** (verbos/acciones), 2–4 para cristianos y 1–3 para no cristianos.")
    if tips:
        out.append("**Sugerencias del instructor:**\n- " + "\n- ".join(tips))

    return "\n\n".join(out) if out else "—"

# -----------------------------
# Leer datos del alumno/hoja
# -----------------------------
pasaje = st.session_state.get("pasaje", "")
estructura = st.session_state.get("estructura", "")
enfasis = st.session_state.get("enfasis", "")
argumento_autor = st.session_state.get("argumento_autor", "")
estrategia = st.session_state.get("estrategia", "— Selecciona —")
conexion = st.session_state.get("conexion_evangelio", "")
ap_crist = st.session_state.get("aplicacion_cristianos", "")
ap_no = st.session_state.get("aplicacion_no_cristianos", "")

st.caption("La evaluación se calcula automáticamente con base en lo llenado en Alumno + Hoja de trabajo.")

# -----------------------------
# Calcular evaluación automática
# -----------------------------
scores = {
    "texto_fiel": score_text_fidelity(pasaje, estructura, enfasis),
    "estructura_clara": score_structure(estructura),
    "enfasis_claro": score_emphasis(enfasis),
    "cristo_centrico": score_christ_centered(estrategia, conexion),
    "aplicacion_concreta": score_application(ap_crist, ap_no),
    "claridad": score_clarity(estructura, argumento_autor, conexion),
    "tono_pastoral": score_pastoral_tone(ap_crist, ap_no, conexion),
}

promedio = round(sum(scores.values()) / len(scores), 2)
comentarios_auto = build_feedback(scores)

# -----------------------------
# UI
# -----------------------------
st.subheader("Resultados automáticos")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Promedio", f"{promedio}/5")
with c2:
    st.metric("Bloques evaluados", str(len(scores)))
with c3:
    st.metric("Estado", "✅ Aprobado" if promedio >= 3.5 else "⚠️ Por mejorar")

st.divider()
st.markdown("### Rúbrica (automática)")
colL, colR = st.columns(2)
with colL:
    st.write(f"**Fidelidad al texto:** {scores['texto_fiel']}/5")
    st.write(f"**Estructura clara:** {scores['estructura_clara']}/5")
    st.write(f"**Énfasis claro:** {scores['enfasis_claro']}/5")
    st.write(f"**Conexión al evangelio:** {scores['cristo_centrico']}/5")
with colR:
    st.write(f"**Aplicación concreta:** {scores['aplicacion_concreta']}/5")
    st.write(f"**Claridad:** {scores['claridad']}/5")
    st.write(f"**Tono pastoral:** {scores['tono_pastoral']}/5")

st.divider()
st.markdown("### Comentarios del instructor (automáticos)")
st.write(comentarios_auto)

# -----------------------------
# (Opcional) Ajuste manual
# -----------------------------
with st.expander("Ajuste manual (opcional)"):
    st.caption("Si quieres, puedes corregir puntajes manualmente. Si no, ignóralo.")
    for k in list(scores.keys()):
        scores[k] = st.slider(k, 1, 5, scores[k], key=f"man_{k}")
    promedio2 = round(sum(scores.values()) / len(scores), 2)
    st.write("**Nuevo promedio:**", promedio2)

# Guardar en session_state (opcional)
st.session_state["evaluacion_sermon_auto"] = {
    "scores": scores,
    "promedio": promedio,
    "comentarios": comentarios_auto,
}
