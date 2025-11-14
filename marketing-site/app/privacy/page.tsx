'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'

export default function PrivacyPolicy() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <div className="pt-32 pb-16">
        <div className="section-container max-w-4xl mx-auto">
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
            Privacy Policy
          </h1>
          <p className="text-gray-600 mb-8">
            Last Updated: November 14, 2025
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 mb-4">
                At Aura Audit AI ("Aura," "we," "our," or "us"), we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and protect information about you when you use our audit automation platform, website, and related services (collectively, the "Services").
              </p>
              <p className="text-gray-700 mb-4">
                We understand that CPA firms and auditors handle sensitive client information, and we are committed to maintaining the highest standards of data protection and confidentiality. This Privacy Policy applies to information we collect from:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Users of our platform (auditors, CPAs, firm staff)</li>
                <li>Visitors to our website</li>
                <li>Individuals who contact us or request information</li>
                <li>Data uploaded to our platform for audit engagements</li>
              </ul>
              <p className="text-gray-700">
                By using our Services, you agree to the collection and use of information in accordance with this Privacy Policy.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Information We Collect</h2>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">2.1 Information You Provide</h3>
              <p className="text-gray-700 mb-4">
                <strong>Account Information:</strong> When you create an account, we collect your name, email address, company name, job title, phone number, and billing information.
              </p>
              <p className="text-gray-700 mb-4">
                <strong>Audit Data:</strong> Data you upload to perform audit engagements, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Trial balance data and financial statements</li>
                <li>Client information (company names, addresses, tax IDs)</li>
                <li>Transaction data and journal entries</li>
                <li>Workpapers, documentation, and supporting evidence</li>
                <li>Notes, comments, and communications within the platform</li>
              </ul>
              <p className="text-gray-700 mb-4">
                <strong>Communications:</strong> Information you provide when contacting us, including support requests, feedback, and inquiries.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">2.2 Information Collected Automatically</h3>
              <p className="text-gray-700 mb-4">
                <strong>Usage Data:</strong> We automatically collect information about your use of the Services, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Pages visited, features used, and actions taken</li>
                <li>Time spent on pages and session duration</li>
                <li>Search queries and filters applied</li>
                <li>Engagement interactions (clicks, downloads, uploads)</li>
              </ul>
              <p className="text-gray-700 mb-4">
                <strong>Device and Browser Information:</strong> IP address, browser type and version, operating system, device identifiers, and screen resolution.
              </p>
              <p className="text-gray-700 mb-4">
                <strong>Cookies and Similar Technologies:</strong> We use cookies, web beacons, and similar technologies to collect information and improve user experience. See Section 8 for details.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">2.3 Information from Third Parties</h3>
              <p className="text-gray-700 mb-4">
                We may receive information from:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Accounting System Integrations:</strong> Data from QuickBooks, Xero, NetSuite, and other connected systems</li>
                <li><strong>Authentication Providers:</strong> Information from SSO providers (Azure AD, Okta, Auth0)</li>
                <li><strong>Payment Processors:</strong> Transaction details from Stripe or other payment providers</li>
                <li><strong>Service Providers:</strong> Analytics and security vendors who help us operate the Services</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. How We Use Your Information</h2>
              <p className="text-gray-700 mb-4">We use the information we collect to:</p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.1 Provide and Improve Services</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Operate, maintain, and deliver the Services</li>
                <li>Process audit engagements and generate workpapers</li>
                <li>Perform AI analysis, anomaly detection, and risk assessment</li>
                <li>Generate reports, disclosures, and documentation</li>
                <li>Provide customer support and respond to inquiries</li>
                <li>Improve our algorithms, models, and features</li>
                <li>Develop new products and services</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.2 Security and Fraud Prevention</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Monitor for security threats and suspicious activity</li>
                <li>Detect and prevent fraud, abuse, and unauthorized access</li>
                <li>Enforce our Terms of Service and acceptable use policies</li>
                <li>Conduct security audits and penetration testing</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.3 Communications</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Send service updates, security alerts, and system notifications</li>
                <li>Provide technical support and account assistance</li>
                <li>Send marketing communications (with your consent)</li>
                <li>Conduct surveys and request feedback</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.4 Legal and Compliance</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Comply with legal obligations and regulatory requirements</li>
                <li>Respond to subpoenas, court orders, and legal processes</li>
                <li>Protect our rights, property, and safety</li>
                <li>Enforce our agreements and policies</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.5 Analytics and Research</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Analyze usage patterns and user behavior (aggregated and anonymized)</li>
                <li>Measure feature adoption and platform performance</li>
                <li>Conduct industry research and benchmarking studies</li>
                <li>Improve AI models using aggregated, anonymized data</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Data Sharing and Disclosure</h2>
              <p className="text-gray-700 mb-4">
                We do not sell your personal information. We share information only as described below:
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.1 Service Providers</h3>
              <p className="text-gray-700 mb-4">
                We share information with trusted third-party service providers who perform services on our behalf, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Cloud infrastructure providers (AWS, Azure)</li>
                <li>AI and machine learning platforms (OpenAI)</li>
                <li>Analytics services (Google Analytics, Mixpanel)</li>
                <li>Payment processors (Stripe)</li>
                <li>Email and communication services (SendGrid)</li>
                <li>Security and monitoring tools</li>
              </ul>
              <p className="text-gray-700 mb-4">
                These service providers are contractually obligated to protect your information and use it only for the purposes we specify.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.2 Business Transfers</h3>
              <p className="text-gray-700 mb-4">
                If we are involved in a merger, acquisition, sale of assets, or bankruptcy, your information may be transferred as part of that transaction. We will notify you before your information is transferred and becomes subject to a different privacy policy.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.3 Legal Requirements</h3>
              <p className="text-gray-700 mb-4">
                We may disclose your information if required to do so by law or in response to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Subpoenas, court orders, or legal processes</li>
                <li>Government or regulatory requests</li>
                <li>Investigations of potential violations of law</li>
                <li>Protection of our rights, property, or safety</li>
                <li>Emergencies involving danger to persons or property</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.4 Aggregated and Anonymized Data</h3>
              <p className="text-gray-700 mb-4">
                We may share aggregated, anonymized data that cannot reasonably be used to identify you or your clients. This includes industry benchmarks, usage statistics, and research findings.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.5 With Your Consent</h3>
              <p className="text-gray-700">
                We may share your information for other purposes with your explicit consent.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data Security</h2>
              <p className="text-gray-700 mb-4">
                We implement industry-leading security measures to protect your information:
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.1 Encryption</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>At Rest:</strong> AES-256 encryption for all stored data</li>
                <li><strong>In Transit:</strong> TLS 1.3 encryption for all data transmissions</li>
                <li><strong>Database Encryption:</strong> Encrypted backups and point-in-time recovery</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.2 Access Controls</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Role-based access control (RBAC) with least-privilege principles</li>
                <li>Multi-factor authentication (MFA) requirements</li>
                <li>Row-level security for multi-tenant data isolation</li>
                <li>Audit logging of all data access and modifications</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.3 Infrastructure Security</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>SOC 2 Type II certified infrastructure</li>
                <li>Regular security audits and penetration testing</li>
                <li>24/7 security monitoring and intrusion detection</li>
                <li>Automated vulnerability scanning and patching</li>
                <li>DDoS protection and rate limiting</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.4 Data Retention</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Audit documentation retained for 7 years (SEC 17 CFR 210.2-06)</li>
                <li>WORM (Write Once Read Many) storage for immutability</li>
                <li>Secure data deletion procedures for expired data</li>
              </ul>

              <p className="text-gray-700 mt-6">
                While we implement robust security measures, no system is completely secure. If you become aware of any security vulnerability or breach, please contact us immediately at security@auraaudit.ai.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Rights and Choices</h2>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.1 Access and Correction</h3>
              <p className="text-gray-700 mb-4">
                You have the right to access, update, or correct your personal information. You can update most information through your account settings or by contacting us.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.2 Data Portability</h3>
              <p className="text-gray-700 mb-4">
                You can export your data in machine-readable formats (JSON, CSV, PDF) at any time through the platform.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.3 Data Deletion</h3>
              <p className="text-gray-700 mb-4">
                You can request deletion of your account and associated data, subject to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Legal retention requirements (e.g., 7-year audit documentation retention)</li>
                <li>Ongoing legal obligations or disputes</li>
                <li>Fraud prevention and security purposes</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.4 Marketing Communications</h3>
              <p className="text-gray-700 mb-4">
                You can opt out of marketing emails by clicking "unsubscribe" in any marketing email or updating your preferences in account settings. You cannot opt out of essential service communications.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.5 Cookie Preferences</h3>
              <p className="text-gray-700 mb-4">
                You can manage cookie preferences through your browser settings or our cookie consent banner.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.6 Do Not Track</h3>
              <p className="text-gray-700">
                Our Services do not currently respond to "Do Not Track" browser signals, but you can control tracking through cookie settings.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. International Data Transfers</h2>
              <p className="text-gray-700 mb-4">
                Aura Audit AI is based in the United States. If you access the Services from outside the U.S., your information may be transferred to, stored, and processed in the U.S. or other countries where our service providers operate.
              </p>
              <p className="text-gray-700 mb-4">
                We comply with applicable data protection laws, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>GDPR:</strong> For European users, we use Standard Contractual Clauses and ensure adequate data protection</li>
                <li><strong>Privacy Shield:</strong> We adhere to recognized frameworks for international data transfers</li>
                <li><strong>Data Localization:</strong> We can accommodate data residency requirements upon request</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Cookies and Tracking Technologies</h2>
              <p className="text-gray-700 mb-4">
                We use cookies and similar technologies to collect information and improve the Services.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.1 Types of Cookies</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Essential Cookies:</strong> Required for authentication, security, and core functionality</li>
                <li><strong>Performance Cookies:</strong> Collect analytics data to improve the Services</li>
                <li><strong>Functional Cookies:</strong> Remember your preferences and settings</li>
                <li><strong>Marketing Cookies:</strong> Track marketing campaign performance (with consent)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.2 Third-Party Cookies</h3>
              <p className="text-gray-700 mb-4">
                We use third-party analytics and advertising services that may set cookies:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Google Analytics (anonymized IP addresses)</li>
                <li>Mixpanel (product analytics)</li>
                <li>Segment (data integration platform)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.3 Managing Cookies</h3>
              <p className="text-gray-700">
                You can control cookies through browser settings or our cookie banner. Note that disabling essential cookies may affect functionality.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Children's Privacy</h2>
              <p className="text-gray-700">
                The Services are not intended for children under 16. We do not knowingly collect information from children under 16. If we learn that we have collected information from a child under 16, we will delete it promptly. If you believe we have collected information from a child, please contact us at privacy@auraaudit.ai.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. California Privacy Rights</h2>
              <p className="text-gray-700 mb-4">
                If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA):
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Right to Know:</strong> Request disclosure of personal information we collect, use, and disclose</li>
                <li><strong>Right to Delete:</strong> Request deletion of your personal information (subject to exceptions)</li>
                <li><strong>Right to Opt-Out:</strong> Opt out of sale of personal information (we do not sell personal information)</li>
                <li><strong>Right to Non-Discrimination:</strong> We will not discriminate against you for exercising your rights</li>
              </ul>
              <p className="text-gray-700">
                To exercise these rights, contact us at privacy@auraaudit.ai or call (555) 123-4567.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Changes to This Privacy Policy</h2>
              <p className="text-gray-700 mb-4">
                We may update this Privacy Policy from time to time to reflect changes in our practices, technology, legal requirements, or other factors. We will notify you of material changes by:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Posting a notice on our website</li>
                <li>Sending an email to the address associated with your account</li>
                <li>Displaying a notice when you log in to the platform</li>
              </ul>
              <p className="text-gray-700">
                The "Last Updated" date at the top of this policy indicates when it was last revised. Your continued use of the Services after the effective date constitutes acceptance of the updated Privacy Policy.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Contact Us</h2>
              <p className="text-gray-700 mb-4">
                If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <p className="text-gray-700 mb-2"><strong>Aura Audit AI - Privacy Team</strong></p>
                <p className="text-gray-700 mb-2">Email: privacy@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Security Issues: security@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Address: 1234 Audit Way, Suite 100, Wilmington, DE 19801</p>
                <p className="text-gray-700 mb-2">Phone: (555) 123-4567</p>
                <p className="text-gray-700 mt-4 text-sm">
                  <strong>Data Protection Officer:</strong> For GDPR-related inquiries, contact dpo@auraaudit.ai
                </p>
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8">
              <p className="text-sm text-gray-600 italic">
                This Privacy Policy is effective as of November 14, 2025. By using Aura Audit AI, you acknowledge that you have read and understood this Privacy Policy and agree to its terms.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
