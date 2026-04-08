import { create } from 'zustand';

export const useUIStore = create((set) => ({
  // Space activo
  activeSpaceId:    null,
  setActiveSpaceId: (id) => set({ activeSpaceId: id }),

  // Filtro de área en el board
  activeAreaFilter:    'all',
  setActiveAreaFilter: (id) => set({ activeAreaFilter: id }),

  // Modal crear card
  createCardOpen:  false,
  openCreateCard:  () => set({ createCardOpen: true }),
  closeCreateCard: () => set({ createCardOpen: false }),

  // Modal crear área
  createAreaOpen:  false,
  openCreateArea:  () => set({ createAreaOpen: true }),
  closeCreateArea: () => set({ createAreaOpen: false }),
}));
