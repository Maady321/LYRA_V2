import threading
import queue
import time
import urllib.request
import urllib.error
import json
import sqlite3
import io
import wave
import sys
from pathlib import Path
import numpy as np
from config.settings import settings
from MJ_AI_Assistant.security.guardian import guardian_kernel

try:
    from kokoro_onnx import Kokoro
    import sounddevice as sd
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False

try:
    from TTS.api import TTS as CoquiTTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

class VoiceSynthesizer:
    def __init__(self):
        # The TTS voice synthesizer is enabled if settings demand it and we are not in a unit test
        self.enabled = settings.TTS_ENABLED and KOKORO_AVAILABLE and ("unittest" not in sys.modules)
        self.q = queue.Queue()
        self.is_speaking = False
        self.stop_requested = False
        self._thread = None
        
        # Kokoro state
        self._kokoro = None
        
        # Native PyTorch Coqui TTS state
        self._coqui_tts = None

        if self.enabled:
            # Detect active engine and verify availability or fallbacks
            print(f"[VoiceSynthesizer] Initializing voice engine with preferred style: {settings.TTS_ENGINE.upper()}")
            
            # Start background consumer thread to process requests asynchronously
            self._thread = threading.Thread(target=self._run_tts_loop, daemon=True)
            self._thread.start()

    def _ensure_kokoro_files(self):
        """
        Secures local presence of the 82M parameter Kokoro model and voices library.
        """
        voice_dir = Path(__file__).parent
        model_path = voice_dir / "kokoro-v0_19.onnx"
        voices_path = voice_dir / "voices.bin"
        
        # Direct Hugging Face mirror endpoints
        model_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx"
        voices_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"
        
        # Github fallback release links
        fallback_model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/v0.1.0/kokoro-v0_19.onnx"
        fallback_voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/v0.1.0/voices.bin"
        
        def download_file(url: str, fallback_url: str, target: Path, desc: str):
            if target.exists():
                return
            print(f"[Kokoro TTS] Caching local {desc} asset...")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=25) as response, open(target, 'wb') as f:
                    f.write(response.read())
                print(f"[Kokoro TTS] Caching complete: {desc}")
            except Exception as e:
                print(f"[Kokoro TTS] Primary link failed: {e}. Retrying with fallback...")
                try:
                    req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=25) as response, open(target, 'wb') as f:
                        f.write(response.read())
                    print(f"[Kokoro TTS] Caching complete from fallback: {desc}")
                except Exception as ef:
                    raise RuntimeError(f"Failed to resolve {desc} model dependencies offline: {ef}")
                    
        download_file(model_url, fallback_model_url, model_path, "ONNX Model Binary")
        download_file(voices_url, fallback_voices_url, voices_path, "Voices Library Package")

    def _test_xtts_api(self) -> bool:
        """
        Quick check if the local Coqui XTTS API server is running on the configured port.
        """
        try:
            # Call simple GET or check server status
            url = f"{settings.XTTS_API_URL}/speakers"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def _load_wav_bytes(self, wav_bytes: bytes):
        """
        Decodes in-memory raw WAV bytes directly into NumPy floating arrays and sample rates
        without requiring any external C libraries (like soundfile/libsndfile).
        """
        with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            data = wf.readframes(n_frames)
            
            # Convert bytes depending on WAV bit resolution
            if sampwidth == 2: # 16-bit PCM
                samples = np.frombuffer(data, dtype=np.int16)
                # Normalize float values to [-1.0, 1.0] for sounddevice
                samples = samples.astype(np.float32) / 32768.0
            elif sampwidth == 1: # 8-bit PCM
                samples = np.frombuffer(data, dtype=np.uint8)
                samples = (samples.astype(np.float32) - 128.0) / 128.0
            elif sampwidth == 4: # 32-bit PCM
                samples = np.frombuffer(data, dtype=np.int32)
                samples = samples.astype(np.float32) / 2147483648.0
            else:
                raise ValueError(f"Unsupported WAV sample width: {sampwidth} bytes")
                
            # If stereo, format to multi-column NumPy array
            if channels > 1:
                samples = samples.reshape(-1, channels)
                
            return samples, framerate

    def _synthesize_xtts_api(self, text: str):
        """
        Synthesizes text using the local Coqui XTTS v2 API server.
        """
        payload = {
            "text": text,
            "speaker_wav": settings.XTTS_SPEAKER,
            "language": settings.XTTS_LANGUAGE
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{settings.XTTS_API_URL}/tts_to_audio",
            data=data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                return response.read()
            else:
                raise RuntimeError(f"XTTS API server returned unexpected status code: {response.status}")

    def _run_tts_loop(self):
        # 1. Primary Engine setup and fallback discovery
        current_engine = settings.TTS_ENGINE.lower()
        
        # Check if XTTS is preferred but API server is not listening
        if current_engine == "xtts":
            api_active = self._test_xtts_api()
            if api_active:
                print(f"[VoiceSynthesizer] Connected to local Coqui XTTS v2 API server on {settings.XTTS_API_URL}!")
            elif COQUI_AVAILABLE:
                print("[VoiceSynthesizer] XTTS API server offline. Loading local PyTorch Coqui TTS model...")
                try:
                    self._coqui_tts = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2")
                    import torch
                    if torch.cuda.is_available():
                        self._coqui_tts.to("cuda")
                except Exception as e:
                    print(f"[VoiceSynthesizer] Local PyTorch Coqui TTS load error: {e}. Falling back to Kokoro ONNX.")
                    current_engine = "kokoro"
            else:
                print("[VoiceSynthesizer] Coqui XTTS v2 API server offline and native TTS library not found.")
                print("[VoiceSynthesizer] Falling back to high-quality Kokoro ONNX model.")
                current_engine = "kokoro"

        # Load Kokoro ONNX if configured or if we fell back to it
        if current_engine == "kokoro":
            if KOKORO_AVAILABLE:
                try:
                    self._ensure_kokoro_files()
                    voice_dir = Path(__file__).parent
                    model_path = voice_dir / "kokoro-v0_19.onnx"
                    voices_path = voice_dir / "voices.bin"
                    self._kokoro = Kokoro(str(model_path), str(voices_path))
                    print("[VoiceSynthesizer] Neural Kokoro ONNX TTS engine active and loaded.")
                except Exception as e:
                    print(f"[VoiceSynthesizer] Failed to load Kokoro ONNX files: {e}. Voice disabled.")
                    self.enabled = False
            else:
                print("[VoiceSynthesizer] Kokoro TTS packages not available. Disabling speech.")
                self.enabled = False

        # 2. Consume from speech synthesis queue
        while self.enabled:
            try:
                text = self.q.get(timeout=0.1)
                self.is_speaking = True
                self.stop_requested = False
                
                clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()
                if not clean_text:
                    self.is_speaking = False
                    continue

                samples = None
                sample_rate = 24000
                
                # Synthesis sequence
                if current_engine == "xtts":
                    try:
                        # Attempt API call
                        if self._test_xtts_api():
                            wav_bytes = self._synthesize_xtts_api(clean_text)
                            samples, sample_rate = self._load_wav_bytes(wav_bytes)
                        # Attempt native model inference if loaded
                        elif self._coqui_tts is not None:
                            temp_dir = Path(__file__).parent / "temp"
                            temp_dir.mkdir(exist_ok=True)
                            temp_path = temp_dir / "synthesis_temp.wav"
                            
                            # Write speaker reference wav check (defaulting or looking locally)
                            speaker_ref = settings.XTTS_SPEAKER
                            # If speaker is in voice directory, use it
                            local_wav = Path(__file__).parent / speaker_ref
                            if local_wav.exists():
                                ref_path = str(local_wav)
                            else:
                                # Fallback or look inside local speakers folder if exists
                                ref_path = speaker_ref
                                
                            self._coqui_tts.tts_to_file(
                                text=clean_text,
                                file_path=str(temp_path),
                                speaker_wav=ref_path,
                                language=settings.XTTS_LANGUAGE
                            )
                            
                            with open(temp_path, 'rb') as f:
                                wav_bytes = f.read()
                            samples, sample_rate = self._load_wav_bytes(wav_bytes)
                        else:
                            raise RuntimeError("Both XTTS API server and local model are unreachable.")
                            
                    except Exception as e:
                        print(f"[VoiceSynthesizer] Coqui XTTS v2 failed: {e}. Attempting Kokoro ONNX fallback...")
                        # Run one-off Kokoro fallback if Kokoro library is loaded
                        if KOKORO_AVAILABLE:
                            try:
                                if self._kokoro is None:
                                    self._ensure_kokoro_files()
                                    voice_dir = Path(__file__).parent
                                    self._kokoro = Kokoro(str(voice_dir / "kokoro-v0_19.onnx"), str(voice_dir / "voices.bin"))
                                samples, sample_rate = self._kokoro.create(
                                    clean_text, 
                                    voice="af_heart", 
                                    speed=1.05, 
                                    lang="en-us"
                                )
                            except Exception as ef:
                                print(f"[VoiceSynthesizer] Kokoro ONNX fallback failed: {ef}")
                        
                elif current_engine == "kokoro" and self._kokoro is not None:
                    try:
                        samples, sample_rate = self._kokoro.create(
                            clean_text, 
                            voice="af_heart", 
                            speed=1.05, 
                            lang="en-us"
                        )
                    except Exception as e:
                        print(f"[VoiceSynthesizer] Kokoro creation failed: {e}")

                # Playback audio if successfully synthesized
                if samples is not None and not self.stop_requested:
                    try:
                        sd.play(samples, sample_rate)
                        while sd.get_stream().active and not self.stop_requested:
                            time.sleep(0.04)
                        if self.stop_requested:
                            sd.stop()
                    except Exception as e:
                        print(f"[VoiceSynthesizer] Sounddevice audio playback exception: {e}")
                        
                self.is_speaking = False
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoiceSynthesizer] Global loop error: {e}")
                self.is_speaking = False
                time.sleep(0.5)

    def speak(self, text: str) -> None:
        """
        Synthesizes speech output aloud using the selected voice model.
        """
        if not self.enabled:
            print(f"[MJ Speech Fallback]: {text}")
            return

        self.q.put(text)

    def interrupt(self) -> None:
        """
        Aborts neural playback instantly on sounddevice stream levels.
        """
        if not self.enabled:
            return
        
        self.stop_requested = True
        try:
            sd.stop()
        except Exception:
            pass
        self.is_speaking = False

    def wait_until_finished(self) -> None:
        """
        Blocks caller thread until speaking queue purges.
        """
        while self.is_speaking or not self.q.empty():
            time.sleep(0.05)
