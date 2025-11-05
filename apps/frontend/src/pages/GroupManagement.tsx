import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAccount } from 'wagmi'
import { Plus, Users, Trash2, UserPlus, Send, Loader2 } from 'lucide-react'

interface Group {
  group_id: string
  name: string
  description: string
  admin_address: string
  member_agents: number[]
  collaboration_rules: any
  created_at: string
  updated_at: string
}

interface Agent {
  token_id: number
  name: string
  capabilities: string[]
  reputation_score: number
}

export default function GroupManagement() {
  const { address, isConnected } = useAccount()
  const queryClient = useQueryClient()
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null)
  const [isAddAgentModalOpen, setIsAddAgentModalOpen] = useState(false)
  const [isDelegateTaskModalOpen, setIsDelegateTaskModalOpen] = useState(false)

  // Fetch groups
  const { data: groupsData, isLoading: isLoadingGroups } = useQuery({
    queryKey: ['groups'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/groups/')
      if (!res.ok) throw new Error('Failed to fetch groups')
      return res.json()
    },
  })

  // Fetch available agents
  const { data: agentsData } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/agents/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ capabilities: [], min_reputation: 0 }),
      })
      if (!res.ok) throw new Error('Failed to fetch agents')
      return res.json()
    },
  })

  // Create group mutation
  const createGroupMutation = useMutation({
    mutationFn: async (data: {
      name: string
      description: string
      initial_agents: number[]
    }) => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/groups/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          admin_address: address,
        }),
      })
      if (!res.ok) throw new Error('Failed to create group')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      setIsCreateModalOpen(false)
    },
  })

  // Add agent to group mutation
  const addAgentMutation = useMutation({
    mutationFn: async ({ groupId, agentId }: { groupId: string; agentId: number }) => {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/groups/${groupId}/add-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId }),
      })
      if (!res.ok) throw new Error('Failed to add agent')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      setIsAddAgentModalOpen(false)
    },
  })

  // Remove agent from group mutation
  const removeAgentMutation = useMutation({
    mutationFn: async ({ groupId, agentId }: { groupId: string; agentId: number }) => {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/groups/${groupId}/remove-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId }),
      })
      if (!res.ok) throw new Error('Failed to remove agent')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })

  // Delegate task to group mutation
  const delegateTaskMutation = useMutation({
    mutationFn: async ({ groupId, task }: { groupId: string; task: any }) => {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/groups/${groupId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
      })
      if (!res.ok) throw new Error('Failed to delegate task')
      return res.json()
    },
    onSuccess: () => {
      setIsDelegateTaskModalOpen(false)
      alert('Task delegated successfully!')
    },
  })

  const groups = groupsData?.groups || []
  const agents = agentsData?.agents || []

  if (!isConnected) {
    return (
      <div className="text-center py-12">
        <Users className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h2 className="text-2xl font-bold mb-2">Connect Your Wallet</h2>
        <p className="text-muted-foreground">
          Please connect your wallet to manage agent groups
        </p>
      </div>
    )
  }

  if (isLoadingGroups) {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Loading groups...</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Group Management</h1>
          <p className="text-muted-foreground">
            Create and manage agent groups for collaborative tasks
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          Create Group
        </button>
      </div>

      {groups.length === 0 ? (
        <div className="bg-card border rounded-lg p-12 text-center">
          <Users className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-xl font-semibold mb-2">No Groups Yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first group to start collaborating with agents
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Create First Group
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {groups.map((group: Group) => (
            <div key={group.group_id} className="bg-card border rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold mb-1">{group.name}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{group.description}</p>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{group.member_agents.length} agents</span>
                    <span>•</span>
                    <span>Created {new Date(group.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setSelectedGroup(group)
                      setIsAddAgentModalOpen(true)
                    }}
                    className="p-2 hover:bg-muted rounded-md"
                    title="Add Agent"
                  >
                    <UserPlus className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      setSelectedGroup(group)
                      setIsDelegateTaskModalOpen(true)
                    }}
                    className="p-2 hover:bg-muted rounded-md"
                    title="Delegate Task"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {group.member_agents.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="text-sm font-semibold mb-3">Member Agents</h4>
                  <div className="space-y-2">
                    {group.member_agents.map((agentId: number) => {
                      const agent = agents.find((a: Agent) => a.token_id === agentId)
                      return (
                        <div
                          key={agentId}
                          className="flex justify-between items-center p-3 bg-muted/50 rounded-md"
                        >
                          <div>
                            <span className="font-medium">
                              {agent?.name || `Agent #${agentId}`}
                            </span>
                            {agent && (
                              <div className="flex gap-1 mt-1">
                                {agent.capabilities.slice(0, 3).map((cap: string) => (
                                  <span
                                    key={cap}
                                    className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded"
                                  >
                                    {cap}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => {
                              if (confirm('Remove this agent from the group?')) {
                                removeAgentMutation.mutate({
                                  groupId: group.group_id,
                                  agentId,
                                })
                              }
                            }}
                            className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 rounded-md"
                            title="Remove Agent"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create Group Modal */}
      {isCreateModalOpen && (
        <CreateGroupModal
          agents={agents}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={(data) => createGroupMutation.mutate(data)}
          isLoading={createGroupMutation.isPending}
        />
      )}

      {/* Add Agent Modal */}
      {isAddAgentModalOpen && selectedGroup && (
        <AddAgentModal
          group={selectedGroup}
          agents={agents.filter((a: Agent) => !selectedGroup.member_agents.includes(a.token_id))}
          onClose={() => setIsAddAgentModalOpen(false)}
          onSubmit={(agentId) =>
            addAgentMutation.mutate({ groupId: selectedGroup.group_id, agentId })
          }
          isLoading={addAgentMutation.isPending}
        />
      )}

      {/* Delegate Task Modal */}
      {isDelegateTaskModalOpen && selectedGroup && (
        <DelegateTaskModal
          group={selectedGroup}
          onClose={() => setIsDelegateTaskModalOpen(false)}
          onSubmit={(task) =>
            delegateTaskMutation.mutate({ groupId: selectedGroup.group_id, task })
          }
          isLoading={delegateTaskMutation.isPending}
        />
      )}
    </div>
  )
}

function CreateGroupModal({
  agents,
  onClose,
  onSubmit,
  isLoading,
}: {
  agents: Agent[]
  onClose: () => void
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedAgents, setSelectedAgents] = useState<number[]>([])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ name, description, initial_agents: selectedAgents })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-2xl font-bold mb-4">Create New Group</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Group Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="Development Team"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows={3}
              placeholder="A team of specialized agents for development tasks"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Initial Agents (Optional)
            </label>
            <div className="max-h-48 overflow-y-auto space-y-2">
              {agents.map((agent: Agent) => (
                <label
                  key={agent.token_id}
                  className="flex items-center gap-3 p-3 border rounded-md hover:bg-muted/50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedAgents.includes(agent.token_id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAgents([...selectedAgents, agent.token_id])
                      } else {
                        setSelectedAgents(selectedAgents.filter((id) => id !== agent.token_id))
                      }
                    }}
                    className="rounded"
                  />
                  <div className="flex-1">
                    <div className="font-medium">{agent.name}</div>
                    <div className="flex gap-1 mt-1">
                      {agent.capabilities.slice(0, 3).map((cap: string) => (
                        <span
                          key={cap}
                          className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded"
                        >
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border rounded-md hover:bg-muted"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? 'Creating...' : 'Create Group'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function AddAgentModal({
  group,
  agents,
  onClose,
  onSubmit,
  isLoading,
}: {
  group: Group
  agents: Agent[]
  onClose: () => void
  onSubmit: (agentId: number) => void
  isLoading: boolean
}) {
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border rounded-lg max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Add Agent to {group.name}</h2>
        <div className="max-h-96 overflow-y-auto space-y-2 mb-4">
          {agents.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              All available agents are already in this group
            </p>
          ) : (
            agents.map((agent: Agent) => (
              <label
                key={agent.token_id}
                className="flex items-center gap-3 p-3 border rounded-md hover:bg-muted/50 cursor-pointer"
              >
                <input
                  type="radio"
                  name="agent"
                  checked={selectedAgent === agent.token_id}
                  onChange={() => setSelectedAgent(agent.token_id)}
                  className="rounded-full"
                />
                <div className="flex-1">
                  <div className="font-medium">{agent.name}</div>
                  <div className="flex gap-1 mt-1">
                    {agent.capabilities.slice(0, 3).map((cap: string) => (
                      <span
                        key={cap}
                        className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </label>
            ))
          )}
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 border rounded-md hover:bg-muted"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            onClick={() => selectedAgent && onSubmit(selectedAgent)}
            className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
            disabled={!selectedAgent || isLoading}
          >
            {isLoading ? 'Adding...' : 'Add Agent'}
          </button>
        </div>
      </div>
    </div>
  )
}

function DelegateTaskModal({
  group,
  onClose,
  onSubmit,
  isLoading,
}: {
  group: Group
  onClose: () => void
  onSubmit: (task: any) => void
  isLoading: boolean
}) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [capability, setCapability] = useState('')
  const [priority, setPriority] = useState(1)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      title,
      description,
      required_capability: capability,
      priority,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border rounded-lg max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Delegate Task to {group.name}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Task Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="Implement user authentication"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows={4}
              placeholder="Detailed task requirements..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Required Capability</label>
            <input
              type="text"
              value={capability}
              onChange={(e) => setCapability(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="coding"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Priority (1-5)
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value={1}>1 - Low</option>
              <option value={2}>2</option>
              <option value={3}>3 - Medium</option>
              <option value={4}>4</option>
              <option value={5}>5 - High</option>
            </select>
          </div>
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border rounded-md hover:bg-muted"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? 'Delegating...' : 'Delegate Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
