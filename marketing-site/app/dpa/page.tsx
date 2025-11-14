'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { FileText, Download, Shield } from 'lucide-react'

export default function DataProcessingAgreement() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <div className="pt-32 pb-16">
        <div className="section-container max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl lg:text-5xl font-display font-bold text-gray-900">
                Data Processing Agreement
              </h1>
              <p className="text-gray-600 mt-2">
                Last Updated: November 14, 2025
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-start gap-3">
              <Shield className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <p className="text-blue-900 font-semibold mb-2">GDPR & Enterprise Compliance</p>
                <p className="text-blue-800 text-sm">
                  This Data Processing Agreement (DPA) is designed for enterprise customers who require GDPR compliance and detailed data processing terms. It supplements our standard Terms of Service and Privacy Policy.
                </p>
              </div>
            </div>
          </div>

          <div className="prose prose-lg max-w-none">
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 mb-4">
                This Data Processing Agreement ("DPA") forms part of the service agreement between Aura Audit AI ("Processor," "we," "our") and you, the customer ("Controller," "you," "your"), and governs the processing of Personal Data (as defined by the GDPR) in connection with the Services.
              </p>
              <p className="text-gray-700 mb-4">
                This DPA applies when:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>You are subject to European data protection laws (GDPR)</li>
                <li>Personal Data of EU residents is processed through our Services</li>
                <li>You require a formal DPA for regulatory compliance</li>
                <li>Your organization's data protection officer requires executed DPA terms</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Definitions</h2>
              <p className="text-gray-700 mb-4">
                For the purposes of this DPA, the following definitions apply:
              </p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-4 text-sm">
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Controller"</p>
                  <p className="text-gray-700">The entity that determines the purposes and means of processing Personal Data (you, the customer).</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Processor"</p>
                  <p className="text-gray-700">The entity that processes Personal Data on behalf of the Controller (Aura Audit AI).</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Personal Data"</p>
                  <p className="text-gray-700">Any information relating to an identified or identifiable natural person, as defined by the GDPR.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Processing"</p>
                  <p className="text-gray-700">Any operation performed on Personal Data, including collection, storage, use, disclosure, or deletion.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Sub-processor"</p>
                  <p className="text-gray-700">Any third party engaged by the Processor to process Personal Data on behalf of the Controller.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"Data Subject"</p>
                  <p className="text-gray-700">An identified or identifiable natural person whose Personal Data is processed.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">"GDPR"</p>
                  <p className="text-gray-700">The General Data Protection Regulation (EU) 2016/679.</p>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Scope and Roles</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.1 Data Controller and Processor</h3>
              <p className="text-gray-700 mb-4">
                <strong>You (the Controller)</strong> determine the purposes and means of processing Personal Data. You are responsible for:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Ensuring lawful basis for processing under GDPR</li>
                <li>Obtaining necessary consents from Data Subjects</li>
                <li>Providing privacy notices to Data Subjects</li>
                <li>Responding to Data Subject rights requests</li>
                <li>Conducting Data Protection Impact Assessments (DPIAs) when required</li>
              </ul>

              <p className="text-gray-700 mb-4">
                <strong>We (the Processor)</strong> process Personal Data solely on your documented instructions. We are responsible for:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Processing Personal Data only as instructed by you</li>
                <li>Implementing appropriate technical and organizational measures</li>
                <li>Ensuring confidentiality of personnel who process Personal Data</li>
                <li>Assisting with Data Subject rights requests</li>
                <li>Assisting with data breach notifications</li>
                <li>Deleting or returning Personal Data upon termination</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">3.2 Subject Matter and Duration</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Subject Matter:</strong> Provision of AI-powered audit automation services</li>
                <li><strong>Duration:</strong> For the term of your service agreement with us</li>
                <li><strong>Nature and Purpose:</strong> Processing of financial, audit, and client data to deliver audit automation services</li>
                <li><strong>Types of Personal Data:</strong> Names, email addresses, financial data, business contact information</li>
                <li><strong>Categories of Data Subjects:</strong> Your employees, clients, and their employees</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Processing Instructions</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.1 Scope of Instructions</h3>
              <p className="text-gray-700 mb-4">
                We will process Personal Data only:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>As necessary to provide the Services under our service agreement</li>
                <li>As documented in this DPA and our Terms of Service</li>
                <li>As instructed by you through use of the Services</li>
                <li>As required by applicable law (with notice to you when legally permissible)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">4.2 Prohibited Processing</h3>
              <p className="text-gray-700 mb-4">
                We will not:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Sell or rent Personal Data to third parties</li>
                <li>Use Personal Data for our own purposes except as permitted by GDPR (e.g., anonymized analytics)</li>
                <li>Process Personal Data outside your instructions without your prior written consent</li>
                <li>Combine Personal Data with data from other sources for profiling or targeted advertising</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Sub-processors</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.1 Authorization</h3>
              <p className="text-gray-700 mb-4">
                You authorize us to engage Sub-processors to assist in providing the Services, subject to the conditions in this section.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.2 Current Sub-processors</h3>
              <p className="text-gray-700 mb-4">
                We currently engage the following Sub-processors:
              </p>
              <div className="overflow-x-auto mb-6">
                <table className="min-w-full border border-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Sub-processor</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Service Provided</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-900 border-b">Location</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700">
                    <tr className="border-b">
                      <td className="px-4 py-3">Amazon Web Services (AWS)</td>
                      <td className="px-4 py-3">Cloud infrastructure and data storage</td>
                      <td className="px-4 py-3">United States (us-east-1)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">Microsoft Azure</td>
                      <td className="px-4 py-3">Alternative cloud infrastructure</td>
                      <td className="px-4 py-3">United States / EU (customer choice)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">OpenAI</td>
                      <td className="px-4 py-3">AI model API services</td>
                      <td className="px-4 py-3">United States</td>
                    </tr>
                    <tr className="border-b">
                      <td className="px-4 py-3">Stripe</td>
                      <td className="px-4 py-3">Payment processing</td>
                      <td className="px-4 py-3">United States</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3">SendGrid</td>
                      <td className="px-4 py-3">Email delivery services</td>
                      <td className="px-4 py-3">United States</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.3 Sub-processor Changes</h3>
              <p className="text-gray-700 mb-4">
                We will provide at least 30 days' advance notice of:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Addition of new Sub-processors</li>
                <li>Replacement of existing Sub-processors</li>
              </ul>
              <p className="text-gray-700 mb-4">
                If you object to a new Sub-processor on reasonable data protection grounds, you may:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Request that we use an alternative Sub-processor (if technically feasible)</li>
                <li>Terminate the service agreement with 30 days' notice</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">5.4 Sub-processor Obligations</h3>
              <p className="text-gray-700 mb-4">
                We ensure that all Sub-processors:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Are bound by written agreements with data protection obligations equivalent to this DPA</li>
                <li>Implement appropriate technical and organizational measures</li>
                <li>Are subject to regular audits and assessments</li>
                <li>Provide Standard Contractual Clauses for international data transfers</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Technical and Organizational Measures</h2>
              <p className="text-gray-700 mb-4">
                We implement and maintain the following security measures to protect Personal Data:
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.1 Encryption</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>AES-256 encryption for data at rest</li>
                <li>TLS 1.3 encryption for data in transit</li>
                <li>Encrypted database backups</li>
                <li>Encryption key management through AWS KMS or Azure Key Vault</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.2 Access Controls</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Role-based access control (RBAC) with least-privilege principles</li>
                <li>Multi-factor authentication (MFA) required for all access</li>
                <li>Row-level security for multi-tenant data isolation</li>
                <li>Automated session timeout after 8 hours</li>
                <li>Regular access reviews and deprovisioning procedures</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.3 Data Minimization</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Collection of only data necessary for service provision</li>
                <li>Automated data retention policies</li>
                <li>Secure deletion procedures for expired data</li>
                <li>Anonymization for analytics and reporting</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.4 System Security</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>SOC 2 Type II certified infrastructure</li>
                <li>24/7 security monitoring and intrusion detection</li>
                <li>Regular penetration testing and vulnerability assessments</li>
                <li>Automated security patching and updates</li>
                <li>DDoS protection and rate limiting</li>
                <li>Incident response and disaster recovery plans</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.5 Personnel Security</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Background checks for all employees with data access</li>
                <li>Confidentiality agreements and data protection training</li>
                <li>Need-to-know access policies</li>
                <li>Regular security awareness training</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">6.6 Audit and Logging</h3>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Comprehensive audit logging of all data access and modifications</li>
                <li>Immutable log storage with 7-year retention</li>
                <li>Real-time alerting for suspicious activities</li>
                <li>Regular log reviews and anomaly detection</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Data Subject Rights</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.1 Assistance with Rights Requests</h3>
              <p className="text-gray-700 mb-4">
                We will assist you in fulfilling Data Subject rights requests, including:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li><strong>Right of Access:</strong> Provide copies of Personal Data</li>
                <li><strong>Right to Rectification:</strong> Correct inaccurate Personal Data</li>
                <li><strong>Right to Erasure:</strong> Delete Personal Data (subject to legal obligations)</li>
                <li><strong>Right to Restriction:</strong> Limit processing of Personal Data</li>
                <li><strong>Right to Portability:</strong> Export Personal Data in machine-readable format</li>
                <li><strong>Right to Object:</strong> Object to certain processing activities</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.2 Response Timeframe</h3>
              <p className="text-gray-700 mb-4">
                We will respond to your requests for assistance within 5 business days and provide reasonable cooperation to help you meet GDPR's 30-day response requirement.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">7.3 Fees</h3>
              <p className="text-gray-700">
                Assistance with Data Subject rights requests is included in your subscription. We may charge reasonable fees for excessive, repetitive, or manifestly unfounded requests.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Data Breaches</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.1 Notification</h3>
              <p className="text-gray-700 mb-4">
                We will notify you without undue delay (and in any event within 72 hours) after becoming aware of a Personal Data breach affecting your data.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.2 Breach Information</h3>
              <p className="text-gray-700 mb-4">
                Our notification will include:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Description of the breach and affected Personal Data</li>
                <li>Likely consequences of the breach</li>
                <li>Measures taken or proposed to address the breach</li>
                <li>Contact information for further inquiries</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">8.3 Cooperation</h3>
              <p className="text-gray-700">
                We will cooperate with you and provide reasonable assistance in investigating and remediating the breach, and in meeting your obligations to notify supervisory authorities and affected Data Subjects.
              </p>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. International Data Transfers</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">9.1 Standard Contractual Clauses</h3>
              <p className="text-gray-700 mb-4">
                For transfers of Personal Data from the European Economic Area (EEA) to countries without an adequacy decision, we rely on:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Standard Contractual Clauses (SCCs) approved by the European Commission</li>
                <li>Supplementary measures to ensure adequate data protection</li>
                <li>Transfer Impact Assessments where required</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">9.2 Data Localization Options</h3>
              <p className="text-gray-700 mb-4">
                For enterprise customers, we can accommodate data residency requirements:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>EU-based data storage (Azure West Europe)</li>
                <li>Restricted data transfers outside your jurisdiction</li>
                <li>Custom data processing locations (subject to technical feasibility)</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Audits and Compliance</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">10.1 Audit Rights</h3>
              <p className="text-gray-700 mb-4">
                Upon reasonable notice, you may:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Request copies of our SOC 2 Type II reports and security certifications</li>
                <li>Submit written questions about our data protection practices</li>
                <li>Request evidence of compliance with this DPA</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">10.2 On-Site Audits</h3>
              <p className="text-gray-700 mb-4">
                If you require an on-site audit:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Provide at least 60 days' advance notice</li>
                <li>Conduct audits no more than once per year (unless required by supervisory authority)</li>
                <li>Execute mutual non-disclosure agreements</li>
                <li>Bear costs of the audit (unless significant non-compliance is found)</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Data Deletion and Return</h2>
              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">11.1 Upon Termination</h3>
              <p className="text-gray-700 mb-4">
                Upon termination of the service agreement, we will:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Provide you with 30 days to export your data</li>
                <li>Delete all Personal Data within 90 days after termination</li>
                <li>Provide certification of deletion upon request</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">11.2 Exceptions</h3>
              <p className="text-gray-700 mb-4">
                We may retain Personal Data to the extent required by:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Legal obligations (e.g., 7-year audit documentation retention)</li>
                <li>Pending litigation or investigations</li>
                <li>Backup systems (deleted within 90 days)</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Limitation of Liability</h2>
              <p className="text-gray-700 mb-4">
                Each party's liability under this DPA is subject to the limitation of liability provisions in the service agreement. However, nothing in this DPA limits either party's liability for:
              </p>
              <ul className="list-disc pl-6 mb-4 text-gray-700 space-y-2">
                <li>Violations of data protection laws</li>
                <li>Data breaches caused by gross negligence or willful misconduct</li>
                <li>Unauthorized disclosure of Personal Data</li>
              </ul>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">13. How to Execute This DPA</h2>
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
                <p className="text-primary-900 font-semibold mb-3">Enterprise Customers</p>
                <p className="text-primary-800 mb-4">
                  To execute this DPA for your organization, please contact us at:
                </p>
                <div className="space-y-2 text-primary-800">
                  <p><strong>Email:</strong> dpa@auraaudit.ai</p>
                  <p><strong>Subject:</strong> DPA Execution Request - [Your Company Name]</p>
                  <p><strong>Include:</strong></p>
                  <ul className="list-disc pl-6 space-y-1 text-sm">
                    <li>Your company's legal name and registration details</li>
                    <li>Contact information for your data protection officer (if applicable)</li>
                    <li>Any specific data processing requirements or restrictions</li>
                    <li>Preferred data residency location (if applicable)</li>
                  </ul>
                </div>
                <div className="mt-4 pt-4 border-t border-primary-300">
                  <a
                    href="mailto:dpa@auraaudit.ai?subject=DPA Execution Request"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                  >
                    <Download className="w-5 h-5" />
                    Request DPA Execution
                  </a>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">14. Contact Information</h2>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <p className="text-gray-700 mb-2"><strong>Aura Audit AI - Data Protection Team</strong></p>
                <p className="text-gray-700 mb-2">Email: dpa@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Data Protection Officer: dpo@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Privacy Team: privacy@auraaudit.ai</p>
                <p className="text-gray-700 mb-2">Address: 1234 Audit Way, Suite 100, Wilmington, DE 19801</p>
                <p className="text-gray-700">Phone: (555) 123-4567</p>
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8">
              <p className="text-sm text-gray-600 italic">
                This Data Processing Agreement is effective as of November 14, 2025, and supplements our Terms of Service and Privacy Policy. For standard (non-enterprise) customers, our Privacy Policy governs data processing practices.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
