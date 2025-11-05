/**
 * Custom hooks for Reputation Registry contract interactions
 */

import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { contracts } from '@/lib/contracts'

/**
 * Get agent reputation score
 */
export function useReputationScore(agentId: number | undefined) {
  const { data, isLoading, refetch } = useReadContract({
    ...contracts.reputationRegistry,
    functionName: 'getReputationScore',
    args: agentId !== undefined ? [BigInt(agentId)] : undefined,
    query: {
      enabled: agentId !== undefined,
    },
  })

  // Convert score from 0-500 to 0.0-5.0
  const averageRating = data ? Number(data[0]) / 100 : 0
  const feedbackCount = data ? Number(data[1]) : 0

  return {
    averageRating,
    feedbackCount,
    isLoading,
    refetch,
  }
}

/**
 * Submit feedback for an agent
 */
export function useSubmitFeedback() {
  const { data: hash, writeContract, isPending, isError, error } = useWriteContract()

  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash,
  })

  const submitFeedback = async (
    agentId: number,
    rating: number, // 1-5
    comment: string,
    paymentProof: string
  ) => {
    // Convert payment proof string to bytes32
    const paymentProofBytes = paymentProof.startsWith('0x') 
      ? paymentProof 
      : `0x${paymentProof}`

    writeContract({
      ...contracts.reputationRegistry,
      functionName: 'submitFeedback',
      args: [
        BigInt(agentId),
        rating,
        comment,
        paymentProofBytes as `0x${string}`,
      ],
    })
  }

  return {
    submitFeedback,
    hash,
    isPending,
    isConfirming,
    isConfirmed,
    isError,
    error,
  }
}

