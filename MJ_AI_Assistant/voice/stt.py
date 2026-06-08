import speech_recognition as sr
from config.settings import settings

class VoiceTranscriber:
    def __init__(self):
        self.enabled = settings.STT_ENABLED
        self.recognizer = None
        if self.enabled:
            try:
                self.recognizer = sr.Recognizer()
            except Exception as e:
                print(f"[VoiceTranscriber] Failed to start microphone listeners: {e}")
                self.enabled = False

    def listen_and_transcribe(self, timeout: int = 5) -> str:
        """
        Listens to microphone input frames and translates speech audio to plain text.
        """
        if not self.enabled or not self.recognizer:
            return ""

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print("[STT] Listening for command...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            print("[STT] Transcribing voice input...")
            # Use Google Web Speech API (free and available by default in speech_recognition)
            transcript = self.recognizer.recognize_google(audio)
            print(f"[STT] Heard: '{transcript}'")
            return transcript
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("[STT] Could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"[STT] API Link Error: {e}")
            return ""
        except Exception as e:
            print(f"[STT] Recording Error: {e}")
            return ""
