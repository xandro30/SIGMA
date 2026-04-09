import { useState } from 'react';
import { color, font, getAreaHex } from '../../tokens';
import BaseEditModal, { Field, fieldStyle } from './BaseEditModal';
import { useUpdateArea } from '../../../entities/area/hooks/useAreas';

const AREA_COLOR_IDS = ['coral','violeta','azul','lima','fucsia','turquesa','naranja','ladrillo','indigo','esmeralda','ambar','miel','limay','dorado','neon'];

export default function EditAreaModal({ area, onClose }) {
  const { mutate: update, isPending } = useUpdateArea();
  const [name,        setName]        = useState(area.name ?? '');
  const [description, setDescription] = useState(area.description ?? '');
  const [colorId,     setColorId]     = useState(area.color_id ?? 'azul');
  const [objectives,  setObjectives]  = useState(area.objectives ?? '');

  const hex = getAreaHex(colorId);

  const handleSave = () => {
    update({ id: area.id, name, description, color_id: colorId, objectives: objectives.trim() || null }, { onSuccess: onClose });
  };

  return (
    <BaseEditModal title="Editar Área" accent={hex} onClose={onClose} onSave={handleSave} saving={isPending}>
      <Field label="Nombre">
        <input value={name} onChange={e => setName(e.target.value)} style={fieldStyle} />
      </Field>
      <Field label="Descripción">
        <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} style={{ ...fieldStyle, resize: 'vertical' }} />
      </Field>
      <Field label="Color">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {AREA_COLOR_IDS.map(id => {
            const h = getAreaHex(id);
            return (
              <button key={id} onClick={() => setColorId(id)} style={{ width: '24px', height: '24px', borderRadius: '50%', background: h, border: colorId === id ? `3px solid ${color.text}` : '3px solid transparent', cursor: 'pointer', transition: 'all 0.1s' }} title={id} />
            );
          })}
        </div>
      </Field>
      <Field label="Objetivos">
        <textarea value={objectives} onChange={e => setObjectives(e.target.value)} rows={4} placeholder="¿Qué quieres lograr con esta área?" style={{ ...fieldStyle, resize: 'vertical' }} />
      </Field>
    </BaseEditModal>
  );
}
