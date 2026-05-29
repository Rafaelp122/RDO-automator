export function Header() {
  return (
    <header className="bg-[var(--color-primary)] h-14 flex items-center px-6 shrink-0 shadow-lg">
      <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center mr-4">
        <div className="w-5 h-5 border-2 border-[var(--color-primary)] rotate-45"></div>
      </div>
      <h1 className="text-[22px] font-bold text-white">RDO Automator</h1>
      <div className="ml-auto flex items-center gap-4">
        <div className="text-white opacity-80 text-xs font-semibold uppercase tracking-wider hidden sm:block">Versão Desktop v2.4</div>
        <div className="w-8 h-8 rounded-full bg-indigo-900/30 flex items-center justify-center text-white text-xs">JS</div>
      </div>
    </header>
  );
}
