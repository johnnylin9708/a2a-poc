/**
 * Custom hooks for Agent Identity Registry contract interactions
 */

import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { contracts, parseAgentCard, type AgentCard } from '@/lib/contracts'

/**
 * Read agent card from blockchain
 */
export function useAgentCard(tokenId: number | undefined) {
  const { data, isError, isLoading, refetch } = useReadContract({
    ...contracts.identityRegistry,
    functionName: 'getAgentCard',
    args: tokenId !== undefined ? [BigInt(tokenId)] : undefined,
    query: {
      enabled: tokenId !== undefined,
    },
  })

  const agentCard: AgentCard | null = data ? parseAgentCard(data) : null

  return {
    agentCard,
    isLoading,
    isError,
    refetch,
  }
}

/**
 * Get total number of registered agents
 */
export function useTotalAgents() {
  const { data, isLoading } = useReadContract({
    ...contracts.identityRegistry,
    functionName: 'totalAgents',
  })

  return {
    totalAgents: data ? Number(data) : 0,
    isLoading,
  }
}

/**
 * Register a new agent
 */
export function useRegisterAgent() {
  const { data: hash, writeContract, isPending, isError, error } = useWriteContract()

  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash,
  })

  const registerAgent = async (
    name: string,
    description: string,
    capabilities: string[],
    endpoint: string,
    metadataURI: string
  ) => {
    writeContract({
      ...contracts.identityRegistry,
      functionName: 'registerAgent',
      args: [name, description, capabilities, endpoint, metadataURI],
    })
  }

  return {
    registerAgent,
    hash,
    isPending,
    isConfirming,
    isConfirmed,
    isError,
    error,
  }
}

