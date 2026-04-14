import { useEffect, useRef } from 'react';

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

export function useFocusTrap(ref, onEscape) {
  const onEscapeRef = useRef(onEscape);
  onEscapeRef.current = onEscape;

  useEffect(() => {
    const prev = document.activeElement;
    ref.current?.focus();
    const handle = (e) => {
      if (e.key === 'Escape') { onEscapeRef.current(); return; }
      if (e.key === 'Tab') {
        const els = Array.from(ref.current?.querySelectorAll(FOCUSABLE) ?? []);
        if (!els.length) return;
        if (e.shiftKey) {
          if (document.activeElement === els[0]) { e.preventDefault(); els[els.length - 1].focus(); }
        } else {
          if (document.activeElement === els[els.length - 1]) { e.preventDefault(); els[0].focus(); }
        }
      }
    };
    document.addEventListener('keydown', handle);
    return () => { document.removeEventListener('keydown', handle); prev?.focus(); };
  // ref is stable (useRef), onEscapeRef is stable — effect runs once per mount
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ref]);
}
