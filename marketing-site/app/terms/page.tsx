'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'

export default function TermsOfService() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <div className="pt-32 pb-16">
        <div className="section-container max-w-4xl mx-auto">
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
            Terms of Service
          </h1>
          <p className="text-gray-600 mb-8">
            Last Updated: November 14, 2025
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 mb-4">
                Welcome to Aura Audit AI. These Terms of Service ("Terms") govern your access to and use of the Aura Audit AI platform, website, and related services (collectively, the "Services"). By accessing or using our Services, you agree to be bound by these Terms.
              </p>
              <p className="text-gray-700 mb-4">
                If you are using the Services on behalf of an organization, you represent and warrant that you have the authority to bind that organization to these Terms, and "you" refers to both you as an individual and the organization you represent.
              </p>
              <p className="text-gray-700">
                If you do not agree to these Terms, you may not access or use the Services.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Description of Services</h2>
              <p className="text-gray-700 mb-4">
                Aura Audit AI provides an enterprise-grade, AI-powered audit automation platform designed for CPA firms and professional auditors. Our Services include:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Automated trial balance normalization and account mapping</li>
                <li>AI-powered journal entry testing and anomaly detection</li>
                <li>Analytical procedures and ratio analysis</li>
                <li>Automated workpaper generation and management</li>
                <li>Disclosure note drafting with AI assistance</li>
                <li>Quality control gates and compliance checks</li>
                <li>Document management and audit trail capabilities</li>
                <li>Integration with accounting systems and third-party services</li>
              </ul>
              <p className="text-gray-700">
                We reserve the right to modify, suspend, or discontinue any part of the Services at any time with reasonable notice to users.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Accounts and Registration</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.1 Account Creation</h3>
              <p className="text-gray-700 mb-4">
                To access the Services, you must create an account and provide accurate, complete, and current information. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.2 Account Security</h3>
              <p className="text-gray-700 mb-4">
                You must immediately notify us of any unauthorized access to or use of your account. We are not liable for any loss or damage arising from your failure to comply with account security requirements.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.3 Account Termination</h3>
              <p className="text-gray-700">
                We reserve the right to suspend or terminate your account if you violate these Terms or engage in fraudulent, illegal, or abusive behavior.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Professional Standards and Use</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.1 Professional Responsibility</h3>
              <p className="text-gray-700 mb-4">
                The Services are tools designed to assist professional auditors and CPAs in performing their work. Users remain solely responsible for:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Exercising professional judgment in all audit decisions</li>
                <li>Reviewing and validating all AI-generated content and recommendations</li>
                <li>Ensuring compliance with applicable professional standards (PCAOB, AICPA, GAAP, etc.)</li>
                <li>Meeting all regulatory and licensing requirements</li>
                <li>Maintaining independence and objectivity standards</li>
              </ul>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.2 No Substitute for Professional Judgment</h3>
              <p className="text-gray-700 mb-4">
                Our AI-powered tools provide suggestions and automate routine tasks, but do not replace the professional judgment, expertise, and responsibility of licensed CPAs and auditors. All output must be reviewed and validated by qualified professionals.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.3 Compliance</h3>
              <p className="text-gray-700">
                You agree to use the Services in compliance with all applicable laws, regulations, and professional standards, including but not limited to SEC regulations, PCAOB standards, AICPA code of professional conduct, and state CPA board requirements.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data and Content</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.1 Your Data</h3>
              <p className="text-gray-700 mb-4">
                You retain all ownership rights to the data you upload to the Services ("Your Data"). By uploading Your Data, you grant us a limited license to use, process, and store Your Data solely to provide and improve the Services.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.2 Data Security</h3>
              <p className="text-gray-700 mb-4">
                We implement industry-standard security measures to protect Your Data, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>AES-256 encryption at rest</li>
                <li>TLS 1.3 encryption in transit</li>
                <li>SOC 2 Type II compliance</li>
                <li>Role-based access controls</li>
                <li>Regular security audits and penetration testing</li>
                <li>7-year retention with WORM storage for audit documentation</li>
              </ul>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.3 Confidentiality</h3>
              <p className="text-gray-700 mb-4">
                We understand that Your Data may include confidential client information subject to professional confidentiality obligations. We treat all Your Data as confidential and will not disclose it to third parties except as necessary to provide the Services or as required by law.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.4 AI Model Training</h3>
              <p className="text-gray-700 mb-4">
                We may use aggregated, anonymized data to improve our AI models and Services. We will never use Your Data to train models in a way that could expose confidential information or identify specific clients.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Acceptable Use</h2>
              <p className="text-gray-700 mb-4">You agree not to:</p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Use the Services for any unlawful purpose or in violation of these Terms</li>
                <li>Attempt to gain unauthorized access to the Services or related systems</li>
                <li>Interfere with or disrupt the integrity or performance of the Services</li>
                <li>Reverse engineer, decompile, or disassemble any aspect of the Services</li>
                <li>Use automated scripts or bots to access the Services without permission</li>
                <li>Share your account credentials with unauthorized individuals</li>
                <li>Upload malicious code, viruses, or harmful content</li>
                <li>Use the Services to compete with Aura Audit AI or develop competing products</li>
                <li>Remove or modify any proprietary notices or labels</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Subscription and Payment</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.1 Subscription Plans</h3>
              <p className="text-gray-700 mb-4">
                Access to the Services is provided on a subscription basis. Subscription plans, pricing, and features are described on our website and in your service agreement.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.2 Payment Terms</h3>
              <p className="text-gray-700 mb-4">
                Subscription fees are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law or as expressly stated in your service agreement.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.3 Price Changes</h3>
              <p className="text-gray-700 mb-4">
                We may change our pricing with 30 days' notice. Price changes will apply at your next renewal period.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.4 Late Payment</h3>
              <p className="text-gray-700">
                If payment is not received by the due date, we may suspend access to the Services until payment is received. We reserve the right to charge late fees and interest on overdue amounts.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Intellectual Property</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.1 Our IP</h3>
              <p className="text-gray-700 mb-4">
                The Services, including all software, algorithms, AI models, designs, text, graphics, and other content, are owned by Aura Audit AI and are protected by copyright, trademark, patent, and other intellectual property laws.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.2 Limited License</h3>
              <p className="text-gray-700 mb-4">
                We grant you a limited, non-exclusive, non-transferable license to access and use the Services for your internal business purposes in accordance with these Terms. This license does not include the right to sublicense, resell, or redistribute the Services.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.3 Feedback</h3>
              <p className="text-gray-700">
                If you provide feedback, suggestions, or ideas about the Services, we may use them without any obligation to you.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Warranties and Disclaimers</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">9.1 Service Availability</h3>
              <p className="text-gray-700 mb-4">
                We strive to provide reliable Services with 99.9% uptime, but we do not guarantee that the Services will be available at all times or free from errors.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">9.2 Disclaimer</h3>
              <p className="text-gray-700 mb-4 font-semibold uppercase">
                THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
              </p>
              <p className="text-gray-700">
                We do not warrant that the Services will meet your requirements, operate without interruption, be error-free, or that defects will be corrected.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-700 mb-4 font-semibold uppercase">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, AURA AUDIT AI SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, REVENUE, DATA, OR GOODWILL ARISING OUT OF OR RELATED TO YOUR USE OF THE SERVICES.
              </p>
              <p className="text-gray-700 mb-4">
                Our total liability to you for all claims arising out of or related to these Terms or the Services shall not exceed the amount you paid us in the 12 months preceding the claim.
              </p>
              <p className="text-gray-700">
                Some jurisdictions do not allow the exclusion or limitation of certain warranties or liabilities, so these limitations may not apply to you.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Indemnification</h2>
              <p className="text-gray-700">
                You agree to indemnify, defend, and hold harmless Aura Audit AI, its affiliates, officers, directors, employees, and agents from any claims, liabilities, damages, losses, and expenses (including reasonable attorneys' fees) arising out of or related to:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Your use of the Services</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any law or regulation</li>
                <li>Your violation of any third-party rights</li>
                <li>Your Data or any content you submit to the Services</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Term and Termination</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">12.1 Term</h3>
              <p className="text-gray-700 mb-4">
                These Terms remain in effect for as long as you access or use the Services.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">12.2 Termination by You</h3>
              <p className="text-gray-700 mb-4">
                You may terminate your account at any time by contacting our support team. Upon termination, you will remain responsible for all fees incurred prior to termination.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">12.3 Termination by Us</h3>
              <p className="text-gray-700 mb-4">
                We may suspend or terminate your access to the Services immediately if you violate these Terms or engage in fraudulent or illegal activity.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">12.4 Effect of Termination</h3>
              <p className="text-gray-700">
                Upon termination, your right to access the Services will cease immediately. We will provide you with a reasonable opportunity to export Your Data. Provisions that by their nature should survive termination will continue to apply.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Dispute Resolution</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">13.1 Governing Law</h3>
              <p className="text-gray-700 mb-4">
                These Terms are governed by the laws of the State of Delaware, without regard to conflict of law principles.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">13.2 Arbitration</h3>
              <p className="text-gray-700 mb-4">
                Any dispute arising out of or related to these Terms or the Services shall be resolved through binding arbitration in accordance with the American Arbitration Association's Commercial Arbitration Rules. The arbitration shall be conducted in Delaware.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">13.3 Exceptions</h3>
              <p className="text-gray-700">
                Either party may seek injunctive relief in court for violations of intellectual property rights or confidentiality obligations.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">14. Changes to Terms</h2>
              <p className="text-gray-700 mb-4">
                We may update these Terms from time to time. We will notify you of material changes by email or through the Services at least 30 days before the changes take effect. Your continued use of the Services after the effective date constitutes acceptance of the updated Terms.
              </p>
              <p className="text-gray-700">
                If you do not agree to the updated Terms, you must stop using the Services and may terminate your account.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">15. General Provisions</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">15.1 Entire Agreement</h3>
              <p className="text-gray-700 mb-4">
                These Terms, together with your service agreement and our Privacy Policy, constitute the entire agreement between you and Aura Audit AI regarding the Services.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">15.2 Severability</h3>
              <p className="text-gray-700 mb-4">
                If any provision of these Terms is found to be invalid or unenforceable, the remaining provisions will remain in full force and effect.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">15.3 Waiver</h3>
              <p className="text-gray-700 mb-4">
                Our failure to enforce any provision of these Terms does not constitute a waiver of that provision.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">15.4 Assignment</h3>
              <p className="text-gray-700 mb-4">
                You may not assign or transfer these Terms or your account without our prior written consent. We may assign these Terms without restriction.
              </p>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">15.5 Force Majeure</h3>
              <p className="text-gray-700">
                We are not liable for any failure or delay in performance due to circumstances beyond our reasonable control, including natural disasters, acts of terrorism, labor disputes, or internet outages.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">16. Contact Information</h2>
              <p className="text-gray-700 mb-4">
                If you have questions about these Terms, please contact us:
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <p className="text-gray-700 mb-2"><strong>Aura Audit AI</strong></p>
                <p className="text-gray-700 mb-2">Email: legal@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Address: 1234 Audit Way, Suite 100, Wilmington, DE 19801</p>
                <p className="text-gray-700">Phone: (555) 123-4567</p>
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8">
              <p className="text-sm text-gray-600 italic">
                These Terms of Service are effective as of November 14, 2025. By using Aura Audit AI, you acknowledge that you have read, understood, and agree to be bound by these Terms.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
