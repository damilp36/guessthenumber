# 🎙️ Voice Guess Game (Streamlit)

An interactive multi‑player number guessing game built with Streamlit.

Players choose secret numbers and take turns guessing each other’s numbers while receiving real‑time voice prompts directly in the browser.

---

## 🚀 Features

* 🎮 Supports 2 to 8 players
* 🔢 Custom secret number selection (0–100)
* 🔄 Turn‑based gameplay
* 🔊 Browser‑based voice prompts (Web Speech API)
* 📜 Guess history tracking
* 🏆 Automatic winner detection
* 🔁 Replay with same players or new setup

---

## 🧠 How It Works

1. Select number of players (2–8)
2. Each player enters:

   * Name
   * Secret number (0–100)
3. Click **Lock in secrets**
4. Click **Start**
5. Players take turns guessing
6. Voice prompt announces:

   * Whose turn it is
   * Whether guess is higher or lower
   * When someone wins

Game continues until a player guesses correctly.

---

## 🛠️ Installation (Local Run)

### 1️⃣ Clone the repository

```
git clone <your-repo-url>
cd <repo-folder>
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run the app

```
streamlit run guessthenumber.py
```

---

## 📦 requirements.txt

```
streamlit>=1.30.0
```

No external voice libraries required.
Voice is handled by the browser using the Web Speech API.

---

## 🌐 Deployment (Streamlit Community Cloud)

1. Push these files to GitHub:

   * `guessthenumber.py`
   * `requirements.txt`
2. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
3. Select your repository
4. Choose the main file (`guessthenumber.py`)
5. Deploy

---

## 🔊 Voice Notes

The app uses browser‑based speech synthesis.

For best experience:

* Use Google Chrome
* Ensure tab is not muted
* Interact with page (click) before expecting audio

---

## 🎯 Future Enhancements (Ideas)

* 🔐 Hidden secret entry mode
* 🎵 Sound effects for correct / wrong guesses
* 📊 Scoreboard system
* 🎨 Enhanced game‑style UI
* 📱 Mobile‑optimized layout

---

## 🏁 License

Open for learning and experimentation.

Feel free to fork, modify, and enhance.

---

Built with ❤️ using Streamlit.
