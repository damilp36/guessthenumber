import { Streamlit } from "streamlit-component-lib";

const btn = document.getElementById("btn");
const statusEl = document.getElementById("status");
const supportEl = document.getElementById("support");

function setStatus(msg) {
  statusEl.textContent = msg;
}

function supportsSpeechRecognition() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

// Convert basic number words up to 100 ("fifty two", "twenty one", etc.)
function wordsToNumber(s) {
  s = (s || "").toLowerCase().replace(/-/g, " ").trim();

  const ones = {
    zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9,
    ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16,
    seventeen: 17, eighteen: 18, nineteen: 19
  };

  const tens = {
    twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90
  };

  // Prefer digits if present
  const m = s.match(/\d+/);
  if (m) return parseInt(m[0], 10);

  const parts = s.split(/\s+/).filter(Boolean);

  let current = 0;

  for (const w of parts) {
    if (w === "and") continue;

    if (w in ones) {
      current += ones[w];
      continue;
    }
    if (w in tens) {
      current += tens[w];
      continue;
    }
    if (w === "hundred") {
      if (current === 0) current = 1;
      current *= 100;
      continue;
    }
  }

  if (!Number.isFinite(current)) return null;
  if (current === 0 && !parts.includes("zero")) return null;
  return current;
}

function startListening(lang) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SR();

  recognition.lang = lang || "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  setStatus("🎧 Listening... (allow microphone permission)");

  recognition.onresult = (event) => {
    const transcript = (event.results?.[0]?.[0]?.transcript || "").trim();
    setStatus(`You said: "${transcript}"`);

    const n = wordsToNumber(transcript);

    if (n === null || Number.isNaN(n)) {
      setStatus(`Could not detect a number from: "${transcript}"`);
      Streamlit.setComponentValue(null);
      return;
    }

    const clamped = Math.max(0, Math.min(100, n));
    setStatus(`✅ Captured: ${clamped}`);
    Streamlit.setComponentValue(clamped);
  };

  recognition.onerror = (event) => {
    setStatus(`Error: ${event.error || "unknown error"}`);
    Streamlit.setComponentValue(null);
  };

  recognition.start();
}

function onRender(event) {
  const args = event.detail.args || {};
  const label = args.label || "🎤 Speak your guess";
  const lang = args.lang || "en-US";

  btn.textContent = label;

  const ok = supportsSpeechRecognition();
  supportEl.textContent = ok ? "OK" : "No Speech API";
  btn.disabled = !ok;

  if (!ok) setStatus("Speech recognition not supported. Use Chrome/Edge.");

  btn.onclick = () => startListening(lang);

  Streamlit.setFrameHeight(110);
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(110);
