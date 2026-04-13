import { useState, useEffect } from 'react';
import { color, font, radius, space, motion } from '../../../shared/tokens';
import { useSetWeekTemplateSlot, useClearWeekTemplateSlot } from '../../../entities/planning/hooks/useTemplateMutations';

const DAYS = [
  { id: 'mon', label: 'Lunes' },
  { id: 'tue', label: 'Martes' },
  { id: 'wed', label: 'Miercoles' },
  { id: 'thu', label: 'Jueves' },
  { id: 'fri', label: 'Viernes' },
  { id: 'sat', label: 'Sabado' },
  { id: 'sun', label: 'Domingo' },
];

export default function WeekTemplateEditor({ template, spaceId, dayTemplates, onDone, onCreate }) {
  const [name, setName] = useState(template?.name ?? '');
  const setSlot = useSetWeekTemplateSlot(spaceId);
  const clearSlot = useClearWeekTemplateSlot(spaceId);
  const isNew = !template?.id;

  // Local slots state — synced from template prop, updated optimistically
  const [slots, setSlots] = useState(() => ({ ...template?.slots }));

  // Re-sync if template prop changes (e.g. after refetch)
  useEffect(() => {
    if (template?.slots) setSlots({ ...template.slots });
  }, [template]);

  const handleCreate = () => {
    if (!name.trim()) return;
    onCreate(name.trim());
  };

  const handleSlotChange = async (weekday, dayTemplateId) => {
    if (!template?.id) return;

    // Optimistic update
    setSlots(prev => ({
      ...prev,
      [weekday]: dayTemplateId || null,
    }));

    if (dayTemplateId) {
      await setSlot.mutateAsync({ templateId: template.id, weekday, dayTemplateId });
    } else {
      await clearSlot.mutateAsync({ templateId: template.id, weekday });
    }
  };

  return (
    <div style={{ padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.lg }}>
      {/* Back + Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
        <button
          onClick={onDone}
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
          {isNew ? 'Nueva plantilla semanal' : 'Editar plantilla'}
        </span>
      </div>

      {/* Name */}
      {isNew && (
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={{ fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Nombre
          </span>
          <input
            type="text" value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Ej: Semana productiva..."
            autoFocus
          />
        </label>
      )}

      {/* Slots — only show for existing templates */}
      {!isNew && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
          <span style={{ fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Asignar plantillas de dia
          </span>

          {DAYS.map(day => {
            const slotValue = slots[day.id] ?? '';

            return (
              <div key={day.id} style={{
                display: 'flex', alignItems: 'center', gap: space.md,
                padding: `${space.sm} 0`,
              }}>
                <span style={{
                  width: '80px', fontFamily: font.sans, fontSize: '13px',
                  fontWeight: 600, color: color.text,
                }}>
                  {day.label}
                </span>
                <select
                  value={slotValue}
                  onChange={e => handleSlotChange(day.id, e.target.value || null)}
                  style={{ flex: 1, fontSize: '12px' }}
                >
                  <option value="">— Sin plantilla</option>
                  {(dayTemplates ?? []).map(dt => (
                    <option key={dt.id} value={dt.id}>{dt.name}</option>
                  ))}
                </select>
              </div>
            );
          })}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: space.sm, justifyContent: 'flex-end', paddingTop: space.sm }}>
        <button onClick={onDone} style={{
          padding: `${space.sm} ${space.lg}`, background: color.s3, color: color.text,
          border: 'none', borderRadius: radius.md, fontFamily: font.sans,
          fontSize: '13px', fontWeight: 600, cursor: 'pointer',
        }}>
          {isNew ? 'Cancelar' : 'Hecho'}
        </button>
        {isNew && (
          <button
            onClick={handleCreate}
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
            Crear
          </button>
        )}
      </div>
    </div>
  );
}
