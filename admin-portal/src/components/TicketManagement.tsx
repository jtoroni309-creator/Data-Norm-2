import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Bug,
  Lightbulb,
  HelpCircle,
  Search,
  Filter,
  ChevronDown,
  CheckCircle2,
  Clock,
  AlertCircle,
  User,
  Calendar,
  MessageSquare,
  Zap,
  Code,
  GitPullRequest,
  ExternalLink,
  X,
  Send,
  Sparkles,
} from 'lucide-react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

type Priority = 'Low' | 'Medium' | 'High' | 'Critical';
type TicketStatus = 'Open' | 'In Progress' | 'Resolved' | 'Closed';
type IssueType = 'Bug' | 'Feature' | 'Support';

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

interface TicketStats {
  total_issues: number;
  open_bugs: number;
  open_features: number;
  open_support: number;
  high_priority: number;
  critical_priority: number;
}

interface BugAnalysis {
  issue_key: string;
  analysis: string;
  suggested_files: string[];
  fix_approach: string;
  pr_url?: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const TicketManagement: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<TicketStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<BugAnalysis | null>(null);
  const [analyzingBug, setAnalyzingBug] = useState(false);

  // Filters
  const [issueTypeFilter, setIssueTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [customerFilter, setCustomerFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Comment state
  const [newComment, setNewComment] = useState('');
  const [commentInternal, setCommentInternal] = useState(false);

  // Load tickets and stats on mount
  useEffect(() => {
    loadTickets();
    loadStats();
  }, [issueTypeFilter, statusFilter, priorityFilter, customerFilter]);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (issueTypeFilter !== 'all') params.append('issue_type', issueTypeFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (priorityFilter !== 'all') params.append('priority', priorityFilter);
      if (customerFilter) params.append('customer_id', customerFilter);

      const response = await fetch(`/api/jira/admin/issues?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
      });

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

  const loadStats = async () => {
    try {
      const response = await fetch('/api/jira/admin/stats', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // ============================================================================
  // TICKET ACTIONS
  // ============================================================================

  const updateTicketStatus = async (issueKey: string, newStatus: TicketStatus) => {
    try {
      const response = await fetch(`/api/jira/admin/issues/${issueKey}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        await loadTickets();
        if (selectedTicket?.key === issueKey) {
          const updatedTicket = await response.json();
          setSelectedTicket(updatedTicket);
        }
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const assignTicket = async (issueKey: string, assigneeEmail: string) => {
    try {
      const response = await fetch(`/api/jira/admin/issues/${issueKey}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({ assignee_email: assigneeEmail }),
      });

      if (response.ok) {
        await loadTickets();
      }
    } catch (error) {
      console.error('Failed to assign ticket:', error);
    }
  };

  const addComment = async (issueKey: string) => {
    if (!newComment.trim()) return;

    try {
      const response = await fetch(`/api/jira/admin/issues/${issueKey}/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({
          comment: newComment,
          internal: commentInternal,
        }),
      });

      if (response.ok) {
        setNewComment('');
        setCommentInternal(false);
        // Reload ticket to show new comment
        await loadTickets();
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  // ============================================================================
  // CLAUDE CODE INTEGRATION
  // ============================================================================

  const analyzeBugWithClaude = async (issueKey: string, autoFix: boolean = false) => {
    try {
      setAnalyzingBug(true);
      setShowAnalysisModal(true);

      const response = await fetch('/api/jira/admin/analyze-bug', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({
          issue_key: issueKey,
          codebase_path: '/home/user/Data-Norm-2',
          auto_fix: autoFix,
          create_pr: autoFix,
        }),
      });

      if (response.ok) {
        const analysis = await response.json();
        setAnalysisResult(analysis);
      }
    } catch (error) {
      console.error('Failed to analyze bug:', error);
    } finally {
      setAnalyzingBug(false);
    }
  };

  // ============================================================================
  // FILTERED TICKETS
  // ============================================================================

  const filteredTickets = tickets.filter((ticket) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        ticket.summary.toLowerCase().includes(query) ||
        ticket.description.toLowerCase().includes(query) ||
        ticket.key.toLowerCase().includes(query)
      );
    }
    return true;
  });

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Ticket Management</h1>
          <p className="text-gray-600">
            Manage customer tickets with AI-powered bug analysis and automated fixes
          </p>
        </motion.div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Issues</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_issues}</p>
                </div>
                <HelpCircle className="w-8 h-8 text-blue-500" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Open Bugs</p>
                  <p className="text-2xl font-bold text-red-600">{stats.open_bugs}</p>
                </div>
                <Bug className="w-8 h-8 text-red-500" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Feature Requests</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.open_features}</p>
                </div>
                <Lightbulb className="w-8 h-8 text-blue-500" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Support Tickets</p>
                  <p className="text-2xl font-bold text-green-600">{stats.open_support}</p>
                </div>
                <HelpCircle className="w-8 h-8 text-green-500" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">High Priority</p>
                  <p className="text-2xl font-bold text-orange-600">{stats.high_priority}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-orange-500" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-lg shadow p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Critical</p>
                  <p className="text-2xl font-bold text-red-600">{stats.critical_priority}</p>
                </div>
                <Zap className="w-8 h-8 text-red-500" />
              </div>
            </motion.div>
          </div>
        )}

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
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

            <select
              value={issueTypeFilter}
              onChange={(e) => setIssueTypeFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="Bug">Bugs</option>
              <option value="Feature">Features</option>
              <option value="Support">Support</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">All Priorities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>

        {/* Tickets Grid */}
        {loading ? (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 mx-auto text-gray-400 animate-spin mb-4" />
            <p className="text-gray-600">Loading tickets...</p>
          </div>
        ) : filteredTickets.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <HelpCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No tickets found</h3>
            <p className="text-gray-600">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredTickets.map((ticket, index) => (
              <motion.div
                key={ticket.key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <span className="font-mono text-sm font-medium text-gray-700">
                        {ticket.key}
                      </span>
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
                      {ticket.labels.includes('customer-reported') && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          Customer Reported
                        </span>
                      )}
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {ticket.summary}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {ticket.description}
                    </p>

                    <div className="flex items-center text-sm text-gray-500 space-x-4">
                      <span className="flex items-center">
                        <User className="w-4 h-4 mr-1" />
                        {ticket.reporter}
                      </span>
                      <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {new Date(ticket.created).toLocaleDateString()}
                      </span>
                      {ticket.assignee && (
                        <span className="flex items-center">
                          <CheckCircle2 className="w-4 h-4 mr-1" />
                          Assigned to {ticket.assignee}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="ml-4 flex flex-col space-y-2">
                    {ticket.labels.some((label) => label === 'Bug') && (
                      <button
                        onClick={() => analyzeBugWithClaude(ticket.key, false)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center text-sm"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Analyze with AI
                      </button>
                    )}

                    {ticket.labels.some((label) => label === 'Bug') && (
                      <button
                        onClick={() => analyzeBugWithClaude(ticket.key, true)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center text-sm"
                      >
                        <Code className="w-4 h-4 mr-2" />
                        Auto-Fix
                      </button>
                    )}

                    <button
                      onClick={() => setSelectedTicket(ticket)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center text-sm"
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Manage
                    </button>

                    <a
                      href={ticket.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center text-sm"
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View in Jira
                    </a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Ticket Management Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedTicket.key}</h2>
                <p className="text-gray-600">{selectedTicket.summary}</p>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Status Update */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Update Status
                </label>
                <select
                  value={selectedTicket.status}
                  onChange={(e) =>
                    updateTicketStatus(selectedTicket.key, e.target.value as TicketStatus)
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Closed">Closed</option>
                </select>
              </div>

              {/* Add Comment */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add Comment
                </label>
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  rows={4}
                  placeholder="Add a comment..."
                />
                <div className="mt-2 flex items-center justify-between">
                  <label className="flex items-center text-sm text-gray-600">
                    <input
                      type="checkbox"
                      checked={commentInternal}
                      onChange={(e) => setCommentInternal(e.target.checked)}
                      className="mr-2"
                    />
                    Internal comment (not visible to customer)
                  </label>
                  <button
                    onClick={() => addComment(selectedTicket.key)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Add Comment
                  </button>
                </div>
              </div>

              {/* Description */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600 whitespace-pre-wrap">{selectedTicket.description}</p>
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <p className="text-sm text-gray-600">Reporter</p>
                  <p className="font-medium">{selectedTicket.reporter}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Priority</p>
                  <p className="font-medium">{selectedTicket.priority}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Created</p>
                  <p className="font-medium">
                    {new Date(selectedTicket.created).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Updated</p>
                  <p className="font-medium">
                    {new Date(selectedTicket.updated).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Bug Analysis Modal */}
      {showAnalysisModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-t-xl">
              <div className="flex items-center">
                <Sparkles className="w-6 h-6 mr-3" />
                <h2 className="text-2xl font-bold">Claude Code AI Analysis</h2>
              </div>
              <button
                onClick={() => {
                  setShowAnalysisModal(false);
                  setAnalysisResult(null);
                }}
                className="text-white hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              {analyzingBug ? (
                <div className="text-center py-12">
                  <div className="relative inline-block">
                    <Code className="w-16 h-16 text-purple-600 animate-pulse mb-4" />
                    <Sparkles className="w-8 h-8 text-yellow-400 absolute -top-2 -right-2 animate-bounce" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Analyzing Bug with Claude AI...
                  </h3>
                  <p className="text-gray-600">
                    Claude is examining the code and generating a fix strategy
                  </p>
                </div>
              ) : analysisResult ? (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <Bug className="w-5 h-5 mr-2 text-red-500" />
                      Bug Analysis
                    </h3>
                    <p className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">
                      {analysisResult.analysis}
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <Code className="w-5 h-5 mr-2 text-blue-500" />
                      Files to Examine
                    </h3>
                    <ul className="space-y-1">
                      {analysisResult.suggested_files.map((file, index) => (
                        <li
                          key={index}
                          className="font-mono text-sm text-gray-700 bg-gray-50 p-2 rounded"
                        >
                          {file}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                      Suggested Fix Approach
                    </h3>
                    <p className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">
                      {analysisResult.fix_approach}
                    </p>
                  </div>

                  {analysisResult.pr_url && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                        <GitPullRequest className="w-5 h-5 mr-2 text-green-500" />
                        Pull Request Created
                      </h3>
                      <a
                        href={analysisResult.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        View Pull Request
                      </a>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default TicketManagement;
