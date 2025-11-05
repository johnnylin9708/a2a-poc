import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Star, ExternalLink, Activity, CheckCircle, Clock, ArrowLeft } from 'lucide-react'
import { agentApi } from '@/lib/api'
import { useAgentCard } from '@/hooks/useAgentRegistry'
import { useReputationScore } from '@/hooks/useReputation'

export default function AgentDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const agentId = id ? parseInt(id) : undefined
  // Fetch from backend (off-chain cache)
  const { data: agent, isLoading: isLoadingAgent, error: agentError } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => agentApi.getAgent(agentId!),
    enabled: !!agentId,
    retry: 2,
  })

  // Fetch from blockchain (on-chain data)
  const { agentCard, isLoading: isLoadingCard } = useAgentCard(agentId)
  const { averageRating, feedbackCount, isLoading: isLoadingReputation } = useReputationScore(agentId)

  const isLoading = isLoadingAgent || isLoadingCard || isLoadingReputation

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
      <div className="bg-card rounded-lg border p-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div className="flex flex-wrap gap-4">
          <button className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
            Delegate Task
          </button>
          <button 
            onClick={() => navigate('/reputation')}
            className="px-6 py-2 border border-primary text-primary rounded-md hover:bg-primary/10"
          >
            Submit Feedback
          </button>
          <button className="px-6 py-2 border rounded-md hover:bg-secondary">
            View History
          </button>
        </div>
      </div>
    </div>
  )
}
