import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import axios from 'axios'

export interface RadarMetrics {
  Terrain: number
  Threat: number
  Logistics: number
  Comms: number
  Weather: number
}

export interface GNNReasoning {
  mission_id: string
  mission_success_probability: number
  route_risk_distribution: Record<string, number>
  critical_asset_scores: any[]
  relational_bottlenecks: any[]
  radar_metrics?: RadarMetrics
}

export interface GraphNode {
  id: string
  label: string
  properties: any
}

interface KGState {
  reasoning: GNNReasoning | null
  units: GraphNode[]
  loading: boolean
  error: string | null
}

const initialState: KGState = {
  reasoning: null,
  units: [],
  loading: false,
  error: null,
}

export const fetchGNNReasoning = createAsyncThunk('kg/fetchReasoning', async (missionId: string) => {
  const response = await axios.get(`/api/v1/kg/reasoning/${missionId}`)
  return response.data as GNNReasoning
})

export const fetchUnits = createAsyncThunk('kg/fetchUnits', async () => {
  const response = await axios.get(`/api/v1/gis/graph?label=Unit`)
  return response.data.nodes as GraphNode[]
})

const kgSlice = createSlice({
  name: 'kg',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchGNNReasoning.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchGNNReasoning.fulfilled, (state, action) => {
        state.loading = false
        state.reasoning = action.payload
      })
      .addCase(fetchGNNReasoning.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Failed to fetch reasoning'
      })
      .addCase(fetchUnits.fulfilled, (state, action) => {
        state.units = action.payload
      })
  },
})

export default kgSlice.reducer
