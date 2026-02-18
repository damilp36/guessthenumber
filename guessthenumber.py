import streamlit as st
from dataclasses import dataclass
from typing import List
import streamlit.components.v1 as components
import html
import time


# ----------------------------
# Number prompt helper
# ----------------------------
def speak(text: str):
    # Always show in UI
    st.session_state["last_prompt"] = text

    # Browser TTS (client-side)
    safe = html.escape(text)
    nonce = str(time.time()).replace(".", "")  # forces re-run even if same text

    components.html(
        f"""
        <div id="tts_{nonce}"></div>
        <script>
        (function() {{
            const text = "{safe}";
            if (!('speechSynthesis' in window)) {{
                console.log("Web Speech API not supported in this browser.");
                return;
            }}

            // Cancel anything currently speaking
            window.speechSynthesis.cancel();

            const u = new SpeechSynthesisUtterance(text);
            u.rate = 1.0;   // 0.1 to 10
            u.pitch = 1.0;  // 0 to 2
            u.volume = 1.0; // 0 to 1

            // Pick an English voice if available (optional)
            const pickVoice = () => {{
                const voices = window.speechSynthesis.getVoices() || [];
                const preferred =
                    voices.find(v => /en-US/i.test(v.lang)) ||
                    voices.find(v => /en/i.test(v.lang)) ||
                    voices[0];
                if (preferred) u.voice = preferred;
                window.speechSynthesis.speak(u);
            }};

            // Some browsers load voices async
            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length) {{
                pickVoice();
            }} else {{
                window.speechSynthesis.onvoiceschanged = pickVoice;
            }}
        }})();
        </script>
        """,
        height=0,
    )



@dataclass
class Player:
    name: str
    secret: int


# ----------------------------
# Session state init
# ----------------------------
def init_state():
    defaults = {
        "phase": "setup",          # setup -> locked -> playing -> finished
        "num_players": 2,
        "players": [],             # List[Player]
        "turn_idx": 0,
        "target_idx": 1,           # player being guessed
        "winner": None,
        "last_prompt": "",
        "history": [],             # list of dicts
        "current_guess": 0,        # initialize widget-backed state BEFORE widget is created
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_game(keep_num_players: bool = True):
    num_players = st.session_state.get("num_players", 2) if keep_num_players else 2
    st.session_state.clear()
    init_state()
    st.session_state["num_players"] = num_players


def next_turn():
    n = len(st.session_state["players"])
    st.session_state["turn_idx"] = (st.session_state["turn_idx"] + 1) % n
    st.session_state["target_idx"] = (st.session_state["turn_idx"] + 1) % n


def reset_guess():
    # safe to call in callbacks
    st.session_state["current_guess"] = 0


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Number Guess Game", page_icon="🎙️", layout="centered")
init_state()

st.title("Number Guess Game")   
st.caption("Players choose secret numbers (0–100). Take turns guessing. Number prompts guide you!")

with st.sidebar:
    st.header("Game Controls")
    if st.button("🔄 Reset game"):
        reset_game()

    st.markdown("---")
    st.write("**Action:**")
    st.info(st.session_state.get("last_prompt", "") or "No prompt yet.")

# ----------------------------
# Phase: Setup
# ----------------------------
if st.session_state["phase"] == "setup":
    st.subheader("1) Setup players")

    st.session_state["num_players"] = st.number_input(
        "Number of players",
        min_value=2,
        max_value=8,
        value=int(st.session_state["num_players"]),
        step=1,
    )

    st.write("Each player enters a **name** and a **secret number** (0–100).")
    st.warning("For a real 'secret' experience, have each player take turns entering while others look away.")

    temp_names = []
    temp_secrets = []

    for i in range(st.session_state["num_players"]):
        with st.expander(f"Player {i+1}", expanded=(i < 2)):
            name = st.text_input(f"Name (Player {i+1})", key=f"name_{i}")
            secret = st.number_input(
                f"Secret number (Player {i+1})",
                min_value=0,
                max_value=100,
                value=0,
                step=1,
                key=f"secret_{i}",
            )
            temp_names.append(name.strip())
            temp_secrets.append(int(secret))

    col1, col2 = st.columns(2)
    with col1:
        lock = st.button("✅ Lock in secrets")
    with col2:
        st.button("🧹 Clear", on_click=reset_game)

    if lock:
        if any(n == "" for n in temp_names):
            st.error("Please enter a name for every player.")
        else:
            st.session_state["players"] = [Player(n, s) for n, s in zip(temp_names, temp_secrets)]
            st.session_state["phase"] = "locked"
            st.success("Secrets locked. Ready to start!")

# ----------------------------
# Phase: Locked -> Start
# ----------------------------
elif st.session_state["phase"] == "locked":
    st.subheader("2) Start game")
    st.write("Players are ready:")
    for p in st.session_state["players"]:
        st.write(f"• **{p.name}**")

    if st.button("▶️ Start"):
        st.session_state["phase"] = "playing"
        st.session_state["turn_idx"] = 0
        st.session_state["target_idx"] = 1 % len(st.session_state["players"])
        st.session_state["winner"] = None
        st.session_state["history"] = []
        reset_guess()

        guesser = st.session_state["players"][st.session_state["turn_idx"]].name
        target = st.session_state["players"][st.session_state["target_idx"]].name
        speak(f"{guesser}, it's your turn. Guess {target}'s number.")
        st.rerun()

# ----------------------------
# Phase: Playing
# ----------------------------
elif st.session_state["phase"] == "playing":
    players: List[Player] = st.session_state["players"]

    guesser_idx = st.session_state["turn_idx"]
    target_idx = st.session_state["target_idx"]

    guesser = players[guesser_idx]
    target = players[target_idx]

    st.subheader("3) Play")
    st.write(f"🎯 **Current turn:** {guesser.name} guesses **{target.name}**'s number")

    st.number_input(
        f"{guesser.name}, enter your guess (0–100)",
        min_value=0,
        max_value=100,
        step=1,
        key="current_guess",
    )

    def submit_guess():
        players_local: List[Player] = st.session_state["players"]
        guesser_i = st.session_state["turn_idx"]
        target_i = st.session_state["target_idx"]

        guesser_local = players_local[guesser_i]
        target_local = players_local[target_i]

        g = int(st.session_state["current_guess"])
        secret = target_local.secret

        if g == secret:
            st.session_state["winner"] = guesser_local.name
            st.session_state["phase"] = "finished"
            st.session_state["history"].append(
                {"guesser": guesser_local.name, "target": target_local.name, "guess": g, "result": "CORRECT"}
            )
            speak(f"Correct! {guesser_local.name} wins! {target_local.name}'s number was {secret}.")
            return
        else:
            hint = "lower" if g > secret else "higher"
            st.session_state["history"].append(
                {"guesser": guesser_local.name, "target": target_local.name, "guess": g, "result": hint.upper()}
            )

            speak(f"{guesser_local.name}, your guess is {hint} than {target_local.name}'s number.")

            # Next player's turn
            next_turn()
            next_guesser = players_local[st.session_state["turn_idx"]].name
            next_target = players_local[st.session_state["target_idx"]].name
            speak(f"{next_guesser}, it's your turn. Guess {next_target}'s number.")

            reset_guess()

    st.button("📣 Submit guess", on_click=submit_guess)

    if st.session_state["history"]:
        st.markdown("---")
        st.write("### 📜 Guess history")
        st.dataframe(st.session_state["history"], use_container_width=True)

# ----------------------------
# Phase: Finished
# ----------------------------
elif st.session_state["phase"] == "finished":
    st.subheader("🏁 Game over")
    st.success(f"🏆 Winner: **{st.session_state['winner']}**")

    if st.session_state["history"]:
        st.write("### 📜 Final guess history")
        st.dataframe(st.session_state["history"], use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Play again (same players)"):
            st.session_state["phase"] = "playing"
            st.session_state["turn_idx"] = 0
            st.session_state["target_idx"] = 1 % len(st.session_state["players"])
            st.session_state["winner"] = None
            st.session_state["history"] = []
            reset_guess()

            speak(
                f"{st.session_state['players'][0].name}, it's your turn. "
                f"Guess {st.session_state['players'][1].name}'s number."
            )
            st.rerun()
    with col2:
        if st.button("🧑‍🤝‍🧑 New players"):
            reset_game(keep_num_players=False)
            st.rerun()
