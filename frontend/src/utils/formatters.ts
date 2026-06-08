/**
 * Formats a size in bytes to a human-readable string (e.g. 4.6 GB)
 */
export function formatBytes(bytes: number, decimals: number = 1): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Formats nanoseconds returned by Ollama to a readable duration string (e.g. 4.5s)
 */
export function formatDuration(nanoseconds: number): string {
  const seconds = nanoseconds / 1_000_000_000;
  return `${seconds.toFixed(2)}s`;
}

/**
 * Formats ISO date string to readable calendar date (e.g. May 18, 2026)
 */
export function formatDate(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}
