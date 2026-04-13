import { useState } from 'react';
import { color, font, radius, space, motion } from '../../../shared/tokens';
import { Plus } from '../../../shared/components/Icons';
import { useDayTemplates } from '../../../entities/planning/hooks/useTemplates';
import { useCreateDayTemplate, useUpdateDayTemplate, useDeleteDayTemplate, useApplyDayTemplate } from '../../../entities/planning/hooks/useTemplateMutations';
import DayTemplateEditor from './DayTemplateEditor';

export default function DayTemplateList({ spaceId, areas, onApplied }) {
  const { data: templates = [] } = useDayTemplates(spaceId);
  const [editing, setEditing] = useState(null); // null = list, 'new' = create, template obj = edit

  const createTemplate = useCreateDayTemplate(spaceId);
  const updateTemplate = useUpdateDayTemplate(spaceId);
  const deleteTemplate = useDeleteDayTemplate(spaceId);
  const applyTemplate = useApplyDayTemplate(spaceId);

  const handleSave = async (data) => {
    if (editing === 'new') {
      await createTemplate.mutateAsync(data);
    } else if (editing?.id) {
      await updateTemplate.mutateAsync({ templateId: editing.id, data });
    }
    setEditing(null);
  };

  const handleDelete = async (templateId) => {
    if (!confirm('Eliminar esta plantilla?')) return;
    await deleteTemplate.mutateAsync(templateId);
  };

  const handleApply = async (templateId) => {
    const today = new Date().toISOString().split('T')[0];
    await applyTemplate.mutateAsync({ templateId, targetDate: today, replaceExisting: false });
    onApplied?.();
  };

  // Show editor
  if (editing !== null) {
    return (
      <DayTemplateEditor
        template={editing === 'new' ? null : editing}
        areas={areas}
        onSave={handleSave}
        onCancel={() => setEditing(null)}
      />
    );
  }

  // List view
  return (
    <div style={{ padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.md }}>
      {templates.length === 0 && (
        <p style={{
          fontFamily: font.sans, fontSize: '13px', color: color.muted2,
          textAlign: 'center', padding: space.xl,
        }}>
          No hay plantillas de dia creadas
        </p>
      )}

      {templates.map(t => {
        const blockCount = t.blocks?.length ?? 0;
        const totalMin = (t.blocks ?? []).reduce((s, b) => s + b.duration, 0);
        const hours = Math.floor(totalMin / 60);
        const mins = totalMin % 60;

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
              {blockCount} bloques · {hours}h{mins > 0 ? `${mins}m` : ''}
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
              Aplicar a hoy
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
        Nueva plantilla de dia
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
        transition: `color ${motion.fast}`,
      }}
    >
      {children}
    </button>
  );
}
