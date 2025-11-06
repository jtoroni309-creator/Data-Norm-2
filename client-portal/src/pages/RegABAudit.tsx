/**
 * Client Portal - Regulation A/B Audit Page
 *
 * Allows clients to submit CMBS deals for audit and track progress
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as PendingIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

interface CMBSDeal {
  id: string;
  deal_name: string;
  deal_number: string;
  cusip?: string;
  current_balance: number;
  dscr?: number;
  ltv?: number;
  status: string;
  submitted_at?: string;
}

interface AuditEngagement {
  id: string;
  audit_name: string;
  status: string;
  total_cmbs_deals: number;
  processed_deals: number;
  total_compliance_checks: number;
  passed_compliance_checks: number;
  failed_compliance_checks: number;
}

export default function RegABAuditPage() {
  const [engagements, setEngagements] = useState<AuditEngagement[]>([]);
  const [selectedEngagement, setSelectedEngagement] = useState<string | null>(null);
  const [deals, setDeals] = useState<CMBSDeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    fetchEngagements();
  }, []);

  useEffect(() => {
    if (selectedEngagement) {
      fetchDeals(selectedEngagement);
    }
  }, [selectedEngagement]);

  const fetchEngagements = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_REG_AB_API_URL || 'http://localhost:8011'}/api/engagements`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEngagements(data);
        if (data.length > 0) {
          setSelectedEngagement(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching engagements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDeals = async (engagementId: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_REG_AB_API_URL || 'http://localhost:8011'}/api/engagements/${engagementId}/deals`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDeals(data);
      }
    } catch (error) {
      console.error('Error fetching deals:', error);
    }
  };

  const getStatusChip = (status: string) => {
    const statusMap: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
      active: { label: 'Active', color: 'success' },
      pending_audit: { label: 'Pending Audit', color: 'warning' },
      audit_complete: { label: 'Complete', color: 'success' },
      draft: { label: 'Draft', color: 'default' },
      ai_processing: { label: 'Processing', color: 'info' },
      cpa_review: { label: 'CPA Review', color: 'primary' },
      finalized: { label: 'Finalized', color: 'success' },
    };

    const statusInfo = statusMap[status] || { label: status, color: 'default' };
    return <Chip label={statusInfo.label} color={statusInfo.color} size="small" />;
  };

  const currentEngagement = engagements.find((e) => e.id === selectedEngagement);
  const progress = currentEngagement
    ? (currentEngagement.processed_deals / Math.max(currentEngagement.total_cmbs_deals, 1)) * 100
    : 0;

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Regulation A/B Audit
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Submit and track CMBS deals for Regulation A/B compliance auditing
        </Typography>
      </Box>

      {engagements.length === 0 ? (
        <Alert severity="info">
          <AlertTitle>No Active Engagements</AlertTitle>
          Contact your CPA firm to initiate a Regulation A/B audit engagement.
        </Alert>
      ) : (
        <>
          {/* Engagement Summary */}
          {currentEngagement && (
            <Card sx={{ mb: 4 }}>
              <CardHeader
                title={currentEngagement.audit_name}
                subheader={`Status: ${currentEngagement.status}`}
                action={getStatusChip(currentEngagement.status)}
              />
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h4" color="primary">
                      {currentEngagement.total_cmbs_deals}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Deals
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h4" color="success.main">
                      {currentEngagement.processed_deals}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Processed
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h4" color="info.main">
                      {currentEngagement.passed_compliance_checks}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Checks Passed
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h4" color="error.main">
                      {currentEngagement.failed_compliance_checks}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Checks Failed
                    </Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Processing Progress
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.round(progress)}%
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={progress} />
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Add CMBS Deal
            </Button>
          </Box>

          {/* Deals Table */}
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Deal Name</TableCell>
                    <TableCell>Deal Number</TableCell>
                    <TableCell>CUSIP</TableCell>
                    <TableCell align="right">Current Balance</TableCell>
                    <TableCell align="right">DSCR</TableCell>
                    <TableCell align="right">LTV</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Submitted</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {deals.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                          No CMBS deals submitted yet. Click "Add CMBS Deal" to get started.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    deals.map((deal) => (
                      <TableRow key={deal.id} hover>
                        <TableCell>{deal.deal_name}</TableCell>
                        <TableCell>{deal.deal_number}</TableCell>
                        <TableCell>{deal.cusip || '—'}</TableCell>
                        <TableCell align="right">
                          ${deal.current_balance.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          {deal.dscr ? deal.dscr.toFixed(2) : '—'}
                        </TableCell>
                        <TableCell align="right">
                          {deal.ltv ? `${deal.ltv.toFixed(1)}%` : '—'}
                        </TableCell>
                        <TableCell>{getStatusChip(deal.status)}</TableCell>
                        <TableCell>
                          {deal.submitted_at
                            ? new Date(deal.submitted_at).toLocaleDateString()
                            : '—'}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </>
      )}

      {/* Add Deal Dialog - Simplified for demo */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add CMBS Deal</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              This is a simplified form. In production, this would include comprehensive CMBS deal data entry.
            </Alert>
            <TextField fullWidth label="Deal Name" margin="normal" />
            <TextField fullWidth label="Deal Number" margin="normal" />
            <TextField fullWidth label="CUSIP" margin="normal" />
            <TextField fullWidth label="Current Balance" type="number" margin="normal" />
            <TextField fullWidth label="DSCR" type="number" margin="normal" />
            <TextField fullWidth label="LTV (%)" type="number" margin="normal" />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenDialog(false)}>
            Submit Deal
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
