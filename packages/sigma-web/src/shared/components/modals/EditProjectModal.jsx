import { useState } from 'react';
import { color, getAreaHex } from '../../tokens';
import BaseEditModal, { Field, fieldStyle } from './BaseEditModal';
import { useUpdateProject } from '../../../entities/project/hooks/useProjects';
import { useAreas } from '../../../entities/area/hooks/useAreas';

const STATUSES = [
  { id: 'active',    label: 'Activo',     c: '#10B981' },
  { id: 'on_hold',   label: 'En pausa',   c: '#F97316' },
  { id: 'completed', label: 'Completado', c: '#6366F1' },
];

export default function EditProjectModal({ project, areaId, onClose }) {
  const { mutate: update, isPending } = useUpdateProject(project.id, areaId);
  const { data: areas = [] } = useAreas();
  const area = areas.find(a => a.id === areaId);
  const hex  = getAreaHex(area?.color_id);

  const [name,        setName]        = useState(project.name ?? '');
  const [description, setDescription] = useState(project.description ?? '');
  const [status,      setStatus]      = useState(project.status ?? 'active');
  const [objectives,  setObjectives]  = useState(project.objectives ?? '');

  const handleSave = () => {
    update({ name, description, status, objectives: objectives.trim() || null }, { onSuccess: onClose });
  };

  return (
    <BaseEditModal title="Editar Proyecto" accent={hex} onClose={onClose} onSave={handleSave} saving={isPending}>
      <Field label="Nombre">
        <input value={name} onChange={e => setName(e.target.value)} style={fieldStyle} />
      </Field>
      <Field label="Estado">
        <div style={{ display: 'flex', gap: '6px' }}>
          {STATUSES.map(s => (
            <button key={s.id} onClick={() => setStatus(s.id)} style={{ flex: 1, padding: '7px 0', borderRadius: '7px', border: `1.5px solid ${status === s.id ? s.c : color.border2}`, background: status === s.id ? `${s.c}20` : 'transparent', color: status === s.id ? s.c : color.muted, cursor: 'pointer', fontSize: '10px', fontWeight: 700 }}>
              {s.label}
            </button>
          ))}
        </div>
      </Field>
      <Field label="Descripción">
        <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} style={{ ...fieldStyle, resize: 'vertical' }} />
      </Field>
      <Field label="Objetivos">
        <textarea value={objectives} onChange={e => setObjectives(e.target.value)} rows={4} placeholder="¿Qué quieres lograr con este proyecto?" style={{ ...fieldStyle, resize: 'vertical' }} />
      </Field>
    </BaseEditModal>
  );
}
