import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { agentApi, reputationApi } from '@/lib/api'
import { Star, ExternalLink, Award, Activity } from 'lucide-react'

export default function AgentDetails() {
  const { tokenId } = useParams<{ tokenId: string }>()

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', tokenId],
    queryFn: () => agentApi.getAgent(Number(tokenId)),
    enabled: !!tokenId,
  })

  const { data: reputation } = useQuery({
    queryKey: ['reputation', tokenId],
    queryFn: () => reputationApi.getReputation(Number(tokenId)),
    enabled: !!tokenId,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!agent) {
    return <div className="text-center py-12">Agent not found</div>
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <h1 className="text-4xl font-bold">{agent.name}</h1>
          {agent.is_active && (
            <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
              Active
            </span>
          )}
        </div>
        <p className="text-muted-foreground">NFT Token ID: #{agent.token_id}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Description</h2>
            <p className="text-muted-foreground">{agent.description}</p>
          </div>

          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Capabilities</h2>
            <div className="flex flex-wrap gap-2">
              {agent.capabilities?.map((cap: string) => (
                <span
                  key={cap}
                  className="px-3 py-2 bg-primary/10 text-primary rounded-md"
                >
                  {cap}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Endpoint</h2>
            <a
              href={agent.endpoint}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-primary hover:underline"
            >
              {agent.endpoint}
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Stats Sidebar */}
        <div className="space-y-6">
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-2 mb-4">
              <Star className="w-5 h-5 text-yellow-400" />
              <h3 className="font-semibold">Reputation</h3>
            </div>
            <div className="text-3xl font-bold mb-2">
              {agent.reputation_score?.toFixed(2) || '0.00'}
            </div>
            <p className="text-sm text-muted-foreground">
              {agent.feedback_count || 0} reviews
            </p>
            {reputation && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  <span className="text-sm font-medium">
                    {reputation.reputation_tier}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5" />
              <h3 className="font-semibold">Statistics</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Total Tasks</span>
                <span className="font-medium">{agent.total_tasks || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Completed</span>
                <span className="font-medium text-green-600">{agent.completed_tasks || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Failed</span>
                <span className="font-medium text-red-600">{agent.failed_tasks || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-card rounded-lg border p-6">
            <h3 className="font-semibold mb-4">Owner</h3>
            <p className="text-sm text-muted-foreground break-all">
              {agent.owner_address}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

