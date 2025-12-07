import { Page, expect } from '@playwright/test';
import path from 'path';

export interface EngagementConfig {
  name: string;
  clientName: string;
  fiscalYearEnd: string;
  comparativeYear: string;
  engagementType: 'Group Audit' | 'Single Entity' | 'SOC 1' | 'SOC 2';
  components: ComponentConfig[];
  materialityThreshold: number;
  performanceMateriality: number;
}

export interface ComponentConfig {
  name: string;
  entityType: 'Parent' | 'Subsidiary';
  ownershipPercentage: number;
  functionalCurrency: 'USD' | 'EUR' | 'GBP' | 'JPY' | 'SGD';
  significanceLevel: 'Significant' | 'Non-Significant' | 'Not Significant';
  auditApproach: 'Full Scope' | 'Specified Procedures' | 'Analytical Review';
}

export interface ClientInviteResult {
  inviteToken: string;
  inviteLink: string;
  clientEmail: string;
}

export const TEST_ENGAGEMENT_CONFIG: EngagementConfig = {
  name: 'Aura Holdings Group Audit - FY2025',
  clientName: 'Aura Holdings Inc.',
  fiscalYearEnd: '2025-12-31',
  comparativeYear: '2024-12-31',
  engagementType: 'Group Audit',
  materialityThreshold: 5000000,
  performanceMateriality: 3750000,
  components: [
    {
      name: 'Aura Holdings Inc. (Parent)',
      entityType: 'Parent',
      ownershipPercentage: 100,
      functionalCurrency: 'USD',
      significanceLevel: 'Significant',
      auditApproach: 'Full Scope',
    },
    {
      name: 'Sub A Manufacturing LLC',
      entityType: 'Subsidiary',
      ownershipPercentage: 100,
      functionalCurrency: 'USD',
      significanceLevel: 'Significant',
      auditApproach: 'Full Scope',
    },
    {
      name: 'Sub B Distribution GmbH',
      entityType: 'Subsidiary',
      ownershipPercentage: 80,
      functionalCurrency: 'EUR',
      significanceLevel: 'Significant',
      auditApproach: 'Full Scope',
    },
    {
      name: 'Sub C SaaS Pte Ltd',
      entityType: 'Subsidiary',
      ownershipPercentage: 60,
      functionalCurrency: 'USD',
      significanceLevel: 'Significant',
      auditApproach: 'Full Scope',
    },
  ],
};

export class EngagementHelper {
  constructor(private page: Page) {}

  /**
   * Create a new Group Audit Engagement
   */
  async createGroupAuditEngagement(config: EngagementConfig = TEST_ENGAGEMENT_CONFIG): Promise<string> {
    // Navigate to engagements page
    await this.page.goto('/engagements');
    await this.page.waitForLoadState('networkidle');

    // Click create new engagement button
    const createButton = await this.page.locator(
      'button:has-text("New Engagement"), button:has-text("Create Engagement"), button:has-text("+ New"), [data-testid="create-engagement"]'
    ).first();
    await createButton.click();

    // Wait for modal/form
    await this.page.waitForSelector('[data-testid="engagement-form"], .engagement-form, form', {
      timeout: 10000,
    });

    // Fill engagement details
    await this.fillEngagementForm(config);

    // Submit and wait for creation
    const submitButton = await this.page.locator(
      'button[type="submit"], button:has-text("Create"), button:has-text("Save")'
    ).first();
    await submitButton.click();

    // Wait for engagement to be created and get ID
    await this.page.waitForURL(/.*engagements\/[a-zA-Z0-9-]+/, { timeout: 30000 });
    const url = this.page.url();
    const engagementId = url.split('/engagements/')[1]?.split('/')[0] || '';

    return engagementId;
  }

  /**
   * Fill the engagement creation form
   */
  private async fillEngagementForm(config: EngagementConfig): Promise<void> {
    // Engagement name
    const nameInput = await this.page.locator(
      'input[name="name"], input[placeholder*="name"], input[label*="Name"], #engagement-name'
    ).first();
    await nameInput.fill(config.name);

    // Client name
    const clientInput = await this.page.locator(
      'input[name="client"], input[placeholder*="client"], input[label*="Client"], #client-name'
    ).first();
    if (await clientInput.isVisible()) {
      await clientInput.fill(config.clientName);
    }

    // Engagement type
    const typeSelect = await this.page.locator(
      'select[name="type"], [data-testid="engagement-type"]'
    ).first();
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption({ label: config.engagementType });
    }

    // Fiscal year end
    const fyeInput = await this.page.locator(
      'input[name="fiscalYearEnd"], input[type="date"][name*="year"], input[placeholder*="year"]'
    ).first();
    if (await fyeInput.isVisible()) {
      await fyeInput.fill(config.fiscalYearEnd);
    }

    // Comparative year
    const compInput = await this.page.locator(
      'input[name="comparativeYear"], input[name*="prior"], input[placeholder*="prior"]'
    ).first();
    if (await compInput.isVisible()) {
      await compInput.fill(config.comparativeYear);
    }

    // Materiality threshold
    const materialityInput = await this.page.locator(
      'input[name="materiality"], input[placeholder*="materiality"], #materiality'
    ).first();
    if (await materialityInput.isVisible()) {
      await materialityInput.fill(config.materialityThreshold.toString());
    }
  }

  /**
   * Configure engagement components (subsidiaries)
   */
  async configureComponents(engagementId: string, components: ComponentConfig[]): Promise<void> {
    // Navigate to components configuration
    await this.page.goto(`/engagements/${engagementId}/components`);
    await this.page.waitForLoadState('networkidle');

    for (const component of components) {
      // Add component
      const addButton = await this.page.locator(
        'button:has-text("Add Component"), button:has-text("Add Entity"), button:has-text("+")'
      ).first();
      await addButton.click();

      // Fill component details
      await this.page.waitForSelector('.component-form, [data-testid="component-form"], form');

      const nameInput = await this.page.locator('input[name="componentName"], input[placeholder*="name"]').first();
      await nameInput.fill(component.name);

      const ownershipInput = await this.page.locator('input[name="ownership"], input[type="number"]').first();
      if (await ownershipInput.isVisible()) {
        await ownershipInput.fill(component.ownershipPercentage.toString());
      }

      const currencySelect = await this.page.locator('select[name="currency"]').first();
      if (await currencySelect.isVisible()) {
        await currencySelect.selectOption(component.functionalCurrency);
      }

      const scopeSelect = await this.page.locator('select[name="auditApproach"], select[name="scope"]').first();
      if (await scopeSelect.isVisible()) {
        await scopeSelect.selectOption({ label: component.auditApproach });
      }

      // Save component
      const saveButton = await this.page.locator('button:has-text("Save"), button:has-text("Add")').first();
      await saveButton.click();

      await this.page.waitForTimeout(1000); // Wait for save
    }
  }

  /**
   * Invite client to engagement
   */
  async inviteClient(engagementId: string, clientEmail: string): Promise<ClientInviteResult> {
    // Navigate to engagement settings or team page
    await this.page.goto(`/engagements/${engagementId}/team`);
    await this.page.waitForLoadState('networkidle');

    // Click invite button
    const inviteButton = await this.page.locator(
      'button:has-text("Invite"), button:has-text("Add User"), button:has-text("Invite Client")'
    ).first();
    await inviteButton.click();

    // Wait for invite modal
    await this.page.waitForSelector('.invite-modal, [data-testid="invite-modal"], form');

    // Enter email
    const emailInput = await this.page.locator('input[type="email"], input[name="email"]').first();
    await emailInput.fill(clientEmail);

    // Select role as client
    const roleSelect = await this.page.locator('select[name="role"], [data-testid="role-select"]').first();
    if (await roleSelect.isVisible()) {
      await roleSelect.selectOption({ label: 'Client' });
    }

    // Send invite
    const sendButton = await this.page.locator(
      'button:has-text("Send"), button:has-text("Invite"), button[type="submit"]'
    ).first();
    await sendButton.click();

    // Wait for success message and capture invite link
    await this.page.waitForSelector('.success-message, [data-testid="invite-success"]', { timeout: 10000 });

    // Try to get the invite link from the page or API response
    let inviteToken = '';
    let inviteLink = '';

    // Check for displayed invite link
    const linkElement = await this.page.locator('.invite-link, [data-testid="invite-link"], code').first();
    if (await linkElement.isVisible()) {
      inviteLink = await linkElement.textContent() || '';
      inviteToken = inviteLink.split('/invite/')[1] || '';
    }

    // If no link displayed, try to get from network response
    if (!inviteToken) {
      const response = await this.page.waitForResponse(
        response => response.url().includes('/invite') && response.status() === 200,
        { timeout: 5000 }
      ).catch(() => null);

      if (response) {
        const data = await response.json().catch(() => ({}));
        inviteToken = data.token || data.inviteToken || '';
        inviteLink = data.inviteLink || `${process.env.CLIENT_PORTAL_URL}/invite/${inviteToken}`;
      }
    }

    return {
      inviteToken,
      inviteLink,
      clientEmail,
    };
  }

  /**
   * Get engagement status
   */
  async getEngagementStatus(engagementId: string): Promise<string> {
    await this.page.goto(`/engagements/${engagementId}`);
    await this.page.waitForLoadState('networkidle');

    const statusElement = await this.page.locator(
      '[data-testid="engagement-status"], .engagement-status, .status-badge'
    ).first();

    return await statusElement.textContent() || 'Unknown';
  }

  /**
   * Navigate to engagement workflow phase
   */
  async navigateToPhase(engagementId: string, phase: string): Promise<void> {
    const phaseUrls: Record<string, string> = {
      'planning': `/engagements/${engagementId}/planning`,
      'risk': `/engagements/${engagementId}/risk-assessment`,
      'materiality': `/engagements/${engagementId}/materiality`,
      'scoping': `/engagements/${engagementId}/group-scoping`,
      'testing': `/engagements/${engagementId}/testing`,
      'consolidation': `/engagements/${engagementId}/consolidation`,
      'financial-statements': `/engagements/${engagementId}/financial-statements`,
      'notes': `/engagements/${engagementId}/notes`,
      'completion': `/engagements/${engagementId}/completion`,
    };

    await this.page.goto(phaseUrls[phase] || `/engagements/${engagementId}/${phase}`);
    await this.page.waitForLoadState('networkidle');
  }
}
