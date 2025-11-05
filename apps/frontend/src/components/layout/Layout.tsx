import { Link } from 'react-router-dom'
import { Bot, Users, Award, Menu } from 'lucide-react'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold">
              <Bot className="w-6 h-6" />
              A2A Ecosystem
            </Link>
            
            <div className="hidden md:flex items-center gap-6">
              <Link to="/" className="flex items-center gap-2 hover:text-primary">
                <Bot className="w-4 h-4" />
                Agents
              </Link>
              <Link to="/groups" className="flex items-center gap-2 hover:text-primary">
                <Users className="w-4 h-4" />
                Groups
              </Link>
              <Link to="/register" className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
                Register Agent
              </Link>
            </div>
            
            <button className="md:hidden">
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      
      <footer className="border-t mt-auto">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>A2A Agent Ecosystem - Built with ERC-8004 + A2A Protocol</p>
        </div>
      </footer>
    </div>
  )
}

