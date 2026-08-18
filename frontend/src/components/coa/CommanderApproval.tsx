import { motion } from 'framer-motion';

export const CommanderApproval = () => {
  return (
    <section className="py-32 px-6 md:px-10 max-w-7xl mx-auto w-full" id="hitl">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
        className="mb-16"
      >
        <h2 className="text-[clamp(3rem,6vw,6rem)] leading-none font-bold text-white tracking-tighter uppercase">
          AI Advises. <br />
          <span className="text-primary-bright">Humans Command.</span>
        </h2>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="max-w-2xl bg-bg-card border border-primary-bright/30 p-8 shadow-[0_0_40px_rgba(0,0,238,0.1)] relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-primary-bright" />
        
        <div className="flex justify-between items-start mb-8">
          <div>
            <h3 className="text-2xl font-bold tracking-widest text-white mb-1">COA / 02</h3>
            <span className="text-xs font-mono bg-semantic-success/20 text-semantic-success px-2 py-1 border border-semantic-success/30">
              RECOMMENDED
            </span>
          </div>
          <div className="text-right">
            <div className="text-[10px] font-mono text-neutral-400">AWAITING</div>
            <div className="text-sm font-bold text-semantic-warning animate-pulse">COMMANDER APPROVAL</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-bg-secondary p-4 border border-white/5">
            <div className="text-[10px] font-mono text-neutral-400 mb-1">MISSION SUCCESS</div>
            <div className="text-xl font-bold text-white">87%</div>
          </div>
          <div className="bg-bg-secondary p-4 border border-white/5">
            <div className="text-[10px] font-mono text-neutral-400 mb-1">RISK</div>
            <div className="text-xl font-bold text-semantic-warning">LOW–MODERATE</div>
          </div>
          <div className="bg-bg-secondary p-4 border border-white/5">
            <div className="text-[10px] font-mono text-neutral-400 mb-1">RESOURCE EFFICIENCY</div>
            <div className="text-xl font-bold text-white">81%</div>
          </div>
          <div className="bg-bg-secondary p-4 border border-white/5">
            <div className="text-[10px] font-mono text-neutral-400 mb-1">CONFIDENCE</div>
            <div className="text-xl font-bold text-white">84%</div>
          </div>
        </div>

        <div className="mb-10">
          <h4 className="text-xs font-bold tracking-widest text-primary-bright mb-4">WHY THIS COA?</h4>
          <ul className="space-y-2 text-sm font-mono text-neutral-300">
            <li className="flex items-center gap-2">
              <span className="text-semantic-success">+</span> Reduced terrain exposure
            </li>
            <li className="flex items-center gap-2">
              <span className="text-semantic-success">+</span> Better communications coverage
            </li>
            <li className="flex items-center gap-2">
              <span className="text-semantic-success">+</span> Higher recovery potential
            </li>
          </ul>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <button className="flex-1 py-3 text-xs font-bold tracking-widest text-white border border-white/20 hover:bg-white/5 transition-colors">
            MODIFY
          </button>
          <button className="flex-1 py-3 text-xs font-bold tracking-widest text-semantic-critical border border-semantic-critical/30 hover:bg-semantic-critical/10 transition-colors">
            REJECT
          </button>
          <button className="flex-1 py-3 text-xs font-bold tracking-widest text-white bg-semantic-success/80 hover:bg-semantic-success transition-colors shadow-[0_0_15px_rgba(34,197,94,0.3)]">
            APPROVE
          </button>
        </div>
      </motion.div>
    </section>
  );
};
