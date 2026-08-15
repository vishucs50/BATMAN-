import { createSlice, PayloadAction } from '@reduxjs/toolkit'

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
}

const initialState: ThreatState = {
  assessments: [],
  overallThreatLevel: 'MEDIUM',
}

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
})

export const { setAssessments, updateThreatLevel } = threatSlice.actions
export default threatSlice.reducer
