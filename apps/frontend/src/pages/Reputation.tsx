import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAccount } from 'wagmi'
import { Star, Trophy, Award, Loader2 } from 'lucide-react'
import { agentApi } from '@/lib/api'
import { useSubmitFeedback } from '@/hooks/useReputation'

export default function Reputation() {
  const { address, isConnected } = useAccount()
  const [activeTab, setActiveTab] = useState<'leaderboard' | 'submit'>('leaderboard')

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Reputation System</h1>
        <p className="text-muted-foreground">
          Track agent performance and submit feedback based on completed tasks
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`px-6 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'leaderboard'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-primary'
          }`}
        >
          <div className="flex items-center gap-2">
            <Trophy className="w-4 h-4" />
            Leaderboard
          </div>
        </button>
        <button
          onClick={() => setActiveTab('submit')}
          className={`px-6 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'submit'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-primary'
          }`}
        >
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4" />
            Submit Feedback
          </div>
        </button>
      </div>

      {activeTab === 'leaderboard' && <LeaderboardTab />}
      {activeTab === 'submit' && <SubmitFeedbackTab isConnected={isConnected} address={address} />}
    </div>
  )
}

function LeaderboardTab() {
  const { data, isLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => fetch('http://127.0.0.1:8000/api/v1/reputation/leaderboard/top')
      .then(res => res.json()),
  })

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-8 h-8 animate-spin mx-auto" />
        <p className="mt-4 text-muted-foreground">Loading leaderboard...</p>
      </div>
    )
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Platinum': return 'bg-purple-100 text-purple-700'
      case 'Gold': return 'bg-yellow-100 text-yellow-700'
      case 'Silver': return 'bg-gray-100 text-gray-700'
      case 'Bronze': return 'bg-orange-100 text-orange-700'
      default: return 'bg-blue-100 text-blue-700'
    }
  }

  return (
    <div className="bg-card rounded-lg border overflow-hidden">
      <table className="w-full">
        <thead className="bg-secondary">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-medium">Rank</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Agent</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Rating</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Reviews</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Tier</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Capabilities</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data?.leaderboard?.map((agent: any) => (
            <tr key={agent.token_id} className="hover:bg-secondary/50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  {agent.rank === 1 && <Trophy className="w-5 h-5 text-yellow-500" />}
                  {agent.rank === 2 && <Trophy className="w-5 h-5 text-gray-400" />}
                  {agent.rank === 3 && <Trophy className="w-5 h-5 text-orange-400" />}
                  <span className="font-semibold">#{agent.rank}</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div>
                  <p className="font-medium">{agent.name}</p>
                  <p className="text-sm text-muted-foreground">ID: {agent.token_id}</p>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="font-semibold">{agent.reputation_score.toFixed(2)}</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="text-muted-foreground">{agent.feedback_count}</span>
              </td>
              <td className="px-6 py-4">
                <span className={`px-2 py-1 text-xs rounded-full ${getTierColor(agent.reputation_tier)}`}>
                  {agent.reputation_tier}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex gap-1">
                  {agent.capabilities.map((cap: string) => (
                    <span
                      key={cap}
                      className="px-2 py-1 bg-primary/10 text-primary text-xs rounded"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {!data?.leaderboard?.length && (
        <div className="text-center py-12 text-muted-foreground">
          No agents in leaderboard yet
        </div>
      )}
    </div>
  )
}

function SubmitFeedbackTab({ isConnected, address }: { isConnected: boolean, address?: string }) {
  const { submitFeedback, isPending, isConfirming, isConfirmed, hash } = useSubmitFeedback()
  const [formData, setFormData] = useState({
    agentId: '',
    rating: 5,
    comment: '',
    paymentProof: '',
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!isConnected) {
      setError('Please connect your wallet first')
      return
    }

    try {
      await submitFeedback(
        parseInt(formData.agentId),
        formData.rating,
        formData.comment,
        formData.paymentProof
      )
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback')
    }
  }

  if (isConfirmed && hash) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="text-green-600 text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-green-900 mb-2">
          Feedback Submitted Successfully!
        </h2>
        <p className="text-green-700 mb-4">
          Your feedback has been recorded on the blockchain.
        </p>
        <div className="text-sm text-gray-600 mb-4">
          <p className="font-mono break-all">Transaction: {hash}</p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Submit Another
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      {!isConnected && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            Please connect your wallet to submit feedback.
          </p>
        </div>
      )}

      <div className="bg-card rounded-lg border p-6">
        <h2 className="text-xl font-semibold mb-4">Submit Agent Feedback</h2>
        <p className="text-sm text-muted-foreground mb-6">
          Provide feedback after completing a task with an agent. You must provide a valid x402 payment proof.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Agent ID *</label>
            <input
              type="number"
              value={formData.agentId}
              onChange={(e) => setFormData({ ...formData, agentId: e.target.value })}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="e.g., 123"
              required
              disabled={isPending || isConfirming}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Rating (1-5 stars) *</label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="5"
                value={formData.rating}
                onChange={(e) => setFormData({ ...formData, rating: parseInt(e.target.value) })}
                className="flex-1"
                disabled={isPending || isConfirming}
              />
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < formData.rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
                <span className="ml-2 font-semibold">{formData.rating}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Comment *</label>
            <textarea
              value={formData.comment}
              onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
              className="w-full px-4 py-2 border rounded-md h-24"
              placeholder="Share your experience with this agent..."
              required
              disabled={isPending || isConfirming}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Payment Proof (x402) *</label>
            <input
              type="text"
              value={formData.paymentProof}
              onChange={(e) => setFormData({ ...formData, paymentProof: e.target.value })}
              className="w-full px-4 py-2 border rounded-md font-mono text-sm"
              placeholder="0x..."
              required
              disabled={isPending || isConfirming}
            />
            <p className="text-xs text-muted-foreground mt-1">
              32-byte hash from your payment transaction
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {(isPending || isConfirming) && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <p className="text-blue-800">
                  {isPending && 'Waiting for wallet confirmation...'}
                  {isConfirming && 'Transaction confirming on blockchain...'}
                </p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={!isConnected || isPending || isConfirming}
            className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {(isPending || isConfirming) && <Loader2 className="w-4 h-4 animate-spin" />}
            {isPending ? 'Confirm in Wallet...' : 
             isConfirming ? 'Confirming...' :
             'Submit Feedback'}
          </button>
        </form>
      </div>
    </div>
  )
}
