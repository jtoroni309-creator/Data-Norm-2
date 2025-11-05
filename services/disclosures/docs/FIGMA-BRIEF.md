# Figma Execution Brief

## Design System

**Framework**: React + Fluent UI v9 (Microsoft Design System)

**Tokens**:
- Colors: Brand primary (#0078D4), neutrals, semantic (success/warning/error)
- Typography: Segoe UI, 12-24pt scale
- Spacing: 4px base unit (4, 8, 12, 16, 24, 32, 48, 64px)
- Border radius: 4px (cards), 2px (inputs)
- Elevation: 0-64 (shadow depths)

**Accessibility**: WCAG 2.2 AA
- Contrast ratios ≥4.5:1
- Keyboard navigation (Tab, Enter, Esc)
- ARIA labels on all interactive elements
- Focus rings (2px, brand color)

---

## Information Architecture

```
/engagements                     [Engagement List]
  ├── /:id                       [Engagement Home - Dashboard]
  ├── /:id/planning              [Planning & Risk Assessment]
  ├── /:id/binder                [Cloud Binder Tree]
  ├── /:id/tb                    [Trial Balance Mapper]
  ├── /:id/analytics             [Analytics Dashboard]
  │   ├── /je-tests              [Journal Entry Tests]
  │   └── /ratios                [Ratio Analysis]
  ├── /:id/disclosures           [Disclosure Studio]
  ├── /:id/finalize              [Finalization Wizard]
  └── /:id/reports               [Reports & Archives]

/client/:id                      [Client Portal (PBC Requests)]
```

---

## Component Library

### Navigation
- **AppShell**: Top nav + side nav + content area
- **SideNav**: Collapsible, icons + labels
- **Breadcrumbs**: Current location trail

### Binder
- **BinderTree**: Hierarchical tree (folders, workpapers, evidence)
- **WorkpaperCard**: Title, status badge, assigned user, last modified
- **ReviewNoteDrawer**: Side panel for adding/clearing notes

### Analytics
- **JEFlagCard**: Anomaly summary (icon, severity, count)
- **RatioChart**: Bar chart with trend arrows
- **OutlierTable**: Sortable table with drill-down

### Disclosures
- **DisclosureEditor**: Rich text editor (TipTap or Lexical)
- **CitationChip**: Inline citation badge (clickable to view source)
- **ConfidenceBadge**: Progress ring (0-100%) with color-coded thresholds

### Finalization
- **QCChecklist**: Checklist with pass/fail/waived states
- **ESignatureWizard**: Multi-step wizard (review → sign → confirm)

---

## User Flows

### Flow 1: Import Trial Balance
1. Navigate to `/engagements/:id/tb`
2. Click "Import Trial Balance"
3. Upload Excel/CSV file
4. Review line-by-line preview with mapping suggestions
5. Accept/reject auto-mappings (confidence ≥70%)
6. Manually map low-confidence lines
7. Save and navigate to Analytics

### Flow 2: Generate Disclosure Draft
1. Navigate to `/engagements/:id/disclosures`
2. Select section (e.g., "Revenue Recognition")
3. Click "Generate Draft"
4. Loading state (skeleton)
5. Review generated note items with citation chips
6. Hover citation chip → tooltip with source excerpt
7. Edit text inline
8. Click "Approve" → status = Prepared

### Flow 3: Lock Binder (Finalization)
1. Navigate to `/engagements/:id/finalize`
2. Review QC checklist (auto-populated)
3. If blocking issues exist → display error toast + list issues
4. Clear blocking issues (complete procedures, clear notes)
5. Re-run QC checks
6. All checks pass → Enable "Sign & Lock" button
7. Click "Sign & Lock" → E-signature modal
8. Partner provides signature (PKI cert or DocuSign)
9. Confirm lock → Binder locked toast
10. Redirect to `/engagements/:id/reports` with WORM URI

---

## Layouts & Breakpoints

**Grid**: 12-column, 16px gutter
**Breakpoints**:
- Desktop: ≥1280px (primary)
- Tablet: 768-1279px (constrained layout)
- Mobile: <768px (not supported in v1; display message)

---

## State Management Patterns

**Server State** (TanStack Query):
- Engagements, trial balances, analytics results, disclosures
- Cache TTL: 5 minutes
- Optimistic updates for mutations

**Client State** (Zustand):
- Selected engagement ID
- Binder tree expanded nodes
- Filters (date range, severity)

---

## Design Deliverables (Figma)

1. **Design System Page**: Tokens, components, variants
2. **Engagement Home**: Dashboard with KPIs, team, timeline
3. **Binder Tree**: Full tree with nested folders + workpapers
4. **Trial Balance Mapper**: Table with confidence badges + mapping UI
5. **Analytics Dashboard**: JE flags, ratio charts, outlier table
6. **Disclosure Studio**: Editor with citation chips + confidence
7. **Finalization Wizard**: QC checklist + e-signature flow
8. **Client Portal**: PBC request list + upload area

**Status**: Ready for Figma design phase after backend stabilizes.
