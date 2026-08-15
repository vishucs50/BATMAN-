import { configureStore } from '@reduxjs/toolkit'
import missionsReducer from './slices/missionsSlice'
import uiReducer from './slices/uiSlice'
import threatReducer from './slices/threatSlice'

export const store = configureStore({
  reducer: {
    missions: missionsReducer,
    ui: uiReducer,
    threats: threatReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
