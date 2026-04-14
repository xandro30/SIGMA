import { useState, useEffect, useRef } from 'react';

/**
 * Countdown timer hook.
 * @param {number|null} initialSeconds - Starting seconds. Pass null to disable the timer.
 * @param {() => void} onExpire - Called once when the countdown reaches 0.
 * @returns {{ secondsLeft: number }}
 */
export function useTrackingTimer(initialSeconds, onExpire) {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds ?? 0);
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  // Reset countdown whenever initialSeconds changes (new session / new round)
  useEffect(() => {
    if (initialSeconds == null) {
      setSecondsLeft(0);
      return;
    }
    setSecondsLeft(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (initialSeconds == null || initialSeconds <= 0) return;

    const id = setInterval(() => {
      setSecondsLeft(s => {
        if (s <= 1) {
          clearInterval(id);
          onExpireRef.current();
          return 0;
        }
        return s - 1;
      });
    }, 1000);

    return () => clearInterval(id);
  // Re-run only when initialSeconds changes so we get a fresh interval per round
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialSeconds]);

  return { secondsLeft };
}
