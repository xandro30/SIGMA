import { useState } from 'react';
import { color, font, radius, space, motion } from '../../../shared/tokens';
import { Plus } from '../../../shared/components/Icons';
import { useWeekTemplates, useDayTemplates } from '../../../entities/planning/hooks/useTemplates';
import { useCreateWeekTemplate, useDeleteWeekTemplate } from '../../../entities/planning/hooks/useTemplateMutations';
import { planningApi } from '../../../api/planning';
import { useQueryClient } from '@tanstack/react-query';
import WeekTemplateEditor from './WeekTemplateEditor';

const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

export default function WeekTemplateList({ spaceId, weekStart, onApplied }) {
  const { data: templates = [] } = useWeekTemplates(spaceId);
  const { data: dayTemplates = [] } = useDayTemplates(spaceId);
  const [editing, setEditing] = useState(null); // null = list, 'new' = create, template obj = edit
  const [replaceExisting, setReplaceExisting] = useState(false);
  const createTemplate = useCreateWeekTemplate(spaceId);
  const deleteTemplate = useDeleteWeekTemplate(spaceId);
  const qc = useQueryClient();

  const handleCreate = async (name) => {
    await createTemplate.mutateAsync({ name });
    setEditing(null);
  };

  const handleDelete = async (templateId) => {
    if (!confirm('Eliminar esta plantilla semanal?')) return;
    await deleteTemplate.mutateAsync(templateId);
  };

  const handleApply = async (templateId) => {
    await planningApi.createWeek(spaceId, { week_start: weekStart }).catch(() => {});
    await planningApi.applyTemplate(spaceId, weekStart, {
      template_id: templateId, replace_existing: replaceExisting,
    });
    qc.invalidateQueries({ queryKey: ['weekDays', spaceId] });
    onApplied?.();
  };

  if (editing !== null) {
    return (
      <WeekTemplateEditor
        template={editing === 'new' ? null : editing}
        spaceId={spaceId}
        dayTemplates={dayTemplates}
        onDone={() => setEditing(null)}
        onCreate={handleCreate}
      />
    );
  }

  return (
    <div style={{ padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.md }}>
      {templates.length === 0 && (
        <p style={{
          fontFamily: font.sans, fontSize: '13px', color: color.muted2,
          textAlign: 'center', padding: space.xl,
        }}>
          No hay plantillas semanales creadas
        </p>
      )}

      {/* Replace toggle */}
      <label style={{
        display: 'flex', alignItems: 'center', gap: space.sm,
        fontFamily: font.sans, fontSize: '12px', color: color.muted,
        cursor: 'pointer', padding: `0 0 ${space.xs}`,
      }}>
        <input
          type="checkbox"
          checked={replaceExisting}
          onChange={e => setReplaceExisting(e.target.checked)}
          style={{ width: '16px', height: '16px', accentColor: color.yellow }}
        />
        Reemplazar bloques existentes
      </label>

      {templates.map(t => {
        const slotsUsed = DAYS.filter(d => t.slots?.[d]).length;
        return (
          <div key={t.id} style={{
            background: color.s2, border: `1px solid ${color.border}`,
            borderRadius: radius.md, padding: space.md,
            display: 'flex', flexDirection: 'column', gap: space.sm,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: font.sans, fontSize: '14px', fontWeight: 600, color: color.text }}>
                {t.name}
              </span>
              <div style={{ display: 'flex', gap: space.xs }}>
                <SmallBtn onClick={() => setEditing(t)}>editar</SmallBtn>
                <SmallBtn onClick={() => handleDelete(t.id)} danger>eliminar</SmallBtn>
              </div>
            </div>
            <div style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2 }}>
              {slotsUsed}/7 dias asignados
            </div>
            {/* Mini slot preview */}
            <div style={{ display: 'flex', gap: '3px' }}>
              {DAYS.map(d => {
                const hasSlot = !!t.slots?.[d];
                return (
                  <div key={d} style={{
                    flex: 1, height: '4px', borderRadius: '2px',
                    background: hasSlot ? color.yellow : color.s3,
                  }} />
                );
              })}
            </div>
            <button
              onClick={() => handleApply(t.id)}
              style={{
                alignSelf: 'flex-start',
                padding: `${space.xs} ${space.md}`,
                background: color.yellowDim, color: color.yellow,
                border: `1px solid ${color.yellow}40`, borderRadius: radius.sm,
                fontFamily: font.sans, fontSize: '11px', fontWeight: 600,
                cursor: 'pointer', transition: `all ${motion.fast}`,
              }}
            >
              Aplicar a esta semana
            </button>
          </div>
        );
      })}

      <button
        onClick={() => setEditing('new')}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: space.xs, padding: space.md,
          background: 'transparent', border: `1px dashed ${color.border2}`,
          borderRadius: radius.md, color: color.muted,
          fontFamily: font.sans, fontSize: '13px', fontWeight: 600,
          cursor: 'pointer', transition: `all ${motion.fast}`,
        }}
      >
        <Plus size="14" />
        Nueva plantilla semanal
      </button>
    </div>
  );
}

function SmallBtn({ children, onClick, danger }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: `2px ${space.sm}`, background: 'transparent',
        border: 'none', borderRadius: radius.xs,
        fontFamily: font.mono, fontSize: '10px', fontWeight: 600,
        color: danger ? '#EF4444' : color.muted, cursor: 'pointer',
      }}
    >
      {children}
    </button>
  );
}
