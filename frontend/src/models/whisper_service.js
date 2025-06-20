const fs = require("fs");
const fetch = require("node-fetch");

async function sendToWhisper(filePath) {
  const response = await fetch("http://localhost:8000/transcribe", {
    method: "POST",
    headers: { "Content-Type": "audio/webm" },
    body: fs.createReadStream(filePath),
  });

  if (!response.ok) throw new Error("Fehler bei Whisper-API");

  const data = await response.json();
  return data.transcription;
}

async function processWithLLM(transcription) {
  const response = await fetch("http://localhost:8000/process_input_debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: transcription }),
  });

  if (!response.ok) throw new Error("Fehler bei LLM-Verarbeitung");

  return await response.json();
}

module.exports = {
  sendToWhisper,
  processWithLLM,
};