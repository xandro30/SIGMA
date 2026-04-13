import { useState, useCallback, useEffect, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { color } from '../../shared/tokens';
import { getMonday, addDays, addMonths, getFirstOfMonth } from '../../shared/dateUtils';
import { useUIStore } from '../../shared/store/useUIStore';
import { useWeek, useWeekDays, useCreateWeek, useSetWeekNotes } from '../../entities/planning/hooks/useWeek';
import { useAddBlock, useUpdateBlock, useRemoveBlock } from '../../entities/planning/hooks/useDayBlocks';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { planningApi } from '../../api/planning';
import { useDragToCreate } from './hooks/useDragToCreate';
import WeekNav from './components/WeekNav';
import WeekGrid from './components/WeekGrid';
import DayView from './components/DayView';
import SprintView from './components/SprintView';
import CycleOverview from './components/CycleOverview';
import MonthView from './components/MonthView';
import BlockEditModal from './components/BlockEditModal';
import TemplatePanel from './components/TemplatePanel';
import CycleManager from './components/CycleManager';

const today = () => new Date().toISOString().split('T')[0];

export default function SchedulingView() {
  const spaceId = useUIStore(s => s.activeSpaceId);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeView = searchParams.get('view') ?? 'week';

  // Date state per view
  const [weekStart, setWeekStart] = useState(() => getMonday());
  const [dayDate, setDayDate] = useState(today);
  const [monthDate, setMonthDate] = useState(() => getFirstOfMonth(today()));

  const [editingBlock, setEditingBlock] = useState(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showCycleManager, setShowCycleManager] = useState(false);
  const qc = useQueryClient();

  const { data: week } = useWeek(spaceId, weekStart);
  const { data: days } = useWeekDays(spaceId, weekStart);
  const { data: areas } = useAreas(spaceId);

  // Fetch active cycle (first found)
  const { data: activeCycle } = useQuery({
    queryKey: ['activeCycle', spaceId],
    queryFn: () => planningApi.getActiveCycle(spaceId).catch(() => null),
    enabled: !!spaceId,
    retry: false,
  });

  // Fetch ALL cycles to find active ones per type
  const { data: allCyclesData } = useQuery({
    queryKey: ['allCycles', spaceId],
    queryFn: () => planningApi.listCycles(spaceId),
    enabled: !!spaceId,
  });

  const allCycles = useMemo(() => {
    const raw = allCyclesData?.cycles ?? allCyclesData ?? [];
    return raw;
  }, [allCyclesData]);

  const activeCycles = useMemo(() => {
    return allCycles.filter(c => c.state === 'active');
  }, [allCycles]);

  // Resolve the cycle for the current view (if it's a cycle view like cycle:sprint, cycle:quarter, etc.)
  const currentCycle = useMemo(() => {
    if (!activeView.startsWith('cycle:')) return null;
    const cycleType = activeView.replace('cycle:', '');
    return activeCycles.find(c => c.cycle_type === cycleType) ?? null;
  }, [activeView, activeCycles]);

  const isCycleView = activeView.startsWith('cycle:');
  const currentCycleType = isCycleView ? activeView.replace('cycle:', '') : null;
  const isSprintView = currentCycleType === 'sprint';
  const isOverviewView = isCycleView && !isSprintView;

  // Day view: fetch single day
  const { data: dayData } = useQuery({
    queryKey: ['singleDay', spaceId, dayDate],
    queryFn: () => planningApi.getDayByDate(spaceId, dayDate).catch(() => null),
    enabled: !!spaceId && activeView === 'day',
  });

  const createWeek = useCreateWeek(spaceId);
  const setNotes = useSetWeekNotes(spaceId, weekStart);
  const addBlock = useAddBlock(spaceId, weekStart);
  const updateBlock = useUpdateBlock(spaceId, weekStart);
  const removeBlock = useRemoveBlock(spaceId, weekStart);

  // Build blocks map for drag overlap detection
  const blocksMap = useMemo(() => {
    const map = {};
    if (activeView === 'day' && dayData) {
      map[dayDate] = dayData.blocks ?? [];
    } else if (days) {
      (days ?? []).forEach(d => { map[d.date] = d.blocks ?? []; });
    }
    return map;
  }, [activeView, dayDate, dayData, days]);

  // Drag-to-create
  const handleDragComplete = useCallback((startMin, duration, dragDayDate) => {
    const h = Math.floor(startMin / 60);
    const m = startMin % 60;
    const startAt = `${dragDayDate}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`;
    setEditingBlock({
      day: null,
      block: { start_at: startAt, duration, area_id: null, notes: '' },
    });
  }, []);

  const { ghostBlock, isDragging, handlers: dragHandlers } = useDragToCreate({
    hourHeightPx: 60,
    startHour: 6,
    existingBlocks: blocksMap,
    onComplete: handleDragComplete,
  });

  // View change handler
  const handleViewChange = useCallback((view) => {
    setSearchParams({ view }, { replace: true });
  }, [setSearchParams]);

  // Navigation handlers per view
  const handlePrev = useCallback(() => {
    if (activeView === 'day') setDayDate(d => addDays(d, -1));
    else if (activeView === 'week') setWeekStart(s => addDays(s, -7));
    else if (activeView === 'month') setMonthDate(d => addMonths(d, -1));
  }, [activeView]);

  const handleNext = useCallback(() => {
    if (activeView === 'day') setDayDate(d => addDays(d, 1));
    else if (activeView === 'week') setWeekStart(s => addDays(s, 7));
    else if (activeView === 'month') setMonthDate(d => addMonths(d, 1));
  }, [activeView]);

  // Navigate from overview to detail view
  const handleDayClick = useCallback((date) => {
    setDayDate(date);
    setSearchParams({ view: 'day' }, { replace: true });
  }, [setSearchParams]);

  const handleWeekClick = useCallback((monday) => {
    setWeekStart(monday);
    setSearchParams({ view: 'week' }, { replace: true });
  }, [setSearchParams]);

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
    if (activeView === 'day') {
      qc.invalidateQueries({ queryKey: ['singleDay', spaceId] });
    }
  };

  const handleBlockDelete = async () => {
    const { day, block } = editingBlock;
    if (block?.id && day?.id) {
      await removeBlock.mutateAsync({ dayId: day.id, blockId: block.id });
    }
    setEditingBlock(null);
    if (activeView === 'day') {
      qc.invalidateQueries({ queryKey: ['singleDay', spaceId] });
    }
  };

  const handleNotesChange = useCallback(async (notes) => {
    await createWeek.mutateAsync(weekStart).catch(() => {});
    await setNotes.mutateAsync(notes);
  }, [createWeek, weekStart, setNotes]);

  const handleCycleChanged = () => {
    qc.invalidateQueries({ queryKey: ['activeCycle', spaceId] });
    qc.invalidateQueries({ queryKey: ['allCycles', spaceId] });
    setShowCycleManager(false);
  };

  // Expose data for sidebar
  useEffect(() => {
    useUIStore.setState({
      _schedulingData: {
        weekStart, week, days, areas, activeCycle,
        onNotesChange: handleNotesChange,
        onManageCycle: () => setShowCycleManager(true),
      },
    });
  }, [weekStart, week, days, areas, activeCycle, handleNotesChange]);

  if (!spaceId) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: color.muted2, fontSize: '13px' }}>
        Selecciona un Space para planificar
      </div>
    );
  }

  // Determine current date label for nav
  const navDate = activeView === 'day' ? dayDate
    : activeView === 'month' ? monthDate
    : weekStart;

  const showActions = activeView === 'day' || activeView === 'week';
  const showNav = !isCycleView; // cycle views have fixed date range

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <WeekNav
        activeView={activeView}
        onViewChange={handleViewChange}
        currentDate={navDate}
        activeCycle={currentCycle ?? activeCycle}
        activeCycles={activeCycles}
        onPrev={handlePrev}
        onNext={handleNext}
        onTemplate={() => setShowTemplates(true)}
        onNewBlock={handleNewBlock}
        showActions={showActions}
        showNav={showNav}
      />

      {/* View content */}
      {activeView === 'day' && (
        <DayView
          date={dayDate}
          day={dayData}
          areas={areas}
          onBlockClick={handleBlockClick}
          dragHandlers={dragHandlers}
          ghostBlock={ghostBlock}
        />
      )}

      {activeView === 'week' && (
        <WeekGrid
          weekStart={weekStart}
          days={days}
          areas={areas}
          onBlockClick={handleBlockClick}
          dragHandlers={dragHandlers}
          ghostBlock={ghostBlock}
        />
      )}

      {isSprintView && (
        <SprintView
          spaceId={spaceId}
          activeCycle={currentCycle}
          areas={areas}
          onDayClick={handleDayClick}
        />
      )}

      {isOverviewView && (
        <CycleOverview
          spaceId={spaceId}
          cycle={currentCycle}
          areas={areas}
          onWeekClick={handleWeekClick}
        />
      )}

      {activeView === 'month' && (
        <MonthView
          monthDate={monthDate}
          spaceId={spaceId}
          areas={areas}
          onDayClick={handleDayClick}
        />
      )}

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
        <TemplatePanel
          spaceId={spaceId}
          areas={areas}
          weekStart={weekStart}
          onClose={() => setShowTemplates(false)}
          onApplied={() => {
            qc.invalidateQueries({ queryKey: ['weekDays', spaceId] });
            qc.invalidateQueries({ queryKey: ['singleDay', spaceId] });
          }}
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
