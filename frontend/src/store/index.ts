import { configureStore } from '@reduxjs/toolkit'
import missionsReducer from './slices/missionsSlice'
import uiReducer from './slices/uiSlice'
import threatReducer from './slices/threatSlice'
import alertsReducer from './slices/alertSlice'
import kgReducer from './slices/kgSlice'
import wargameReducer from './slices/wargameSlice'
export const store = configureStore({
  reducer: {
    missions: missionsReducer,
    ui: uiReducer,
    threats: threatReducer,
    alerts: alertsReducer,
    kg: kgReducer,
    wargame: wargameReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
