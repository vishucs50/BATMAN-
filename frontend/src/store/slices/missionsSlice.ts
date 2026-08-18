import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import axios from 'axios'

export interface Objective {
  id: string
  mission_id: string
  obj_type: string
  priority: number
  status: string
  description?: string
  deadline?: string
}

export interface COA {
  id: string
  mission_id: string
  coa_number: number
  name: string
  style: string
  status: string
  utility_score: number
  explanation?: any
}

export interface Mission {
  id: string
  mission_code: string
  mission_type: string
  status: 'PLANNING' | 'APPROVED' | 'EXECUTING' | 'COMPLETE' | 'ABORTED'
  classification: string
  created_at: string
  updated_at: string
  objectives?: Objective[]
  coas?: COA[]
}

interface MissionsState {
  list: Mission[]
  selected: Mission | null
  coas: COA[]
  loading: boolean
  error: string | null
}

const initialState: MissionsState = {
  list: [],
  selected: null,
  coas: [],
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

export const createMission = createAsyncThunk('missions/create', async (mission: Partial<Mission>) => {
  const response = await axios.post('/api/v1/missions', mission)
  return response.data as Mission
})

export const createWhatIfBranch = createAsyncThunk(
  'missions/createWhatIfBranch',
  async ({ missionId, overrides }: { missionId: string, overrides: any }) => {
    const response = await axios.post(`/api/v1/missions/${missionId}/what-if`, overrides)
    return response.data as Mission
  }
)

export const fetchMissionCOAs = createAsyncThunk('missions/fetchCOAs', async (missionId: string) => {
  const response = await axios.get(`/api/v1/missions/${missionId}/coas`)
  return response.data as COA[]
})

export const generateCOAs = createAsyncThunk('missions/generateCOAs', async (missionId: string) => {
  const response = await axios.post(`/api/v1/missions/${missionId}/coas/generate`)
  return response.data as COA[]
})

export const approveCOA = createAsyncThunk('missions/approveCOA', async ({ missionId, coaId }: { missionId: string, coaId: string }) => {
  const response = await axios.post(`/api/v1/missions/${missionId}/coas/${coaId}/approve`)
  return response.data as COA
})

export const simulateCOA = createAsyncThunk('missions/simulateCOA', async ({ missionId, coaId }: { missionId: string, coaId: string }) => {
  const response = await axios.post(`/api/v1/missions/${missionId}/coas/${coaId}/simulate`)
  return response.data as COA
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
      .addCase(createMission.fulfilled, (state, action) => {
        state.list.unshift(action.payload)
        state.selected = action.payload
      })
      .addCase(createWhatIfBranch.fulfilled, (state, action) => {
        state.list.unshift(action.payload)
        state.selected = action.payload
        state.coas = []
      })
      .addCase(fetchMissionCOAs.fulfilled, (state, action) => {
        state.coas = action.payload
      })
      .addCase(generateCOAs.fulfilled, (state, action) => {
        state.coas = action.payload
      })
      .addCase(approveCOA.fulfilled, (state, action) => {
        const approved = action.payload
        const idx = state.coas.findIndex(c => c.id === approved.id)
        if (idx >= 0) state.coas[idx] = approved
        if (state.selected) state.selected.status = 'APPROVED'
      })
  },
})

export const { selectMission, clearError } = missionsSlice.actions
export default missionsSlice.reducer
