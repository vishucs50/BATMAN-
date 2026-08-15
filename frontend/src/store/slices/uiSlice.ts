import { createSlice, PayloadAction } from '@reduxjs/toolkit'

type ActiveView = 'command' | 'coa' | 'wargame' | 'logistics' | 'kg' | 'aar'

interface UIState {
  activeView: ActiveView
  sidebarCollapsed: boolean
  mapStyle: string
}

const initialState: UIState = {
  activeView: 'command',
  sidebarCollapsed: false,
  mapStyle: 'dark',
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setActiveView(state, action: PayloadAction<ActiveView>) {
      state.activeView = action.payload
    },
    toggleSidebar(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
  },
})

export const { setActiveView, toggleSidebar } = uiSlice.actions
export default uiSlice.reducer
