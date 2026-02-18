import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
import streamlit.components.v1 as components
import html
import time

from voice_guess_component import voice_guess


# ============================
# Browser helpers (TTS + SFX)
# ============================
def speak(text: str):
    """Browser TTS (client-side). Always mirrors prompt in sidebar."""
    st.session_state["last_prompt"] = text

    safe = html.escape(text)
    nonce = str(time.time()).replace(".", "")

    components.html(
        f"""
        <div id="tts_{nonce}"></div>
        <script>
        (function() {{
            const text = "{safe}";
            if (!('speechSynthesis' in window)) return;

            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.rate = 1.0;
            u.pitch = 1.0;
            u.volume = 1.0;

            const pickVoice = () => {{
                const voices = window.speechSynthesis.getVoices() || [];
                const preferred =
                    voices.find(v => /en-US/i.test(v.lang)) ||
                    voices.find(v => /en/i.test(v.lang)) ||
                    voices[0];
                if (preferred) u.voice = preferred;
                window.speechSynthesis.speak(u);
            }};

            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length) pickVoice();
            else window.speechSynthesis.onvoiceschanged = pickVoice;
        }})();
        </script>
        """,
        height=0,
    )


def play_sound(kind: str):
    """
    Lightweight browser sound effects via WebAudio.
    kind: "success", "fail", "turn"
    """
    nonce = str(time.time()).replace(".", "")
    safe_kind = html.escape(kind)

    components.html(
        f"""
        <div id="sfx_{nonce}"></div>
        <script>
        (function() {{
          const kind = "{safe_kind}";
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          if (!AudioContext) return;

          const ctx = new AudioContext();

          function beep(freq, durMs, type="sine", gain=0.12) {{
            const osc = ctx.createOscillator();
            const g = ctx.createGain();
            osc.type = type;
            osc.frequency.value = freq;
            g.gain.value = gain;
            osc.connect(g);
            g.connect(ctx.destination);
            osc.start();
            setTimeout(() => {{ osc.stop(); }}, durMs);
          }}

          // Patterns
          if (kind === "turn") {{
            beep(880, 90, "sine", 0.10);
          }} else if (kind === "success") {{
            beep(660, 120, "sine", 0.12);
            setTimeout(() => beep(990, 140, "sine", 0.12), 140);
          }} else if (kind === "fail") {{
            beep(180, 220, "sawtooth", 0.10);
          }}
        }})();
        </script>
        """,
        height=0,
    )


# ============================
# Data model
# ============================
@dataclass
class Player:
    name: str
    secret: int


# ============================
# Session state
# ============================
def init_state():
    defaults = {
        # Phases:
        # setup_names -> secret_entry -> locked -> playing -> finished
        "phase": "setup_names",
        "num_players": 2,

        "player_names": [],          # list[str]
        "secrets": {},               # Dict[str, int] name -> secret
        "players": [],               # List[Player]

        "secret_entry_idx": 0,       # which player is entering secret now
        "show_pass_screen": True,    # show pass-device screen between secret entries

        "turn_idx": 0,
        "target_idx": 1,
        "winner": None,

        "last_prompt": "",
        "history": [],               # list[dict]

        # Scoreboard
        "scoreboard": {},            # name -> {"wins":int,"attempts":int}
        "round_attempts": {},        # name -> attempts in current round

        # Gameplay
        "current_guess": None,       # last captured guess int
        "last_captured_guess": None, # display convenience
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_game(keep_num_players: bool = True):
    num_players = st.session_state.get("num_players", 2) if keep_num_players else 2
    st.session_state.clear()
    init_state()
    st.session_state["num_players"] = num_players


def build_players_from_state():
    names = st.session_state["player_names"]
    secrets = st.session_state["secrets"]
    st.session_state["players"] = [Player(n, int(secrets[n])) for n in names]


def next_turn():
    n = len(st.session_state["players"])
    st.session_state["turn_idx"] = (st.session_state["turn_idx"] + 1) % n
    st.session_state["target_idx"] = (st.session_state["turn_idx"] + 1) % n


def ensure_scoreboard(names: List[str]):
    sb = st.session_state["scoreboard"]
    for n in names:
        if n not in sb:
            sb[n] = {"wins": 0, "attempts": 0}
    st.session_state["scoreboard"] = sb


def reset_round_attempts():
    st.session_state["round_attempts"] = {n: 0 for n in st.session_state["player_names"]}


# ============================
# UI
# ============================
st.set_page_config(page_title="Number Guess Game", page_icon="🎙️", layout="centered")
init_state()

st.title("🎙️ Number Guess Game")
st.caption("Be the smartest guesser! Players take turns guessing each other's secret numbers (0–100) using their voice. May the best ear win!")

with st.sidebar:
    st.header("Game Controls")

    if st.button("🔄 Reset everything"):
        reset_game(keep_num_players=False)
        st.rerun()

    if st.button("🔁 Reset round (keep scoreboard)"):
        # Keep scoreboard but restart round setup
        st.session_state["phase"] = "setup_names"
        st.session_state["player_names"] = []
        st.session_state["secrets"] = {}
        st.session_state["players"] = []
        st.session_state["secret_entry_idx"] = 0
        st.session_state["show_pass_screen"] = True
        st.session_state["history"] = []
        st.session_state["winner"] = None
        st.session_state["current_guess"] = None
        st.session_state["last_captured_guess"] = None
        st.rerun()

    st.markdown("---")
    st.write("**Last prompt:**")
    st.info(st.session_state.get("last_prompt", "") or "No prompt yet.")

    st.markdown("---")
    if st.session_state.get("scoreboard"):
        st.write("**🏆 Scoreboard**")
        sb_rows = []
        for name, stats in st.session_state["scoreboard"].items():
            sb_rows.append(
                {"Player": name, "Wins": stats["wins"], "Total Attempts": stats["attempts"]}
            )
        st.dataframe(sb_rows, use_container_width=True, hide_index=True)


# ============================
# Phase: Setup names
# ============================
if st.session_state["phase"] == "setup_names":
    st.subheader("1) Setup players")

    st.session_state["num_players"] = st.number_input(
        "Number of players",
        min_value=2,
        max_value=8,
        value=int(st.session_state["num_players"]),
        step=1,
    )

    st.write("Enter **player names** first. Secrets will be entered privately next (hidden secret entry mode).")

    temp_names = []
    for i in range(int(st.session_state["num_players"])):
        name = st.text_input(f"Player {i+1} name", key=f"name_{i}")
        temp_names.append(name.strip())

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➡️ Continue to secret entry"):
            if any(n == "" for n in temp_names):
                st.error("Please enter a name for every player.")
            else:
                st.session_state["player_names"] = temp_names
                st.session_state["secrets"] = {}
                st.session_state["secret_entry_idx"] = 0
                st.session_state["show_pass_screen"] = True
                ensure_scoreboard(temp_names)
                reset_round_attempts()
                st.session_state["phase"] = "secret_entry"
                speak("Secret entry mode. Pass the device to player one.")
                play_sound("turn")
                st.rerun()
    with c2:
        st.button("🧹 Clear", on_click=reset_game)


# ============================
# Phase: Secret entry (Hidden mode)
# ============================
elif st.session_state["phase"] == "secret_entry":
    names = st.session_state["player_names"]
    idx = st.session_state["secret_entry_idx"]

    if idx >= len(names):
        # all done
        build_players_from_state()
        st.session_state["phase"] = "locked"
        speak("All secrets locked. Ready to start.")
        st.rerun()

    current_name = names[idx]

    st.subheader("2) Hidden secret entry mode 🔐")

    # Pass-device screen (prevents shoulder-surfing)
    if st.session_state["show_pass_screen"]:
        st.warning(f"Pass the device to **{current_name}**. Others should look away.")
        if st.button("✅ I'm ready (start secret entry)"):
            st.session_state["show_pass_screen"] = False
            play_sound("turn")
            st.rerun()
    else:
        st.info(f"**{current_name}**, enter your secret number privately.")

        # Masked input (password) for secret
        secret_text = st.text_input(
            "Secret number (0–100)",
            type="password",
            key=f"secret_text_{idx}",
            placeholder="e.g., 42",
        )

        st.caption("Tip: Use digits (0–100). This field is masked.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔒 Save secret & pass device"):
                try:
                    secret_val = int(secret_text.strip())
                except Exception:
                    st.error("Please enter a valid integer between 0 and 100.")
                    st.stop()

                if not (0 <= secret_val <= 100):
                    st.error("Secret must be between 0 and 100.")
                    st.stop()

                st.session_state["secrets"][current_name] = secret_val
                st.session_state["secret_entry_idx"] = idx + 1
                st.session_state["show_pass_screen"] = True

                next_name = names[idx + 1] if (idx + 1) < len(names) else None
                if next_name:
                    speak(f"Secret saved. Pass the device to {next_name}.")
                else:
                    speak("Secret saved. All secrets entered.")

                play_sound("turn")
                st.rerun()

        with c2:
            if st.button("↩️ Back to names"):
                st.session_state["phase"] = "setup_names"
                st.rerun()

        # Progress
        st.markdown("---")
        st.write("**Progress**")
        st.progress(min(1.0, (idx / max(1, len(names)))))

        # Don’t display actual secrets
        st.write("Secrets entered so far:")
        entered = list(st.session_state["secrets"].keys())
        st.write(", ".join(entered) if entered else "None yet")


# ============================
# Phase: Locked -> Start
# ============================
elif st.session_state["phase"] == "locked":
    st.subheader("3) Start game")
    st.write("Players:")
    for p in st.session_state["players"]:
        st.write(f"• **{p.name}**")

    if st.button("▶️ Start"):
        st.session_state["phase"] = "playing"
        st.session_state["turn_idx"] = 0
        st.session_state["target_idx"] = 1 % len(st.session_state["players"])
        st.session_state["winner"] = None
        st.session_state["history"] = []
        st.session_state["current_guess"] = None
        st.session_state["last_captured_guess"] = None
        reset_round_attempts()

        guesser = st.session_state["players"][st.session_state["turn_idx"]].name
        target = st.session_state["players"][st.session_state["target_idx"]].name
        speak(f"{guesser}, it's your turn. Guess {target}'s number.")
        play_sound("turn")
        st.rerun()


# ============================
# Phase: Playing
# ============================
elif st.session_state["phase"] == "playing":
    players: List[Player] = st.session_state["players"]
    guesser = players[st.session_state["turn_idx"]]
    target = players[st.session_state["target_idx"]]

    st.subheader("4) Play")
    st.write(f"🎯 **Current turn:** {guesser.name} guesses **{target.name}**'s number")

    # Voice component (force remount each turn so button stays responsive)
    round_key = f"voice_guess_{st.session_state['turn_idx']}_{len(st.session_state['history'])}"
    captured = voice_guess(label="🎤 Speak your guess", lang="en-US", key=round_key)

    if captured is not None:
        st.session_state["current_guess"] = captured
        st.session_state["last_captured_guess"] = captured
        st.success(f"Captured guess: {captured}")

    if st.session_state.get("last_captured_guess") is not None:
        st.caption(f"Last captured: **{st.session_state['last_captured_guess']}**")

    def submit_guess():
        players_local: List[Player] = st.session_state["players"]
        guesser_i = st.session_state["turn_idx"]
        target_i = st.session_state["target_idx"]

        guesser_local = players_local[guesser_i]
        target_local = players_local[target_i]

        g = st.session_state.get("current_guess")
        if g is None:
            speak("No voice guess captured yet. Click the microphone and speak a number.")
            play_sound("fail")
            return

        g = int(g)
        secret = int(target_local.secret)

        # Scoreboard: attempts
        st.session_state["scoreboard"][guesser_local.name]["attempts"] += 1
        st.session_state["round_attempts"][guesser_local.name] += 1

        if g == secret:
            st.session_state["winner"] = guesser_local.name
            st.session_state["phase"] = "finished"
            st.session_state["history"].append(
                {
                    "guesser": guesser_local.name,
                    "target": target_local.name,
                    "guess": g,
                    "result": "CORRECT",
                }
            )
            st.session_state["scoreboard"][guesser_local.name]["wins"] += 1

            speak(
                f"Correct! {guesser_local.name} wins! "
                f"{target_local.name}'s number was {secret}."
            )
            play_sound("success")
            return
        else:
            hint = "lower" if g > secret else "higher"
            st.session_state["history"].append(
                {
                    "guesser": guesser_local.name,
                    "target": target_local.name,
                    "guess": g,
                    "result": hint.upper(),
                }
            )

            speak(f"{guesser_local.name}, your guess is {hint} than {target_local.name}'s number.")
            play_sound("fail")

            # Advance turn
            next_turn()
            next_guesser = players_local[st.session_state["turn_idx"]].name
            next_target = players_local[st.session_state["target_idx"]].name
            speak(f"{next_guesser}, it's your turn. Guess {next_target}'s number.")
            play_sound("turn")

            # Clear guess for next player
            st.session_state["current_guess"] = None
            st.session_state["last_captured_guess"] = None

    st.button("📣 Submit guess", on_click=submit_guess)

    # History
    if st.session_state["history"]:
        st.markdown("---")
        st.write("### 📜 Guess history")
        st.dataframe(st.session_state["history"], use_container_width=True, hide_index=True)

    # Round scoreboard view
    st.markdown("---")
    st.write("### 📊 Round attempts")
    ra = [{"Player": n, "Attempts": a} for n, a in st.session_state["round_attempts"].items()]
    st.dataframe(ra, use_container_width=True, hide_index=True)


# ============================
# Phase: Finished
# ============================
elif st.session_state["phase"] == "finished":
    st.subheader("🏁 Game over")
    st.success(f"🏆 Winner: **{st.session_state['winner']}**")

    # Final guess history
    if st.session_state["history"]:
        st.write("### 📜 Final guess history")
        st.dataframe(st.session_state["history"], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.write("### 📊 Scoreboard")
    sb_rows = []
    for name, stats in st.session_state["scoreboard"].items():
        sb_rows.append({"Player": name, "Wins": stats["wins"], "Total Attempts": stats["attempts"]})
    st.dataframe(sb_rows, use_container_width=True, hide_index=True)

    st.write("### 🧮 Attempts this round")
    ra = [{"Player": n, "Attempts": a} for n, a in st.session_state["round_attempts"].items()]
    st.dataframe(ra, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔁 Play again (same players & secrets)"):
            st.session_state["phase"] = "playing"
            st.session_state["turn_idx"] = 0
            st.session_state["target_idx"] = 1 % len(st.session_state["players"])
            st.session_state["winner"] = None
            st.session_state["history"] = []
            st.session_state["current_guess"] = None
            st.session_state["last_captured_guess"] = None
            reset_round_attempts()

            p0 = st.session_state["players"][0].name
            p1 = st.session_state["players"][1].name
            speak(f"{p0}, it's your turn. Guess {p1}'s number.")
            play_sound("turn")
            st.rerun()

    with c2:
        if st.button("🔐 New secrets (same names)"):
            st.session_state["phase"] = "secret_entry"
            st.session_state["secrets"] = {}
            st.session_state["players"] = []
            st.session_state["secret_entry_idx"] = 0
            st.session_state["show_pass_screen"] = True
            st.session_state["history"] = []
            st.session_state["winner"] = None
            st.session_state["current_guess"] = None
            st.session_state["last_captured_guess"] = None
            reset_round_attempts()

            speak("New secret entry mode. Pass the device to player one.")
            play_sound("turn")
            st.rerun()

    with c3:
        if st.button("🧑‍🤝‍🧑 New players"):
            reset_game(keep_num_players=False)
            st.rerun()
