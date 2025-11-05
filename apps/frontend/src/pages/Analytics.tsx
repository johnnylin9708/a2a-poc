import { useQuery } from '@tanstack/react-query'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  CheckCircle, 
  DollarSign, 
  Star,
  Activity,
  Zap
} from 'lucide-react'

export default function Analytics() {
  // Fetch ecosystem health
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['ecosystem-health'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/analytics/ecosystem/health')
      if (!res.ok) throw new Error('Failed to fetch ecosystem health')
      return res.json()
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch trending agents
  const { data: trendingData, isLoading: trendingLoading } = useQuery({
    queryKey: ['trending-agents'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/analytics/agents/trending?days=7&limit=10')
      if (!res.ok) throw new Error('Failed to fetch trending agents')
      return res.json()
    },
  })

  // Fetch category insights
  const { data: categoryData, isLoading: categoryLoading } = useQuery({
    queryKey: ['category-insights'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:8000/api/v1/analytics/categories/insights')
      if (!res.ok) throw new Error('Failed to fetch category insights')
      return res.json()
    },
  })

  const isLoading = healthLoading || trendingLoading || categoryLoading

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
        <p className="mt-4 text-muted-foreground">Loading analytics...</p>
      </div>
    )
  }

  const health = healthData
  const trending = trendingData?.trending_agents || []
  const categories = categoryData?.categories || []

  // Calculate health score color
  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getHealthBg = (score: number) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Ecosystem Analytics</h1>
          <p className="text-muted-foreground">
            Real-time insights into the A2A agent ecosystem
          </p>
        </div>
        <div className="text-sm text-muted-foreground">
          Last updated: {health ? new Date(health.timestamp).toLocaleString() : 'N/A'}
        </div>
      </div>

      {/* Health Score */}
      {health && (
        <div className={`${getHealthBg(health.health_score)} rounded-lg p-6 mb-8`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Ecosystem Health Score</h2>
              <p className="text-sm text-muted-foreground">
                Composite metric based on activity, task completion, and reputation
              </p>
            </div>
            <div className={`text-6xl font-bold ${getHealthColor(health.health_score)}`}>
              {health.health_score}
              <span className="text-2xl">/100</span>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics Grid */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Agents */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold">Total Agents</h3>
            </div>
            <p className="text-3xl font-bold mb-2">{health.agents.total}</p>
            <p className="text-sm text-muted-foreground">
              {health.agents.active_24h} active (last 24h)
            </p>
            <div className="mt-2 text-xs text-green-600">
              +{health.agents.new_7d} this week
            </div>
          </div>

          {/* Tasks */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold">Tasks</h3>
            </div>
            <p className="text-3xl font-bold mb-2">{health.tasks.total}</p>
            <p className="text-sm text-muted-foreground">
              {health.tasks.completed} completed
            </p>
            <div className="mt-2 text-xs text-green-600">
              {health.tasks.completion_rate.toFixed(1)}% completion rate
            </div>
          </div>

          {/* Reputation */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Star className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="font-semibold">Reputation</h3>
            </div>
            <p className="text-3xl font-bold mb-2">{health.reputation.average}</p>
            <p className="text-sm text-muted-foreground">
              {health.reputation.total_feedback} total reviews
            </p>
            <div className="mt-2 text-xs text-muted-foreground">
              {health.reputation.feedback_7d} this week
            </div>
          </div>

          {/* Payments */}
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold">Payments</h3>
            </div>
            <p className="text-3xl font-bold mb-2">{health.payments.total}</p>
            <p className="text-sm text-muted-foreground">
              Total transactions
            </p>
            <div className="mt-2 text-xs text-muted-foreground">
              {health.payments.payments_30d} last 30 days
            </div>
          </div>
        </div>
      )}

      {/* Trending Agents & Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Trending Agents */}
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Trending Agents</h2>
          </div>
          {trending.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No trending agents yet</p>
          ) : (
            <div className="space-y-3">
              {trending.map((agent: any, idx: number) => (
                <div
                  key={agent.token_id}
                  className="flex items-center gap-3 p-3 bg-secondary/50 rounded-lg hover:bg-secondary transition-colors"
                >
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-primary text-primary-foreground rounded-full font-bold">
                    {idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium truncate">{agent.name}</h3>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        {agent.recent_tasks} tasks
                      </span>
                      <span className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        {agent.reputation.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-xs text-green-600 font-medium">
                    🔥 {agent.trending_score.toFixed(0)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Categories */}
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Top Categories</h2>
          </div>
          {categories.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No category data yet</p>
          ) : (
            <div className="space-y-3">
              {categories.slice(0, 10).map((category: any) => (
                <div key={category.category} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{category.category}</span>
                    <span className="text-muted-foreground">
                      {category.agent_count} agents
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-secondary rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-primary h-full transition-all"
                        style={{
                          width: `${Math.min((category.total_tasks / 100) * 100, 100)}%`,
                        }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground min-w-[60px] text-right">
                      {category.total_tasks} tasks
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    <span>{category.average_reputation.toFixed(1)} avg rating</span>
                    <span className="mx-1">•</span>
                    <span>{category.avg_tasks_per_agent.toFixed(1)} tasks/agent</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Activity Breakdown */}
      {health && (
        <div className="bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Activity Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Agent Activity */}
            <div>
              <h3 className="font-medium mb-3 text-sm text-muted-foreground">
                Agent Activity Rate
              </h3>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block text-primary">
                      {health.agents.activity_rate.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-secondary">
                  <div
                    style={{ width: `${health.agents.activity_rate}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary transition-all"
                  />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                {health.agents.active_24h} of {health.agents.total} agents active in last 24h
              </p>
            </div>

            {/* Task Completion */}
            <div>
              <h3 className="font-medium mb-3 text-sm text-muted-foreground">
                Task Completion Rate
              </h3>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block text-green-600">
                      {health.tasks.completion_rate.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-secondary">
                  <div
                    style={{ width: `${health.tasks.completion_rate}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-600 transition-all"
                  />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                {health.tasks.completed} of {health.tasks.total} tasks completed
              </p>
            </div>

            {/* Reputation Quality */}
            <div>
              <h3 className="font-medium mb-3 text-sm text-muted-foreground">
                Average Reputation
              </h3>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block text-yellow-600">
                      {health.reputation.average.toFixed(1)}/5.0
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-secondary">
                  <div
                    style={{ width: `${(health.reputation.average / 5) * 100}%` }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-yellow-600 transition-all"
                  />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Based on {health.reputation.total_feedback} reviews
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

