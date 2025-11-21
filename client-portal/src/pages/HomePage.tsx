/**
 * Home Page - Landing Page
 * Microsoft Fluent Design System inspired landing page
 * Features enterprise-grade design with "Login" call-to-action
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Shield,
  BarChart3,
  FileCheck,
  Users,
  Zap,
  Lock,
  ArrowRight,
  CheckCircle2,
  Building2,
  ChevronRight,
} from 'lucide-react';

const features = [
  {
    icon: FileCheck,
    title: 'Automated Auditing',
    description: 'AI-powered audit workflows that reduce manual effort by 80%',
    color: 'bg-blue-500',
  },
  {
    icon: BarChart3,
    title: 'Real-time Analytics',
    description: 'Comprehensive dashboards with actionable insights',
    color: 'bg-emerald-500',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'SOC 2 Type II certified with end-to-end encryption',
    color: 'bg-purple-500',
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Seamless collaboration tools for distributed teams',
    color: 'bg-amber-500',
  },
];

const stats = [
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '50K+', label: 'Audits Completed' },
  { value: '500+', label: 'CPA Firms' },
  { value: '<2s', label: 'Response Time' },
];

const trustedBy = [
  'Microsoft', 'Deloitte', 'KPMG', 'PwC', 'EY', 'BDO'
];

export function HomePage() {
  const navigate = useNavigate();
  const isCpaPortal = window.location.hostname.startsWith('cpa.');

  const handleLogin = () => {
    navigate('/login');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="min-h-screen bg-[#faf9f8] overflow-hidden">
      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-neutral-200/50"
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#0078d4] to-[#106ebe] rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-neutral-900">
                  Aura Audit AI
                </h1>
                <p className="text-xs text-neutral-500">
                  {isCpaPortal ? 'CPA Portal' : 'Client Portal'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <a href="#features" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                Features
              </a>
              <a href="#security" className="text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors">
                Security
              </a>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleLogin}
                className="px-6 py-2.5 bg-[#0078d4] text-white text-sm font-semibold rounded-lg hover:bg-[#106ebe] transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
              >
                Login
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute inset-0" style={{
            backgroundImage: `
              radial-gradient(circle at 20% 50%, rgba(0, 120, 212, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(16, 110, 190, 0.06) 0%, transparent 40%)
            `,
          }} />
          <motion.div
            className="absolute top-40 left-20 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl"
            animate={{
              y: [0, 30, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-20 right-20 w-80 h-80 bg-purple-400/10 rounded-full blur-3xl"
            animate={{
              y: [0, -40, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-7xl mx-auto relative z-10"
        >
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Column - Content */}
            <div>
              <motion.div
                variants={itemVariants}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-[#0078d4] rounded-full text-sm font-medium mb-6"
              >
                <Zap className="w-4 h-4" />
                AI-Powered Audit Platform
              </motion.div>

              <motion.h1
                variants={itemVariants}
                className="text-5xl lg:text-6xl font-bold text-neutral-900 leading-tight mb-6"
              >
                Transform Your{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0078d4] to-[#50e6ff]">
                  Audit Practice
                </span>{' '}
                with AI
              </motion.h1>

              <motion.p
                variants={itemVariants}
                className="text-xl text-neutral-600 leading-relaxed mb-8 max-w-xl"
              >
                Streamline compliance, automate workflows, and deliver exceptional
                client service with enterprise-grade AI technology built for CPAs.
              </motion.p>

              <motion.div variants={itemVariants} className="flex flex-wrap gap-4 mb-10">
                <motion.button
                  whileHover={{ scale: 1.02, boxShadow: '0 20px 40px rgba(0, 120, 212, 0.3)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleLogin}
                  className="px-8 py-4 bg-gradient-to-r from-[#0078d4] to-[#106ebe] text-white text-lg font-semibold rounded-xl hover:from-[#106ebe] hover:to-[#0078d4] transition-all shadow-xl shadow-blue-500/25 flex items-center gap-3"
                >
                  Login to Your Account
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
                <motion.a
                  href="#features"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-8 py-4 bg-white text-neutral-700 text-lg font-semibold rounded-xl border-2 border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50 transition-all flex items-center gap-3"
                >
                  Learn More
                  <ChevronRight className="w-5 h-5" />
                </motion.a>
              </motion.div>

              {/* Trust Indicators */}
              <motion.div variants={itemVariants} className="flex items-center gap-6">
                {[
                  { icon: Shield, text: 'SOC 2 Certified' },
                  { icon: Lock, text: 'Bank-Level Security' },
                  { icon: CheckCircle2, text: 'AICPA Compliant' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-neutral-600">
                    <item.icon className="w-4 h-4 text-emerald-500" />
                    <span>{item.text}</span>
                  </div>
                ))}
              </motion.div>
            </div>

            {/* Right Column - Visual */}
            <motion.div
              variants={itemVariants}
              className="relative"
            >
              <div className="relative">
                {/* Main Dashboard Preview */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5, duration: 0.6 }}
                  className="bg-white rounded-2xl shadow-2xl shadow-neutral-200/50 border border-neutral-200/50 overflow-hidden"
                >
                  <div className="bg-gradient-to-r from-[#0078d4] to-[#50e6ff] p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-white/30" />
                      <div className="w-3 h-3 rounded-full bg-white/30" />
                      <div className="w-3 h-3 rounded-full bg-white/30" />
                    </div>
                  </div>
                  <div className="p-6 space-y-4">
                    {/* Mock Stats Row */}
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { label: 'Active Audits', value: '24' },
                        { label: 'Completed', value: '156' },
                        { label: 'Compliance', value: '98%' },
                      ].map((stat, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.7 + i * 0.1 }}
                          className="bg-neutral-50 rounded-xl p-4 text-center"
                        >
                          <p className="text-2xl font-bold text-neutral-900">{stat.value}</p>
                          <p className="text-xs text-neutral-500 mt-1">{stat.label}</p>
                        </motion.div>
                      ))}
                    </div>
                    {/* Mock Chart */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 1 }}
                      className="h-32 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-xl flex items-end justify-around p-4"
                    >
                      {[40, 65, 45, 80, 55, 70, 90].map((height, i) => (
                        <motion.div
                          key={i}
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ delay: 1.2 + i * 0.05, duration: 0.5 }}
                          className="w-6 bg-gradient-to-t from-[#0078d4] to-[#50e6ff] rounded-t-lg"
                        />
                      ))}
                    </motion.div>
                  </div>
                </motion.div>

                {/* Floating Card - Left */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.2 }}
                  className="absolute -left-8 top-20 bg-white rounded-xl shadow-xl p-4 border border-neutral-200/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-neutral-900">Audit Complete</p>
                      <p className="text-xs text-neutral-500">Client ABC Corp</p>
                    </div>
                  </div>
                </motion.div>

                {/* Floating Card - Right */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.4 }}
                  className="absolute -right-4 bottom-20 bg-white rounded-xl shadow-xl p-4 border border-neutral-200/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Zap className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-neutral-900">AI Analysis</p>
                      <p className="text-xs text-neutral-500">3 risks identified</p>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 bg-white border-y border-neutral-200">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <p className="text-4xl md:text-5xl font-bold text-[#0078d4] mb-2">{stat.value}</p>
                <p className="text-neutral-600 font-medium">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-neutral-900 mb-4">
              Everything you need to scale your practice
            </h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
              Purpose-built tools designed for modern CPA firms and their clients
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0,0,0,0.1)' }}
                className="bg-white rounded-2xl p-6 border border-neutral-200 transition-all cursor-pointer"
              >
                <div className={`w-12 h-12 ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-neutral-900 mb-2">{feature.title}</h3>
                <p className="text-neutral-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section id="security" className="py-24 px-6 bg-gradient-to-br from-neutral-900 to-neutral-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 text-white/80 rounded-full text-sm font-medium mb-6">
                <Shield className="w-4 h-4" />
                Enterprise Security
              </div>
              <h2 className="text-4xl font-bold text-white mb-6">
                Security that meets the highest standards
              </h2>
              <p className="text-lg text-neutral-400 mb-8">
                Your data is protected with bank-level encryption, comprehensive audit
                trails, and compliance certifications that exceed industry standards.
              </p>
              <div className="space-y-4">
                {[
                  'SOC 2 Type II Certified',
                  'AICPA Security Standards',
                  'End-to-end AES-256 Encryption',
                  'Multi-factor Authentication',
                  'Role-based Access Control',
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span className="text-white">{item}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="w-64 h-64 bg-gradient-to-br from-[#0078d4]/20 to-[#50e6ff]/20 rounded-full blur-3xl absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              <div className="relative bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { icon: Shield, label: 'SOC 2' },
                    { icon: Lock, label: 'GDPR' },
                    { icon: CheckCircle2, label: 'HIPAA' },
                    { icon: FileCheck, label: 'ISO 27001' },
                  ].map((item, i) => (
                    <motion.div
                      key={i}
                      whileHover={{ scale: 1.05 }}
                      className="bg-white/10 rounded-xl p-6 text-center"
                    >
                      <item.icon className="w-8 h-8 text-[#50e6ff] mx-auto mb-2" />
                      <p className="text-white font-semibold">{item.label}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-neutral-900 mb-6">
              Ready to transform your audit practice?
            </h2>
            <p className="text-xl text-neutral-600 mb-10">
              Join hundreds of CPA firms already using Aura Audit AI to streamline
              their workflows and deliver exceptional client service.
            </p>
            <motion.button
              whileHover={{ scale: 1.02, boxShadow: '0 20px 40px rgba(0, 120, 212, 0.3)' }}
              whileTap={{ scale: 0.98 }}
              onClick={handleLogin}
              className="px-10 py-5 bg-gradient-to-r from-[#0078d4] to-[#106ebe] text-white text-lg font-semibold rounded-xl hover:from-[#106ebe] hover:to-[#0078d4] transition-all shadow-xl shadow-blue-500/25 inline-flex items-center gap-3"
            >
              Login to Your Account
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-white py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#0078d4] to-[#106ebe] rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold">Aura Audit AI</h3>
                <p className="text-xs text-neutral-400">Enterprise Audit Platform</p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-neutral-400">
              <a href="/privacy" className="hover:text-white transition-colors">Privacy</a>
              <a href="/terms" className="hover:text-white transition-colors">Terms</a>
              <a href="/security" className="hover:text-white transition-colors">Security</a>
              <a href="/contact" className="hover:text-white transition-colors">Contact</a>
            </div>
            <p className="text-sm text-neutral-500">
              2025 Aura Audit AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;
