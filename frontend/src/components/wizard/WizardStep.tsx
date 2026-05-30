import { use, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { WizardContext } from './WizardProvider';

interface WizardStepProps {
  step: number;
  title: string;
  children: ReactNode;
}

function Step({ step, title, children }: WizardStepProps) {
  const {
    state: { activeSegment, completedSteps },
    actions: { openStep },
  } = use(WizardContext)!;

  const isExpanded = activeSegment === step;
  const isCompleted = completedSteps.has(step);
  const isLocked = step === 3 && (!completedSteps.has(1) || !completedSteps.has(2));

  return (
    <div className={`bg-white border border-[var(--color-card-border)] rounded-[12px] shadow-sm mb-4 flex flex-col overflow-hidden transition-all duration-300 ${isLocked ? 'opacity-50 grayscale select-none' : ''}`}>
      <StepHeader
        step={step}
        title={title}
        isExpanded={isExpanded}
        isCompleted={isCompleted}
        isLocked={isLocked}
        onToggle={() => { if (!isLocked) openStep(step); }}
      />
      <StepContent isExpanded={isExpanded && !isLocked}>
        {children}
      </StepContent>
    </div>
  );
}

interface StepHeaderProps {
  step: number;
  title: string;
  isExpanded: boolean;
  isCompleted: boolean;
  isLocked: boolean;
  onToggle: () => void;
}

function StepHeader({ step, title, isExpanded, isCompleted, isLocked, onToggle }: StepHeaderProps) {
  return (
    <button
      className={`w-full p-4 flex items-center justify-between transition-colors ${isLocked ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-slate-50'}`}
      onClick={onToggle}
      title={isLocked ? 'Conclua os passos 1 e 2 acima para liberar o mapeamento de células' : undefined}
    >
      <div className="flex items-center gap-3">
        <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-1 ${isLocked ? 'bg-slate-200' : isCompleted ? 'bg-green-500' : 'border-2 border-[var(--color-primary)] bg-white'}`}>
          {isLocked ? (
            <Lock size={12} className="text-slate-500" />
          ) : isCompleted ? (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
          ) : (
            <span className="text-[11px] font-bold text-[var(--color-primary)]">0{step}</span>
          )}
        </div>
        <h2 className={`text-[14px] font-bold ${isLocked ? 'text-slate-500' : 'text-[var(--color-primary)]'}`}>
          {title} {isLocked && <span className="opacity-70 font-normal ml-1">(Bloqueado)</span>}
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-[var(--color-text-secondary)]">
          {!isLocked && (isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />)}
        </div>
      </div>
    </button>
  );
}

function StepContent({ children, isExpanded }: { children: ReactNode; isExpanded: boolean }) {
  return (
    <AnimatePresence initial={false}>
      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
          <div className="px-6 pb-6 pt-2 border-t border-[var(--color-card-border)] bg-white h-full relative z-0">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export const Wizard = { Step, StepHeader, StepContent };
