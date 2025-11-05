import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Star, ExternalLink, Activity, CheckCircle, Clock, ArrowLeft, Send, MessageSquare } from 'lucide-react'
import { agentApi } from '@/lib/api'
import { useAgentCard } from '@/hooks/useAgentRegistry'
import { useReputationScore } from '@/hooks/useReputation'

export default function AgentDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const agentId = id ? parseInt(id) : undefined
  const [isDelegateModalOpen, setIsDelegateModalOpen] = useState(false)
  // Fetch from backend (off-chain cache)
  const { data: agent, isLoading: isLoadingAgent, error: agentError } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => agentApi.getAgent(agentId!),
    enabled: !!agentId,
    retry: 2,
    refetchOnWindowFocus: false,
  })

  // Fetch from blockchain (on-chain data)
  const { agentCard, isLoading: isLoadingCard } = useAgentCard(agentId)
  const { averageRating, feedbackCount, isLoading: isLoadingReputation } = useReputationScore(agentId)

  // Fetch agent feedback history
  const { data: feedbackData, isLoading: isLoadingFeedback } = useQuery({
    queryKey: ['agent-feedback', agentId],
    queryFn: () => fetch(`http://127.0.0.1:8000/api/v1/reputation/${agentId}/history?limit=10`)
      .then(res => res.json()),
    enabled: !!agentId,
  })

  // Fetch agent tasks
  const { data: tasksData } = useQuery({
    queryKey: ['agent-tasks', agentId],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/tasks/?agent_id=${agentId}&limit=5`)
      if (!res.ok) throw new Error('Failed to fetch tasks')
      return res.json()
    },
    enabled: !!agentId,
  })

  // Delegate task mutation
  const delegateTaskMutation = useMutation({
    mutationFn: async (taskData: any) => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/tasks/delegate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          task_data: taskData,
        }),
      })
      if (!res.ok) throw new Error('Failed to delegate task')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-tasks', agentId] })
      setIsDelegateModalOpen(false)
      alert('Task delegated successfully!')
    },
  })

  const isLoading = isLoadingAgent || isLoadingCard || isLoadingReputation
  const tasks = tasksData?.tasks || []

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
        <p className="mt-4 text-muted-foreground">Loading agent details...</p>
      </div>
    )
  }

  if (agentError) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-2">Error loading agent</p>
        <p className="text-sm text-muted-foreground mb-4">{agentError.message}</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          Back to Agents
        </button>
      </div>
    )
  }

  if (!agent && !agentCard) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Agent not found</p>
        <p className="text-sm text-muted-foreground mt-2">Agent ID: {agentId}</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          Back to Agents
        </button>
      </div>
    )
  }

  const displayAgent = agent || agentCard

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-muted-foreground hover:text-primary mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Agents
      </button>

      {/* Header */}
      <div className="bg-card rounded-lg border p-8 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">{displayAgent?.name}</h1>
            <p className="text-sm text-muted-foreground">Agent ID: #{agentId}</p>
          </div>
          {displayAgent?.is_active !== false && (
            <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
              Active
            </span>
          )}
        </div>

        <p className="text-muted-foreground mb-6">{displayAgent?.description}</p>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-secondary/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-yellow-600 mb-1">
              <Star className="w-4 h-4 fill-current" />
              <span className="text-2xl font-bold">
                {averageRating.toFixed(1)}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              {feedbackCount} reviews
            </p>
          </div>

          <div className="bg-secondary/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-600 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-2xl font-bold">
                {agent?.total_tasks || 0}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">Total tasks</p>
          </div>

          <div className="bg-secondary/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-green-600 mb-1">
              <CheckCircle className="w-4 h-4" />
              <span className="text-2xl font-bold">
                {agent?.completed_tasks || 0}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">Completed</p>
          </div>

          <div className="bg-secondary/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-2xl font-bold">
                {agent?.created_at ? 
                  new Date(agent.created_at).toLocaleDateString() : 
                  'N/A'
                }
              </span>
            </div>
            <p className="text-xs text-muted-foreground">Joined</p>
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div className="bg-card rounded-lg border p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Capabilities</h2>
        <div className="flex flex-wrap gap-2">
          {(displayAgent?.capabilities || []).map((cap: string) => (
            <span
              key={cap}
              className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>

      {/* Technical Details */}
      <div className="bg-card rounded-lg border p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Technical Details</h2>
        <dl className="space-y-3">
          <div>
            <dt className="text-sm font-medium text-muted-foreground">Endpoint</dt>
            <dd className="mt-1 flex items-center gap-2">
              <code className="text-sm bg-secondary px-2 py-1 rounded">
                {displayAgent?.endpoint}
              </code>
              <a
                href={displayAgent?.endpoint}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </dd>
          </div>

          <div>
            <dt className="text-sm font-medium text-muted-foreground">Owner Address</dt>
            <dd className="mt-1">
              <code className="text-sm bg-secondary px-2 py-1 rounded">
                {displayAgent?.owner_address || agentCard?.owner}
              </code>
            </dd>
          </div>

          {displayAgent?.metadata_uri && (
            <div>
              <dt className="text-sm font-medium text-muted-foreground">Metadata URI</dt>
              <dd className="mt-1 flex items-center gap-2">
                <code className="text-sm bg-secondary px-2 py-1 rounded break-all">
                  {displayAgent.metadata_uri}
                </code>
                <a
                  href={displayAgent.metadata_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </dd>
            </div>
          )}
        </dl>
      </div>

      {/* Actions */}
      <div className="bg-card rounded-lg border p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div className="flex flex-wrap gap-4">
          <button 
            onClick={() => setIsDelegateModalOpen(true)}
            className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            <Send className="w-4 h-4" />
            Delegate Task
          </button>
          <button 
            onClick={() => navigate('/reputation')}
            className="px-6 py-2 border border-primary text-primary rounded-md hover:bg-primary/10"
          >
            Submit Feedback
          </button>
        </div>
      </div>

      {/* Recent Tasks */}
      {tasks.length > 0 && (
        <div className="bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Tasks</h2>
          <div className="space-y-3">
            {tasks.map((task: any) => (
              <div key={task.task_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium">{task.title}</h3>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      task.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : task.status === 'failed'
                        ? 'bg-red-100 text-red-700'
                        : task.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{task.description}</p>
                <p className="text-xs text-muted-foreground">
                  Created {new Date(task.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feedback History */}
      {!isLoadingFeedback && feedbackData?.feedbacks && feedbackData.feedbacks.length > 0 && (
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Feedback History</h2>
            <span className="text-sm text-muted-foreground">
              ({feedbackData.total} total)
            </span>
          </div>
          <div className="space-y-4">
            {feedbackData.feedbacks.map((feedback: any, index: number) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-secondary/50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {/* Star Rating */}
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < feedback.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="font-semibold text-sm">{feedback.rating}/5</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(feedback.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                {/* Comment */}
                <p className="text-sm mb-3">{feedback.comment}</p>
                
                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <span>From: {feedback.reviewer_address.slice(0, 6)}...{feedback.reviewer_address.slice(-4)}</span>
                  </div>
                  {feedback.tx_hash && (
                    <a
                      href={`https://etherscan.io/tx/${feedback.tx_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View on Chain
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Delegate Task Modal */}
      {isDelegateModalOpen && (
        <DelegateTaskModal
          agentName={displayAgent?.name}
          onClose={() => setIsDelegateModalOpen(false)}
          onSubmit={(taskData) => delegateTaskMutation.mutate(taskData)}
          isLoading={delegateTaskMutation.isPending}
        />
      )}
    </div>
  )
}

function DelegateTaskModal({
  agentName,
  onClose,
  onSubmit,
  isLoading,
}: {
  agentName?: string
  onClose: () => void
  onSubmit: (taskData: any) => void
  isLoading: boolean
}) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [taskType, setTaskType] = useState('general')
  const [priority, setPriority] = useState(3)
  const [deadline, setDeadline] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      title,
      description,
      task_type: taskType,
      priority,
      deadline: deadline || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border rounded-lg max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">
          Delegate Task to {agentName}
        </h2>
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
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Task Type</label>
              <select
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="general">General</option>
                <option value="coding">Coding</option>
                <option value="testing">Testing</option>
                <option value="debugging">Debugging</option>
                <option value="documentation">Documentation</option>
              </select>
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
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Deadline (Optional)
            </label>
            <input
              type="datetime-local"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            />
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
