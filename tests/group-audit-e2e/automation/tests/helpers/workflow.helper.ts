import { Page, expect } from '@playwright/test';

export interface WorkflowStepResult {
  phase: string;
  status: 'passed' | 'failed' | 'skipped' | 'warning';
  startTime: Date;
  endTime: Date;
  duration: number;
  details: string;
  screenshots: string[];
  errors: string[];
}

export interface AuditOutput {
  type: string;
  fileName: string;
  format: string;
  size: number;
  generatedAt: Date;
  downloadUrl?: string;
}

export const WORKFLOW_PHASES = [
  'planning',
  'risk-assessment',
  'materiality',
  'group-scoping',
  'component-auditors',
  'substantive-testing',
  'consolidation',
  'financial-statements',
  'notes',
  'completion',
  'partner-review',
] as const;

export type WorkflowPhase = typeof WORKFLOW_PHASES[number];

export class WorkflowHelper {
  private results: WorkflowStepResult[] = [];

  constructor(private page: Page) {}

  /**
   * Run the complete audit workflow
   */
  async runFullWorkflow(engagementId: string): Promise<WorkflowStepResult[]> {
    for (const phase of WORKFLOW_PHASES) {
      const result = await this.executePhase(engagementId, phase);
      this.results.push(result);

      // If a critical phase fails, stop the workflow
      if (result.status === 'failed' && this.isCriticalPhase(phase)) {
        break;
      }
    }

    return this.results;
  }

  /**
   * Execute a single workflow phase
   */
  async executePhase(engagementId: string, phase: WorkflowPhase): Promise<WorkflowStepResult> {
    const startTime = new Date();
    const screenshots: string[] = [];
    const errors: string[] = [];
    let status: 'passed' | 'failed' | 'skipped' | 'warning' = 'passed';
    let details = '';

    try {
      // Navigate to phase
      await this.page.goto(`/engagements/${engagementId}/${phase}`);
      await this.page.waitForLoadState('networkidle');

      // Take initial screenshot
      const screenshotPath = `./reports/screenshots/${phase}-start.png`;
      await this.page.screenshot({ path: screenshotPath, fullPage: true });
      screenshots.push(screenshotPath);

      // Execute phase-specific logic
      switch (phase) {
        case 'planning':
          details = await this.executePlanningPhase();
          break;
        case 'risk-assessment':
          details = await this.executeRiskAssessmentPhase();
          break;
        case 'materiality':
          details = await this.executeMaterialityPhase();
          break;
        case 'group-scoping':
          details = await this.executeGroupScopingPhase();
          break;
        case 'component-auditors':
          details = await this.executeComponentAuditorsPhase();
          break;
        case 'substantive-testing':
          details = await this.executeSubstantiveTestingPhase();
          break;
        case 'consolidation':
          details = await this.executeConsolidationPhase();
          break;
        case 'financial-statements':
          details = await this.executeFinancialStatementsPhase();
          break;
        case 'notes':
          details = await this.executeNotesPhase();
          break;
        case 'completion':
          details = await this.executeCompletionPhase();
          break;
        case 'partner-review':
          details = await this.executePartnerReviewPhase();
          break;
      }

      // Take completion screenshot
      const completionScreenshot = `./reports/screenshots/${phase}-complete.png`;
      await this.page.screenshot({ path: completionScreenshot, fullPage: true });
      screenshots.push(completionScreenshot);

    } catch (error: any) {
      status = 'failed';
      errors.push(error.message);
      details = `Phase failed: ${error.message}`;

      // Take error screenshot
      const errorScreenshot = `./reports/screenshots/${phase}-error.png`;
      await this.page.screenshot({ path: errorScreenshot, fullPage: true });
      screenshots.push(errorScreenshot);
    }

    const endTime = new Date();

    return {
      phase,
      status,
      startTime,
      endTime,
      duration: endTime.getTime() - startTime.getTime(),
      details,
      screenshots,
      errors,
    };
  }

  /**
   * Planning Phase Execution
   */
  private async executePlanningPhase(): Promise<string> {
    // Check for planning checklist
    const checklistItems = await this.page.locator('.checklist-item, [data-testid="planning-item"]').count();

    // Complete planning tasks
    const completeButtons = await this.page.locator(
      'button:has-text("Complete"), input[type="checkbox"]:not(:checked)'
    ).all();

    for (const button of completeButtons.slice(0, 5)) {
      await button.click();
      await this.page.waitForTimeout(500);
    }

    // Generate planning memo
    const generateButton = await this.page.locator(
      'button:has-text("Generate"), button:has-text("AI Generate")'
    ).first();
    if (await generateButton.isVisible()) {
      await generateButton.click();
      await this.page.waitForSelector('.generation-complete, [data-status="complete"]', { timeout: 60000 });
    }

    return `Planning phase completed. ${checklistItems} checklist items reviewed.`;
  }

  /**
   * Risk Assessment Phase Execution
   */
  private async executeRiskAssessmentPhase(): Promise<string> {
    // Trigger AI risk identification
    const aiButton = await this.page.locator(
      'button:has-text("Identify Risks"), button:has-text("AI Analysis"), button:has-text("Generate")'
    ).first();

    if (await aiButton.isVisible()) {
      await aiButton.click();
      await this.page.waitForSelector('.risk-identified, .analysis-complete', { timeout: 90000 });
    }

    // Count identified risks
    const riskCount = await this.page.locator('.risk-item, [data-testid="risk"]').count();

    // Review and accept risks
    const acceptButtons = await this.page.locator('button:has-text("Accept"), button:has-text("Confirm")').all();
    for (const btn of acceptButtons.slice(0, 10)) {
      if (await btn.isVisible()) {
        await btn.click();
        await this.page.waitForTimeout(300);
      }
    }

    return `Risk assessment completed. ${riskCount} risks identified.`;
  }

  /**
   * Materiality Phase Execution
   */
  private async executeMaterialityPhase(): Promise<string> {
    // Calculate materiality
    const calculateButton = await this.page.locator(
      'button:has-text("Calculate"), button:has-text("Compute")'
    ).first();

    if (await calculateButton.isVisible()) {
      await calculateButton.click();
      await this.page.waitForSelector('.materiality-calculated, .result', { timeout: 30000 });
    }

    // Get materiality values
    const materialityValue = await this.page.locator('.materiality-amount, [data-testid="materiality"]').textContent();
    const performanceMateriality = await this.page.locator('.performance-materiality, [data-testid="pm"]').textContent();

    // Approve materiality
    const approveButton = await this.page.locator('button:has-text("Approve"), button:has-text("Accept")').first();
    if (await approveButton.isVisible()) {
      await approveButton.click();
    }

    return `Materiality: ${materialityValue || 'N/A'}, Performance Materiality: ${performanceMateriality || 'N/A'}`;
  }

  /**
   * Group Scoping Phase Execution
   */
  private async executeGroupScopingPhase(): Promise<string> {
    // Run group scoping analysis
    const analyzeButton = await this.page.locator(
      'button:has-text("Analyze"), button:has-text("Scope"), button:has-text("Run Analysis")'
    ).first();

    if (await analyzeButton.isVisible()) {
      await analyzeButton.click();
      await this.page.waitForSelector('.scoping-complete, .analysis-result', { timeout: 60000 });
    }

    // Count components
    const significantCount = await this.page.locator('[data-significance="significant"]').count();
    const totalComponents = await this.page.locator('.component-row, [data-testid="component"]').count();

    return `Group scoping completed. ${significantCount}/${totalComponents} significant components identified.`;
  }

  /**
   * Component Auditors Phase Execution
   */
  private async executeComponentAuditorsPhase(): Promise<string> {
    // This phase handles instructions to component auditors
    const instructionCount = await this.page.locator('.instruction-item, [data-testid="instruction"]').count();

    // Generate instructions
    const generateButton = await this.page.locator('button:has-text("Generate Instructions")').first();
    if (await generateButton.isVisible()) {
      await generateButton.click();
      await this.page.waitForSelector('.instructions-generated', { timeout: 60000 });
    }

    return `Component auditor instructions prepared. ${instructionCount} instructions generated.`;
  }

  /**
   * Substantive Testing Phase Execution
   */
  private async executeSubstantiveTestingPhase(): Promise<string> {
    // Run AI-powered testing
    const runTestsButton = await this.page.locator(
      'button:has-text("Run Tests"), button:has-text("Execute"), button:has-text("AI Test")'
    ).first();

    if (await runTestsButton.isVisible()) {
      await runTestsButton.click();
      await this.page.waitForSelector('.tests-complete, .testing-result', { timeout: 120000 });
    }

    // Count test results
    const passedTests = await this.page.locator('[data-status="passed"]').count();
    const failedTests = await this.page.locator('[data-status="failed"]').count();
    const totalTests = passedTests + failedTests;

    return `Substantive testing completed. ${passedTests}/${totalTests} tests passed.`;
  }

  /**
   * Consolidation Phase Execution
   */
  private async executeConsolidationPhase(): Promise<string> {
    // Run consolidation
    const consolidateButton = await this.page.locator(
      'button:has-text("Consolidate"), button:has-text("Run Consolidation")'
    ).first();

    if (await consolidateButton.isVisible()) {
      await consolidateButton.click();
      await this.page.waitForSelector('.consolidation-complete', { timeout: 90000 });
    }

    // Check eliminations
    const eliminationsCount = await this.page.locator('.elimination-entry, [data-testid="elimination"]').count();

    // Check FX translation
    const fxAdjustments = await this.page.locator('.fx-adjustment, [data-testid="fx"]').count();

    return `Consolidation completed. ${eliminationsCount} eliminations, ${fxAdjustments} FX adjustments.`;
  }

  /**
   * Financial Statements Phase Execution
   */
  private async executeFinancialStatementsPhase(): Promise<string> {
    // Generate financial statements
    const generateButton = await this.page.locator(
      'button:has-text("Generate"), button:has-text("Create Financial Statements")'
    ).first();

    if (await generateButton.isVisible()) {
      await generateButton.click();
      await this.page.waitForSelector('.fs-generated, .financial-statements-ready', { timeout: 120000 });
    }

    // Verify statements exist
    const statements = ['Balance Sheet', 'Income Statement', 'Cash Flow', 'Equity'];
    let generatedCount = 0;

    for (const stmt of statements) {
      const element = await this.page.locator(`text=${stmt}`).first();
      if (await element.isVisible()) {
        generatedCount++;
      }
    }

    return `Financial statements generated. ${generatedCount}/${statements.length} statements ready.`;
  }

  /**
   * Notes Phase Execution
   */
  private async executeNotesPhase(): Promise<string> {
    // Run Note Generator
    const generateNotesButton = await this.page.locator(
      'button:has-text("Generate Notes"), button:has-text("AI Notes"), button:has-text("Create Notes")'
    ).first();

    if (await generateNotesButton.isVisible()) {
      await generateNotesButton.click();
      await this.page.waitForSelector('.notes-generated, .notes-complete', { timeout: 180000 });
    }

    // Count generated notes
    const notesCount = await this.page.locator('.note-item, [data-testid="note"]').count();

    return `Notes generated. ${notesCount} disclosure notes created.`;
  }

  /**
   * Completion Phase Execution
   */
  private async executeCompletionPhase(): Promise<string> {
    // Complete audit checklist
    const checklistItems = await this.page.locator('.completion-item, [data-testid="completion-check"]').all();
    let completedCount = 0;

    for (const item of checklistItems) {
      const checkbox = await item.locator('input[type="checkbox"]').first();
      if (await checkbox.isVisible() && !(await checkbox.isChecked())) {
        await checkbox.click();
        completedCount++;
        await this.page.waitForTimeout(300);
      }
    }

    return `Completion phase finished. ${completedCount} checklist items completed.`;
  }

  /**
   * Partner Review Phase Execution
   */
  private async executePartnerReviewPhase(): Promise<string> {
    // Route to partner
    const routeButton = await this.page.locator(
      'button:has-text("Route to Partner"), button:has-text("Submit for Review")'
    ).first();

    if (await routeButton.isVisible()) {
      await routeButton.click();
      await this.page.waitForSelector('.routed-success, .review-pending', { timeout: 30000 });
    }

    return `Audit routed to partner for final review.`;
  }

  /**
   * Check if phase is critical (failure should stop workflow)
   */
  private isCriticalPhase(phase: WorkflowPhase): boolean {
    return ['planning', 'materiality', 'substantive-testing', 'consolidation', 'financial-statements'].includes(phase);
  }

  /**
   * Generate all audit outputs
   */
  async generateOutputs(engagementId: string): Promise<AuditOutput[]> {
    const outputs: AuditOutput[] = [];

    // Navigate to outputs/export page
    await this.page.goto(`/engagements/${engagementId}/outputs`);
    await this.page.waitForLoadState('networkidle');

    // Generate Note output
    const noteGenButton = await this.page.locator('button:has-text("Generate Notes")').first();
    if (await noteGenButton.isVisible()) {
      await noteGenButton.click();
      await this.page.waitForSelector('.notes-ready', { timeout: 120000 });
      outputs.push({
        type: 'Notes',
        fileName: 'financial_statement_notes.pdf',
        format: 'PDF',
        size: 0,
        generatedAt: new Date(),
      });
    }

    // Generate Advanced Financial Statements
    const fsGenButton = await this.page.locator('button:has-text("Generate Financial Statements")').first();
    if (await fsGenButton.isVisible()) {
      await fsGenButton.click();
      await this.page.waitForSelector('.fs-ready', { timeout: 120000 });
      outputs.push({
        type: 'Financial Statements',
        fileName: 'audited_financial_statements.pdf',
        format: 'PDF',
        size: 0,
        generatedAt: new Date(),
      });
    }

    // Generate Audit Report
    const reportGenButton = await this.page.locator('button:has-text("Generate Audit Report")').first();
    if (await reportGenButton.isVisible()) {
      await reportGenButton.click();
      await this.page.waitForSelector('.report-ready', { timeout: 120000 });
      outputs.push({
        type: 'Audit Report',
        fileName: 'independent_auditor_report.pdf',
        format: 'PDF',
        size: 0,
        generatedAt: new Date(),
      });
    }

    return outputs;
  }

  /**
   * Download final audit package
   */
  async downloadFinalPackage(engagementId: string): Promise<string> {
    await this.page.goto(`/engagements/${engagementId}/outputs`);
    await this.page.waitForLoadState('networkidle');

    const downloadButton = await this.page.locator(
      'button:has-text("Download Package"), button:has-text("Export All"), a:has-text("Download")'
    ).first();

    if (await downloadButton.isVisible()) {
      const [download] = await Promise.all([
        this.page.waitForEvent('download'),
        downloadButton.click(),
      ]);

      const path = await download.path();
      return path || '';
    }

    return '';
  }

  /**
   * Get all workflow results
   */
  getResults(): WorkflowStepResult[] {
    return this.results;
  }
}
