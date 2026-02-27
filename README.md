# 🎙️ Voice Guess Game (Streamlit + Custom Voice Component)

An interactive multi-player number guessing game built with **Streamlit** and a custom **browser voice recognition component**.

Players choose secret numbers and take turns guessing each other’s numbers using real voice input — no typing required.

---

## 🚀 Features

* 🎮 Supports 2 to 8 players
* 🔢 Custom secret number selection (0–100)
* 🔄 Turn-based gameplay
* 🎤 Real voice input (SpeechRecognition API)
* 🔊 Real voice prompts (SpeechSynthesis API)
* 🧠 Converts spoken words ("fifty two") to numbers (52)
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
5. Players take turns speaking their guess
6. The browser:

   * Captures microphone input
   * Converts spoken number to integer
   * Sends it to Streamlit
7. Voice prompt announces:

   * Whether guess is higher or lower
   * When someone wins

Game continues until a player guesses correctly.

---

# 🛠️ Local Installation

## 1️⃣ Clone the repository

```
git clone <your-repo-url>
cd <repo-folder>
```

---

## 2️⃣ Install Python dependencies

```
pip install -r requirements.txt
```

---

## 3️⃣ Install Frontend Dependencies (Custom Component)

Navigate to the frontend directory:

```
cd voice_guess_component/frontend
npm install
```

Then build the component:

```
npm run build
```

This generates:

```
voice_guess_component/frontend/dist/
```

⚠️ You must build the frontend before running the app.

---

## 4️⃣ Run the App

From the root project folder:

```
streamlit run guessthenumber.py
```

---

# 📦 requirements.txt

```
streamlit>=1.30.0
```

No external Python voice libraries required. Voice processing is handled entirely in the browser.

---

# 🎤 Voice System Architecture

This app uses two browser APIs:

### 🔊 SpeechSynthesis API

Used for voice prompts (text-to-speech).

### 🎙️ SpeechRecognition API

Used for:

* Capturing microphone input
* Converting speech to text
* Extracting numeric values
* Returning the number to Python via a custom Streamlit component

The custom component frontend is bundled using Vite.

---

# 🌐 Browser Compatibility

Best experience:

* ✅ Google Chrome
* ✅ Microsoft Edge

Not fully supported:

* ⚠️ Safari (partial support)
* ❌ Firefox (no SpeechRecognition API)

Microphone permission must be allowed.

---

# ☁️ Deployment Notes

If deploying to Streamlit Community Cloud:

1. Push the entire repository including:

   * `voice_guess_component/`
   * The built `dist/` folder
2. Make sure `frontend/dist` is committed to GitHub
3. Only `streamlit` is required in `requirements.txt`

No Node.js installation is required on Streamlit Cloud if the `dist` folder is already built and committed.

---

# 📁 Project Structure

```
.
├── guessthenumber.py
├── requirements.txt
└── voice_guess_component/
    ├── __init__.py
    └── frontend/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        ├── index.js
        └── dist/
```

---

# 🎯 Future Enhancements

* 🔐 Hidden secret entry mode
* 🎵 Sound effects for correct / incorrect guesses
* 📊 Scoreboard system
* 🎨 Enhanced animated game UI
* 🤖 AI voice personality modes
* 📱 Mobile optimization

---

# 🏁 License

Open for learning, experimentation, and extension.

Feel free to fork, improve, and build upon it.

---

Built with ❤️ using Streamlit and a custom voice component.
