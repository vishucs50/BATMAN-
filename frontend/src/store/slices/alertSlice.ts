import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface Alert {
  type: string
  title: string
  msg: string
  severity: string
  timestamp: string
}

interface AlertState {
  alerts: Alert[]
  connected: boolean
}

const initialState: AlertState = {
  alerts: [],
  connected: false,
}

const alertSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    setConnectionStatus(state, action: PayloadAction<boolean>) {
      state.connected = action.payload
    },
    addAlert(state, action: PayloadAction<Alert>) {
      state.alerts.unshift(action.payload)
    },
    clearAlerts(state) {
      state.alerts = []
    }
  },
})

export const { setConnectionStatus, addAlert, clearAlerts } = alertSlice.actions
export default alertSlice.reducer
