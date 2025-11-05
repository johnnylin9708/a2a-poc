/**
 * Contract ABIs and helper functions
 */

import { contractAddresses } from './wagmi.config'

// Contract ABIs (simplified - you can import full ABIs from artifacts)
export const AgentIdentityRegistryABI = [
  {
    "inputs": [
      { "internalType": "string", "name": "name", "type": "string" },
      { "internalType": "string", "name": "description", "type": "string" },
      { "internalType": "string[]", "name": "capabilities", "type": "string[]" },
      { "internalType": "string", "name": "endpoint", "type": "string" },
      { "internalType": "string", "name": "metadataURI", "type": "string" }
    ],
    "name": "registerAgent",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "tokenId", "type": "uint256" }],
    "name": "getAgentCard",
    "outputs": [
      { "internalType": "string", "name": "name", "type": "string" },
      { "internalType": "string", "name": "description", "type": "string" },
      { "internalType": "string[]", "name": "capabilities", "type": "string[]" },
      { "internalType": "string", "name": "endpoint", "type": "string" },
      { "internalType": "string", "name": "metadataURI", "type": "string" },
      { "internalType": "uint256", "name": "createdAt", "type": "uint256" },
      { "internalType": "bool", "name": "isActive", "type": "bool" },
      { "internalType": "address", "name": "owner", "type": "address" }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalAgents",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  }
] as const

export const ReputationRegistryABI = [
  {
    "inputs": [
      { "internalType": "uint256", "name": "agentId", "type": "uint256" },
      { "internalType": "uint8", "name": "rating", "type": "uint8" },
      { "internalType": "string", "name": "comment", "type": "string" },
      { "internalType": "bytes32", "name": "paymentProof", "type": "bytes32" }
    ],
    "name": "submitFeedback",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "agentId", "type": "uint256" }],
    "name": "getReputationScore",
    "outputs": [
      { "internalType": "uint256", "name": "averageRating", "type": "uint256" },
      { "internalType": "uint256", "name": "feedbackCount", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const

export const ValidationRegistryABI = [
  {
    "inputs": [{ "internalType": "uint256", "name": "agentId", "type": "uint256" }],
    "name": "getValidationStats",
    "outputs": [
      { "internalType": "uint256", "name": "totalValidations", "type": "uint256" },
      { "internalType": "uint256", "name": "passedValidations", "type": "uint256" },
      { "internalType": "uint256", "name": "failedValidations", "type": "uint256" },
      { "internalType": "uint256", "name": "lastValidationTime", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const

// Contract addresses
export const contracts = {
  identityRegistry: {
    address: contractAddresses.identityRegistry as `0x${string}`,
    abi: AgentIdentityRegistryABI,
  },
  reputationRegistry: {
    address: contractAddresses.reputationRegistry as `0x${string}`,
    abi: ReputationRegistryABI,
  },
  validationRegistry: {
    address: contractAddresses.validationRegistry as `0x${string}`,
    abi: ValidationRegistryABI,
  },
}

// Helper to format agent card data
export interface AgentCard {
  name: string
  description: string
  capabilities: string[]
  endpoint: string
  metadataURI: string
  createdAt: bigint
  isActive: boolean
  owner: string
}

export function parseAgentCard(data: any): AgentCard {
  return {
    name: data[0],
    description: data[1],
    capabilities: data[2],
    endpoint: data[3],
    metadataURI: data[4],
    createdAt: BigInt(data[5]),
    isActive: data[6],
    owner: data[7],
  }
}

