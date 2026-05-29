import React from "react";

interface ContractFieldsProps {
  startDate: string;
  prazo: number;
  mes: number;
  ano: number;
  onChange: (field: string, value: string | number) => void;
}

export function ContractFields({ startDate, prazo, mes, ano, onChange }: ContractFieldsProps) {
  return (
    <div className="mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
      <h4 className="text-label mb-3">Periodo do Contrato</h4>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Data Inicio</label>
          <input
            type="date"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={startDate}
            onChange={(e) => onChange("startDate", e.target.value)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Prazo (dias)</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={prazo}
            min={1}
            onChange={(e) => onChange("prazo", parseInt(e.target.value) || 0)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Mes</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={mes}
            min={1}
            max={12}
            onChange={(e) => onChange("mes", parseInt(e.target.value) || 1)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Ano</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={ano}
            min={2020}
            max={2100}
            onChange={(e) => onChange("ano", parseInt(e.target.value) || 2026)}
          />
        </div>
      </div>
    </div>
  );
}
