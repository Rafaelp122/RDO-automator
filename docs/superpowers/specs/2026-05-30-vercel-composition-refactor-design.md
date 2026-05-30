# Design: Vercel Composition Patterns Refactor

**Date:** 2026-05-30  
**Skill:** vercel-composition-patterns v1.0.0  
**React:** 19.0.1

## Scope

Refatorar o frontend RDO Automator aplicando todas as regras do skill
vercel-composition-patterns: compound components, context providers com
interfaces `state/actions/meta`, variantes explícitas, state decoupling, e
React 19 APIs.

## Current Anti-Patterns

| Anti-pattern | Skill Rule | Location |
|---|---|---|
| Boolean `isInteractive` switch | `architecture-avoid-boolean-props` | `TemplatePreview.tsx` |
| Boolean `disabled` lock | `architecture-avoid-boolean-props` | `AccordionSection.tsx` |
| Monolithic parent component | `architecture-compound-components` | `App.tsx` (269 lines, 13 useState) |
| State coupled to UI | `state-decouple-implementation` | All state in App.tsx, prop drilled |
| No context interfaces | `state-context-interface` | Zero `createContext` usage |
| No provider boundaries | `state-lift-state` | Footer button must call App callback |
| Hidden conditional modes | `patterns-explicit-variants` | `isInteractive` mode switch |
| No React 19 APIs used | `react19-no-forwardref` | N/A (no context yet; will use `use()`) |

## Architecture

### Provider Hierarchy

```
WizardProvider
├── DataSourceProvider
│   ├── SourceFileUpload (lê DataSourceContext, wrappa FileUpload)
│   └── DataSource.Preview (lê DataSourceContext)
├── TemplateSourceProvider
│   ├── TemplateFileUpload (lê TemplateSourceContext, wrappa FileUpload)
│   └── TemplatePreview.ReadOnly (lê TemplateSourceContext)
├── MappingProvider
│   ├── MappingSection (lê MappingContext)
│   └── TemplatePreview.Interactive (lê MappingContext + TemplateSourceContext)
└── Footer GenerateButton (lê 3 contexts + contract useState do App)
```

Note: `ContractFields` stays prop-based — 4 fields com 1 consumidor, provider
seria YAGNI. O `App.tsx` mantém `useState` para contract (único estado que
sobra fora de provider).

### Context Interfaces

All contexts follow the `{ state, actions, meta }` pattern:

**WizardContext:**
```typescript
interface WizardContextValue {
  state: { activeSegment: number; completedSteps: Set<number> }
  actions: { openStep(n: number): void; closeAll(): void; completeStep(n: number): void }
  meta: {}
}
```

**DataSourceContext:**
```typescript
interface DataSourceContextValue {
  state: { fileName: string | null; file: File | null; sheets: Sheet[]; isComplete: boolean }
  actions: { upload(name: string, f: File): Promise<void>; clear(): void; toggleSheet(name: string): void; toggleColumn(sheetName: string, col: string): void; confirm(): void }
  meta: {}
}
```

**TemplateSourceContext:**
```typescript
interface TemplateSourceContextValue {
  state: { fileName: string | null; file: File | null; sheets: TemplateSheet[]; isComplete: boolean }
  actions: { upload(name: string, f: File): Promise<void>; clear(): void; confirm(): void }
  meta: {}
}
```

**MappingContext:**
```typescript
interface MappingContextValue {
  state: { mappings: MappingData[]; selectedCell: string | null; formatTemplate: string; listSeparator: string; listConnector: string }
  actions: { selectCell(ref: string): void; addColumnToFormat(col: string): void; updateFormat(text: string): void; addMapping(): void; removeMapping(id: string): void; setSeparator(v: string): void; setConnector(v: string): void }
  meta: { textareaRef: React.RefObject<HTMLTextAreaElement> }
}
```

### Data Flow Between Providers

- `WizardProvider` wraps all providers. Child providers call
  `wizardActions.completeStep(n)` on confirmation.
- `WizardProvider` auto-advances: step 1 complete -> open step 2; step 2
  complete -> open step 3.
- `WizardProvider` locks step 3 until steps 1 and 2 are both complete.
- The Generate button in the footer reads `file` from both
  `DataSourceContext` and `TemplateSourceContext`, and `mappings` from
  `MappingContext` — no prop drilling from App.

### Compound Components

**Wizard:**
```typescript
const Wizard = { Step, StepHeader, StepContent }
```
- `Wizard.Step` reads from WizardContext to determine disabled/expanded/completed state
- Replaces `AccordionSection` — no more `disabled`, `isExpanded`, `isCompleted` props

**TemplatePreview:**
```typescript
const TemplatePreview = { ReadOnly, Interactive }
```
- `TemplatePreview.ReadOnly` — renders grid + "Confirmar Template" button; calls
  `templateSourceActions.confirm()`
- `TemplatePreview.Interactive` — renders grid + cell click handlers; reads
  from `MappingContext` for `selectedCell` and `mappedCells`
- Both share a private `TemplatePreviewGrid` for the table rendering (no
  boolean `isInteractive`)

**DataSource:**
```typescript
const DataSource = { Provider, Preview }
```
- `DataSource.Preview` replaces current `DataPreview` — reads from
  `DataSourceContext` instead of props

### File Structure

```
src/components/
├── Header.tsx                        # unchanged
├── ContractFields.tsx                # unchanged (prop-based, single consumer)
├── FileUpload.tsx                    # unchanged
├── wizard/
│   ├── WizardProvider.tsx            # context + provider + step logic
│   └── WizardStep.tsx                # Step, StepHeader, StepContent
├── datasource/
│   ├── DataSourceProvider.tsx        # context + provider + API call
│   ├── DataPreview.tsx               # reads DataSourceContext
│   └── SourceFileUpload.tsx          # wraps FileUpload, reads DataSourceContext
├── templatesource/
│   ├── TemplateSourceProvider.tsx    # context + provider + API call
│   ├── TemplateFileUpload.tsx        # wraps FileUpload, reads TemplateSourceContext
│   └── TemplateSourcePreview.tsx     # ReadOnly variant wrapper
├── mapping/
│   ├── MappingProvider.tsx           # context + provider
│   └── MappingSection.tsx            # reads MappingContext
└── templatepreview/
    ├── TemplatePreviewGrid.tsx       # shared grid (no isInteractive)
    ├── TemplatePreviewReadOnly.tsx
    └── TemplatePreviewInteractive.tsx

src/
├── App.tsx                           # ~50 lines — just composes providers
├── types.ts                          # updated with context interfaces
```

### App.tsx After Refactor

```typescript
export default function App() {
  const [contractStart, setContractStart] = useState("2026-01-01")
  const [contractPrazo, setContractPrazo] = useState(30)
  const [contractMes, setContractMes] = useState(1)
  const [contractAno, setContractAno] = useState(2026)
  const contract = { startDate: contractStart, prazo: contractPrazo, mes: contractMes, ano: contractAno }

  return (
    <WizardProvider>
      <DataSourceProvider>
        <TemplateSourceProvider>
          <MappingProvider>
            <div className="h-screen flex flex-col ...">
              <Header />
              <main>
                <Wizard.Step step={1} title="1. Dados da Medição">
                  <ContractFields startDate={contractStart} prazo={contractPrazo}
                    mes={contractMes} ano={contractAno}
                    onChange={(f, v) => { /* ...setters... */ }} />
                  <SourceFileUpload />
                  <DataSource.Preview />
                </Wizard.Step>
                <Wizard.Step step={2} title="2. Template do Relatório">
                  <TemplateFileUpload />
                  <TemplatePreview.ReadOnly />
                </Wizard.Step>
                <Wizard.Step step={3} title="3. Mapeamento de Células">
                  <MappingSection />
                  <TemplatePreview.Interactive />
                </Wizard.Step>
              </main>
              <GenerateFooter contract={contract} />
            </div>
          </MappingProvider>
        </TemplateSourceProvider>
      </DataSourceProvider>
    </WizardProvider>
  );
}
```

## What Changes and What Stays

### Changed
- `App.tsx` — becomes thin provider composition (~50 lines)
- `AccordionSection.tsx` — deleted, replaced by `Wizard.Step`
- `TemplatePreview.tsx` — deleted, replaced by `TemplatePreview.ReadOnly`,
  `TemplatePreview.Interactive`, and shared `TemplatePreviewGrid`
- `DataPreview.tsx` — rewritten to read from `DataSourceContext`
- `MappingSection.tsx` — rewritten to read from `MappingContext`
- `types.ts` — added context interface types
- New files: `WizardProvider.tsx`, `WizardStep.tsx`, `DataSourceProvider.tsx`, `SourceFileUpload.tsx`, `TemplateSourceProvider.tsx`, `TemplateFileUpload.tsx`, `TemplateSourcePreview.tsx`, `MappingProvider.tsx`, `TemplatePreviewGrid.tsx`, `TemplatePreviewReadOnly.tsx`, `TemplatePreviewInteractive.tsx`, `GenerateFooter.tsx`

### Unchanged
- `Header.tsx` — static, no state
- `ContractFields.tsx` — 4 simple form fields, single consumer, prop-based stays
- `FileUpload.tsx` — pure UI widget, stays prop-based (single purpose, no boolean mode switches)
- `services/api.ts` — pure functions, no changes
- `index.css` — no changes
- `vite.config.ts`, `tsconfig.json`, `package.json` — no changes

## React 19 Compliance

- `use()` instead of `useContext()` for all context reads
- `ref` as regular prop (no `forwardRef`)

## Verification

- `npm run lint` (tsc --noEmit) must pass with zero errors
- Manual smoke test: upload source, confirm preview, upload template, confirm
  preview, create mappings, generate report
