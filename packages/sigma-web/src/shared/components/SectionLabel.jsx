import { color, font } from '../tokens';
export default function SectionLabel({ children, style = {} }) {
  return (
    <p style={{
      margin: '0 0 10px',
      fontSize: '10px',
      color: color.muted2,
      fontFamily: font.mono,
      letterSpacing: '0.12em',
      fontWeight: 700,
      textTransform: 'uppercase',
      ...style,
    }}>
      {children}
    </p>
  );
}
