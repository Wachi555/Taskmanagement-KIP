import whisper
model = whisper.load_model("small")  # Options: tiny, base, small, medium, large
result = model.transcribe("data\Me at the zoo 4.mp3")
print(result["text"])