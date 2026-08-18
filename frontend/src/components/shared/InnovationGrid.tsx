import { motion } from 'framer-motion';

const innovations = [
  {
    title: 'MISSION MEMORY',
    desc: 'Previous missions represented as semantic/graph embeddings.',
    meta: 'NEO4J / VECTOR DB'
  },
  {
    title: 'READINESS SCORE',
    desc: 'Personnel + Equipment + Logistics + Communications + Training.',
    meta: 'REAL-TIME AGGREGATION'
  },
  {
    title: 'TERRAIN INTELLIGENCE',
    desc: 'Trafficability, chokepoints, cover, LZ analysis and environmental conditions.',
    meta: 'GIS / ELEVATION'
  },
  {
    title: 'COMMS PLANNING',
    desc: 'RF propagation, communication shadows and relay planning.',
    meta: 'PHYSICS ENGINE'
  },
  {
    title: 'COLLABORATIVE PLANNING',
    desc: 'Multiple officers working on the same plan.',
    meta: 'CRDT / WEBSOCKET'
  },
  {
    title: 'OFFLINE VOICE PLANNING',
    desc: 'Air-gapped speech interface.',
    meta: 'LOCAL WHISPER'
  },
  {
    title: 'LOGISTICS FORECASTING',
    desc: '72-hour supply forecasting.',
    meta: 'TIME-SERIES'
  },
  {
    title: 'OPORD GENERATION',
    desc: 'Structured order generation from approved mission data.',
    meta: 'LLM (LOCAL)'
  }
];

export const InnovationGrid = () => {
  return (
    <section className="py-32 px-6 md:px-10 max-w-7xl mx-auto w-full">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
        className="mb-16 border-b border-white/5 pb-6"
      >
        <h3 className="text-xl font-mono tracking-widest text-white uppercase">Platform Differentiators</h3>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {innovations.map((item, idx) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: idx * 0.05 }}
            className="p-4 border border-white/10 bg-bg-card hover:bg-bg-secondary hover:border-primary-bright/30 transition-colors group flex flex-col justify-between min-h-[160px]"
          >
            <div>
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-sm font-bold text-white tracking-wider">{item.title}</h4>
                <span className="text-primary-bright group-hover:translate-x-1 transition-transform opacity-0 group-hover:opacity-100">→</span>
              </div>
              <p className="text-[11px] font-mono text-neutral-400 leading-relaxed">
                {item.desc}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/5 text-[9px] font-mono text-primary-bright/70 tracking-widest">
              MODULE: {item.meta}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
