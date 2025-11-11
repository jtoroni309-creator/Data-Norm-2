import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  Plus,
  MoreVertical,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Shield,
  Edit,
  Trash2,
  Ban,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Chip } from '../components/ui/Chip';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'manager';
  status: 'active' | 'inactive' | 'suspended';
  joinDate: string;
  lastActive: string;
  tickets: number;
  avatar?: string;
}

const mockUsers: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'admin',
    status: 'active',
    joinDate: '2024-01-15',
    lastActive: '2 hours ago',
    tickets: 12,
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    role: 'manager',
    status: 'active',
    joinDate: '2024-02-20',
    lastActive: '1 day ago',
    tickets: 8,
  },
  {
    id: '3',
    name: 'Bob Johnson',
    email: 'bob.johnson@example.com',
    role: 'user',
    status: 'active',
    joinDate: '2024-03-10',
    lastActive: '5 minutes ago',
    tickets: 24,
  },
  {
    id: '4',
    name: 'Alice Williams',
    email: 'alice.williams@example.com',
    role: 'user',
    status: 'inactive',
    joinDate: '2024-01-05',
    lastActive: '1 week ago',
    tickets: 3,
  },
  {
    id: '5',
    name: 'Charlie Brown',
    email: 'charlie.brown@example.com',
    role: 'manager',
    status: 'suspended',
    joinDate: '2024-04-12',
    lastActive: '3 days ago',
    tickets: 15,
  },
];

export const UserManagement: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [users] = useState<User[]>(mockUsers);

  const filteredUsers = users.filter((user) => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = !selectedRole || user.role === selectedRole;
    const matchesStatus = !selectedStatus || user.status === selectedStatus;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleBadge = (role: string) => {
    const variants: Record<string, 'info' | 'success' | 'warning'> = {
      admin: 'info',
      manager: 'success',
      user: 'neutral' as any,
    };
    return <Badge variant={variants[role] || 'neutral'}>{role.toUpperCase()}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'error'> = {
      active: 'success',
      inactive: 'warning',
      suspended: 'error',
    };
    return <Badge variant={variants[status]}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">User Management</h1>
          <p className="text-neutral-600 mt-1">Manage all users and their permissions</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outlined" icon={<Download size={18} />}>
            Export
          </Button>
          <Button variant="filled" icon={<Plus size={18} />}>
            Add User
          </Button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card variant="elevated">
          <CardContent padding="medium">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <Input
                  variant="outlined"
                  placeholder="Search users by name or email..."
                  icon={<Search size={18} />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Role Filter */}
              <div className="flex gap-2">
                <Chip
                  variant="filter"
                  selected={selectedRole === null}
                  onClick={() => setSelectedRole(null)}
                >
                  All Roles
                </Chip>
                <Chip
                  variant="filter"
                  selected={selectedRole === 'admin'}
                  onClick={() => setSelectedRole(selectedRole === 'admin' ? null : 'admin')}
                >
                  Admin
                </Chip>
                <Chip
                  variant="filter"
                  selected={selectedRole === 'manager'}
                  onClick={() => setSelectedRole(selectedRole === 'manager' ? null : 'manager')}
                >
                  Manager
                </Chip>
                <Chip
                  variant="filter"
                  selected={selectedRole === 'user'}
                  onClick={() => setSelectedRole(selectedRole === 'user' ? null : 'user')}
                >
                  User
                </Chip>
              </div>

              {/* Status Filter */}
              <div className="flex gap-2">
                <Chip
                  variant="filter"
                  selected={selectedStatus === 'active'}
                  onClick={() => setSelectedStatus(selectedStatus === 'active' ? null : 'active')}
                >
                  Active
                </Chip>
                <Chip
                  variant="filter"
                  selected={selectedStatus === 'inactive'}
                  onClick={() => setSelectedStatus(selectedStatus === 'inactive' ? null : 'inactive')}
                >
                  Inactive
                </Chip>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Users', value: users.length, color: 'bg-primary-100 text-primary-700' },
          { label: 'Active', value: users.filter(u => u.status === 'active').length, color: 'bg-success-100 text-success-700' },
          { label: 'Inactive', value: users.filter(u => u.status === 'inactive').length, color: 'bg-warning-100 text-warning-700' },
          { label: 'Suspended', value: users.filter(u => u.status === 'suspended').length, color: 'bg-error-100 text-error-700' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + index * 0.1 }}
          >
            <Card variant="filled">
              <CardContent padding="medium">
                <p className="text-sm font-medium text-neutral-600">{stat.label}</p>
                <p className={`text-3xl font-bold mt-2 ${stat.color}`}>{stat.value}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Users Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card variant="elevated">
          <CardHeader
            title="All Users"
            subtitle={`${filteredUsers.length} users found`}
          />
          <CardContent padding="none">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-surface-container-high">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">User</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">Role</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">Join Date</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">Last Active</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-700">Tickets</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-neutral-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {filteredUsers.map((user, index) => (
                    <motion.tr
                      key={user.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + index * 0.05 }}
                      className="hover:bg-surface-container-low transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 flex items-center justify-center text-white font-medium">
                            {user.name.split(' ').map(n => n[0]).join('')}
                          </div>
                          <div>
                            <p className="font-medium text-neutral-900">{user.name}</p>
                            <p className="text-sm text-neutral-600">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">{getRoleBadge(user.role)}</td>
                      <td className="px-6 py-4">{getStatusBadge(user.status)}</td>
                      <td className="px-6 py-4 text-sm text-neutral-700">{user.joinDate}</td>
                      <td className="px-6 py-4 text-sm text-neutral-700">{user.lastActive}</td>
                      <td className="px-6 py-4">
                        <Badge variant="info" size="small">{user.tickets}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="text" size="small" icon={<Edit size={16} />} />
                          <Button variant="text" size="small" icon={<Ban size={16} />} />
                          <Button variant="text" size="small" icon={<Trash2 size={16} />} />
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
