import { motion } from 'framer-motion';

export const COAVisualization = () => {
  return (
    <section className="py-32 px-6 md:px-10 max-w-7xl mx-auto w-full">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
        
        {/* Plan Stage */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
        >
          <h3 className="text-xs font-mono tracking-widest text-primary-bright mb-8">PLAN GENERATION</h3>
          <div className="flex flex-col gap-6">
            <div className="border border-white/10 p-6 flex justify-between items-center bg-bg-card group hover:border-primary-bright/50 transition-colors">
              <div>
                <div className="text-xl font-bold text-white mb-1">COA-01</div>
                <div className="text-[10px] font-mono text-neutral-400">BOLD STRATEGY</div>
              </div>
              <div className="w-12 h-1 bg-white/20 group-hover:bg-primary-bright transition-colors" />
            </div>
            
            <div className="border border-primary-bright/50 p-6 flex justify-between items-center bg-primary-dark/10 shadow-[0_0_20px_rgba(0,0,238,0.1)]">
              <div>
                <div className="text-xl font-bold text-white mb-1">COA-02</div>
                <div className="text-[10px] font-mono text-primary-bright">BALANCED (RECOMMENDED)</div>
              </div>
              <div className="w-12 h-1 bg-primary-bright" />
            </div>

            <div className="border border-white/10 p-6 flex justify-between items-center bg-bg-card group hover:border-primary-bright/50 transition-colors">
              <div>
                <div className="text-xl font-bold text-white mb-1">COA-03</div>
                <div className="text-[10px] font-mono text-neutral-400">CAUTIOUS STRATEGY</div>
              </div>
              <div className="w-12 h-1 bg-white/20 group-hover:bg-primary-bright transition-colors" />
            </div>
          </div>
        </motion.div>

        {/* Simulate Stage */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h3 className="text-xs font-mono tracking-widest text-primary-bright mb-8 flex justify-between items-center">
            <span>MONTE CARLO SIMULATION</span>
            <span className="animate-pulse text-white">500 RUNS / COA</span>
          </h3>
          
          <div className="flex flex-col gap-8 bg-bg-card border border-white/5 p-8 h-[312px] justify-center">
            
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-neutral-300">COA-01</span>
                <span className="text-white">74%</span>
              </div>
              <div className="w-full bg-bg-main h-2">
                <motion.div 
                  initial={{ width: 0 }}
                  whileInView={{ width: '74%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.5, delay: 0.5 }}
                  className="h-full bg-white/40" 
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-primary-bright font-bold">COA-02</span>
                <span className="text-white font-bold">87%</span>
              </div>
              <div className="w-full bg-bg-main h-2 shadow-[0_0_10px_rgba(61,61,255,0.2)]">
                <motion.div 
                  initial={{ width: 0 }}
                  whileInView={{ width: '87%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.5, delay: 0.5 }}
                  className="h-full bg-primary-bright" 
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-neutral-300">COA-03</span>
                <span className="text-white">63%</span>
              </div>
              <div className="w-full bg-bg-main h-2">
                <motion.div 
                  initial={{ width: 0 }}
                  whileInView={{ width: '63%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.5, delay: 0.5 }}
                  className="h-full bg-white/40" 
                />
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/5 flex gap-4 text-[10px] font-mono text-neutral-500">
              <span className="flex items-center gap-1"><div className="w-2 h-2 bg-primary-bright" /> SUCCESS DISTRIBUTION</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 bg-semantic-critical/50" /> RISK DISTRIBUTION</span>
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
};
