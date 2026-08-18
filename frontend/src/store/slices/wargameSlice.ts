import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

export interface SimulationStats {
  id: string
  coa_id: string
  run_count: number
  success_rate: number
  mean_casualties: number
  std_casualties: number
  timeline_p50_min: number
  timeline_p95_min: number
  roe_violation_rate: number
  fuel_consumed_mean: number
  ammo_consumed_mean: number
}

interface WargameState {
  lastSimId: string | null
  stats: SimulationStats | null
  loading: boolean
  error: string | null
}

const initialState: WargameState = {
  lastSimId: null,
  stats: null,
  loading: false,
  error: null,
}

export const fetchSimulationStats = createAsyncThunk('wargame/fetchStats', async (simId: string) => {
  const response = await axios.get(`/api/v1/simulation/${simId}`)
  return response.data as SimulationStats
})

const wargameSlice = createSlice({
  name: 'wargame',
  initialState,
  reducers: {
    setLastSimId(state, action) {
      state.lastSimId = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSimulationStats.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchSimulationStats.fulfilled, (state, action) => {
        state.loading = false
        state.stats = action.payload
      })
      .addCase(fetchSimulationStats.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Failed to fetch sim stats'
      })
  },
})

export const { setLastSimId } = wargameSlice.actions
export default wargameSlice.reducer
