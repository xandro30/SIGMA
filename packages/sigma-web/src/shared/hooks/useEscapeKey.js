import { useEffect } from 'react';

/**
 * Calls `handler` when the Escape key is pressed.
 * Automatically cleans up on unmount.
 */
export function useEscapeKey(handler) {
  useEffect(() => {
    if (!handler) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') handler();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [handler]);
}
