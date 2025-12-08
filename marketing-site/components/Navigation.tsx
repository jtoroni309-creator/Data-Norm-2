'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import {
  Menu,
  X,
  ChevronDown,
  Brain,
  Bot,
  Lightbulb,
  ShieldCheck,
  LineChart,
  ArrowRight,
  FileText,
  BookOpen,
  HelpCircle,
  Headphones,
  Mail,
} from 'lucide-react'

const services = [
  {
    name: 'AI-Powered Audits',
    description: 'Complete audit automation with AI analysis',
    href: '/services/ai-audit',
    icon: Brain,
    color: 'from-blue-500 to-cyan-500',
  },
  {
    name: 'AI Agents',
    description: 'Custom autonomous agents for any workflow',
    href: '/services/ai-agents',
    icon: Bot,
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'R&D Tax Credits',
    description: 'Maximize credits with AI qualification',
    href: '/services/rd-tax-credit',
    icon: Lightbulb,
    color: 'from-green-500 to-emerald-500',
  },
  {
    name: 'SOC Compliance',
    description: 'SOC 1, 2, 3 examination platform',
    href: '/services/soc-compliance',
    icon: ShieldCheck,
    color: 'from-indigo-500 to-purple-500',
  },
  {
    name: 'Financial Analysis',
    description: '50+ ratios with industry benchmarks',
    href: '/services/financial-analysis',
    icon: LineChart,
    color: 'from-cyan-500 to-blue-500',
  },
]

const resources = [
  { name: 'Blog', href: '/blog', icon: BookOpen, description: 'Insights and updates' },
  { name: 'Case Studies', href: '/case-studies', icon: FileText, description: 'Customer success stories' },
  { name: 'Documentation', href: '/api', icon: FileText, description: 'API & developer docs' },
  { name: 'FAQ', href: '/faq', icon: HelpCircle, description: 'Common questions' },
  { name: 'Support', href: '/support', icon: Headphones, description: 'Get help' },
  { name: 'Contact', href: '/contact', icon: Mail, description: 'Talk to us' },
]

const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isServicesOpen, setIsServicesOpen] = useState(false)
  const [isResourcesOpen, setIsResourcesOpen] = useState(false)
  const servicesRef = useRef<HTMLDivElement>(null)
  const resourcesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (servicesRef.current && !servicesRef.current.contains(event.target as Node)) {
        setIsServicesOpen(false)
      }
      if (resourcesRef.current && !resourcesRef.current.contains(event.target as Node)) {
        setIsResourcesOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-lg'
          : 'bg-transparent'
      }`}
    >
      <div className="section-container">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center group">
            <Image
              src="/logo.svg"
              alt="Aura AI"
              width={150}
              height={45}
              className="transform group-hover:scale-105 transition-transform"
              priority
            />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {/* Services Dropdown */}
            <div ref={servicesRef} className="relative">
              <button
                onClick={() => {
                  setIsServicesOpen(!isServicesOpen)
                  setIsResourcesOpen(false)
                }}
                className={`flex items-center space-x-1 px-4 py-2 rounded-lg font-medium transition-all ${
                  isServicesOpen
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                <span>Services</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${isServicesOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Services Mega Menu */}
              {isServicesOpen && (
                <div className="absolute top-full left-0 mt-2 w-[600px] bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden animate-fade-in-up">
                  <div className="p-6">
                    <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
                      Our Services
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {services.map((service) => (
                        <Link
                          key={service.name}
                          href={service.href}
                          onClick={() => setIsServicesOpen(false)}
                          className="group flex items-center space-x-4 p-3 rounded-xl hover:bg-gray-50 transition-all"
                        >
                          <div className={`w-12 h-12 bg-gradient-to-r ${service.color} rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                            <service.icon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                              {service.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {service.description}
                            </div>
                          </div>
                          <ArrowRight className="w-5 h-5 text-gray-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                        </Link>
                      ))}
                    </div>
                  </div>
                  <div className="bg-gradient-to-r from-primary-50 to-accent-50 p-4 border-t border-gray-100">
                    <Link
                      href="/#demo"
                      onClick={() => setIsServicesOpen(false)}
                      className="flex items-center justify-center space-x-2 text-primary-600 font-semibold hover:text-primary-700 transition-colors"
                    >
                      <span>See all services in action</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              )}
            </div>

            {/* Pricing Link */}
            <Link
              href="/#pricing"
              className="px-4 py-2 text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-lg font-medium transition-all"
            >
              Pricing
            </Link>

            {/* Resources Dropdown */}
            <div ref={resourcesRef} className="relative">
              <button
                onClick={() => {
                  setIsResourcesOpen(!isResourcesOpen)
                  setIsServicesOpen(false)
                }}
                className={`flex items-center space-x-1 px-4 py-2 rounded-lg font-medium transition-all ${
                  isResourcesOpen
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                <span>Resources</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${isResourcesOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Resources Dropdown */}
              {isResourcesOpen && (
                <div className="absolute top-full right-0 mt-2 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden animate-fade-in-up">
                  <div className="p-4">
                    {resources.map((resource) => (
                      <Link
                        key={resource.name}
                        href={resource.href}
                        onClick={() => setIsResourcesOpen(false)}
                        className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-50 transition-all"
                      >
                        <resource.icon className="w-5 h-5 text-gray-500" />
                        <div>
                          <div className="font-medium text-gray-900">{resource.name}</div>
                          <div className="text-xs text-gray-500">{resource.description}</div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* About Link */}
            <Link
              href="/about"
              className="px-4 py-2 text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-lg font-medium transition-all"
            >
              About
            </Link>

            {/* CTA Buttons */}
            <div className="flex items-center space-x-3 ml-4">
              <Link
                href="https://portal.auraai.toroniandcompany.com/login"
                className="px-5 py-2.5 border-2 border-primary-600 text-primary-600 font-semibold rounded-xl hover:bg-primary-50 transition-all"
              >
                Login
              </Link>
              <Link
                href="/#demo"
                className="px-5 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/25 hover:scale-105 transition-all"
              >
                Get Started
              </Link>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-700" />
            ) : (
              <Menu className="w-6 h-6 text-gray-700" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden absolute top-full left-0 right-0 bg-white shadow-xl border-t border-gray-100 max-h-[calc(100vh-5rem)] overflow-y-auto">
            <div className="py-4 px-4 space-y-2">
              {/* Mobile Services Section */}
              <div className="pb-4 border-b border-gray-100">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-3">
                  Services
                </div>
                {services.map((service) => (
                  <Link
                    key={service.name}
                    href={service.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 rounded-xl transition-colors"
                  >
                    <div className={`w-10 h-10 bg-gradient-to-r ${service.color} rounded-lg flex items-center justify-center`}>
                      <service.icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{service.name}</div>
                      <div className="text-xs text-gray-500">{service.description}</div>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Mobile Resources Section */}
              <div className="pb-4 border-b border-gray-100">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-3">
                  Resources
                </div>
                {resources.map((resource) => (
                  <Link
                    key={resource.name}
                    href={resource.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 rounded-xl transition-colors"
                  >
                    <resource.icon className="w-5 h-5 text-gray-500" />
                    <span className="font-medium text-gray-900">{resource.name}</span>
                  </Link>
                ))}
              </div>

              {/* Mobile Other Links */}
              <Link
                href="/#pricing"
                className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link
                href="/about"
                className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                About
              </Link>

              {/* Mobile CTA Buttons */}
              <div className="pt-4 space-y-3">
                <Link
                  href="https://portal.auraai.toroniandcompany.com/login"
                  className="block px-4 py-3 border-2 border-primary-600 text-primary-600 font-semibold rounded-xl text-center"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/#demo"
                  className="block px-4 py-3 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-xl text-center"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navigation
