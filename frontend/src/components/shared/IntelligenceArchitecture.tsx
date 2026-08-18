import { motion } from 'framer-motion';

const subsystems = [
  'KNOWLEDGE GRAPH',
  'HTN PLANNER',
  'BAYESIAN NETWORK',
  'GNN / GAT',
  'CASE-BASED REASONING',
  'RULE ENGINE',
  'MONTE CARLO',
  'ACO',
  'MULTI-AGENT SIMULATION'
];

export const IntelligenceArchitecture = () => {
  return (
    <section className="py-32 px-6 md:px-10 bg-bg-main w-full border-t border-white/5" id="architecture-network">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-16 items-center">
        
        <div className="flex-1 w-full">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-[clamp(3rem,5vw,5rem)] leading-none font-bold text-white tracking-tighter uppercase mb-6">
              Not One AI. <br />
              <span className="text-primary-bright">An Intelligence System.</span>
            </h2>
            <p className="text-lg text-neutral-400 max-w-lg font-light">
              BATMAN does not rely on a single black-box model. It uses a neuro-symbolic architecture connecting multiple specialized solvers to guarantee explainability and doctrine compliance.
            </p>
          </motion.div>
        </div>

        <div className="flex-1 w-full relative">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,0,238,0.1)_0%,transparent_70%)] pointer-events-none" />
          
          <div className="flex items-center justify-between gap-8 h-full relative z-10">
            {/* Subsystems List */}
            <div className="flex flex-col gap-3">
              {subsystems.map((sys, idx) => (
                <motion.div
                  key={sys}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.05 }}
                  className="px-4 py-2 bg-bg-card border border-white/10 text-[10px] font-mono text-neutral-300 relative group"
                >
                  {sys}
                  <div className="absolute -right-8 top-1/2 -translate-y-1/2 w-8 h-[1px] bg-primary-bright/30" />
                </motion.div>
              ))}
            </div>

            {/* Central Node */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="relative"
            >
              <div className="w-48 h-48 rounded-full border border-primary-bright flex items-center justify-center bg-primary-dark/10 shadow-[0_0_30px_rgba(61,61,255,0.2)]">
                <div className="text-center">
                  <div className="text-xl font-bold tracking-widest text-white">COA ENGINE</div>
                  <div className="text-[10px] font-mono text-primary-bright mt-2 animate-pulse">SYNTHESIZING</div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

      </div>
    </section>
  );
};
