/**
 * Employees Page
 * Manage employees involved in R&D activities
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Plus,
  Edit3,
  Trash2,
  Upload,
  Download,
  Search,
  X,
  Save,
  Loader2,
  User,
  Briefcase,
  DollarSign,
  Clock,
  Info,
} from 'lucide-react';
import studyService from '../services/study.service';
import toast from 'react-hot-toast';
import type { RDEmployee } from '../types';

export default function EmployeesPage() {
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState<RDEmployee[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<RDEmployee | null>(null);
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState<Partial<RDEmployee>>({
    name: '',
    title: '',
    department: '',
    annual_wages: 0,
    qualified_time_percentage: 0,
    rd_activities: '',
  });

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const data = await studyService.getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error('Failed to load employees:', error);
      toast.error('Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!formData.name) {
      toast.error('Employee name is required');
      return;
    }

    setSaving(true);
    try {
      const created = await studyService.createEmployee(formData);
      setEmployees([...employees, created]);
      setShowAddModal(false);
      resetForm();
      toast.success('Employee added');
    } catch {
      toast.error('Failed to add employee');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async () => {
    if (!editingEmployee) return;

    setSaving(true);
    try {
      const updated = await studyService.updateEmployee(editingEmployee.id, formData);
      setEmployees(employees.map((e) => (e.id === editingEmployee.id ? updated : e)));
      setEditingEmployee(null);
      resetForm();
      toast.success('Employee updated');
    } catch {
      toast.error('Failed to update employee');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (employeeId: string) => {
    if (!confirm('Are you sure you want to delete this employee?')) return;

    try {
      await studyService.deleteEmployee(employeeId);
      setEmployees(employees.filter((e) => e.id !== employeeId));
      toast.success('Employee deleted');
    } catch {
      toast.error('Failed to delete employee');
    }
  };

  const openEditModal = (employee: RDEmployee) => {
    setFormData({
      name: employee.name,
      title: employee.title,
      department: employee.department,
      annual_wages: employee.annual_wages,
      qualified_time_percentage: employee.qualified_time_percentage,
      rd_activities: employee.rd_activities || '',
    });
    setEditingEmployee(employee);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      title: '',
      department: '',
      annual_wages: 0,
      qualified_time_percentage: 0,
      rd_activities: '',
    });
  };

  const filteredEmployees = employees.filter(
    (emp) =>
      emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalQualifiedWages = employees.reduce(
    (sum, emp) => sum + (emp.annual_wages * emp.qualified_time_percentage) / 100,
    0
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
              <p className="text-gray-600">Add employees who performed qualified R&D activities</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="fluent-btn-secondary">
              <Upload className="w-4 h-4" />
              Import
            </button>
            <button onClick={() => setShowAddModal(true)} className="fluent-btn-primary">
              <Plus className="w-5 h-5" />
              Add Employee
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div className="fluent-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900">{employees.length}</p>
            </div>
          </div>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Qualified Wages</p>
              <p className="text-2xl font-bold text-gray-900">
                ${totalQualifiedWages.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </p>
            </div>
          </div>
        </div>
        <div className="fluent-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg. Qualified Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {employees.length > 0
                  ? (
                      employees.reduce((sum, emp) => sum + emp.qualified_time_percentage, 0) /
                      employees.length
                    ).toFixed(0)
                  : 0}
                %
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-4"
      >
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search employees by name, title, or department..."
            className="fluent-input pl-10"
          />
        </div>
      </motion.div>

      {/* Employees List */}
      {filteredEmployees.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fluent-card p-12 text-center"
        >
          <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {searchTerm ? 'No Employees Found' : 'No Employees Yet'}
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm
              ? 'Try adjusting your search terms'
              : 'Add employees who performed qualified R&D activities'}
          </p>
          {!searchTerm && (
            <button onClick={() => setShowAddModal(true)} className="fluent-btn-primary">
              <Plus className="w-5 h-5" />
              Add Your First Employee
            </button>
          )}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="fluent-card overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Employee</th>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Department</th>
                  <th className="text-right px-6 py-3 text-sm font-semibold text-gray-900">Annual Wages</th>
                  <th className="text-right px-6 py-3 text-sm font-semibold text-gray-900">Qualified %</th>
                  <th className="text-right px-6 py-3 text-sm font-semibold text-gray-900">Qualified Wages</th>
                  <th className="text-right px-6 py-3 text-sm font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredEmployees.map((employee) => (
                  <tr key={employee.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                          <User className="w-5 h-5 text-gray-500" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{employee.name}</p>
                          <p className="text-sm text-gray-500">{employee.title}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{employee.department}</td>
                    <td className="px-6 py-4 text-right text-gray-900">
                      ${employee.annual_wages.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-sm font-medium">
                        {employee.qualified_time_percentage}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-green-600">
                      ${((employee.annual_wages * employee.qualified_time_percentage) / 100).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEditModal(employee)}
                          className="p-2 hover:bg-gray-100 rounded-lg"
                        >
                          <Edit3 className="w-4 h-4 text-gray-600" />
                        </button>
                        <button
                          onClick={() => handleDelete(employee.id)}
                          className="p-2 hover:bg-red-50 rounded-lg"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Add/Edit Modal */}
      <AnimatePresence>
        {(showAddModal || editingEmployee) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            onClick={() => {
              setShowAddModal(false);
              setEditingEmployee(null);
              resetForm();
            }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-lg bg-white rounded-2xl shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">
                  {editingEmployee ? 'Edit Employee' : 'Add Employee'}
                </h2>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingEmployee(null);
                    resetForm();
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="fluent-label">Full Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="fluent-input"
                      placeholder="John Smith"
                    />
                  </div>
                  <div>
                    <label className="fluent-label">Title</label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="fluent-input"
                      placeholder="Software Engineer"
                    />
                  </div>
                  <div>
                    <label className="fluent-label">Department</label>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      className="fluent-input"
                      placeholder="Engineering"
                    />
                  </div>
                  <div>
                    <label className="fluent-label">Annual Wages ($)</label>
                    <input
                      type="number"
                      value={formData.annual_wages || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, annual_wages: parseFloat(e.target.value) || 0 })
                      }
                      className="fluent-input"
                      placeholder="75000"
                    />
                  </div>
                  <div>
                    <label className="fluent-label">Qualified Time (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={formData.qualified_time_percentage || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          qualified_time_percentage: Math.min(100, Math.max(0, parseFloat(e.target.value) || 0)),
                        })
                      }
                      className="fluent-input"
                      placeholder="50"
                    />
                  </div>
                </div>

                <div>
                  <label className="fluent-label">R&D Activities Description</label>
                  <textarea
                    value={formData.rd_activities}
                    onChange={(e) => setFormData({ ...formData, rd_activities: e.target.value })}
                    className="fluent-textarea"
                    rows={3}
                    placeholder="Describe the R&D activities this employee performs..."
                  />
                </div>

                <div className="p-3 bg-blue-50 rounded-lg flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-600 mt-0.5" />
                  <p className="text-sm text-blue-800">
                    Qualified time percentage represents the portion of time this employee spends on
                    qualified R&D activities.
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingEmployee(null);
                    resetForm();
                  }}
                  className="fluent-btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={editingEmployee ? handleUpdate : handleAdd}
                  disabled={saving}
                  className="fluent-btn-primary"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  {editingEmployee ? 'Update' : 'Add'} Employee
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
