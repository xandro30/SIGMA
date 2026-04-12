import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { color } from '../../shared/tokens';
import { getMonday, addDays } from '../../shared/dateUtils';
import { useUIStore } from '../../shared/store/useUIStore';
import { useWeek, useWeekDays, useCreateWeek, useSetWeekNotes, useApplyWeekTemplate } from '../../entities/planning/hooks/useWeek';
import { useAddBlock, useUpdateBlock, useRemoveBlock } from '../../entities/planning/hooks/useDayBlocks';
import { useWeekTemplates } from '../../entities/planning/hooks/useTemplates';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { planningApi } from '../../api/planning';
import WeekNav from './components/WeekNav';
import WeekGrid from './components/WeekGrid';
import BlockEditModal from './components/BlockEditModal';
import TemplateSelector from './components/TemplateSelector';
import CycleManager from './components/CycleManager';

export default function SchedulingView() {
  const spaceId = useUIStore(s => s.activeSpaceId);
  const [weekStart, setWeekStart] = useState(() => getMonday());
  const [editingBlock, setEditingBlock] = useState(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showCycleManager, setShowCycleManager] = useState(false);
  const qc = useQueryClient();

  const { data: week } = useWeek(spaceId, weekStart);
  const { data: days } = useWeekDays(spaceId, weekStart);
  const { data: areas } = useAreas(spaceId);
  const { data: templates } = useWeekTemplates(spaceId);

  // Fetch active cycle — used by sidebar and CycleManager
  const { data: activeCycle } = useQuery({
    queryKey: ['activeCycle', spaceId],
    queryFn: () => planningApi.getActiveCycle(spaceId).catch(() => null),
    enabled: !!spaceId,
    retry: false,
  });

  const createWeek = useCreateWeek(spaceId);
  const setNotes = useSetWeekNotes(spaceId, weekStart);
  const applyTemplate = useApplyWeekTemplate(spaceId, weekStart);
  const addBlock = useAddBlock(spaceId, weekStart);
  const updateBlock = useUpdateBlock(spaceId, weekStart);
  const removeBlock = useRemoveBlock(spaceId, weekStart);

  const handlePrev = useCallback(() => setWeekStart(s => addDays(s, -7)), []);
  const handleNext = useCallback(() => setWeekStart(s => addDays(s, 7)), []);

  const handleNewBlock = () => setEditingBlock({ day: null, block: null });
  const handleBlockClick = (day, block) => setEditingBlock({ day, block });

  const handleBlockSave = async (data) => {
    const { day, block } = editingBlock;
    if (block?.id && day?.id) {
      await updateBlock.mutateAsync({ dayId: day.id, blockId: block.id, ...data });
    } else {
      await createWeek.mutateAsync(weekStart).catch(() => {});
      const blockDate = data.start_at?.split('T')[0];
      if (!blockDate) return;
      const dayResp = await planningApi.createDay(spaceId, { date: blockDate });
      await addBlock.mutateAsync({ dayId: dayResp.id, ...data });
    }
    setEditingBlock(null);
  };

  const handleBlockDelete = async () => {
    const { day, block } = editingBlock;
    if (block?.id && day?.id) {
      await removeBlock.mutateAsync({ dayId: day.id, blockId: block.id });
    }
    setEditingBlock(null);
  };

  const handleApplyTemplate = async ({ templateId, replaceExisting }) => {
    await createWeek.mutateAsync(weekStart).catch(() => {});
    await applyTemplate.mutateAsync({ templateId, replaceExisting });
    setShowTemplates(false);
  };

  const handleNotesChange = async (notes) => {
    await createWeek.mutateAsync(weekStart).catch(() => {});
    await setNotes.mutateAsync(notes);
  };

  const handleCycleChanged = () => {
    qc.invalidateQueries({ queryKey: ['activeCycle', spaceId] });
    setShowCycleManager(false);
  };

  // Expose data for sidebar via store
  useUIStore.setState({
    _schedulingData: {
      weekStart, week, days, areas, activeCycle,
      onNotesChange: handleNotesChange,
      onManageCycle: () => setShowCycleManager(true),
    },
  });

  if (!spaceId) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: color.muted2, fontSize: '13px' }}>
        Selecciona un Space para planificar
      </div>
    );
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <WeekNav
        weekStart={weekStart}
        onPrev={handlePrev}
        onNext={handleNext}
        onTemplate={() => setShowTemplates(true)}
        onNewBlock={handleNewBlock}
      />
      <WeekGrid
        weekStart={weekStart}
        days={days}
        areas={areas}
        onBlockClick={handleBlockClick}
      />

      {editingBlock && (
        <BlockEditModal
          block={editingBlock.block}
          areas={areas}
          onSave={handleBlockSave}
          onDelete={editingBlock.block?.id ? handleBlockDelete : null}
          onClose={() => setEditingBlock(null)}
        />
      )}

      {showTemplates && (
        <TemplateSelector
          templates={templates}
          onApply={handleApplyTemplate}
          onClose={() => setShowTemplates(false)}
        />
      )}

      {showCycleManager && (
        <CycleManager
          spaceId={spaceId}
          areas={areas}
          onClose={() => setShowCycleManager(false)}
          onChanged={handleCycleChanged}
        />
      )}
    </div>
  );
}
