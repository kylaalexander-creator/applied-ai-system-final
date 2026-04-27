import os
import random

import streamlit as st
from dotenv import load_dotenv

from logic_utils import (
    LEVELS,
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)
from memory_store import clear_memory, load_total_score, save_game
from rag_hints import (
    get_achievements,
    get_game_over_message,
    get_hint,
    get_level_suggestion,
    get_pregame_prediction,
    get_pregame_reveal,
    get_skill_surge_config,
    get_surge_summary,
)

load_dotenv()

AI_ENABLED = bool(os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400;1,400&display=swap');

/* ── Background ── */
.stApp {
    background-color: #FDF0EC;
    background-image:
        radial-gradient(ellipse at 15% 10%, rgba(180, 50, 70, 0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 90%, rgba(140, 30, 60, 0.06) 0%, transparent 55%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(175deg, #6B1625 0%, #9B2335 100%);
    border-right: 2px solid #C4405A;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption {
    color: #FFE8EC !important;
    font-family: 'Lora', Georgia, serif !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,200,210,0.4) !important;
    color: #FFE8EC !important;
}

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #6B1625 !important;
    letter-spacing: 0.5px;
}
h1 {
    text-align: center;
    border-bottom: 2px solid #C4405A;
    padding-bottom: 10px;
    margin-bottom: 4px;
}
p, label, .stMarkdown, li {
    font-family: 'Lora', Georgia, serif !important;
    color: #3D1010 !important;
}
.stCaption p {
    color: #9B4555 !important;
    font-style: italic;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #C4405A !important;
    color: #FFF5F5 !important;
    border: 1px solid #9B2335 !important;
    border-radius: 3px !important;
    font-family: 'Lora', Georgia, serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px;
    padding: 0.4rem 1.2rem !important;
    transition: background-color 0.2s, transform 0.1s;
}
.stButton > button:hover {
    background-color: #9B2335 !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0px); }

/* ── Text input ── */
.stTextInput > div > div > input {
    border: 1.5px solid #C4405A !important;
    border-radius: 3px !important;
    background-color: #FFF8F6 !important;
    color: #3D1010 !important;
    font-family: 'Lora', Georgia, serif !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6B1625 !important;
    box-shadow: 0 0 0 2px rgba(107, 22, 37, 0.15) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 3px !important;
    font-family: 'Lora', Georgia, serif !important;
}

/* ── Checkbox ── */
.stCheckbox label span {
    color: #3D1010 !important;
    font-family: 'Lora', Georgia, serif !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border: 1.5px solid #C4405A !important;
    background-color: #FFF8F6 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #FFF5F2;
    border: 1px solid #E8B0B0;
    border-radius: 4px;
    padding: 10px 16px !important;
    text-align: center;
}
[data-testid="stMetricLabel"] p {
    font-family: 'Lora', Georgia, serif !important;
    color: #9B4555 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #6B1625 !important;
    font-size: 1.8rem !important;
}

/* ── Divider ── */
hr { border-color: #E8A0A0 !important; opacity: 0.6; }

/* ── Expander ── */
details > summary {
    font-family: 'Lora', Georgia, serif !important;
    color: #9B2335 !important;
}

/* ── Progress bar (surge) ── */
[data-testid="stProgressBar"] > div > div {
    background-color: #C4405A !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: styled message card ───────────────────────────────────────────────

def hint_card(text: str, tone: str = "neutral") -> None:
    colors = {
        "neutral": ("#FFF0F2", "#C4405A", "#6B1625"),
        "success": ("#F0FFF4", "#2E7D52", "#1A4D32"),
        "error":   ("#FFF0F0", "#C44040", "#6B1625"),
        "info":    ("#FFF5E8", "#9B6020", "#5C3A10"),
        "surge":   ("#1A0508", "#C4405A", "#FFB0C0"),
    }
    bg, border, text_color = colors.get(tone, colors["neutral"])
    st.markdown(
        f"""<div style="
            background:{bg};border-left:3px solid {border};
            border-radius:0 4px 4px 0;padding:10px 16px;margin:8px 0;
            font-family:'Lora',Georgia,serif;font-style:italic;
            color:{text_color};font-size:0.95rem;line-height:1.5;
        ">{text}</div>""",
        unsafe_allow_html=True,
    )


# ── Session state defaults ────────────────────────────────────────────────────

def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("level_select", "Level 3")
_init("secret", None)
_init("attempts", 1)
_init("score", 0)
_init("status", "playing")
_init("history", [])
_init("game_over_message", None)
_init("level_change_message", None)
# Running score — seeded from file so it survives page reloads
_init("total_score", load_total_score())
# Prediction state
_init("prediction", None)
_init("prediction_msg", None)
_init("prediction_reveal", None)
_init("achievements", [])
# Surge state
_init("surge_active", False)
_init("surge_config", None)
_init("surge_game_index", 0)
_init("surge_results", [])
_init("surge_total_score", 0)
_init("surge_summary", None)


def _on_level_change() -> None:
    st.session_state.secret = None
    st.session_state.attempts = 1
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.game_over_message = None
    st.session_state.level_change_message = None
    st.session_state.prediction = None
    st.session_state.prediction_msg = None
    st.session_state.prediction_reveal = None
    st.session_state.achievements = []


# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.header("Settings")

if st.session_state.surge_active:
    st.sidebar.markdown(
        "<p style='color:#FFB0C0;font-size:0.85rem;text-align:center;"
        "letter-spacing:2px;font-weight:bold;'>⚡ SKILL SURGE ACTIVE</p>",
        unsafe_allow_html=True,
    )
    cfg = st.session_state.surge_config
    game_cfg = cfg["games"][st.session_state.surge_game_index]
    st.sidebar.caption(f"Challenge {st.session_state.surge_game_index + 1} of 5")
    st.sidebar.caption(f"Range: {game_cfg['low']} – {game_cfg['high']}")
    st.sidebar.caption(f"Attempts: {game_cfg['attempts']}")
    st.sidebar.caption(f"Surge Score: {st.session_state.surge_total_score}")
    st.sidebar.divider()
    if st.sidebar.button("✕ Exit Surge", use_container_width=True):
        st.session_state.surge_active = False
        st.session_state.surge_config = None
        st.session_state.surge_game_index = 0
        st.session_state.surge_results = []
        st.session_state.surge_total_score = 0
        st.session_state.surge_summary = None
        st.session_state.status = "playing"
        st.session_state.history = []
        st.session_state.game_over_message = None
        st.session_state.secret = None
        st.rerun()
else:
    difficulty = st.sidebar.selectbox("Level", LEVELS, key="level_select", on_change=_on_level_change)
    attempt_limit = get_attempt_limit(difficulty)
    low, high = get_range_for_difficulty(difficulty)
    st.sidebar.caption(f"Range: {low} – {high}")
    st.sidebar.caption(f"Attempts: {attempt_limit}")
    if AI_ENABLED:
        st.sidebar.caption("🤖 AI hints on")
    st.sidebar.divider()
    if AI_ENABLED:
        if st.sidebar.button("⚡ Skill Surge", use_container_width=True):
            with st.spinner("Analyzing your weak spots…"):
                try:
                    config = get_skill_surge_config()
                    if config:
                        st.session_state.surge_config = config
                        st.session_state.surge_active = True
                        st.session_state.surge_game_index = 0
                        st.session_state.surge_results = []
                        st.session_state.surge_total_score = 0
                        st.session_state.surge_summary = None
                        first = config["games"][0]
                        st.session_state.secret = random.randint(first["low"], first["high"])
                        st.session_state.attempts = 1
                        st.session_state.score = 0
                        st.session_state.status = "playing"
                        st.session_state.history = []
                        st.session_state.game_over_message = None
                        st.rerun()
                    else:
                        st.sidebar.warning("Play at least 5 games to unlock Skill Surge.")
                except Exception as e:
                    st.sidebar.error(f"Could not build surge: {e}")

    st.sidebar.divider()
    confirm_reset = st.sidebar.checkbox("Confirm reset", key="confirm_reset")
    if st.sidebar.button("Reset All Progress", use_container_width=True, disabled=not confirm_reset):
        clear_memory()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Resolve active game parameters ───────────────────────────────────────────

if st.session_state.surge_active:
    game_cfg = st.session_state.surge_config["games"][st.session_state.surge_game_index]
    difficulty = game_cfg["level"]
    low, high, attempt_limit = game_cfg["low"], game_cfg["high"], game_cfg["attempts"]
else:
    difficulty = st.session_state.level_select
    low, high = get_range_for_difficulty(difficulty)
    attempt_limit = get_attempt_limit(difficulty)

if st.session_state.secret is None:
    st.session_state.secret = random.randint(low, high)
    st.session_state.prediction_reveal = None
    st.session_state.achievements = []
    if AI_ENABLED and not st.session_state.surge_active:
        try:
            pred, pred_msg = get_pregame_prediction(difficulty, attempt_limit)
            st.session_state.prediction = pred
            st.session_state.prediction_msg = pred_msg
        except Exception:
            st.session_state.prediction = None
            st.session_state.prediction_msg = None


# ── Header ────────────────────────────────────────────────────────────────────

st.title("Game Glitch Investigator")
if not st.session_state.surge_active:
    st.caption("A number guessing game with memory.")

# ── Surge banner ──────────────────────────────────────────────────────────────

if st.session_state.surge_active:
    cfg = st.session_state.surge_config
    game_cfg = cfg["games"][st.session_state.surge_game_index]
    idx = st.session_state.surge_game_index

    st.markdown(
        f"""<div style="
            background:linear-gradient(135deg,#3D0010 0%,#6B1625 100%);
            border:1px solid #C4405A;border-radius:6px;
            padding:16px 20px;margin:8px 0 16px 0;
        ">
          <p style="color:#FFB0C0;font-family:'Playfair Display',serif;font-size:1.1rem;
                    margin:0 0 4px 0;letter-spacing:1px;">
            ⚡ SKILL SURGE — Challenge {idx + 1} of 5
          </p>
          <p style="color:#FF8090;font-family:'Lora',Georgia,serif;font-size:1rem;
                    font-weight:bold;margin:0 0 4px 0;">
            {game_cfg['challenge_name']}
          </p>
          <p style="color:#E8C0C8;font-family:'Lora',Georgia,serif;font-size:0.85rem;
                    font-style:italic;margin:0;">
            {game_cfg['taunt']}
          </p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.progress((idx) / 5)


# ── Game info & metrics ───────────────────────────────────────────────────────

st.markdown(
    f"<p style='text-align:center;font-size:0.95rem;color:#9B4555;font-style:italic;'>"
    f"Guess a number between <strong>{low}</strong> and <strong>{high}</strong></p>",
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
running = st.session_state.total_score + st.session_state.score
m1.metric("Running Score", running, delta=st.session_state.score if st.session_state.score != 0 else None)
m2.metric("Attempts Left", attempt_limit - st.session_state.attempts + 1)
if st.session_state.surge_active:
    m3.metric("Surge Score", st.session_state.surge_total_score)
else:
    m3.metric("Level", difficulty.replace("Level ", ""))


# ── Controls ─────────────────────────────────────────────────────────────────

game_key = f"guess_{difficulty}_{st.session_state.surge_game_index}"
raw_guess = st.text_input(
    "Your guess:", key=game_key, label_visibility="collapsed",
    placeholder=f"Enter a number between {low} and {high}…"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess", use_container_width=True)
with col2:
    new_game = st.button("New Game", use_container_width=True)
with col3:
    show_hint = st.checkbox("Show hints", value=True)

if (
    st.session_state.prediction_msg
    and st.session_state.status == "playing"
    and not st.session_state.surge_active
):
    hint_card(f"Prediction: {st.session_state.prediction_msg}", "info")

with st.expander("Debug"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Level:", difficulty)
    st.write("Surge active:", st.session_state.surge_active)
    st.write("History:", st.session_state.history)


# ── New game (exits surge) ────────────────────────────────────────────────────

if new_game:
    st.session_state.surge_active = False
    st.session_state.surge_config = None
    st.session_state.surge_game_index = 0
    st.session_state.surge_results = []
    st.session_state.surge_total_score = 0
    st.session_state.surge_summary = None
    st.session_state.attempts = 1
    st.session_state.secret = None
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.game_over_message = None
    st.session_state.level_change_message = None
    st.session_state.prediction = None
    st.session_state.prediction_msg = None
    st.session_state.prediction_reveal = None
    st.session_state.achievements = []
    hint_card("New game started — good luck.", "info")
    st.rerun()


# ── Game over state ───────────────────────────────────────────────────────────

if st.session_state.status != "playing":
    tone = "success" if st.session_state.status == "won" else "error"
    if st.session_state.game_over_message:
        hint_card(st.session_state.game_over_message, tone)

    if st.session_state.prediction_reveal and not st.session_state.surge_active:
        hint_card(f"Prediction check: {st.session_state.prediction_reveal}", "info")

    for ach in (st.session_state.achievements or []):
        hint_card(f"Achievement unlocked — {ach['title']}: {ach['description']}", "success")

    if st.session_state.surge_active:
        idx = st.session_state.surge_game_index
        if idx < 4:
            if st.button("Next Challenge →", use_container_width=True):
                st.session_state.surge_game_index += 1
                nxt = st.session_state.surge_config["games"][st.session_state.surge_game_index]
                st.session_state.secret = random.randint(nxt["low"], nxt["high"])
                st.session_state.attempts = 1
                st.session_state.score = 0
                st.session_state.status = "playing"
                st.session_state.history = []
                st.session_state.game_over_message = None
                st.rerun()
        else:
            # Surge complete
            if st.session_state.surge_summary:
                hint_card(f"⚡ Surge complete — {st.session_state.surge_summary}", "surge")
            wins = sum(1 for r in st.session_state.surge_results if r["result"] == "won")
            st.markdown(
                f"<p style='text-align:center;font-family:Playfair Display,serif;"
                f"color:#6B1625;font-size:1.1rem;'>"
                f"Final Surge Score: <strong>{st.session_state.surge_total_score}</strong> "
                f"— {wins}/5 wins</p>",
                unsafe_allow_html=True,
            )
            if st.button("End Skill Surge", use_container_width=True):
                st.session_state.surge_active = False
                st.session_state.surge_config = None
                st.session_state.surge_game_index = 0
                st.session_state.surge_results = []
                st.session_state.surge_total_score = 0
                st.session_state.surge_summary = None
                st.session_state.status = "playing"
                st.session_state.history = []
                st.session_state.game_over_message = None
                st.session_state.secret = None
                st.rerun()
    else:
        if st.session_state.level_change_message:
            hint_card(st.session_state.level_change_message, "info")

    st.stop()


# ── Surge result recorder (must be defined before submit block) ───────────────

def _record_surge_result(result: str, level: str, attempts: int, score: int) -> None:
    """Append result to surge tracking and generate summary on last game."""
    st.session_state.surge_results.append({
        "result": result, "level": level,
        "attempts": attempts, "score": score,
    })
    st.session_state.surge_total_score += score

    if st.session_state.surge_game_index == 4:
        try:
            st.session_state.surge_summary = get_surge_summary(
                st.session_state.surge_results,
                st.session_state.surge_total_score,
            )
        except Exception:
            wins = sum(1 for r in st.session_state.surge_results if r["result"] == "won")
            st.session_state.surge_summary = (
                f"{wins}/5 wins. Total surge score: {st.session_state.surge_total_score}."
            )


# ── Submit guess ──────────────────────────────────────────────────────────────

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        hint_card(err, "error")
    else:
        st.session_state.history.append(guess_int)
        secret = st.session_state.secret
        outcome, static_message = check_guess(guess_int, secret)

        if show_hint and outcome != "Win":
            if AI_ENABLED:
                with st.spinner(""):
                    try:
                        hint = get_hint(
                            guess=guess_int,
                            direction=outcome,
                            attempt=st.session_state.attempts,
                            max_attempts=attempt_limit,
                            difficulty=difficulty,
                            history=st.session_state.history,
                            game_range=(low, high),
                        )
                        hint_card(hint, "surge" if st.session_state.surge_active else "neutral")
                    except Exception:
                        hint_card(static_message)
            else:
                hint_card(static_message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.session_state.total_score += st.session_state.score
            end_msg = f"You found it — the secret was {secret}. Score: {st.session_state.score}"

            if st.session_state.surge_active:
                _record_surge_result("won", difficulty, st.session_state.attempts, st.session_state.score)

            if AI_ENABLED and not st.session_state.surge_active:
                with st.spinner(""):
                    try:
                        save_game({
                            "difficulty": difficulty,
                            "secret": secret,
                            "guesses": list(st.session_state.history),
                            "attempts": st.session_state.attempts,
                            "score": st.session_state.score,
                            "result": "won",
                            "range": f"{low}-{high}",
                        })
                        end_msg = get_game_over_message(
                            result="won", secret=secret,
                            attempts=st.session_state.attempts,
                            score=st.session_state.score,
                            difficulty=difficulty,
                            history=list(st.session_state.history),
                            game_range=(low, high),
                        )
                        lvl_msg, new_level = get_level_suggestion(difficulty)
                        if new_level:
                            st.session_state.level_select = new_level
                            st.session_state.level_change_message = lvl_msg
                        if st.session_state.prediction is not None:
                            try:
                                st.session_state.prediction_reveal = get_pregame_reveal(
                                    st.session_state.prediction, st.session_state.attempts, "won"
                                )
                            except Exception:
                                pass
                        try:
                            st.session_state.achievements = get_achievements(
                                "won", difficulty, st.session_state.attempts, st.session_state.score
                            )
                        except Exception:
                            st.session_state.achievements = []
                    except Exception:
                        pass

            st.session_state.game_over_message = end_msg
            hint_card(end_msg, "success")

            if not st.session_state.surge_active:
                st.markdown(
                    f"<p style='font-family:Lora,Georgia,serif;font-size:0.85rem;"
                    f"color:#9B4555;text-align:center;'>"
                    f"<em>{difficulty} · {st.session_state.attempts} attempt(s) · "
                    f"guesses: {', '.join(map(str, st.session_state.history))}</em></p>",
                    unsafe_allow_html=True,
                )

        else:
            st.session_state.attempts += 1
            if st.session_state.attempts > attempt_limit:
                st.session_state.status = "lost"
                st.session_state.total_score += st.session_state.score
                end_msg = f"Out of attempts — the secret was {secret}. Score: {st.session_state.score}"

                if st.session_state.surge_active:
                    _record_surge_result("lost", difficulty, st.session_state.attempts - 1, st.session_state.score)

                if AI_ENABLED and not st.session_state.surge_active:
                    with st.spinner(""):
                        try:
                            save_game({
                                "difficulty": difficulty,
                                "secret": secret,
                                "guesses": list(st.session_state.history),
                                "attempts": st.session_state.attempts - 1,
                                "score": st.session_state.score,
                                "result": "lost",
                                "range": f"{low}-{high}",
                            })
                            end_msg = get_game_over_message(
                                result="lost", secret=secret,
                                attempts=st.session_state.attempts - 1,
                                score=st.session_state.score,
                                difficulty=difficulty,
                                history=list(st.session_state.history),
                                game_range=(low, high),
                            )
                            lvl_msg, new_level = get_level_suggestion(difficulty)
                            if new_level:
                                st.session_state.level_select = new_level
                                st.session_state.level_change_message = lvl_msg
                            if st.session_state.prediction is not None:
                                try:
                                    st.session_state.prediction_reveal = get_pregame_reveal(
                                        st.session_state.prediction, st.session_state.attempts - 1, "lost"
                                    )
                                except Exception:
                                    pass
                            try:
                                st.session_state.achievements = get_achievements(
                                    "lost", difficulty, st.session_state.attempts - 1, st.session_state.score
                                )
                            except Exception:
                                st.session_state.achievements = []
                        except Exception:
                            pass

                st.session_state.game_over_message = end_msg
                hint_card(end_msg, "error")


st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
