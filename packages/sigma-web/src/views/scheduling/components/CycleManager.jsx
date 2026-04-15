import { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { color, font, radius, space, elevation, motion, overlay } from '../../../shared/tokens';
import { X, Plus } from '../../../shared/components/Icons';
import { planningApi } from '../../../api/planning';
import { useEscapeKey } from '../../../shared/hooks/useEscapeKey';

const CYCLE_TYPES = [
  { value: 'sprint', label: 'Sprint', desc: '1-4 semanas' },
  { value: 'quarter', label: 'Quarter', desc: '~3 meses' },
  { value: 'semester', label: 'Semestre', desc: '~6 meses' },
  { value: 'annual', label: 'Anual', desc: '1 año' },
];

export default function CycleManager({ spaceId, areas, onClose, onChanged }) {
  useEscapeKey(onClose);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');
  const [cycleType, setCycleType] = useState('sprint');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [budgetArea, setBudgetArea] = useState('');
  const [budgetMinutes, setBudgetMinutes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCycleId, setSelectedCycleId] = useState(null);
  const qc = useQueryClient();

  // Fetch all cycles for this space
  const { data: allCycles } = useQuery({
    queryKey: ['allCycles', spaceId],
    queryFn: () => planningApi.listCycles(spaceId),
    enabled: !!spaceId,
  });

  const cycles = allCycles?.cycles ?? allCycles ?? [];
  const activeCycles = cycles.filter(c => c.state === 'active');
  const draftCycles = cycles.filter(c => c.state === 'draft');
  const closedCycles = cycles.filter(c => c.state === 'closed');
  const selectedCycle = cycles.find(c => c.id === selectedCycleId);

  const handleCreate = async () => {
    if (!name || !startDate || !endDate) return;
    setLoading(true); setError(null);
    try {
      const created = await planningApi.createCycle(spaceId, {
        name, cycle_type: cycleType,
        date_range: { start: startDate, end: endDate },
      });
      setCreating(false); setName(''); setStartDate(''); setEndDate('');
      qc.invalidateQueries({ queryKey: ['allCycles', spaceId] });
      setSelectedCycleId(created.id);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleActivate = async () => {
    if (!selectedCycle) return;
    setLoading(true); setError(null);
    try {
      await planningApi.activateCycle(spaceId, selectedCycle.id);
      qc.invalidateQueries({ queryKey: ['allCycles', spaceId] });
      qc.invalidateQueries({ queryKey: ['activeCycle', spaceId] });
      onChanged?.();
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleClose = async () => {
    if (!selectedCycle) return;
    setLoading(true); setError(null);
    try {
      await planningApi.closeCycle(spaceId, selectedCycle.id);
      qc.invalidateQueries({ queryKey: ['allCycles', spaceId] });
      qc.invalidateQueries({ queryKey: ['activeCycle', spaceId] });
      onChanged?.();
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleAddBudget = async () => {
    if (!selectedCycle || !budgetArea || !budgetMinutes) return;
    setLoading(true); setError(null);
    try {
      await planningApi.setBudget(spaceId, selectedCycle.id, {
        area_id: budgetArea, minutes: Number(budgetMinutes),
      });
      setBudgetArea(''); setBudgetMinutes('');
      qc.invalidateQueries({ queryKey: ['allCycles', spaceId] });
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div onClick={onClose} style={{ position: 'absolute', inset: 0, background: overlay.scrim, animation: 'fadeIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards' }} />
      <div style={{
        position: 'relative', width: '500px', maxWidth: '92vw', maxHeight: '85vh',
        background: color.s2, borderRadius: radius.lg, boxShadow: elevation[3],
        padding: space['2xl'], display: 'flex', flexDirection: 'column', gap: space.lg,
        overflowY: 'auto', animation: 'scaleInFlex 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 700, color: color.text, margin: 0 }}>
            Gestionar ciclos
          </h3>
          <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', color: color.muted, cursor: 'pointer', padding: space.xs }}>
            <X size="18" />
          </button>
        </div>

        {error && (
          <div style={{ padding: space.sm, background: 'rgba(239,68,68,0.12)', borderRadius: radius.sm, fontFamily: font.sans, fontSize: '12px', color: '#EF4444' }}>
            {error}
          </div>
        )}

        {/* Active cycles */}
        {activeCycles.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
            <Label>Ciclos activos</Label>
            {activeCycles.map(c => (
              <CycleCard key={c.id} cycle={c} selected={selectedCycleId === c.id}
                onClick={() => setSelectedCycleId(selectedCycleId === c.id ? null : c.id)} />
            ))}
          </div>
        )}

        {/* Draft cycles */}
        {draftCycles.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
            <Label>Borradores</Label>
            {draftCycles.map(c => (
              <CycleCard key={c.id} cycle={c} selected={selectedCycleId === c.id}
                onClick={() => setSelectedCycleId(selectedCycleId === c.id ? null : c.id)} />
            ))}
          </div>
        )}

        {/* Selected cycle detail */}
        {selectedCycle && (
          <div style={{ background: color.s1, borderRadius: radius.md, padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.md }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
              <span style={{ fontFamily: font.sans, fontSize: '14px', fontWeight: 600, color: color.text }}>{selectedCycle.name}</span>
              <StateBadge state={selectedCycle.state} />
              <TypeBadge type={selectedCycle.cycle_type} />
            </div>
            <div style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted }}>
              {selectedCycle.date_range?.start} — {selectedCycle.date_range?.end}
            </div>

            {/* Budgets */}
            {selectedCycle.area_budgets?.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
                <Label>Budgets</Label>
                {selectedCycle.area_budgets.map(b => {
                  const area = (areas ?? []).find(a => a.id === b.area_id);
                  return (
                    <div key={b.area_id} style={{ display: 'flex', justifyContent: 'space-between', fontFamily: font.mono, fontSize: '11px', color: color.muted }}>
                      <span>{area?.name ?? b.area_id.slice(0, 8)}</span>
                      <span>{b.minutes} min</span>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Add budget (only if not closed) */}
            {selectedCycle.state !== 'closed' && (
              <div style={{ display: 'flex', gap: space.sm, alignItems: 'flex-end' }}>
                <div style={{ flex: 1 }}>
                  <Label>Area</Label>
                  <select value={budgetArea} onChange={e => setBudgetArea(e.target.value)} style={{ fontSize: '12px' }}>
                    <option value="">Seleccionar...</option>
                    {(areas ?? []).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                  </select>
                </div>
                <div style={{ width: '100px' }}>
                  <Label>Minutos</Label>
                  <input type="number" min={0} step={60} value={budgetMinutes} onChange={e => setBudgetMinutes(e.target.value)} style={{ fontSize: '12px' }} />
                </div>
                <button onClick={handleAddBudget} disabled={!budgetArea || !budgetMinutes || loading}
                  style={{ ...btnBase, padding: `${space.sm} ${space.md}`, background: color.s3, color: color.text, opacity: (!budgetArea || !budgetMinutes) ? 0.38 : 1, marginBottom: '1px' }}>
                  <Plus size="14" />
                </button>
              </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: space.sm, paddingTop: space.xs }}>
              {selectedCycle.state === 'draft' && (
                <button onClick={handleActivate} disabled={loading} style={{ ...btnBase, background: color.yellow, color: '#000' }}>
                  Activar
                </button>
              )}
              {selectedCycle.state !== 'closed' && (
                <button onClick={handleClose} disabled={loading} style={{ ...btnBase, background: 'rgba(239,68,68,0.15)', color: '#EF4444' }}>
                  Cerrar
                </button>
              )}
            </div>
          </div>
        )}

        {/* Closed cycles (collapsed) */}
        {closedCycles.length > 0 && (
          <details style={{ cursor: 'pointer' }}>
            <summary style={{ fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted, textTransform: 'uppercase', letterSpacing: '0.1em', padding: `${space.xs} 0` }}>
              Cerrados ({closedCycles.length})
            </summary>
            <div style={{ display: 'flex', flexDirection: 'column', gap: space.xs, paddingTop: space.sm }}>
              {closedCycles.map(c => (
                <CycleCard key={c.id} cycle={c} selected={false} onClick={() => {}} compact />
              ))}
            </div>
          </details>
        )}

        {/* Create new */}
        {!creating ? (
          <button onClick={() => setCreating(true)} style={{ ...btnBase, background: color.yellowDim, color: color.yellow, border: `1px dashed ${color.borderAccent}`, justifyContent: 'center' }}>
            + Crear ciclo
          </button>
        ) : (
          <div style={{ background: color.s1, borderRadius: radius.md, padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.md }}>
            <Label>Nuevo ciclo</Label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Sprint 1, Q2 2026..." />
            <div style={{ display: 'flex', gap: space.sm }}>
              {CYCLE_TYPES.map(t => (
                <button key={t.value} onClick={() => setCycleType(t.value)}
                  style={{
                    ...btnBase, flex: 1, flexDirection: 'column', padding: space.sm, fontSize: '11px',
                    background: cycleType === t.value ? color.yellowDim : color.s3,
                    color: cycleType === t.value ? color.yellow : color.text,
                    border: cycleType === t.value ? `1px solid ${color.borderAccent}` : '1px solid transparent',
                  }}>
                  <span style={{ fontWeight: 700 }}>{t.label}</span>
                  <span style={{ fontFamily: font.mono, fontSize: '9px', color: color.muted }}>{t.desc}</span>
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: space.sm }}>
              <div style={{ flex: 1 }}>
                <Label>Inicio</Label>
                <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
              </div>
              <div style={{ flex: 1 }}>
                <Label>Fin</Label>
                <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: space.sm, justifyContent: 'flex-end' }}>
              <button onClick={() => setCreating(false)} style={{ ...btnBase, background: color.s3, color: color.text }}>Cancelar</button>
              <button onClick={handleCreate} disabled={!name || !startDate || !endDate || loading}
                style={{ ...btnBase, background: color.yellow, color: '#000', opacity: (!name || !startDate || !endDate) ? 0.38 : 1 }}>
                Crear
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────

function CycleCard({ cycle, selected, onClick, compact }) {
  const [hov, setHov] = useState(false);
  return (
    <button onClick={onClick} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
      style={{
        display: 'flex', alignItems: 'center', gap: space.sm, width: '100%', textAlign: 'left',
        padding: compact ? `${space.xs} ${space.md}` : space.md,
        background: selected ? color.yellowDim : hov ? color.s3 : color.s2,
        border: selected ? `1px solid ${color.borderAccent}` : `1px solid ${color.border}`,
        borderRadius: radius.md, cursor: 'pointer', transition: `all ${motion.fast}`,
      }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: space.xs }}>
          <span style={{ fontFamily: font.sans, fontSize: compact ? '11px' : '13px', fontWeight: 600, color: color.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {cycle.name}
          </span>
          <TypeBadge type={cycle.cycle_type} />
        </div>
        <div style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>
          {cycle.date_range?.start} — {cycle.date_range?.end}
        </div>
      </div>
      <StateBadge state={cycle.state} />
    </button>
  );
}

function Label({ children }) {
  return (
    <span style={{ display: 'block', fontFamily: font.mono, fontSize: '10px', fontWeight: 700, color: color.muted, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: space.xs }}>
      {children}
    </span>
  );
}

function StateBadge({ state }) {
  const styles = {
    draft: { bg: 'rgba(107,114,128,0.12)', color: '#6B7280', label: 'DRAFT' },
    active: { bg: 'rgba(34,197,94,0.12)', color: '#22C55E', label: 'ACTIVO' },
    closed: { bg: 'rgba(107,114,128,0.12)', color: '#6B7280', label: 'CERRADO' },
  };
  const s = styles[state] ?? styles.draft;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '3px',
      padding: `2px ${space.sm}`, background: s.bg, borderRadius: radius.xl,
      fontFamily: font.mono, fontSize: '9px', fontWeight: 700, color: s.color,
      textTransform: 'uppercase', letterSpacing: '0.05em',
    }}>
      <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: s.color }} />
      {s.label}
    </span>
  );
}

function TypeBadge({ type }) {
  if (!type) return null;
  const labels = { sprint: 'Sprint', quarter: 'Trimestre', semester: 'Semestre', annual: 'Año' };
  return (
    <span style={{
      padding: `1px ${space.xs}`, background: color.s3, borderRadius: radius.xs,
      fontFamily: font.mono, fontSize: '9px', fontWeight: 600, color: color.muted,
      textTransform: 'uppercase',
    }}>
      {labels[type] ?? type}
    </span>
  );
}

const btnBase = {
  display: 'flex', alignItems: 'center', gap: space.xs,
  padding: `${space.sm} ${space.lg}`, border: 'none', borderRadius: radius.md,
  fontFamily: font.sans, fontSize: '13px', fontWeight: 600, cursor: 'pointer',
  transition: `all ${motion.fast}`,
};
