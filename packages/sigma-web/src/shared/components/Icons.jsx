/**
 * SVG icon components — replaces Unicode emoji usage.
 * All icons: 1em default size, currentColor fill, no stroke.
 */

const I = ({ d, size = '1em', ...props }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    {typeof d === 'string' ? <path d={d} /> : d}
  </svg>
);

export const ChevronLeft  = (p) => <I d="M15 18l-6-6 6-6" {...p} />;
export const ChevronRight = (p) => <I d="M9 6l6 6-6 6" {...p} />;
export const ChevronDown  = (p) => <I d="M6 9l6 6 6-6" {...p} />;
export const Plus         = (p) => <I d={<><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>} {...p} />;
export const X            = (p) => <I d={<><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>} {...p} />;
export const Calendar     = (p) => <I d={<><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></>} {...p} />;
export const Layout       = (p) => <I d={<><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></>} {...p} />;
export const BarChart     = (p) => <I d={<><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></>} {...p} />;
export const Clock        = (p) => <I d={<><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></>} {...p} />;
export const Trash        = (p) => <I d={<><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></>} {...p} />;
