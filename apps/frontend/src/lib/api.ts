import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Agent {
  token_id: number
  name: string
  description: string
  capabilities: string[]
  endpoint: string
  metadata_uri: string
  owner_address: string
  created_at: string
  is_active: boolean
  reputation_score: number
  feedback_count: number
}

export interface Group {
  group_id: string
  name: string
  description: string
  admin_address: string
  member_agents: number[]
  collaboration_rules: any
  created_at: string
  updated_at: string
}

export const agentApi = {
  discoverAgents: async (params: {
    capability?: string
    min_reputation?: number
    is_active?: boolean
    limit?: number
    offset?: number
  }) => {
    const response = await api.post('/agents/discover', params)
    return response.data
  },

  getAgent: async (tokenId: number): Promise<Agent> => {
    const response = await api.get(`/agents/${tokenId}`)
    return response.data
  },

  registerAgent: async (data: any) => {
    const response = await api.post('/agents/register', data)
    return response.data
  },

  getAgentStatus: async (tokenId: number) => {
    const response = await api.get(`/agents/${tokenId}/status`)
    return response.data
  },
}

export const groupApi = {
  createGroup: async (data: {
    name: string
    description: string
    admin_address: string
    initial_agents: number[]
  }): Promise<Group> => {
    const response = await api.post('/groups/', data)
    return response.data
  },

  getGroup: async (groupId: string): Promise<Group> => {
    const response = await api.get(`/groups/${groupId}`)
    return response.data
  },

  listGroups: async (limit = 20, offset = 0) => {
    const response = await api.get('/groups/', { params: { limit, offset } })
    return response.data
  },

  addAgentToGroup: async (groupId: string, agentId: number) => {
    const response = await api.post(`/groups/${groupId}/add-agent`, { agent_id: agentId })
    return response.data
  },

  delegateTask: async (groupId: string, task: any) => {
    const response = await api.post(`/groups/${groupId}/tasks`, task)
    return response.data
  },
}

export const reputationApi = {
  getReputation: async (agentId: number) => {
    const response = await api.get(`/reputation/${agentId}`)
    return response.data
  },

  submitFeedback: async (data: any) => {
    const response = await api.post('/reputation/feedback', data)
    return response.data
  },
}

export default api

