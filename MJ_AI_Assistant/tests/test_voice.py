import unittest
import os
import sys
from pathlib import Path
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice.tts import VoiceSynthesizer
from config.settings import settings

class TestVoiceSynthesizer(unittest.TestCase):
    def setUp(self):
        # Force enable TTS for the test but keep it off main loops where sounddevice might block
        self.tts = VoiceSynthesizer()
        
    def test_wav_decoder_mono_16bit(self):
        """
        Verifies that our custom wave decoder converts 16-bit PCM bytes correctly.
        """
        import io
        import wave
        
        # 1. Create a mock WAV in memory (1 second, 16000Hz, 16-bit PCM, Mono)
        sample_rate = 16000
        num_samples = 16000
        mock_pcm_data = np.zeros(num_samples, dtype=np.int16)
        
        wav_buf = io.BytesIO()
        with wave.open(wav_buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(mock_pcm_data.tobytes())
            
        wav_bytes = wav_buf.getvalue()
        
        # 2. Parse using the new decoder
        samples, rate = self.tts._load_wav_bytes(wav_bytes)
        
        self.assertEqual(rate, sample_rate)
        self.assertEqual(len(samples), num_samples)
        self.assertEqual(samples.dtype, np.float32)
        # Check normalization (zeros should remain zero)
        self.assertTrue(np.allclose(samples, 0.0))

    def test_test_xtts_api_failure_handling(self):
        """
        Confirms that when the API server is offline, self._test_xtts_api handles it gracefully and returns False.
        """
        # Change the API url to a non-existent host/port to guarantee offline
        original_url = settings.XTTS_API_URL
        settings.XTTS_API_URL = "http://127.0.0.1:9999"
        
        api_active = self.tts._test_xtts_api()
        self.assertFalse(api_active)
        
        # Restore URL
        settings.XTTS_API_URL = original_url

if __name__ == "__main__":
    unittest.main()
