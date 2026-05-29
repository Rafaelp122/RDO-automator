import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface AccordionSectionProps {
  title: string;
  stepNumber: number;
  isExpanded: boolean;
  isCompleted: boolean;
  disabled?: boolean;
  disabledMessage?: string;
  onToggle: () => void;
  children: React.ReactNode;
}

export function AccordionSection({ 
  title, 
  stepNumber, 
  isExpanded, 
  isCompleted, 
  disabled = false,
  disabledMessage,
  onToggle, 
  children 
}: AccordionSectionProps) {
  return (
    <div className={`bg-white border border-[var(--color-card-border)] rounded-[12px] shadow-sm mb-4 flex flex-col overflow-hidden transition-all duration-300 ${disabled ? 'opacity-50 grayscale select-none' : ''}`}>
      <button 
        className={`w-full p-4 flex items-center justify-between transition-colors ${disabled ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-slate-50'}`}
        onClick={() => {
          if (!disabled) onToggle();
        }}
        title={disabled ? (disabledMessage || 'Bloqueado') : undefined}
      >
        <div className="flex items-center gap-3">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-1 ${disabled ? 'bg-slate-200' : isCompleted ? 'bg-green-500' : 'border-2 border-[var(--color-primary)] bg-white'}`}>
            {disabled ? (
              <Lock size={12} className="text-slate-500" />
            ) : isCompleted ? (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
            ) : (
              <span className="text-[11px] font-bold text-[var(--color-primary)]">0{stepNumber}</span>
            )}
          </div>
          <h2 className={`text-[14px] font-bold ${disabled ? 'text-slate-500' : 'text-[var(--color-primary)]'}`}>
            {title} {disabled && <span className="opacity-70 font-normal ml-1">(Bloqueado)</span>}
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-[var(--color-text-secondary)]">
            {!disabled && (isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />)}
          </div>
        </div>
      </button>
      
      <AnimatePresence initial={false}>
        {isExpanded && !disabled && (
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
    </div>
  );
}
