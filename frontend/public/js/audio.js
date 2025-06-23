let mediaRecorder;
let recordedChunks = [];
let isPaused = false;

function showError(message) {
  alert("Error: " + message);
}

export function setupAudioRecorder() {
  const mainBtn = document.getElementById("audio-main-btn");
  const uploadBtn = document.getElementById("audio-upload-btn");
  const fileInput = document.getElementById("audioFile");
  const pauseBtn = document.getElementById("audio-pause-btn");
  const continueBtn = document.getElementById("audio-continue-btn");
  const stopBtn = document.getElementById("audio-stop-btn");
  const rerecordBtn = document.getElementById("audio-rerecord-btn");
  const processBtn = document.getElementById("audio-process-btn");
  const transcriptionOutput = document.getElementById("transcription-output");
  const proccessingBtn = document.getElementById("processing-text-btn");

  function setState(state) {
    [mainBtn, uploadBtn, pauseBtn, continueBtn, stopBtn, rerecordBtn, processBtn, proccessingBtn].forEach(btn => btn.classList.add("d-none"));
    if (state === "idle") {
      mainBtn.classList.remove("d-none");
      uploadBtn.classList.remove("d-none");
    } else if (state === "recording") {
      pauseBtn.classList.remove("d-none");
      stopBtn.classList.remove("d-none");
    } else if (state === "paused") {
      continueBtn.classList.remove("d-none");
      stopBtn.classList.remove("d-none");
    } else if (state === "stopped") {
      rerecordBtn.classList.remove("d-none");
      processBtn.classList.remove("d-none");
    } else if (state === "processing") {
      proccessingBtn.classList.remove("d-none");
    }
  }

  setState("idle");

 mainBtn.addEventListener("click", async () => {
  recordedChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      sampleRate: 44100,
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true
    }
  });

  // Fallback-Logik für MIME-Typen
  let mimeType = "";
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
    mimeType = "audio/webm;codecs=opus";
  } else if (MediaRecorder.isTypeSupported("audio/webm")) {
    mimeType = "audio/webm";
  } else if (MediaRecorder.isTypeSupported("audio/ogg")) {
    mimeType = "audio/ogg";
  }

  let options = {};
  if (mimeType) {
    options.mimeType = mimeType;
  }

  try {
    mediaRecorder = new MediaRecorder(stream, options);
  } catch (e) {
    showError("Audioaufnahme wird von deinem Browser nicht unterstützt.");
    return;
  }

  mediaRecorder.ondataavailable = e => recordedChunks.push(e.data);
  mediaRecorder.onstop = () => setState("stopped");
  mediaRecorder.start();
  setState("recording");
  isPaused = false;
  });

  uploadBtn.addEventListener("click", () => {
    fileInput.value = ""; // Reset file input
    fileInput.click();
  });

  pauseBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.pause();
      isPaused = true;
      setState("paused");
    }
  });

  continueBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "paused") {
      mediaRecorder.resume();
      isPaused = false;
      setState("recording");
    }
  });

  stopBtn.addEventListener("click", () => {
    if (mediaRecorder && (mediaRecorder.state === "recording" || mediaRecorder.state === "paused")) {
      mediaRecorder.stop();
    }
  });

  rerecordBtn.addEventListener("click", () => {
    setState("idle");
    transcriptionOutput.textContent = "";
  });

  processBtn.addEventListener("click", async () => {
    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    await uploadAndTranscribe(blob);
  });

  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadAndTranscribe(file);
    }
  });

  async function uploadAndTranscribe(fileBlob) {
  setState("processing");
  transcriptionOutput.textContent = "Audio wird verarbeitet...";
  const formData = new FormData();

  // Use the original filename if available (for uploads), otherwise default to webm
  let filename = "audio.webm";
  if (fileBlob instanceof File && fileBlob.name) {
    filename = fileBlob.name;
  }
  formData.append("file", fileBlob, filename);

  try {
    const res = await fetch("http://localhost:8000/transcribe", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    if (!result.success) {
      throw new Error(result.error || "Fehler bei der Transkription.");
    }
    const transcription = result.output;
    const anamneseField = document.getElementById("inputText");
    if (anamneseField) {
      anamneseField.value = transcription;
    }
    transcriptionOutput.textContent = transcription;
  } catch (err) {
    showError(err.message);
    transcriptionOutput.textContent = "Fehler bei der Transkription.";
  }
  setState("idle");
  }
}