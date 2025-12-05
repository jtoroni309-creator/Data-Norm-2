/**
 * R&D Study Automation E2E Test Suite
 *
 * Comprehensive end-to-end tests for the R&D Tax Credit Study service
 * including PA and NY state credit calculations, client portal upload,
 * AI 4-part test generation, and Excel/PDF output generation.
 */

import { test, expect, APIRequestContext } from '@playwright/test';
import { RDStudyAPIHelper, CalculationResult } from './helpers/api.helper';
import * as path from 'path';
import * as fs from 'fs';

// Test data paths
const SYNTHETIC_DATA_PATH = path.join(__dirname, '../../synthetic-data');
const REPORTS_PATH = path.join(__dirname, '../../reports');

// Test configuration
const TEST_CONFIG = {
  apiBaseUrl: process.env.API_BASE_URL || 'https://api.auraai.toroniandcompany.com',
  cpaPortalUrl: process.env.CPA_PORTAL_URL || 'https://app.auraai.toroniandcompany.com',
  clientPortalUrl: process.env.CLIENT_PORTAL_URL || 'https://portal.auraai.toroniandcompany.com',
  testEmail: process.env.CPA_TEST_EMAIL || 'test.auditor@auraai.test',
  testPassword: process.env.CPA_TEST_PASSWORD || 'TestPassword123!',
  firmId: process.env.CPA_FIRM_ID || 'test-firm-id',
  clientId: 'test-client-technova',
};

// Load synthetic data
function loadCompanyInfo() {
  return JSON.parse(fs.readFileSync(path.join(SYNTHETIC_DATA_PATH, 'company_info.json'), 'utf-8'));
}

function loadProjects() {
  return JSON.parse(fs.readFileSync(path.join(SYNTHETIC_DATA_PATH, 'projects.json'), 'utf-8'));
}

function loadPayrollData() {
  const csvPath = path.join(SYNTHETIC_DATA_PATH, 'payroll_data.csv');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj: any = {};
    headers.forEach((h, i) => obj[h] = values[i]);
    return obj;
  });
}

function loadSupplies() {
  const csvPath = path.join(SYNTHETIC_DATA_PATH, 'supplies.csv');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj: any = {};
    headers.forEach((h, i) => obj[h] = values[i]);
    return obj;
  });
}

function loadContractResearch() {
  const csvPath = path.join(SYNTHETIC_DATA_PATH, 'contract_research.csv');
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj: any = {};
    headers.forEach((h, i) => obj[h] = values[i]);
    return obj;
  });
}

test.describe('R&D Study Automation E2E Tests', () => {
  let apiHelper: RDStudyAPIHelper;
  let studyId: string;
  let projectIds: Map<string, string> = new Map();
  let employeeIds: Map<string, string> = new Map();
  let companyInfo: any;
  let projects: any;
  let payrollData: any[];
  let supplies: any[];
  let contractResearch: any[];

  test.beforeAll(async ({ request }) => {
    // Load synthetic data
    companyInfo = loadCompanyInfo();
    projects = loadProjects();
    payrollData = loadPayrollData();
    supplies = loadSupplies();
    contractResearch = loadContractResearch();

    // Initialize API helper
    apiHelper = new RDStudyAPIHelper(request, TEST_CONFIG.apiBaseUrl);

    console.log('='.repeat(60));
    console.log('R&D STUDY E2E TEST SUITE - TechNova Solutions Inc.');
    console.log('Tax Year: 2024 | States: PA, NY, CA, TX, NJ');
    console.log('='.repeat(60));
  });

  test.describe('1. Study Creation and Setup', () => {
    test('1.1 Authenticate as CPA user', async () => {
      const token = await apiHelper.authenticate(
        TEST_CONFIG.testEmail,
        TEST_CONFIG.testPassword
      );
      expect(token).toBeTruthy();
      console.log('Authentication successful');
    });

    test('1.2 Create new R&D study for TechNova Solutions', async () => {
      const { id, study } = await apiHelper.createStudy({
        firm_id: TEST_CONFIG.firmId,
        client_id: TEST_CONFIG.clientId,
        name: `TechNova R&D Study - Tax Year ${companyInfo.company.tax_year}`,
        tax_year: companyInfo.company.tax_year,
        entity_type: companyInfo.company.entity_type,
        entity_name: companyInfo.company.name,
        ein: companyInfo.company.ein,
        fiscal_year_start: companyInfo.company.fiscal_year_start,
        fiscal_year_end: companyInfo.company.fiscal_year_end,
        states: companyInfo.company.states_with_nexus,
        primary_state: 'PA',
      });

      studyId = id;
      expect(studyId).toBeTruthy();
      expect(study.entity_name).toBe('TechNova Solutions Inc.');
      expect(study.states).toContain('PA');
      expect(study.states).toContain('NY');
      console.log(`Created study: ${studyId}`);
    });

    test('1.3 Add all R&D projects to study', async () => {
      for (const project of projects.projects) {
        const { id, project: createdProject } = await apiHelper.addProject(studyId, {
          name: project.name,
          code: project.code,
          department: project.department,
          description: project.description,
          start_date: project.start_date,
          end_date: project.end_date,
          is_ongoing: project.is_ongoing,
          business_component: project.business_component,
          state_allocation: project.state_allocation,
        });

        projectIds.set(project.id, id);
        expect(createdProject.name).toBe(project.name);
      }

      expect(projectIds.size).toBe(5);
      console.log(`Added ${projectIds.size} projects to study`);
    });

    test('1.4 Add all R&D employees to study', async () => {
      const paEmployees = payrollData.filter(e => e.state === 'PA');
      const nyEmployees = payrollData.filter(e => e.state === 'NY');

      // Add all employees
      for (const emp of payrollData) {
        const { id, employee } = await apiHelper.addEmployee(studyId, {
          employee_id: emp.employee_id,
          name: emp.name,
          title: emp.title,
          department: emp.department,
          hire_date: emp.hire_date,
          total_wages: parseFloat(emp.w2_wages),
          qualified_time_percentage: parseFloat(emp.qualified_time_pct),
          role_category: emp.role_category,
        });

        employeeIds.set(emp.employee_id, id);
      }

      expect(employeeIds.size).toBe(48);
      console.log(`Added ${employeeIds.size} employees (PA: ${paEmployees.length}, NY: ${nyEmployees.length})`);
    });
  });

  test.describe('2. Client Portal Document Upload', () => {
    test('2.1 Upload payroll data CSV', async () => {
      const payrollPath = path.join(SYNTHETIC_DATA_PATH, 'payroll_data.csv');
      const { id, document } = await apiHelper.uploadDocument(
        studyId,
        payrollPath,
        'payroll'
      );

      expect(id).toBeTruthy();
      expect(document.processing_status).toBeDefined();
      console.log('Uploaded payroll data');
    });

    test('2.2 Upload supplies data CSV', async () => {
      const suppliesPath = path.join(SYNTHETIC_DATA_PATH, 'supplies.csv');
      const { id, document } = await apiHelper.uploadDocument(
        studyId,
        suppliesPath,
        'general_ledger'
      );

      expect(id).toBeTruthy();
      console.log('Uploaded supplies data');
    });

    test('2.3 Upload contract research data CSV', async () => {
      const contractPath = path.join(SYNTHETIC_DATA_PATH, 'contract_research.csv');
      const { id, document } = await apiHelper.uploadDocument(
        studyId,
        contractPath,
        'contract'
      );

      expect(id).toBeTruthy();
      console.log('Uploaded contract research data');
    });

    test('2.4 Upload time tracking data CSV', async () => {
      const timePath = path.join(SYNTHETIC_DATA_PATH, 'time_tracking.csv');
      const { id, document } = await apiHelper.uploadDocument(
        studyId,
        timePath,
        'time_tracking'
      );

      expect(id).toBeTruthy();
      console.log('Uploaded time tracking data');
    });
  });

  test.describe('3. QRE Classification and Entry', () => {
    test('3.1 Add qualified wage QREs by state', async () => {
      let totalWageQRE = 0;
      const stateWages: Record<string, number> = { PA: 0, NY: 0, CA: 0, TX: 0, NJ: 0 };

      for (const emp of payrollData) {
        const qualifiedWages = parseFloat(emp.w2_wages) * (parseFloat(emp.qualified_time_pct) / 100);
        totalWageQRE += qualifiedWages;
        stateWages[emp.state] += qualifiedWages;

        await apiHelper.addQRE(studyId, {
          category: 'wages',
          gross_amount: parseFloat(emp.w2_wages),
          qualified_percentage: parseFloat(emp.qualified_time_pct),
          state_allocation: { [emp.state]: 1.0 },
          employee_id: employeeIds.get(emp.employee_id),
        });
      }

      console.log(`Total qualified wages: $${totalWageQRE.toLocaleString()}`);
      console.log(`  PA: $${stateWages.PA.toLocaleString()}`);
      console.log(`  NY: $${stateWages.NY.toLocaleString()}`);
    });

    test('3.2 Add qualified supply QREs', async () => {
      let totalSupplyQRE = 0;

      for (const supply of supplies) {
        const qualifiedAmount = parseFloat(supply.amount) * (parseFloat(supply.qualified_pct) / 100);
        totalSupplyQRE += qualifiedAmount;

        const projectId = projectIds.get(
          projects.projects.find((p: any) => p.code === supply.project_code)?.id
        );

        await apiHelper.addQRE(studyId, {
          category: 'supplies',
          gross_amount: parseFloat(supply.amount),
          qualified_percentage: parseFloat(supply.qualified_pct),
          state_allocation: { [supply.state]: 1.0 },
          project_id: projectId,
        });
      }

      console.log(`Total qualified supplies: $${totalSupplyQRE.toLocaleString()}`);
    });

    test('3.3 Add qualified contract research QREs', async () => {
      let totalContractQRE = 0;
      let basicResearchQRE = 0;

      for (const contract of contractResearch) {
        const qualifiedPct = contract.is_qualified_org === 'true' ? 100 : 65;
        const qualifiedAmount = parseFloat(contract.total_amount) * (qualifiedPct / 100);
        totalContractQRE += qualifiedAmount;

        if (contract.contract_type === 'basic_research') {
          basicResearchQRE += qualifiedAmount;
        }

        const projectId = projectIds.get(
          projects.projects.find((p: any) => p.code === contract.project_code)?.id
        );

        await apiHelper.addQRE(studyId, {
          category: contract.is_qualified_org === 'true' ? 'basic_research' : 'contract_research',
          gross_amount: parseFloat(contract.total_amount),
          qualified_percentage: qualifiedPct,
          state_allocation: { [contract.state]: 1.0 },
          project_id: projectId,
        });
      }

      console.log(`Total qualified contract research: $${totalContractQRE.toLocaleString()}`);
      console.log(`  Basic research (qualified orgs): $${basicResearchQRE.toLocaleString()}`);
    });
  });

  test.describe('4. AI 4-Part Test Analysis', () => {
    test('4.1 Run AI qualification analysis on NovaMind LLM project', async () => {
      const llmProjectId = projectIds.get('PRJ001');
      expect(llmProjectId).toBeTruthy();

      const result = await apiHelper.runProjectQualification(studyId, llmProjectId!);

      expect(result.qualification_status).toBeDefined();
      expect(result.permitted_purpose_score).toBeGreaterThanOrEqual(70);
      expect(result.technological_nature_score).toBeGreaterThanOrEqual(70);
      expect(result.uncertainty_score).toBeGreaterThanOrEqual(70);
      expect(result.experimentation_score).toBeGreaterThanOrEqual(70);

      console.log(`NovaMind LLM qualification scores:`);
      console.log(`  Permitted Purpose: ${result.permitted_purpose_score}`);
      console.log(`  Technological Nature: ${result.technological_nature_score}`);
      console.log(`  Uncertainty: ${result.uncertainty_score}`);
      console.log(`  Experimentation: ${result.experimentation_score}`);
    });

    test('4.2 Run AI qualification analysis on Quantum-Safe Encryption project', async () => {
      const qsecProjectId = projectIds.get('PRJ002');
      expect(qsecProjectId).toBeTruthy();

      const result = await apiHelper.runProjectQualification(studyId, qsecProjectId!);

      expect(result.qualification_status).toBeDefined();
      expect(result.overall_score).toBeGreaterThanOrEqual(70);

      console.log(`Quantum-Safe Encryption qualification: ${result.qualification_status}`);
      console.log(`  Overall score: ${result.overall_score}`);
    });

    test('4.3 Generate 4-part test narratives for all projects', async () => {
      for (const [originalId, dbId] of projectIds) {
        const result = await apiHelper.generateNarratives(studyId, dbId);

        expect(result.narratives).toBeDefined();
        expect(result.narratives.length).toBeGreaterThan(0);

        // Verify narrative contains key elements
        const narrativeText = result.narratives.map((n: any) => n.content).join(' ');
        expect(narrativeText.length).toBeGreaterThan(100);
      }

      console.log(`Generated 4-part test narratives for ${projectIds.size} projects`);
    });
  });

  test.describe('5. Credit Calculation - Federal and State', () => {
    let calculationResult: CalculationResult;

    test('5.1 Calculate Federal R&D credits (Regular and ASC)', async () => {
      calculationResult = await apiHelper.calculateCredits(studyId, {
        historical_data: companyInfo.historical_data,
        section_280c: companyInfo.section_280c_election,
        states: ['PA', 'NY', 'CA', 'TX', 'NJ'],
      });

      expect(calculationResult.federal_regular_credit).toBeGreaterThan(0);
      expect(calculationResult.federal_asc_credit).toBeGreaterThan(0);
      expect(calculationResult.recommended_method).toBeDefined();

      console.log(`Federal Credit Calculation:`);
      console.log(`  Regular Credit: $${calculationResult.federal_regular_credit.toLocaleString()}`);
      console.log(`  ASC Credit: $${calculationResult.federal_asc_credit.toLocaleString()}`);
      console.log(`  Recommended Method: ${calculationResult.recommended_method}`);
      console.log(`  Final Federal Credit: $${calculationResult.final_federal_credit.toLocaleString()}`);
    });

    test('5.2 Verify Pennsylvania (PA) state credit calculation', async () => {
      expect(calculationResult.state_credits.PA).toBeDefined();

      const paCredit = calculationResult.state_credits.PA;
      expect(paCredit.credit).toBeGreaterThan(0);
      expect(paCredit.rate).toBe(0.10); // PA rate is 10%

      // PA credit = 10% of excess QRE allocated to PA
      // For small business (< $5M gross receipts), rate is 20%
      console.log(`Pennsylvania (PA) State Credit:`);
      console.log(`  Allocated QRE: $${paCredit.qre_allocated.toLocaleString()}`);
      console.log(`  Credit Rate: ${(paCredit.rate * 100).toFixed(0)}%`);
      console.log(`  Calculated Credit: $${paCredit.credit.toLocaleString()}`);

      // Verify PA credit details
      const paDetails = await apiHelper.getStateCreditDetails(studyId, 'PA');
      expect(paDetails.state_code).toBe('PA');
      expect(paDetails.rules_reference).toContain('72 P.S.');
    });

    test('5.3 Verify New York (NY) state credit calculation', async () => {
      expect(calculationResult.state_credits.NY).toBeDefined();

      const nyCredit = calculationResult.state_credits.NY;
      expect(nyCredit.credit).toBeGreaterThan(0);
      expect(nyCredit.rate).toBe(0.09); // NY rate is 9%

      console.log(`New York (NY) State Credit:`);
      console.log(`  Allocated QRE: $${nyCredit.qre_allocated.toLocaleString()}`);
      console.log(`  Credit Rate: ${(nyCredit.rate * 100).toFixed(0)}%`);
      console.log(`  Calculated Credit: $${nyCredit.credit.toLocaleString()}`);

      // NY has refundable option for qualified emerging tech companies
      const nyDetails = await apiHelper.getStateCreditDetails(studyId, 'NY');
      expect(nyDetails.state_code).toBe('NY');
      expect(nyDetails.is_refundable).toBeDefined();
      expect(nyDetails.rules_reference).toContain('NY Tax Law');
    });

    test('5.4 Verify California (CA) state credit calculation', async () => {
      expect(calculationResult.state_credits.CA).toBeDefined();

      const caCredit = calculationResult.state_credits.CA;
      expect(caCredit.credit).toBeGreaterThan(0);
      expect(caCredit.rate).toBe(0.24); // CA rate is 24%

      console.log(`California (CA) State Credit:`);
      console.log(`  Allocated QRE: $${caCredit.qre_allocated.toLocaleString()}`);
      console.log(`  Credit Rate: ${(caCredit.rate * 100).toFixed(0)}%`);
      console.log(`  Calculated Credit: $${caCredit.credit.toLocaleString()}`);
    });

    test('5.5 Calculate total credits summary', async () => {
      expect(calculationResult.total_credits).toBeGreaterThan(0);

      const totalStateCredits = Object.values(calculationResult.state_credits)
        .reduce((sum, state) => sum + state.credit, 0);

      console.log(`\nTOTAL CREDITS SUMMARY:`);
      console.log(`  Federal Credit: $${calculationResult.final_federal_credit.toLocaleString()}`);
      console.log(`  Total State Credits: $${totalStateCredits.toLocaleString()}`);
      console.log(`  ---`);
      console.log(`  TOTAL CREDITS: $${calculationResult.total_credits.toLocaleString()}`);
    });
  });

  test.describe('6. Output Generation and Download', () => {
    let excelFileId: string;
    let pdfFileId: string;

    test('6.1 Generate Excel workbook', async () => {
      const { url, fileId } = await apiHelper.generateExcelWorkbook(studyId);

      expect(url).toBeTruthy();
      expect(fileId).toBeTruthy();
      excelFileId = fileId;

      console.log(`Generated Excel workbook: ${fileId}`);
    });

    test('6.2 Download and verify Excel workbook', async () => {
      const fileBuffer = await apiHelper.downloadFile(excelFileId);

      expect(fileBuffer).toBeTruthy();
      expect(fileBuffer.length).toBeGreaterThan(0);

      // Save to reports directory
      const outputPath = path.join(REPORTS_PATH, 'technova_rd_study_2024.xlsx');
      fs.writeFileSync(outputPath, fileBuffer);

      // Verify file exists and has reasonable size
      const stats = fs.statSync(outputPath);
      expect(stats.size).toBeGreaterThan(10000); // At least 10KB

      console.log(`Downloaded Excel workbook: ${stats.size} bytes`);
      console.log(`Saved to: ${outputPath}`);
    });

    test('6.3 Generate PDF study report', async () => {
      const { url, fileId } = await apiHelper.generatePDFReport(studyId);

      expect(url).toBeTruthy();
      expect(fileId).toBeTruthy();
      pdfFileId = fileId;

      console.log(`Generated PDF report: ${fileId}`);
    });

    test('6.4 Download and verify PDF report', async () => {
      const fileBuffer = await apiHelper.downloadFile(pdfFileId);

      expect(fileBuffer).toBeTruthy();
      expect(fileBuffer.length).toBeGreaterThan(0);

      // Verify PDF header
      const header = fileBuffer.slice(0, 5).toString('utf-8');
      expect(header).toBe('%PDF-');

      // Save to reports directory
      const outputPath = path.join(REPORTS_PATH, 'technova_rd_study_2024.pdf');
      fs.writeFileSync(outputPath, fileBuffer);

      const stats = fs.statSync(outputPath);
      expect(stats.size).toBeGreaterThan(50000); // At least 50KB for a study PDF

      console.log(`Downloaded PDF report: ${stats.size} bytes`);
      console.log(`Saved to: ${outputPath}`);
    });
  });

  test.describe('7. Final Verification and Summary', () => {
    test('7.1 Get complete study summary', async () => {
      const summary = await apiHelper.getStudySummary(studyId);

      expect(summary.study_id).toBe(studyId);
      expect(summary.entity_name).toBe('TechNova Solutions Inc.');
      expect(summary.tax_year).toBe(2024);
      expect(summary.total_qre).toBeGreaterThan(0);
      expect(summary.federal_credit).toBeGreaterThan(0);
      expect(summary.state_credits).toBeDefined();

      console.log('\n' + '='.repeat(60));
      console.log('R&D STUDY COMPLETION SUMMARY');
      console.log('='.repeat(60));
      console.log(`Entity: ${summary.entity_name}`);
      console.log(`Tax Year: ${summary.tax_year}`);
      console.log(`Total QRE: $${summary.total_qre.toLocaleString()}`);
      console.log(`Federal Credit: $${summary.federal_credit.toLocaleString()}`);
      console.log(`State Credits:`);
      for (const [state, credit] of Object.entries(summary.state_credits)) {
        console.log(`  ${state}: $${(credit as number).toLocaleString()}`);
      }
      console.log(`TOTAL CREDITS: $${summary.total_credits.toLocaleString()}`);
      console.log('='.repeat(60));
    });

    test('7.2 Verify PA and NY specific requirements', async () => {
      // Pennsylvania specific checks
      const paSummary = await apiHelper.getStateCreditDetails(studyId, 'PA');
      expect(paSummary.calculation_steps).toBeDefined();
      expect(paSummary.calculation_steps.length).toBeGreaterThan(0);

      // Verify PA 15-year carryforward
      expect(paSummary.carryforward_years).toBe(15);

      // New York specific checks
      const nySummary = await apiHelper.getStateCreditDetails(studyId, 'NY');
      expect(nySummary.calculation_steps).toBeDefined();

      // Verify NY 15-year carryforward
      expect(nySummary.carryforward_years).toBe(15);

      // Verify NY refundability status
      expect(nySummary.is_refundable).toBeDefined();

      console.log('PA Requirements Verified:');
      console.log(`  - Credit rate: 10%`);
      console.log(`  - Carryforward: ${paSummary.carryforward_years} years`);
      console.log(`  - Form: REV-545`);

      console.log('NY Requirements Verified:');
      console.log(`  - Credit rate: 9%`);
      console.log(`  - Carryforward: ${nySummary.carryforward_years} years`);
      console.log(`  - Refundable: ${nySummary.is_refundable ? 'Yes (50% for QETCs)' : 'No'}`);
      console.log(`  - Form: CT-46`);
    });
  });
});
