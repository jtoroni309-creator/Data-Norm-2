import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Bug,
  Lightbulb,
  HelpCircle,
  Send,
  CheckCircle2,
  Clock,
  AlertCircle,
  Upload,
  X,
  ExternalLink,
  Search,
  Filter,
} from 'lucide-react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

type TicketType = 'bug' | 'feature' | 'support';
type Priority = 'Low' | 'Medium' | 'High' | 'Critical';
type TicketStatus = 'Open' | 'In Progress' | 'Resolved' | 'Closed';

interface Ticket {
  key: string;
  summary: string;
  description: string;
  status: TicketStatus;
  priority: Priority;
  created: string;
  updated: string;
  reporter: string;
  assignee?: string;
  labels: string[];
  url: string;
}

interface BugReportForm {
  summary: string;
  description: string;
  priority: Priority;
  environment?: string;
  stepsToReproduce?: string;
  expectedBehavior?: string;
  actualBehavior?: string;
  screenshot?: File;
}

interface FeatureRequestForm {
  summary: string;
  description: string;
  priority: Priority;
  businessValue?: string;
  useCase?: string;
}

interface SupportTicketForm {
  summary: string;
  description: string;
  priority: Priority;
  category?: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const SupportCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'submit' | 'my-tickets'>('submit');
  const [ticketType, setTicketType] = useState<TicketType>('bug');
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [bugForm, setBugForm] = useState<BugReportForm>({
    summary: '',
    description: '',
    priority: 'Medium',
    environment: '',
    stepsToReproduce: '',
    expectedBehavior: '',
    actualBehavior: '',
  });

  const [featureForm, setFeatureForm] = useState<FeatureRequestForm>({
    summary: '',
    description: '',
    priority: 'Medium',
    businessValue: '',
    useCase: '',
  });

  const [supportForm, setSupportForm] = useState<SupportTicketForm>({
    summary: '',
    description: '',
    priority: 'Medium',
    category: 'technical',
  });

  // Load user's tickets
  useEffect(() => {
    if (activeTab === 'my-tickets') {
      loadMyTickets();
    }
  }, [activeTab]);

  const loadMyTickets = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const tenant = JSON.parse(localStorage.getItem('tenant') || '{}');

      const response = await fetch(
        `/api/jira/my-tickets?email=${user.email}&customer_id=${tenant.id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTickets(data);
      }
    } catch (error) {
      console.error('Failed to load tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // FORM SUBMISSION HANDLERS
  // ============================================================================

  const submitBugReport = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const tenant = JSON.parse(localStorage.getItem('tenant') || '{}');

      const response = await fetch('/api/jira/bug-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          summary: bugForm.summary,
          description: bugForm.description,
          reporter_email: user.email,
          customer_id: tenant.id,
          priority: bugForm.priority,
          environment: bugForm.environment,
          steps_to_reproduce: bugForm.stepsToReproduce,
          expected_behavior: bugForm.expectedBehavior,
          actual_behavior: bugForm.actualBehavior,
        }),
      });

      if (response.ok) {
        setSubmitSuccess(true);
        setBugForm({
          summary: '',
          description: '',
          priority: 'Medium',
          environment: '',
          stepsToReproduce: '',
          expectedBehavior: '',
          actualBehavior: '',
        });
        setTimeout(() => setSubmitSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to submit bug report:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitFeatureRequest = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const tenant = JSON.parse(localStorage.getItem('tenant') || '{}');

      const response = await fetch('/api/jira/feature-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          summary: featureForm.summary,
          description: featureForm.description,
          requester_email: user.email,
          customer_id: tenant.id,
          priority: featureForm.priority,
          business_value: featureForm.businessValue,
          use_case: featureForm.useCase,
        }),
      });

      if (response.ok) {
        setSubmitSuccess(true);
        setFeatureForm({
          summary: '',
          description: '',
          priority: 'Medium',
          businessValue: '',
          useCase: '',
        });
        setTimeout(() => setSubmitSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to submit feature request:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitSupportTicket = async () => {
    try {
      setLoading(true);
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const tenant = JSON.parse(localStorage.getItem('tenant') || '{}');

      const response = await fetch('/api/jira/support-ticket', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          summary: supportForm.summary,
          description: supportForm.description,
          requester_email: user.email,
          customer_id: tenant.id,
          priority: supportForm.priority,
          category: supportForm.category,
        }),
      });

      if (response.ok) {
        setSubmitSuccess(true);
        setSupportForm({
          summary: '',
          description: '',
          priority: 'Medium',
          category: 'technical',
        });
        setTimeout(() => setSubmitSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to submit support ticket:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (ticketType === 'bug') await submitBugReport();
    else if (ticketType === 'feature') await submitFeatureRequest();
    else await submitSupportTicket();
  };

  // ============================================================================
  // FILTERED TICKETS
  // ============================================================================

  const filteredTickets = tickets.filter((ticket) => {
    const matchesStatus = filterStatus === 'all' || ticket.status === filterStatus;
    const matchesSearch =
      searchQuery === '' ||
      ticket.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Support Center</h1>
          <p className="text-gray-600">
            Report bugs, request features, or get help from our support team
          </p>
        </motion.div>

        {/* Tabs */}
        <div className="flex space-x-2 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('submit')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'submit'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Submit Ticket
          </button>
          <button
            onClick={() => setActiveTab('my-tickets')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'my-tickets'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            My Tickets
          </button>
        </div>

        {/* Submit Ticket Tab */}
        {activeTab === 'submit' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Ticket Type Selection */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Type</h2>

              <button
                onClick={() => setTicketType('bug')}
                className={`w-full p-6 rounded-lg border-2 transition-all ${
                  ticketType === 'bug'
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Bug className={`w-8 h-8 mb-3 ${ticketType === 'bug' ? 'text-red-500' : 'text-gray-400'}`} />
                <h3 className="font-semibold text-lg mb-2">Bug Report</h3>
                <p className="text-sm text-gray-600">
                  Report issues or errors you've encountered
                </p>
              </button>

              <button
                onClick={() => setTicketType('feature')}
                className={`w-full p-6 rounded-lg border-2 transition-all ${
                  ticketType === 'feature'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Lightbulb className={`w-8 h-8 mb-3 ${ticketType === 'feature' ? 'text-blue-500' : 'text-gray-400'}`} />
                <h3 className="font-semibold text-lg mb-2">Feature Request</h3>
                <p className="text-sm text-gray-600">
                  Suggest new features or improvements
                </p>
              </button>

              <button
                onClick={() => setTicketType('support')}
                className={`w-full p-6 rounded-lg border-2 transition-all ${
                  ticketType === 'support'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <HelpCircle className={`w-8 h-8 mb-3 ${ticketType === 'support' ? 'text-green-500' : 'text-gray-400'}`} />
                <h3 className="font-semibold text-lg mb-2">Support Ticket</h3>
                <p className="text-sm text-gray-600">
                  Get help with billing, training, or general questions
                </p>
              </button>
            </motion.div>

            {/* Ticket Form */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="lg:col-span-2"
            >
              <div className="bg-white rounded-xl shadow-lg p-8">
                <form onSubmit={handleSubmit}>
                  {/* Bug Report Form */}
                  {ticketType === 'bug' && (
                    <>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">Report a Bug</h2>

                      <div className="space-y-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Summary *
                          </label>
                          <input
                            type="text"
                            value={bugForm.summary}
                            onChange={(e) => setBugForm({ ...bugForm, summary: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="Brief description of the issue"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Priority *
                          </label>
                          <select
                            value={bugForm.priority}
                            onChange={(e) =>
                              setBugForm({ ...bugForm, priority: e.target.value as Priority })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="Low">Low - Minor inconvenience</option>
                            <option value="Medium">Medium - Affects workflow</option>
                            <option value="High">High - Major functionality broken</option>
                            <option value="Critical">Critical - System unusable</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description *
                          </label>
                          <textarea
                            value={bugForm.description}
                            onChange={(e) => setBugForm({ ...bugForm, description: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={4}
                            placeholder="Detailed description of the bug"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Steps to Reproduce
                          </label>
                          <textarea
                            value={bugForm.stepsToReproduce}
                            onChange={(e) =>
                              setBugForm({ ...bugForm, stepsToReproduce: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={3}
                            placeholder="1. Go to...\n2. Click on...\n3. See error..."
                          />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Expected Behavior
                            </label>
                            <textarea
                              value={bugForm.expectedBehavior}
                              onChange={(e) =>
                                setBugForm({ ...bugForm, expectedBehavior: e.target.value })
                              }
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                              rows={2}
                              placeholder="What should happen"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Actual Behavior
                            </label>
                            <textarea
                              value={bugForm.actualBehavior}
                              onChange={(e) =>
                                setBugForm({ ...bugForm, actualBehavior: e.target.value })
                              }
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                              rows={2}
                              placeholder="What actually happens"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Environment
                          </label>
                          <input
                            type="text"
                            value={bugForm.environment}
                            onChange={(e) => setBugForm({ ...bugForm, environment: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="Browser, OS, etc."
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {/* Feature Request Form */}
                  {ticketType === 'feature' && (
                    <>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">Request a Feature</h2>

                      <div className="space-y-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Feature Title *
                          </label>
                          <input
                            type="text"
                            value={featureForm.summary}
                            onChange={(e) =>
                              setFeatureForm({ ...featureForm, summary: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="What feature would you like?"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Priority *
                          </label>
                          <select
                            value={featureForm.priority}
                            onChange={(e) =>
                              setFeatureForm({ ...featureForm, priority: e.target.value as Priority })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="Low">Low - Nice to have</option>
                            <option value="Medium">Medium - Would improve workflow</option>
                            <option value="High">High - Important for our business</option>
                            <option value="Critical">Critical - Blocking our adoption</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description *
                          </label>
                          <textarea
                            value={featureForm.description}
                            onChange={(e) =>
                              setFeatureForm({ ...featureForm, description: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={4}
                            placeholder="Describe the feature in detail"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Use Case
                          </label>
                          <textarea
                            value={featureForm.useCase}
                            onChange={(e) =>
                              setFeatureForm({ ...featureForm, useCase: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={3}
                            placeholder="How would you use this feature?"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Business Value
                          </label>
                          <textarea
                            value={featureForm.businessValue}
                            onChange={(e) =>
                              setFeatureForm({ ...featureForm, businessValue: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={3}
                            placeholder="How would this benefit your business?"
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {/* Support Ticket Form */}
                  {ticketType === 'support' && (
                    <>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">Get Support</h2>

                      <div className="space-y-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Subject *
                          </label>
                          <input
                            type="text"
                            value={supportForm.summary}
                            onChange={(e) =>
                              setSupportForm({ ...supportForm, summary: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="What do you need help with?"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Category *
                          </label>
                          <select
                            value={supportForm.category}
                            onChange={(e) =>
                              setSupportForm({ ...supportForm, category: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="technical">Technical Support</option>
                            <option value="billing">Billing Question</option>
                            <option value="training">Training Request</option>
                            <option value="account">Account Management</option>
                            <option value="other">Other</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Priority *
                          </label>
                          <select
                            value={supportForm.priority}
                            onChange={(e) =>
                              setSupportForm({ ...supportForm, priority: e.target.value as Priority })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          >
                            <option value="Low">Low - General question</option>
                            <option value="Medium">Medium - Need help soon</option>
                            <option value="High">High - Urgent assistance needed</option>
                            <option value="Critical">Critical - Business impact</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description *
                          </label>
                          <textarea
                            value={supportForm.description}
                            onChange={(e) =>
                              setSupportForm({ ...supportForm, description: e.target.value })
                            }
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            rows={6}
                            placeholder="Provide details about your request"
                            required
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {/* Submit Button */}
                  <div className="mt-8 flex items-center justify-between">
                    {submitSuccess && (
                      <div className="flex items-center text-green-600">
                        <CheckCircle2 className="w-5 h-5 mr-2" />
                        <span>Ticket submitted successfully!</span>
                      </div>
                    )}
                    <button
                      type="submit"
                      disabled={loading}
                      className="ml-auto px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center"
                    >
                      {loading ? (
                        <>
                          <Clock className="w-5 h-5 mr-2 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5 mr-2" />
                          Submit Ticket
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          </div>
        )}

        {/* My Tickets Tab */}
        {activeTab === 'my-tickets' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-4 flex items-center space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search tickets..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="text-gray-400 w-5 h-5" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="all">All Status</option>
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Closed">Closed</option>
                </select>
              </div>
            </div>

            {/* Tickets List */}
            {loading ? (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 mx-auto text-gray-400 animate-spin mb-4" />
                <p className="text-gray-600">Loading tickets...</p>
              </div>
            ) : filteredTickets.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <HelpCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No tickets found</h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery || filterStatus !== 'all'
                    ? 'Try adjusting your filters'
                    : "You haven't submitted any tickets yet"}
                </p>
                {!searchQuery && filterStatus === 'all' && (
                  <button
                    onClick={() => setActiveTab('submit')}
                    className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Submit Your First Ticket
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredTickets.map((ticket) => (
                  <motion.div
                    key={ticket.key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className="font-mono text-sm text-gray-500">{ticket.key}</span>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              ticket.status === 'Open'
                                ? 'bg-blue-100 text-blue-800'
                                : ticket.status === 'In Progress'
                                ? 'bg-yellow-100 text-yellow-800'
                                : ticket.status === 'Resolved'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {ticket.status}
                          </span>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              ticket.priority === 'Critical'
                                ? 'bg-red-100 text-red-800'
                                : ticket.priority === 'High'
                                ? 'bg-orange-100 text-orange-800'
                                : ticket.priority === 'Medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {ticket.priority}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {ticket.summary}
                        </h3>
                        <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                          {ticket.description}
                        </p>
                        <div className="flex items-center text-sm text-gray-500 space-x-4">
                          <span>Created: {new Date(ticket.created).toLocaleDateString()}</span>
                          <span>Updated: {new Date(ticket.updated).toLocaleDateString()}</span>
                          {ticket.assignee && <span>Assignee: {ticket.assignee}</span>}
                        </div>
                      </div>
                      <a
                        href={ticket.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-4 px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors flex items-center"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </a>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SupportCenter;
