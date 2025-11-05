import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { agentApi } from '@/lib/api'
import { Search, Star, ExternalLink } from 'lucide-react'

export default function Dashboard() {
  const [searchCapability, setSearchCapability] = useState('')
  const [minReputation, setMinReputation] = useState(0)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['agents', searchCapability, minReputation],
    queryFn: () => agentApi.discoverAgents({
      capability: searchCapability || undefined,
      min_reputation: minReputation,
      limit: 20,
      offset: 0,
    }),
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Agent Dashboard</h1>
        <p className="text-muted-foreground">
          Discover and interact with AI agents in the ecosystem
        </p>
      </div>

      {/* Search and Filter */}
      <div className="bg-card rounded-lg border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-2">
              Search by Capability
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="e.g. coding, testing, deployment"
                value={searchCapability}
                onChange={(e) => setSearchCapability(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-md"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Min Reputation
            </label>
            <select
              value={minReputation}
              onChange={(e) => setMinReputation(Number(e.target.value))}
              className="w-full px-4 py-2 border rounded-md"
            >
              <option value={0}>All Agents</option>
              <option value={3.0}>3.0+ Stars</option>
              <option value={4.0}>4.0+ Stars</option>
              <option value={4.5}>4.5+ Stars</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={() => refetch()}
          className="mt-4 px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Search
        </button>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading agents...</p>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">
              Found {data?.total || 0} agents
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.agents?.map((agent: any) => (
              <Link
                key={agent.token_id}
                to={`/agents/${agent.token_id}`}
                className="bg-card rounded-lg border p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      NFT #{agent.token_id}
                    </p>
                  </div>
                  {agent.is_active && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                      Active
                    </span>
                  )}
                </div>

                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {agent.description}
                </p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {agent.capabilities?.slice(0, 3).map((cap: string) => (
                    <span
                      key={cap}
                      className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded"
                    >
                      {cap}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">
                      {agent.reputation_score?.toFixed(2) || '0.00'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      ({agent.feedback_count || 0})
                    </span>
                  </div>
                  <ExternalLink className="w-4 h-4 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </div>

          {!data?.agents?.length && (
            <div className="text-center py-12 bg-card rounded-lg border">
              <p className="text-muted-foreground">No agents found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

