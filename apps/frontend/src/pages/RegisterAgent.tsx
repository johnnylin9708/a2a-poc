import React, { useState } from 'react'
import { useAccount } from 'wagmi'
import { useNavigate } from 'react-router-dom'
import { Loader2, Plus, X } from 'lucide-react'
import { useRegisterAgent } from '@/hooks/useAgentRegistry'

export default function RegisterAgent() {
  const { address, isConnected } = useAccount()
  const navigate = useNavigate()
  const { registerAgent, isPending, isConfirming, isConfirmed, hash } = useRegisterAgent()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    endpoint: '',
  })
  const [capabilities, setCapabilities] = useState<string[]>([])
  const [newCapability, setNewCapability] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [syncError, setSyncError] = useState('')
  const [tokenId, setTokenId] = useState<number | null>(null)

  const handleAddCapability = () => {
    if (newCapability.trim() && !capabilities.includes(newCapability.trim())) {
      setCapabilities([...capabilities, newCapability.trim()])
      setNewCapability('')
    }
  }

  const handleRemoveCapability = (index: number) => {
    setCapabilities(capabilities.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!isConnected) {
      setError('Please connect your wallet first')
      return
    }

    if (capabilities.length === 0) {
      setError('Please add at least one capability')
      return
    }

    try {
      setIsUploading(true)

      // Step 1: Prepare metadata for IPFS
      const metadata = {
        name: formData.name,
        description: formData.description,
        capabilities,
        endpoint: formData.endpoint,
        version: '1.0',
        created_at: new Date().toISOString(),
      }

      // Step 2: Upload metadata to IPFS via backend
      const uploadResponse = await fetch('http://127.0.0.1:8000/api/v1/ipfs/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metadata),
      })

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload metadata to IPFS')
      }

      const { ipfs_uri } = await uploadResponse.json()
      console.log('Metadata uploaded to IPFS:', ipfs_uri)

      setIsUploading(false)

      // Step 3: Register agent on blockchain via wallet
      await registerAgent(
        formData.name,
        formData.description,
        capabilities,
        formData.endpoint,
        ipfs_uri
      )
    } catch (err: any) {
      console.error('Registration error:', err)
      setError(err.message || 'Failed to register agent')
      setIsUploading(false)
    }
  }

  // Sync agent to database after confirmation
  React.useEffect(() => {
    if (isConfirmed && hash && !syncing && !tokenId && !syncError) {
      setSyncing(true)
      fetch('http://127.0.0.1:8000/api/v1/agents/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_hash: hash }),
      })
        .then(res => res.json())
        .then(data => {
          console.log('Agent synced:', data)
          setTokenId(data.token_id)
          setSyncing(false)
        })
        .catch(err => {
          console.error('Failed to sync agent:', err)
          setSyncError(err.message)
          setSyncing(false)
        })
    }
  }, [isConfirmed, hash, syncing, tokenId, syncError])

  // If transaction is confirmed, show success
  if (isConfirmed && hash) {

    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <div className="text-green-600 text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-green-900 mb-2">
            Agent Registered Successfully!
          </h2>
          <p className="text-green-700 mb-4">
            Your agent has been registered on the blockchain.
          </p>
          <div className="text-sm text-gray-600 mb-4">
            <p className="font-mono break-all">Transaction: {hash}</p>
            {tokenId && <p className="mt-2">Token ID: #{tokenId}</p>}
          </div>
          
          {syncing ? (
            <div className="flex items-center justify-center gap-2 text-blue-700">
              <div className="animate-spin w-4 h-4 border-2 border-blue-700 border-t-transparent rounded-full" />
              <span>Syncing to database...</span>
            </div>
          ) : syncError ? (
            <div className="mb-4 text-red-700">
              <p>Sync failed: {syncError}</p>
              <p className="text-sm mt-2">But your agent is on the blockchain!</p>
            </div>
          ) : null}
          
          <div className="flex gap-4 justify-center mt-4">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              disabled={syncing}
            >
              View All Agents
            </button>
            {tokenId && (
              <button
                onClick={() => navigate(`/agents/${tokenId}`)}
                className="px-6 py-2 border border-primary text-primary rounded-md hover:bg-primary/10"
              >
                View Agent Details
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-4xl font-bold mb-2">Register New Agent</h1>
      <p className="text-muted-foreground mb-8">
        Create a new AI agent identity on the blockchain. This will mint an ERC-721 NFT.
      </p>

      {!isConnected && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-yellow-800">
            Please connect your wallet to register an agent.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-card rounded-lg border p-6 space-y-4">
          <h2 className="text-xl font-semibold mb-4">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">Agent Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="e.g., Code Generator Agent"
              required
              disabled={isUploading || isPending || isConfirming}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description *</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border rounded-md h-24"
              placeholder="Describe what your agent does..."
              required
              disabled={isUploading || isPending || isConfirming}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Endpoint URL *</label>
            <input
              type="url"
              value={formData.endpoint}
              onChange={(e) => setFormData({ ...formData, endpoint: e.target.value })}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="https://your-agent.example.com/a2a"
              required
              disabled={isUploading || isPending || isConfirming}
            />
            <p className="text-xs text-muted-foreground mt-1">
              The A2A protocol endpoint where your agent can receive tasks
            </p>
          </div>
        </div>

        {/* Capabilities */}
        <div className="bg-card rounded-lg border p-6 space-y-4">
          <h2 className="text-xl font-semibold mb-4">Capabilities</h2>

          <div>
            <label className="block text-sm font-medium mb-2">Add Capabilities *</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newCapability}
                onChange={(e) => setNewCapability(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCapability())}
                className="flex-1 px-4 py-2 border rounded-md"
                placeholder="e.g., coding, testing, deployment"
                disabled={isUploading || isPending || isConfirming}
              />
              <button
                type="button"
                onClick={handleAddCapability}
                className="px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-md"
                disabled={isUploading || isPending || isConfirming}
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {capabilities.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {capabilities.map((cap, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary rounded-full"
                >
                  {cap}
                  <button
                    type="button"
                    onClick={() => handleRemoveCapability(index)}
                    className="hover:text-primary/70"
                    disabled={isUploading || isPending || isConfirming}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Transaction Status */}
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

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!isConnected || isUploading || isPending || isConfirming}
          className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {(isUploading || isPending || isConfirming) && (
            <Loader2 className="w-4 h-4 animate-spin" />
          )}
          {isUploading ? 'Uploading to IPFS...' : 
           isPending ? 'Confirm in Wallet...' :
           isConfirming ? 'Confirming...' :
           'Register Agent'}
        </button>
      </form>
    </div>
  )
}
