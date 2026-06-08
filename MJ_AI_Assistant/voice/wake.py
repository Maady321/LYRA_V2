import time
import threading
import speech_recognition as sr
from voice.tts import VoiceSynthesizer
from voice.stt import VoiceTranscriber
from config.settings import settings

class WakeWordListener:
    def __init__(self, callback_func=None):
        self.callback = callback_func
        self.tts = VoiceSynthesizer()
        self.recognizer = sr.Recognizer()
        self.wake_words = ["hey mj", "hello mj", "hi mj", "hey emj", "hello emj"]

    def start_listening_loop(self) -> None:
        """
        Monitors microphone for MJ hotwords, then transitions to an active,
        continuous conversational loop with auto-silence and interruptible TTS.
        """
        print("\n[WAKE WORD] Continuous listener active. Listening for 'Hey MJ'...")
        
        in_conversation = False
        last_interaction_time = time.time()
        conversation_timeout = 15.0  # seconds of silence before auto-standby
        transcriber = VoiceTranscriber()
        
        def monitor_barge_in():
            """
            Background thread monitoring microphone for interruptions while speaking.
            """
            while True:
                if self.tts.is_speaking:
                    try:
                        # Open micro and listen for short burst of sound/words
                        with sr.Microphone() as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.15)
                            audio = self.recognizer.listen(source, timeout=0.2, phrase_time_limit=1.5)
                        
                        # Transcribe to see if user is speaking
                        phrase = self.recognizer.recognize_google(audio).lower().strip()
                        if phrase:
                            print(f"\n[BARGE-IN] User interrupted with: '{phrase}'! Halting TTS...")
                            self.tts.interrupt()
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        pass
                    except Exception as e:
                        # Silent catch for audio hardware quirks during parallel swaps
                        pass
                time.sleep(0.1)
        
        # Launch dedicated barge-in worker
        barge_thread = threading.Thread(target=monitor_barge_in, daemon=True)
        barge_thread.start()

        while True:
            try:
                if not in_conversation:
                    # PASSIVE WAKE-WORD MODE
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=4)
                        
                    phrase = self.recognizer.recognize_google(audio).lower().strip()
                    print(f"[WAKE WORD] Heard phonetic chunk: '{phrase}'")

                    is_matched = any(wake in phrase for wake in self.wake_words)
                    if is_matched:
                        print("\n[WAKE WORD] Hotword detected! Entering conversational thread...")
                        self.tts.speak("Hello! I am ready. What is your objective?")
                        self.tts.wait_until_finished()
                        in_conversation = True
                        last_interaction_time = time.time()
                else:
                    # ACTIVE CONVERSATION MODE (Continuous voice loop)
                    print(f"\n[CONVERSATION] Listening directly (Standby in {int(conversation_timeout - (time.time() - last_interaction_time))}s)...")
                    spoken_cmd = transcriber.listen_and_transcribe(timeout=6)
                    
                    if spoken_cmd:
                        last_interaction_time = time.time()
                        cleaned_cmd = spoken_cmd.lower().strip()
                        
                        # Check exit or standby triggers
                        if any(exit_phrase in cleaned_cmd for exit_phrase in ["goodbye", "thank you", "go to sleep", "standby", "quit", "exit"]):
                            self.tts.speak("Understood. Returning to standby mode. Let me know if you need anything.")
                            self.tts.wait_until_finished()
                            in_conversation = False
                            continue
                        
                        if self.callback:
                            print(f"[CONVERSATION] Processing command: '{spoken_cmd}'")
                            self.callback(spoken_cmd)
                    else:
                        # No command detected, check standby timeout
                        elapsed = time.time() - last_interaction_time
                        if elapsed >= conversation_timeout:
                            print(f"[AUTO-SILENCE] No voice detected for {conversation_timeout}s. Returning to standby.")
                            self.tts.speak("Going to standby now.")
                            self.tts.wait_until_finished()
                            in_conversation = False
                
                time.sleep(0.4)
            except sr.UnknownValueError:
                if in_conversation:
                    elapsed = time.time() - last_interaction_time
                    if elapsed >= conversation_timeout:
                        print(f"[AUTO-SILENCE] Standby timeout reached.")
                        self.tts.speak("Standby active.")
                        self.tts.wait_until_finished()
                        in_conversation = False
                continue
            except Exception as e:
                print(f"[WAKE WORD] Loop error: {e}")
                time.sleep(2)

def dummy_wake_callback(command: str):
    print(f"\n[WAKE CALLBACK] Triggering processing for spoken command: '{command}'")

if __name__ == "__main__":
    listener = WakeWordListener(dummy_wake_callback)
    listener.start_listening_loop()
