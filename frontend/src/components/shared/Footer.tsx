
export const Footer = () => {
  return (
    <footer className="w-full bg-bg-main border-t border-white/5 py-16 px-6 mt-24">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
        <div className="flex flex-col max-w-sm">
          <span className="text-2xl font-bold tracking-wider text-white mb-2">BATMAN</span>
          <span className="text-xs tracking-widest text-neutral-400 leading-relaxed mb-6 uppercase">
            BATTLEFIELD ANALYTICS & TACTICAL MISSION ASSISTANCE NETWORK
          </span>
          <span className="text-[10px] font-mono text-neutral-500 border border-neutral-500/30 px-2 py-1 inline-block w-max">
            ACADEMIC / RESEARCH PROTOTYPE
          </span>
        </div>
        
        <div className="flex flex-col space-y-3 text-xs font-mono tracking-widest text-neutral-400">
          <a href="#platform" className="hover:text-white transition-colors uppercase">Platform</a>
          <a href="#architecture" className="hover:text-white transition-colors uppercase">Architecture</a>
          <a href="#capabilities" className="hover:text-white transition-colors uppercase">Capabilities</a>
          <a href="#operations" className="hover:text-white transition-colors uppercase">Operations</a>
          <a href="#documentation" className="hover:text-white transition-colors uppercase">Documentation</a>
        </div>
        
        <div className="flex flex-col items-start md:items-end text-left md:text-right">
          <span className="text-sm tracking-widest text-primary-bright font-semibold mb-2">
            AI-ASSISTED. HUMAN-CONTROLLED.
          </span>
          <div className="w-12 h-1 bg-accent-dark"></div>
        </div>
      </div>
    </footer>
  );
};
