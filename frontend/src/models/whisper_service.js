const fs = require("fs");
const fetch = require("node-fetch");

async function sendToWhisper(filePath) {
  const response = await fetch("http://localhost:8000/transcribe", {
    method: "POST",
    headers: { "Content-Type": "audio/webm" },
    body: fs.createReadStream(filePath),
  });

  const data = await response.json();
  if (!data.success) throw new Error(data.error || "Fehler bei der Transkription");
  return data.output;
}

async function processWithLLM(transcription) {
  const response = await fetch("http://localhost:8000/process_input_debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: transcription }),
  });

  const data = await response.json();
  if (!data.success) throw new Error(data.error || "Fehler bei LLM-Verarbeitung");
  return data.output;
}

module.exports = {
  sendToWhisper,
  processWithLLM,
};