'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Bot,
  Brain,
  Sparkles,
  Code2,
  Puzzle,
  Workflow,
  Zap,
  Shield,
  Settings,
  Play,
  ArrowRight,
  CheckCircle2,
  MessageSquare,
  FileSearch,
  Calculator,
  TrendingUp,
  Database,
  Lock,
  Layers,
  Terminal,
  Cpu,
  Network,
  Gauge,
  RefreshCw,
  GitBranch,
  Package,
  Boxes,
  Wand2,
} from 'lucide-react'

export default function AIAgentsPage() {
  const preBuiltAgents = [
    {
      name: 'Transaction Analyzer',
      description: 'Analyzes journal entries, identifies anomalies, and flags suspicious patterns using ML models.',
      capabilities: ['Pattern detection', 'Anomaly scoring', 'Trend analysis', 'Risk assessment'],
      icon: TrendingUp,
    },
    {
      name: 'Disclosure Drafter',
      description: 'Generates GAAP-compliant financial statement disclosures with proper ASC citations.',
      capabilities: ['30+ ASC topics', 'Materiality aware', 'Citation linking', 'Format templates'],
      icon: FileSearch,
    },
    {
      name: 'Ratio Calculator',
      description: 'Computes 50+ financial ratios with industry benchmarking and trend analysis.',
      capabilities: ['Industry comparisons', 'Historical trends', 'Threshold alerts', 'Visual reports'],
      icon: Calculator,
    },
    {
      name: 'Fraud Detector',
      description: 'Multi-layer fraud detection using ensemble models and behavioral analytics.',
      capabilities: ['Benford analysis', 'Network detection', 'Behavior modeling', 'Risk scoring'],
      icon: Shield,
    },
    {
      name: 'Document Extractor',
      description: 'Extracts and validates data from invoices, contracts, bank statements, and more.',
      capabilities: ['OCR processing', 'Data validation', 'Multi-format support', 'Auto-classification'],
      icon: Database,
    },
    {
      name: 'Compliance Checker',
      description: 'Validates transactions against regulatory requirements and internal policies.',
      capabilities: ['PCAOB standards', 'SOX compliance', 'Policy validation', 'Gap analysis'],
      icon: CheckCircle2,
    },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-purple-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 right-1/4 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[120px]" />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8">
              <Bot className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-purple-600">AI Agent Platform</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">Autonomous AI Agents</span>
              <span className="block gradient-text">For Every Task</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Deploy pre-built AI agents or create custom ones tailored to your firm's unique workflows.
              Our agent framework handles complex, multi-step accounting tasks autonomously—with full
              transparency and human oversight.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/#demo"
                className="group px-8 py-4 bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Explore Agents</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/api"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300 flex items-center space-x-2"
              >
                <Code2 className="w-5 h-5" />
                <span>API Documentation</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* What Are AI Agents */}
      <section className="py-24 bg-white/50">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
                What Are
                <span className="block gradient-text">AI Agents?</span>
              </h2>
              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                AI Agents are autonomous software entities that can understand goals, break them into tasks,
                execute complex workflows, and make decisions—all while maintaining complete transparency
                about their reasoning and actions.
              </p>
              <p className="text-lg text-slate-600 mb-8">
                Unlike simple automation or chatbots, Aura's AI Agents can:
              </p>

              <div className="space-y-4">
                {[
                  { icon: Brain, text: 'Reason through complex, multi-step problems' },
                  { icon: Workflow, text: 'Orchestrate sequences of actions autonomously' },
                  { icon: RefreshCw, text: 'Learn from feedback and improve over time' },
                  { icon: GitBranch, text: 'Handle exceptions and edge cases intelligently' },
                  { icon: MessageSquare, text: 'Communicate their reasoning in plain language' },
                  { icon: Lock, text: 'Operate within defined guardrails and permissions' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-slate-700 font-medium">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glassmorphism rounded-3xl p-8 shadow-xl">
              <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-semibold">Transaction Analyzer Agent</div>
                    <div className="text-slate-400 text-sm">Processing engagement data...</div>
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  {[
                    { task: 'Loading Q4 trial balance...', status: 'complete', time: '0.3s' },
                    { task: 'Mapping 847 accounts...', status: 'complete', time: '1.2s' },
                    { task: 'Analyzing 147,382 transactions...', status: 'complete', time: '4.7s' },
                    { task: 'Running Benford\'s analysis...', status: 'complete', time: '0.8s' },
                    { task: 'Detecting anomaly patterns...', status: 'running', time: '...' },
                    { task: 'Generating findings report...', status: 'pending', time: '' },
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between glassmorphism-dark rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-3">
                        {item.status === 'complete' && <CheckCircle2 className="w-4 h-4 text-green-400" />}
                        {item.status === 'running' && <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />}
                        {item.status === 'pending' && <div className="w-4 h-4 rounded-full border-2 border-slate-600" />}
                        <span className={`text-sm ${item.status === 'pending' ? 'text-slate-500' : 'text-slate-300'}`}>
                          {item.task}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">{item.time}</span>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                  <div className="text-sm text-slate-400">Progress</div>
                  <div className="text-sm text-purple-400 font-semibold">78% Complete</div>
                </div>
                <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500" style={{ width: '78%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pre-Built Agents */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Pre-Built Agents
              <span className="block gradient-text">Ready to Deploy</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Start immediately with our library of specialized agents, each trained on millions of
              accounting transactions and designed for specific audit and accounting workflows.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {preBuiltAgents.map((agent, index) => (
              <div key={index} className="group glassmorphism rounded-3xl p-8 hover:shadow-2xl transition-all duration-500">
                <div className="w-14 h-14 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                  <agent.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{agent.name}</h3>
                <p className="text-slate-600 mb-6">{agent.description}</p>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.map((cap, idx) => (
                    <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Custom Agent Builder */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center space-x-2 px-4 py-2 bg-purple-500/20 rounded-full mb-6">
                <Wand2 className="w-5 h-5 text-purple-400" />
                <span className="text-sm font-medium text-purple-400">Custom Agent Builder</span>
              </div>

              <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
                Build Custom Agents
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                  For Your Unique Workflows
                </span>
              </h2>

              <p className="text-xl text-slate-400 mb-8">
                Our no-code/low-code agent builder empowers your team to create specialized AI agents
                tailored to your firm's unique methodologies, client needs, and compliance requirements.
              </p>

              <div className="space-y-6">
                {[
                  {
                    icon: Puzzle,
                    title: 'Drag-and-Drop Builder',
                    description: 'Visual workflow designer—no coding required. Connect pre-built components to create complex agent behaviors.',
                  },
                  {
                    icon: Code2,
                    title: 'SDK & API Access',
                    description: 'For developers: Full Python and TypeScript SDKs with complete API access for advanced customization.',
                  },
                  {
                    icon: Boxes,
                    title: 'Component Library',
                    description: 'Hundreds of pre-built actions, conditions, and integrations to compose your agents.',
                  },
                  {
                    icon: Shield,
                    title: 'Guardrails & Governance',
                    description: 'Define permissions, approval workflows, and boundaries to ensure agents operate within policy.',
                  },
                ].map((item, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white mb-1">{item.title}</h3>
                      <p className="text-slate-400">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glassmorphism-dark rounded-3xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <Terminal className="w-6 h-6 text-purple-400" />
                  <span className="text-white font-semibold">Agent Builder</span>
                </div>
                <div className="flex space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
              </div>

              <pre className="text-sm text-slate-300 overflow-x-auto">
{`from aura import Agent, Task, Action

# Define custom agent
class RevenueAnalyzer(Agent):
    """Custom agent for ASC 606 revenue analysis"""

    def __init__(self):
        super().__init__(
            name="Revenue Recognition Analyzer",
            description="Analyzes revenue for ASC 606 compliance"
        )

    @Task("Identify revenue contracts")
    async def find_contracts(self, transactions):
        # AI identifies contract patterns
        contracts = await self.ai.detect_patterns(
            transactions,
            pattern_type="revenue_contract"
        )
        return contracts

    @Task("Analyze performance obligations")
    async def analyze_obligations(self, contracts):
        # Decompose into obligations
        for contract in contracts:
            obligations = await self.ai.extract(
                contract,
                "performance_obligations"
            )
            yield self.assess_recognition(obligations)

    @Action("Generate disclosure")
    async def draft_disclosure(self, analysis):
        # AI drafts ASC 606 disclosure
        return await self.ai.generate(
            template="asc606_disclosure",
            data=analysis
        )

# Deploy agent
agent = RevenueAnalyzer()
results = await agent.run(engagement_data)`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Agent Architecture */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Enterprise-Grade
              <span className="block gradient-text">Agent Architecture</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Built for reliability, security, and scale—our agent infrastructure handles millions of
              transactions with enterprise-grade controls.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Cpu,
                title: 'Scalable Compute',
                description: 'Auto-scaling infrastructure handles peak loads. Process unlimited transactions without performance degradation.',
              },
              {
                icon: Lock,
                title: 'Security First',
                description: 'SOC 2 Type II certified. AES-256 encryption, RBAC, and complete audit trails for all agent actions.',
              },
              {
                icon: Network,
                title: 'Multi-Agent Orchestration',
                description: 'Agents can collaborate on complex tasks, sharing context and coordinating workflows automatically.',
              },
              {
                icon: Gauge,
                title: 'Real-Time Monitoring',
                description: 'Full observability into agent performance, resource usage, and decision-making processes.',
              },
            ].map((item, index) => (
              <div key={index} className="text-center glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <item.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">{item.title}</h3>
                <p className="text-slate-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Real-World
              <span className="block gradient-text">Agent Applications</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                title: 'Continuous Audit Monitoring',
                description: 'Deploy agents that continuously monitor client transactions, flagging anomalies and compliance issues in real-time rather than waiting for year-end.',
                results: ['80% reduction in surprise findings', 'Real-time risk visibility', 'Proactive issue resolution'],
              },
              {
                title: 'Automated Workpaper Preparation',
                description: 'Agents automatically gather evidence, populate workpapers, and cross-reference documentation—reducing prep time by 70%.',
                results: ['70% faster prep time', 'Consistent documentation', 'Automatic cross-referencing'],
              },
              {
                title: 'Client Communication Agent',
                description: 'AI agent that drafts client communications, PBC requests, and status updates based on engagement progress and findings.',
                results: ['50% reduction in admin time', 'Consistent messaging', 'Faster response times'],
              },
              {
                title: 'Regulatory Change Monitor',
                description: 'Agent that monitors regulatory updates, analyzes impact on client engagements, and recommends procedure adjustments.',
                results: ['Zero missed updates', 'Impact analysis', 'Procedure recommendations'],
              },
            ].map((useCase, index) => (
              <div key={index} className="glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <h3 className="text-2xl font-bold text-slate-900 mb-4">{useCase.title}</h3>
                <p className="text-slate-600 mb-6">{useCase.description}</p>
                <div className="space-y-2">
                  {useCase.results.map((result, idx) => (
                    <div key={idx} className="flex items-center text-sm">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mr-3" />
                      <span className="text-slate-700">{result}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-purple-600 via-pink-600 to-red-500 text-white">
        <div className="section-container text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Ready to Deploy Your First Agent?
          </h2>
          <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
            Start with our pre-built agents or build custom ones tailored to your firm's needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/#demo"
              className="px-8 py-4 bg-white text-slate-900 font-semibold rounded-2xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/api"
              className="px-8 py-4 border-2 border-white text-white font-semibold rounded-2xl hover:bg-white/10 transition-all duration-300 flex items-center space-x-2"
            >
              <Code2 className="w-5 h-5" />
              <span>View API Docs</span>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
