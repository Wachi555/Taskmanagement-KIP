let mediaRecorder;
let recordedChunks = [];

function showError(message) {
  alert("Error: " + message);
}

function displayResults(result) {
  console.log("Transcription:", result.transcription);
  // Optional: display in the HTML
  const outputElement = document.getElementById("transcription-output");
  if (outputElement) {
    outputElement.textContent = result.transcription;
  }
}

export function setupAudioRecorder() {
  const recordBtn = document.getElementById("record-btn");
  const stopBtn = document.getElementById("stop-btn");
  const sendBtn = document.getElementById("send-audio-btn");

  recordBtn.addEventListener("click", async () => {
    recordedChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => recordedChunks.push(e.data);
    mediaRecorder.start();
    recordBtn.disabled = true;
    stopBtn.disabled = false;
  });

  stopBtn.addEventListener("click", () => {
    mediaRecorder.stop();
    stopBtn.disabled = true;
    sendBtn.disabled = false;
  });

  sendBtn.addEventListener("click", async () => {
    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("file", blob, "recording.webm");

    console.log("Audio Blob size:", blob.size);  // should be > 1 KB
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();  // Listen to your own recording

    try {
      const res = await fetch("http://localhost:8000/transcribe", {
        method: "POST",
        body: formData
      });
      const result = await res.json();
      const transcription = result.transcription;
      const anamneseField = document.getElementById("inputText"); // change to actual ID
      if (anamneseField) {
        anamneseField.value = transcription;
      }
    } catch (err) {
      showError(err.message);
    }
  });
}
