import { useState } from 'react';
import { color, font, radius, space, motion } from '../../../shared/tokens';
import { Plus } from '../../../shared/components/Icons';

export default function DayTemplateEditor({ template, areas, onSave, onCancel }) {
  const [name, setName] = useState(template?.name ?? '');
  const [blocks, setBlocks] = useState(() => {
    if (!template?.blocks?.length) return [];
    return template.blocks.map(b => ({
      id: b.id ?? crypto.randomUUID(),
      startTime: `${String(b.start_at?.hour ?? 9).padStart(2, '0')}:${String(b.start_at?.minute ?? 0).padStart(2, '0')}`,
      duration: b.duration ?? 60,
      areaId: b.area_id ?? '',
      notes: b.notes ?? '',
    }));
  });

  const addBlock = () => {
    setBlocks(prev => [...prev, {
      id: crypto.randomUUID(),
      startTime: '09:00',
      duration: 60,
      areaId: '',
      notes: '',
    }]);
  };

  const updateBlock = (id, field, value) => {
    setBlocks(prev => prev.map(b => b.id === id ? { ...b, [field]: value } : b));
  };

  const removeBlock = (id) => {
    setBlocks(prev => prev.filter(b => b.id !== id));
  };

  const parseTime = (timeStr) => {
    const [h, m] = (timeStr ?? '09:00').split(':').map(Number);
    return { hour: h, minute: m };
  };

  const handleSubmit = () => {
    if (!name.trim()) return;
    const payload = {
      name: name.trim(),
      blocks: blocks.map(b => ({
        start_at: parseTime(b.startTime),
        duration: Number(b.duration),
        area_id: b.areaId || null,
        notes: b.notes,
      })),
    };
    onSave(payload);
  };

  return (
    <div style={{ padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.lg }}>
      {/* Back + Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
        <button
          onClick={onCancel}
          style={{
            background: 'none', border: 'none', color: color.muted,
            cursor: 'pointer', fontFamily: font.sans, fontSize: '13px',
          }}
        >
          ← Volver
        </button>
        <span style={{
          fontFamily: font.sans, fontSize: '14px', fontWeight: 700, color: color.text,
        }}>
          {template ? 'Editar plantilla' : 'Nueva plantilla'}
        </span>
      </div>

      {/* Name */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
        <span style={{ fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Nombre
        </span>
        <input
          type="text" value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Ej: Dia laboral, Dia ligero..."
          autoFocus
        />
      </label>

      {/* Blocks */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
        <span style={{ fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Bloques ({blocks.length})
        </span>

        {blocks.map(b => (
          <div key={b.id} style={{
            background: color.s2, border: `1px solid ${color.border}`,
            borderRadius: radius.sm, padding: space.sm,
            display: 'flex', flexDirection: 'column', gap: space.xs,
          }}>
            <div style={{ display: 'flex', gap: space.sm, alignItems: 'center' }}>
              {/* Start time — free input HH:MM */}
              <input
                type="time"
                value={b.startTime}
                onChange={e => updateBlock(b.id, 'startTime', e.target.value)}
                style={{ width: '100px', fontSize: '12px' }}
              />

              {/* Duration */}
              <input
                type="number" min={5} step={5}
                value={b.duration}
                onChange={e => updateBlock(b.id, 'duration', e.target.value)}
                style={{ width: '60px', fontSize: '12px', textAlign: 'center' }}
              />
              <span style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>min</span>

              {/* Remove */}
              <button
                onClick={() => removeBlock(b.id)}
                style={{
                  marginLeft: 'auto', background: 'none', border: 'none',
                  color: '#EF4444', cursor: 'pointer', fontSize: '14px', padding: '0 4px',
                }}
              >
                ×
              </button>
            </div>

            {/* Area */}
            <select
              value={b.areaId}
              onChange={e => updateBlock(b.id, 'areaId', e.target.value)}
              style={{ fontSize: '12px' }}
            >
              <option value="">Sin área</option>
              {(areas ?? []).map(a => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </div>
        ))}

        <button
          onClick={addBlock}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: space.xs, padding: space.sm,
            background: 'transparent', border: `1px dashed ${color.border2}`,
            borderRadius: radius.sm, color: color.muted,
            fontFamily: font.sans, fontSize: '12px', cursor: 'pointer',
          }}
        >
          <Plus size="12" /> Bloque
        </button>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: space.sm, justifyContent: 'flex-end', paddingTop: space.sm }}>
        <button onClick={onCancel} style={{
          padding: `${space.sm} ${space.lg}`, background: color.s3, color: color.text,
          border: 'none', borderRadius: radius.md, fontFamily: font.sans,
          fontSize: '13px', fontWeight: 600, cursor: 'pointer',
        }}>
          Cancelar
        </button>
        <button
          onClick={handleSubmit}
          disabled={!name.trim()}
          style={{
            padding: `${space.sm} ${space.lg}`,
            background: name.trim() ? color.yellow : color.s3,
            color: name.trim() ? '#000' : color.muted,
            border: 'none', borderRadius: radius.md, fontFamily: font.sans,
            fontSize: '13px', fontWeight: 600,
            cursor: name.trim() ? 'pointer' : 'not-allowed',
            opacity: name.trim() ? 1 : 0.38,
          }}
        >
          {template ? 'Guardar' : 'Crear'}
        </button>
      </div>
    </div>
  );
}
