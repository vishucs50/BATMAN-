import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import axios from 'axios'

export interface Mission {
  id: string
  mission_code: string
  mission_type: string
  status: 'PLANNING' | 'APPROVED' | 'EXECUTING' | 'COMPLETE' | 'ABORTED'
  classification: string
  created_at: string
  updated_at: string
}

interface MissionsState {
  list: Mission[]
  selected: Mission | null
  loading: boolean
  error: string | null
}

const initialState: MissionsState = {
  list: [],
  selected: null,
  loading: false,
  error: null,
}

export const fetchMissions = createAsyncThunk('missions/fetchAll', async () => {
  const response = await axios.get('/api/v1/missions')
  return response.data.missions as Mission[]
})

export const fetchMission = createAsyncThunk('missions/fetchOne', async (id: string) => {
  const response = await axios.get(`/api/v1/missions/${id}`)
  return response.data as Mission
})

const missionsSlice = createSlice({
  name: 'missions',
  initialState,
  reducers: {
    selectMission(state, action: PayloadAction<Mission | null>) {
      state.selected = action.payload
    },
    clearError(state) {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMissions.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchMissions.fulfilled, (state, action) => {
        state.loading = false
        state.list = action.payload
      })
      .addCase(fetchMissions.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message ?? 'Failed to fetch missions'
      })
      .addCase(fetchMission.fulfilled, (state, action) => {
        state.selected = action.payload
      })
  },
})

export const { selectMission, clearError } = missionsSlice.actions
export default missionsSlice.reducer
