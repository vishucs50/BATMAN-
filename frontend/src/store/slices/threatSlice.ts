import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import axios from 'axios'

export interface ThreatAssessment {
  id: string
  threat_type: string
  probability: number
  confidence: number
  risk_score: number
  location?: { lat: number; lon: number }
  assessed_at: string
}

interface ThreatState {
  assessments: ThreatAssessment[]
  overallThreatLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  loading: boolean
  error: string | null
}

const initialState: ThreatState = {
  assessments: [],
  overallThreatLevel: 'MEDIUM',
  loading: false,
  error: null,
}

export const fetchThreatAssessment = createAsyncThunk('threats/fetchAssessment', async (missionId: string) => {
  const response = await axios.get(`/api/v1/threats/missions/${missionId}`)
  return response.data as ThreatAssessment[]
})

const threatSlice = createSlice({
  name: 'threats',
  initialState,
  reducers: {
    setAssessments(state, action: PayloadAction<ThreatAssessment[]>) {
      state.assessments = action.payload
    },
    updateThreatLevel(state, action: PayloadAction<ThreatState['overallThreatLevel']>) {
      state.overallThreatLevel = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchThreatAssessment.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchThreatAssessment.fulfilled, (state, action) => {
        state.loading = false
        state.assessments = action.payload
        if (action.payload.length > 0) {
          const maxRisk = Math.max(...action.payload.map(t => t.risk_score))
          state.overallThreatLevel = maxRisk > 7 ? 'CRITICAL' : maxRisk > 4 ? 'HIGH' : maxRisk > 2 ? 'MEDIUM' : 'LOW'
        }
      })
      .addCase(fetchThreatAssessment.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Failed to fetch threats'
      })
  },
})

export const { setAssessments, updateThreatLevel } = threatSlice.actions
export default threatSlice.reducer
