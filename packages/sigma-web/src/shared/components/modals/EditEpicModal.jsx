import { useState } from 'react';
import { color, getAreaHex } from '../../tokens';
import BaseEditModal, { Field, fieldStyle } from './BaseEditModal';
import { useUpdateEpic } from '../../../entities/epic/hooks/useEpics';
import { useAreas } from '../../../entities/area/hooks/useAreas';
import { useUIStore } from '../../store/useUIStore';

export default function EditEpicModal({ epic, areaId, onClose }) {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { mutate: update, isPending } = useUpdateEpic(epic.id, activeSpaceId);
  const { data: areas = [] } = useAreas();
  const area = areas.find(a => a.id === areaId);
  const hex  = getAreaHex(area?.color_id);

  const [name,        setName]        = useState(epic.name ?? '');
  const [description, setDescription] = useState(epic.description ?? '');

  const handleSave = () => {
    update({ name, description }, { onSuccess: onClose });
  };

  return (
    <BaseEditModal title="Editar Épica" accent={hex} onClose={onClose} onSave={handleSave} saving={isPending}>
      <Field label="Nombre">
        <input value={name} onChange={e => setName(e.target.value)} style={fieldStyle} />
      </Field>
      <Field label="Descripción">
        <textarea value={description} onChange={e => setDescription(e.target.value)} rows={4} style={{ ...fieldStyle, resize: 'vertical' }} />
      </Field>
    </BaseEditModal>
  );
}
