import Link from 'next/link'
import { Twitter, Linkedin, Github, Mail, Youtube, Shield, FileText } from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-300">
      <div className="section-container py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <img src="/logo.svg" alt="Aura AI" className="h-10 w-auto" />
            </div>
            <p className="text-gray-400 mb-6 max-w-sm">
              Enterprise-grade audit automation platform. Empowering CPA firms with AI-powered intelligence to deliver faster, more accurate audits.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://twitter.com/auraauditai"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/auraauditai"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="https://www.youtube.com/@auraauditai"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors"
                aria-label="YouTube"
              >
                <Youtube className="w-5 h-5" />
              </a>
              <a
                href="https://github.com/auraauditai"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@auraaudit.ai"
                className="w-10 h-10 bg-gray-800 hover:bg-primary-600 rounded-lg flex items-center justify-center transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Services Column */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Services</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/services/ai-audit" className="hover:text-primary-400 transition-colors">
                  AI-Powered Audits
                </Link>
              </li>
              <li>
                <Link href="/services/ai-agents" className="hover:text-primary-400 transition-colors">
                  AI Agents
                </Link>
              </li>
              <li>
                <Link href="/services/rd-tax-credit" className="hover:text-primary-400 transition-colors">
                  R&D Tax Credits
                </Link>
              </li>
              <li>
                <Link href="/services/soc-compliance" className="hover:text-primary-400 transition-colors">
                  SOC Compliance
                </Link>
              </li>
              <li>
                <Link href="/services/financial-analysis" className="hover:text-primary-400 transition-colors">
                  Financial Analysis
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Company</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/about" className="hover:text-primary-400 transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-primary-400 transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/blog" className="hover:text-primary-400 transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/case-studies" className="hover:text-primary-400 transition-colors">
                  Case Studies
                </Link>
              </li>
              <li>
                <Link href="/careers" className="hover:text-primary-400 transition-colors">
                  Careers
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Resources</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/api" className="hover:text-primary-400 transition-colors">
                  API Documentation
                </Link>
              </li>
              <li>
                <Link href="/support" className="hover:text-primary-400 transition-colors">
                  Support Center
                </Link>
              </li>
              <li>
                <Link href="/faq" className="hover:text-primary-400 transition-colors">
                  FAQ
                </Link>
              </li>
              <li>
                <Link href="/security" className="hover:text-primary-400 transition-colors">
                  Security
                </Link>
              </li>
              <li>
                <Link href="/#pricing" className="hover:text-primary-400 transition-colors">
                  Pricing
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Compliance Column */}
          <div>
            <h3 className="text-white font-semibold text-lg mb-4">Legal</h3>
            <ul className="space-y-3">
              <li>
                <Link href="/privacy" className="hover:text-primary-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-primary-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/sla" className="hover:text-primary-400 transition-colors">
                  SLA
                </Link>
              </li>
              <li>
                <Link href="/gdpr" className="hover:text-primary-400 transition-colors">
                  GDPR Compliance
                </Link>
              </li>
              <li>
                <Link href="/dpa" className="hover:text-primary-400 transition-colors">
                  Data Processing
                </Link>
              </li>
              <li>
                <Link href="/cookies" className="hover:text-primary-400 transition-colors">
                  Cookie Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Trust Badges */}
        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="flex flex-wrap justify-center gap-6 mb-8">
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 rounded-lg">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-400">SOC 2 Type II</span>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 rounded-lg">
              <Shield className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-400">GDPR Compliant</span>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 rounded-lg">
              <FileText className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-gray-400">PCAOB Standards</span>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-gray-800/50 rounded-lg">
              <Shield className="w-5 h-5 text-cyan-500" />
              <span className="text-sm text-gray-400">256-bit Encryption</span>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-gray-500 text-sm">
              &copy; {currentYear} Aura AI. All rights reserved.
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link href="/sitemap.xml" className="text-gray-500 hover:text-primary-400 transition-colors">
                Sitemap
              </Link>
              <span className="text-gray-700">|</span>
              <Link href="/privacy" className="text-gray-500 hover:text-primary-400 transition-colors">
                Privacy
              </Link>
              <span className="text-gray-700">|</span>
              <Link href="/terms" className="text-gray-500 hover:text-primary-400 transition-colors">
                Terms
              </Link>
              <span className="text-gray-700">|</span>
              <Link href="/sla" className="text-gray-500 hover:text-primary-400 transition-colors">
                SLA
              </Link>
              <span className="text-gray-700">|</span>
              <Link href="/gdpr" className="text-gray-500 hover:text-primary-400 transition-colors">
                GDPR
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
