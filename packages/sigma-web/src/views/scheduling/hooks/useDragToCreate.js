import { useState, useCallback, useRef } from 'react';

const DRAG_THRESHOLD = 5;
const SNAP_MINUTES = 15;
const MIN_DURATION = 15;

export function useDragToCreate({ hourHeightPx, startHour, existingBlocks, onComplete }) {
  const [ghostBlock, setGhostBlock] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const dragState = useRef(null);

  const posToTime = useCallback((y) => {
    const totalMinutes = (y / hourHeightPx) * 60 + startHour * 60;
    const snapped = Math.round(totalMinutes / SNAP_MINUTES) * SNAP_MINUTES;
    return Math.max(startHour * 60, Math.min(23 * 60 + 45, snapped));
  }, [hourHeightPx, startHour]);

  const timeToY = useCallback((minutes) => {
    return ((minutes - startHour * 60) / 60) * hourHeightPx;
  }, [hourHeightPx, startHour]);

  const checkOverlap = useCallback((startMin, endMin, dayDate) => {
    if (!existingBlocks) return false;
    const dayBlocks = Array.isArray(existingBlocks)
      ? existingBlocks
      : (existingBlocks[dayDate] ?? []);
    return dayBlocks.some(b => {
      const bStart = new Date(b.start_at);
      const bStartMin = bStart.getHours() * 60 + bStart.getMinutes();
      const bEndMin = bStartMin + b.duration;
      return startMin < bEndMin && endMin > bStartMin;
    });
  }, [existingBlocks]);

  const formatTime = (totalMinutes) => {
    const h = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  };

  const handleMouseDown = useCallback((e, dayDate) => {
    if (e.button !== 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const startMin = posToTime(y);

    dragState.current = {
      dayDate,
      startY: e.clientY,
      startMin,
      rect,
      activated: false,
    };

    e.preventDefault();
  }, [posToTime]);

  const handleMouseMove = useCallback((e) => {
    if (!dragState.current) return;
    const ds = dragState.current;

    if (!ds.activated) {
      const dist = Math.abs(e.clientY - ds.startY);
      if (dist < DRAG_THRESHOLD) return;
      ds.activated = true;
      setIsDragging(true);
    }

    const y = e.clientY - ds.rect.top;
    const currentMin = posToTime(y);
    const topMin = Math.min(ds.startMin, currentMin);
    const bottomMin = Math.max(ds.startMin, currentMin);
    const duration = Math.max(MIN_DURATION, bottomMin - topMin);
    const hasOverlap = checkOverlap(topMin, topMin + duration, ds.dayDate);

    setGhostBlock({
      top: timeToY(topMin),
      height: (duration / 60) * hourHeightPx,
      startMin: topMin,
      duration,
      label: `${formatTime(topMin)} – ${formatTime(topMin + duration)}`,
      hasOverlap,
      dayDate: ds.dayDate,
    });
  }, [posToTime, timeToY, hourHeightPx, checkOverlap]);

  const handleMouseUp = useCallback((e) => {
    if (!dragState.current) return;
    const ds = dragState.current;

    if (!ds.activated) {
      const rect = ds.rect;
      const y = e.clientY - rect.top;
      const clickMin = posToTime(y);
      const hasOverlap = checkOverlap(clickMin, clickMin + 60, ds.dayDate);

      dragState.current = null;
      setGhostBlock(null);
      setIsDragging(false);

      if (!hasOverlap) {
        onComplete(clickMin, 60, ds.dayDate);
      }
      return;
    }

    const currentGhost = ghostBlock;
    dragState.current = null;
    setGhostBlock(null);
    setIsDragging(false);

    if (currentGhost && !currentGhost.hasOverlap) {
      onComplete(currentGhost.startMin, currentGhost.duration, currentGhost.dayDate);
    }
  }, [posToTime, checkOverlap, onComplete, ghostBlock]);

  const cancelDrag = useCallback(() => {
    dragState.current = null;
    setGhostBlock(null);
    setIsDragging(false);
  }, []);

  return {
    ghostBlock,
    isDragging,
    handlers: { handleMouseDown, handleMouseMove, handleMouseUp },
    cancelDrag,
  };
}
