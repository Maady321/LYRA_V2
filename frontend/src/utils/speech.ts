/**
 * System Speech Synthesis Voice Utilities
 */

const femaleVoiceNames = [
  "heera",
  "zira",
  "hazel",
  "samantha",
  "victoria",
  "karen",
  "moira",
  "tessa",
  "susan",
  "google us english",
  "female"
];

/**
 * Asynchronously retrieves a high-quality female voice from the system's available speech synthesis voices.
 * Handles the asynchronous/lazy loading behavior of the window.speechSynthesis API.
 */
export function getFemaleVoice(): Promise<SpeechSynthesisVoice | null> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      resolve(null);
      return;
    }

    const findVoice = (): SpeechSynthesisVoice | null => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) {
        return null;
      }

      // Prioritize specific warm female voices
      for (const name of femaleVoiceNames) {
        const found = voices.find(v => v.name.toLowerCase().includes(name));
        if (found) {
          return found;
        }
      }

      // Fallback to any voice with 'female' in the name
      const fallbackFemale = voices.find(v => v.name.toLowerCase().includes("female"));
      if (fallbackFemale) {
        return fallbackFemale;
      }

      return null;
    };

    // 1. Try to resolve immediately if voices are already loaded
    const immediateVoice = findVoice();
    if (immediateVoice) {
      resolve(immediateVoice);
      return;
    }

    // 2. Set up event listener for asynchronous voice loading
    const oldOnVoicesChanged = window.speechSynthesis.onvoiceschanged;
    
    const handleVoicesChanged = (e: Event) => {
      // Call existing handler if one was registered previously
      if (oldOnVoicesChanged) {
        try {
          (oldOnVoicesChanged as any)(e);
        } catch (err) {
          console.error("Error in previous onvoiceschanged handler:", err);
        }
      }

      const voice = findVoice();
      if (voice) {
        // Unregister this listener to prevent leaks
        window.speechSynthesis.onvoiceschanged = oldOnVoicesChanged;
        resolve(voice);
      }
    };

    window.speechSynthesis.onvoiceschanged = handleVoicesChanged;

    // 3. Fail-safe timeout (e.g. 1.2s) in case event doesn't trigger or no female voice is found
    setTimeout(() => {
      const finalVoice = findVoice();
      // If we found a voice, restore the handler and resolve
      if (window.speechSynthesis.onvoiceschanged === handleVoicesChanged) {
        window.speechSynthesis.onvoiceschanged = oldOnVoicesChanged;
      }
      resolve(finalVoice);
    }, 1200);
  });
}

/**
 * Returns a specific voice tailored to the agent's persona.
 */
export async function getVoiceForAgent(agentName: string): Promise<SpeechSynthesisVoice | null> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      resolve(null);
      return;
    }
    
    const assignVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) return null;
      
      const lowerAgent = agentName.toLowerCase();
      
      if (lowerAgent.includes("lyra")) {
        // Lyra gets the main warm female voice
        return voices.find(v => femaleVoiceNames.some(n => v.name.toLowerCase().includes(n))) || voices[0];
      } 
      else if (lowerAgent.includes("coder") || lowerAgent.includes("stark")) {
        // Coder / Execution agent gets a male voice (e.g. David, Mark, Male)
        const maleNames = ["david", "mark", "paul", "male"];
        return voices.find(v => maleNames.some(n => v.name.toLowerCase().includes(n))) || voices[1] || voices[0];
      }
      else if (lowerAgent.includes("db admin") || lowerAgent.includes("researcher") || lowerAgent.includes("banner")) {
        // Secondary female or another neutral voice
        const altNames = ["hazel", "susan", "google uk english female"];
        return voices.find(v => altNames.some(n => v.name.toLowerCase().includes(n))) || voices[2] || voices[0];
      }
      else {
        // Fallback for anyone else
        return voices[0];
      }
    };
    
    const immediate = assignVoice();
    if (immediate) {
      resolve(immediate);
      return;
    }
    
    setTimeout(() => {
      resolve(assignVoice());
    }, 500);
  });
}
