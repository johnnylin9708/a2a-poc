import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { hardhat, sepolia, mainnet } from 'wagmi/chains'

// Get contract addresses from environment
export const contractAddresses = {
  identityRegistry: import.meta.env.VITE_IDENTITY_REGISTRY_ADDRESS || '0x5FbDB2315678afecb367f032d93F642f64180aa3',
  reputationRegistry: import.meta.env.VITE_REPUTATION_REGISTRY_ADDRESS || '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
  validationRegistry: import.meta.env.VITE_VALIDATION_REGISTRY_ADDRESS || '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0',
}

// Custom Hardhat chain configuration
const hardhatChain = {
  ...hardhat,
  rpcUrls: {
    default: {
      http: [import.meta.env.VITE_RPC_URL || 'http://127.0.0.1:8545'],
    },
    public: {
      http: [import.meta.env.VITE_RPC_URL || 'http://127.0.0.1:8545'],
    },
  },
}

export const config = getDefaultConfig({
  appName: 'A2A Agent Ecosystem',
  projectId: import.meta.env.VITE_WALLETCONNECT_PROJECT_ID || 'YOUR_PROJECT_ID',
  chains: [hardhatChain, sepolia, mainnet],
  ssr: false,
})

