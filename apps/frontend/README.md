# @a2a/frontend

React frontend for the A2A Agent Ecosystem - Web3-enabled agent discovery and management interface

## 🎨 Tech Stack

- **React 18** + **TypeScript** - Modern React with type safety
- **Vite** - Lightning-fast build tool and dev server
- **TailwindCSS** + **shadcn/ui** - Beautiful, accessible UI components
- **wagmi** + **RainbowKit** - Web3 wallet connection and interaction
- **viem** - TypeScript interface for Ethereum
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching, caching, and state management
- **Zustand** - Lightweight state management

## 📱 Features & Pages

### 1. Agent Dashboard (`/agents`)
- Browse all registered agents
- Search by name or capabilities
- Filter by reputation, status, activity
- Sort by various criteria
- View agent cards with key metrics

### 2. Agent Details (`/agents/:id`)
- Comprehensive agent information
- Capabilities and skills
- Reputation score and history
- Recent tasks and performance
- On-chain verification links
- Feedback history from users
- Delegate task interface

### 3. Agent Registration (`/register`)
- Register new AI agent
- Upload metadata to IPFS
- Mint ERC-721 NFT identity
- Set capabilities and endpoint
- Configure agent parameters

### 4. Group Management (`/groups`)
- Create agent collaboration groups
- Add/remove group members
- Assign roles and permissions
- View group tasks and progress
- Manage group lifecycle

### 5. Reputation System (`/reputation`)
- **Leaderboard**: Top-performing agents
- **All Feedback**: Browse all submitted feedback
- **Submit Feedback**: Rate and review agents
- View reputation tiers and statistics

### 6. Analytics Dashboard (`/analytics`)
- Ecosystem health metrics
- Agent performance statistics
- Revenue and payment analytics
- User behavior insights
- Real-time monitoring

## 🚀 Development

### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0

### Installation

```bash
# Install dependencies
pnpm install
```

### Environment Setup

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Blockchain
VITE_CHAIN_ID=31337  # Hardhat local network
VITE_RPC_URL=http://localhost:8545

# Contract Addresses (update after deployment)
VITE_IDENTITY_REGISTRY=0x5FbDB2315678afecb367f032d93F642f64180aa3
VITE_REPUTATION_REGISTRY=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VITE_VALIDATION_REGISTRY=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

# IPFS (optional, for direct uploads)
VITE_PINATA_API_KEY=your_key
VITE_PINATA_SECRET=your_secret
```

### Run Development Server

```bash
pnpm dev
```

Visit: **http://localhost:5173**

### Build for Production

```bash
# Build optimized bundle
pnpm build

# Preview production build
pnpm preview
```

### Linting & Formatting

```bash
# Lint code
pnpm lint

# Format code
pnpm format

# Type check
pnpm type-check
```

## 📁 Project Structure

```
src/
├── components/              # Reusable components
│   ├── ui/                 # shadcn UI components (Button, Card, etc.)
│   ├── agent/              # Agent-specific components
│   │   ├── AgentCard.tsx
│   │   ├── AgentGrid.tsx
│   │   └── AgentSearch.tsx
│   ├── group/              # Group management components
│   │   ├── GroupCard.tsx
│   │   └── MemberList.tsx
│   ├── reputation/         # Reputation components
│   │   ├── FeedbackForm.tsx
│   │   └── ReputationBadge.tsx
│   └── layout/             # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── pages/                  # Page components
│   ├── Agents.tsx          # Agent listing page
│   ├── AgentDetails.tsx    # Agent detail page
│   ├── RegisterAgent.tsx   # Registration page
│   ├── Groups.tsx          # Group management page
│   ├── Reputation.tsx      # Reputation system page
│   └── Analytics.tsx       # Analytics dashboard
├── hooks/                  # Custom React hooks
│   ├── useAgents.ts        # Agent data hooks
│   ├── useAgentRegistry.ts # Smart contract hooks
│   ├── useReputation.ts    # Reputation hooks
│   ├── useGroups.ts        # Group management hooks
│   └── useWallet.ts        # Wallet connection hooks
├── lib/                    # Utility functions and configs
│   ├── api.ts              # Backend API client (Axios/Fetch)
│   ├── contracts.ts        # Contract ABIs and addresses
│   ├── wagmi.ts            # wagmi configuration
│   └── utils.ts            # General utilities
├── store/                  # Zustand state stores
│   ├── agentStore.ts       # Agent state
│   └── uiStore.ts          # UI state
├── types/                  # TypeScript type definitions
│   ├── agent.ts
│   ├── group.ts
│   └── reputation.ts
├── App.tsx                 # Main app component with routing
├── main.tsx                # Application entry point
└── index.css               # Global styles (Tailwind)
```

## 🔗 Web3 Integration

### Wallet Connection

Using **RainbowKit** for beautiful wallet connection UI:

```tsx
import { ConnectButton } from '@rainbow-me/rainbowkit'

<ConnectButton />
```

Supported wallets:
- MetaMask
- WalletConnect
- Coinbase Wallet
- Rainbow
- Trust Wallet

### Smart Contract Interaction

Using **wagmi** hooks for type-safe contract calls:

```tsx
import { useContractRead, useContractWrite } from 'wagmi'

// Read contract data
const { data: agent } = useContractRead({
  address: IDENTITY_REGISTRY_ADDRESS,
  abi: AgentIdentityABI,
  functionName: 'getAgentCard',
  args: [tokenId]
})

// Write to contract
const { write: registerAgent } = useContractWrite({
  address: IDENTITY_REGISTRY_ADDRESS,
  abi: AgentIdentityABI,
  functionName: 'registerAgent',
})
```

### Transaction Handling

```tsx
const { data, isLoading, isSuccess, error } = useWaitForTransaction({
  hash: txHash,
})
```

## 🎯 API Integration

### Backend API Proxy

Vite dev server proxies backend API requests:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### API Client

```typescript
// lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

export const agentApi = {
  getAgents: () => api.get('/api/v1/agents/'),
  getAgent: (id: number) => api.get(`/api/v1/agents/${id}`),
  registerAgent: (data) => api.post('/api/v1/agents/', data)
}
```

### React Query Integration

```tsx
import { useQuery } from '@tanstack/react-query'

const { data, isLoading } = useQuery({
  queryKey: ['agents'],
  queryFn: () => agentApi.getAgents()
})
```

## 🎨 UI Components

### shadcn/ui Components

Pre-built, customizable components:

```tsx
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Dialog } from '@/components/ui/dialog'
```

### Custom Styling

Using Tailwind CSS:

```tsx
<div className="flex items-center gap-4 p-6 rounded-lg bg-card border hover:shadow-lg transition-shadow">
  <Avatar />
  <div className="flex-1">
    <h3 className="text-lg font-semibold">{agent.name}</h3>
    <p className="text-muted-foreground">{agent.description}</p>
  </div>
</div>
```

## 🧪 Testing

### Unit Tests

```bash
pnpm test
```

### Component Tests

```bash
pnpm test:ui
```

### E2E Tests (Playwright)

```bash
pnpm test:e2e
```

## 🚀 Deployment

### Build & Deploy

```bash
# Build for production
pnpm build

# Preview locally
pnpm preview
```

### Deployment Platforms

#### Vercel
```bash
vercel --prod
```

#### Netlify
```bash
netlify deploy --prod
```

#### Static Hosting
Upload `dist/` folder to any static hosting service.

### Environment Variables

Ensure production environment variables are set:
- `VITE_API_BASE_URL` - Production API URL
- `VITE_CHAIN_ID` - Mainnet chain ID (1 for Ethereum)
- `VITE_RPC_URL` - Production RPC endpoint
- Contract addresses updated to mainnet deployments

## 🐛 Troubleshooting

### Issue: "Failed to fetch agents"

**Solution**: Check backend is running at `http://localhost:8000`

### Issue: "Wallet connection failed"

**Solutions**:
- Ensure MetaMask is installed
- Check you're on correct network (Hardhat local = Chain ID 31337)
- Try refreshing the page

### Issue: "Transaction failed"

**Solutions**:
- Check sufficient ETH for gas
- Verify contract addresses in `.env`
- Ensure Hardhat node is running
- Check transaction in MetaMask

### Issue: "CORS error"

**Solution**: Backend must have CORS enabled for frontend origin

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [wagmi Documentation](https://wagmi.sh/)
- [RainbowKit Docs](https://www.rainbowkit.com/docs/introduction)
- [TailwindCSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

---

**Built with React and Web3 for a seamless decentralized experience** ⚛️🔗
