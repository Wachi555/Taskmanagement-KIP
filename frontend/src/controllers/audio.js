const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const whisperService = require("../models/whisper_service");

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/upload-audio", upload.single("file"), async (req, res) => {
  try {
    const filePath = path.resolve(req.file.path);
    const transcription = await whisperService.sendToWhisper(filePath);
    fs.unlinkSync(filePath); // cleanup temp file

    const result = await whisperService.processWithLLM(transcription);
    if (!result.success) throw new Error(result.error || "Fehler bei der Verarbeitung");
    res.json(result.output);
  } catch (err) {
    console.error("Audio upload error:", err);
    res.status(500).json({ error: "Fehler beim Verarbeiten der Audiodatei" });
  }
});

module.exports = router;