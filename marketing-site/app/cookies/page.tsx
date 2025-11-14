'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Cookie, Shield, BarChart3, Settings } from 'lucide-react'

export default function CookiePolicy() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <div className="pt-32 pb-16">
        <div className="section-container max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center">
              <Cookie className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl lg:text-5xl font-display font-bold text-gray-900">
                Cookie Policy
              </h1>
              <p className="text-gray-600 mt-2">
                Last Updated: November 14, 2025
              </p>
            </div>
          </div>

          <div className="prose prose-lg max-w-none">
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. What Are Cookies?</h2>
              <p className="text-gray-700 mb-4">
                Cookies are small text files that are placed on your device (computer, smartphone, or tablet) when you visit our website. They help us provide you with a better experience by remembering your preferences, analyzing how you use our services, and improving our platform.
              </p>
              <p className="text-gray-700">
                Cookies can be "session cookies" (deleted when you close your browser) or "persistent cookies" (remain on your device for a set period or until manually deleted).
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. How We Use Cookies</h2>
              <p className="text-gray-700 mb-6">
                Aura Audit AI uses cookies and similar technologies for the following purposes:
              </p>

              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <Shield className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Essential Cookies</h3>
                      <p className="text-sm text-gray-700">
                        Required for core functionality, authentication, and security. Cannot be disabled.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <BarChart3 className="w-6 h-6 text-accent-600 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Performance Cookies</h3>
                      <p className="text-sm text-gray-700">
                        Collect analytics data to help us understand usage patterns and improve the platform.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <Settings className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Functional Cookies</h3>
                      <p className="text-sm text-gray-700">
                        Remember your preferences, settings, and choices for a personalized experience.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <Cookie className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Marketing Cookies</h3>
                      <p className="text-sm text-gray-700">
                        Track marketing campaign effectiveness and deliver relevant content (with consent).
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Types of Cookies We Use</h2>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.1 Essential Cookies (Always Active)</h3>
              <p className="text-gray-700 mb-4">
                These cookies are necessary for the website to function and cannot be disabled. They include:
              </p>
              <div className="overflow-x-auto mb-6">
                <table className="min-w-full border border-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Cookie Name</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Purpose</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Duration</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700">
                    <tr className="border-b">
                      <td className="px-4 py-3">session_token</td>
                      <td className="px-4 py-3">User authentication and session management</td>
                      <td className="px-4 py-3">8 hours</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">csrf_token</td>
                      <td className="px-4 py-3">Security protection against cross-site request forgery</td>
                      <td className="px-4 py-3">Session</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">cookie_consent</td>
                      <td className="px-4 py-3">Remember your cookie preferences</td>
                      <td className="px-4 py-3">1 year</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3">load_balancer</td>
                      <td className="px-4 py-3">Route requests to appropriate server</td>
                      <td className="px-4 py-3">Session</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-8">3.2 Performance and Analytics Cookies</h3>
              <p className="text-gray-700 mb-4">
                These cookies help us understand how visitors interact with our website by collecting and reporting information anonymously:
              </p>
              <div className="overflow-x-auto mb-6">
                <table className="min-w-full border border-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Service</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Purpose</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Duration</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700">
                    <tr className="border-b">
                      <td className="px-4 py-3">Google Analytics (_ga, _gid)</td>
                      <td className="px-4 py-3">Track page views, user behavior, and traffic sources</td>
                      <td className="px-4 py-3">2 years / 24 hours</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">Mixpanel (mp_*)</td>
                      <td className="px-4 py-3">Product analytics and feature usage tracking</td>
                      <td className="px-4 py-3">1 year</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3">Segment (ajs_*)</td>
                      <td className="px-4 py-3">Data integration and analytics aggregation</td>
                      <td className="px-4 py-3">1 year</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-8">3.3 Functional Cookies</h3>
              <p className="text-gray-700 mb-4">
                These cookies enable enhanced functionality and personalization:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>user_preferences:</strong> Remember your display settings, language, and UI preferences (1 year)</li>
                <li><strong>recent_searches:</strong> Store your recent search queries for quick access (30 days)</li>
                <li><strong>dashboard_layout:</strong> Remember your customized dashboard configuration (6 months)</li>
                <li><strong>notification_settings:</strong> Store your notification preferences (1 year)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-8">3.4 Marketing and Advertising Cookies</h3>
              <p className="text-gray-700 mb-4">
                With your consent, we use marketing cookies to deliver relevant advertisements and measure campaign effectiveness:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>LinkedIn Insight Tag:</strong> Track conversions from LinkedIn ads and retarget visitors (90 days)</li>
                <li><strong>Google Ads:</strong> Measure ad performance and enable remarketing (90 days)</li>
                <li><strong>Facebook Pixel:</strong> Track conversions and build custom audiences (90 days)</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Third-Party Cookies</h2>
              <p className="text-gray-700 mb-4">
                Some cookies are placed by third-party services that appear on our pages. We do not control these cookies, and you should check the third-party websites for more information:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Google Analytics:</strong> <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Google Privacy Policy</a></li>
                <li><strong>Mixpanel:</strong> <a href="https://mixpanel.com/legal/privacy-policy/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Mixpanel Privacy Policy</a></li>
                <li><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">LinkedIn Privacy Policy</a></li>
                <li><strong>OpenAI:</strong> <a href="https://openai.com/privacy/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">OpenAI Privacy Policy</a></li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. How to Manage Cookies</h2>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.1 Cookie Preferences on Our Website</h3>
              <p className="text-gray-700 mb-4">
                When you first visit our website, you'll see a cookie consent banner where you can:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Accept all cookies</li>
                <li>Accept only essential cookies</li>
                <li>Customize your preferences by cookie category</li>
              </ul>
              <p className="text-gray-700 mb-4">
                You can change your cookie preferences at any time by clicking the "Cookie Settings" link in the footer of our website.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.2 Browser Settings</h3>
              <p className="text-gray-700 mb-4">
                Most web browsers allow you to control cookies through their settings. You can:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Delete all cookies from your browser</li>
                <li>Block all cookies from being set</li>
                <li>Block third-party cookies only</li>
                <li>Receive alerts when cookies are being sent</li>
              </ul>

              <p className="text-gray-700 mb-4">
                <strong>Browser-specific instructions:</strong>
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Google Chrome</a></li>
                <li><a href="https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Mozilla Firefox</a></li>
                <li><a href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Apple Safari</a></li>
                <li><a href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Microsoft Edge</a></li>
              </ul>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 my-6">
                <p className="text-amber-900 font-semibold mb-2">⚠️ Important Note</p>
                <p className="text-amber-800 text-sm">
                  Blocking or deleting essential cookies will prevent you from using certain features of our platform, including logging in and accessing your account. Performance cookies help us improve the platform, so we encourage you to keep them enabled.
                </p>
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.3 Opt-Out of Targeted Advertising</h3>
              <p className="text-gray-700 mb-4">
                You can opt out of targeted advertising through these services:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><a href="http://optout.networkadvertising.org/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Network Advertising Initiative (NAI)</a></li>
                <li><a href="http://optout.aboutads.info/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Digital Advertising Alliance (DAA)</a></li>
                <li><a href="https://www.youronlinechoices.com/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">European Interactive Digital Advertising Alliance (EDAA)</a></li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.4 Mobile Device Settings</h3>
              <p className="text-gray-700 mb-4">
                On mobile devices, you can control tracking through:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>iOS:</strong> Settings → Privacy → Tracking → Disable "Allow Apps to Request to Track"</li>
                <li><strong>Android:</strong> Settings → Google → Ads → Opt out of Ads Personalization</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Do Not Track Signals</h2>
              <p className="text-gray-700 mb-4">
                Some browsers include a "Do Not Track" (DNT) feature that signals to websites that you do not want to have your online activity tracked. Currently, there is no universal standard for how websites should respond to DNT signals.
              </p>
              <p className="text-gray-700">
                At this time, our website does not respond to DNT browser signals. However, you can manage your cookie preferences through our cookie banner or browser settings as described above.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Updates to This Cookie Policy</h2>
              <p className="text-gray-700 mb-4">
                We may update this Cookie Policy from time to time to reflect changes in our practices, technology, or legal requirements. When we make material changes, we will:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Update the "Last Updated" date at the top of this page</li>
                <li>Notify you through a banner on our website</li>
                <li>Request your consent again if required by law</li>
              </ul>
              <p className="text-gray-700">
                We encourage you to review this Cookie Policy periodically to stay informed about how we use cookies.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Contact Us</h2>
              <p className="text-gray-700 mb-4">
                If you have questions about our use of cookies or this Cookie Policy, please contact us:
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <p className="text-gray-700 mb-2"><strong>Aura Audit AI - Privacy Team</strong></p>
                <p className="text-gray-700 mb-2">Email: privacy@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Cookie Questions: cookies@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Address: 1234 Audit Way, Suite 100, Wilmington, DE 19801</p>
                <p className="text-gray-700">Phone: (555) 123-4567</p>
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8">
              <p className="text-sm text-gray-600 italic">
                This Cookie Policy is effective as of November 14, 2025. By continuing to use Aura Audit AI, you acknowledge that you have read and understood this Cookie Policy.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
