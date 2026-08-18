import { motion } from 'framer-motion';

const operations = [
  { id: '01', title: 'BORDER OPERATIONS', desc: 'Abstract terrain intelligence and infiltration routing.' },
  { id: '02', title: 'HIGH-ALTITUDE LOGISTICS', desc: 'Mountain terrain, supply routes and weather impact.' },
  { id: '03', title: 'URBAN OPERATIONS', desc: 'Building geometry, sightlines and route analysis.' },
  { id: '04', title: 'CONVOY PROTECTION', desc: 'Route risk assessment and logistics tracking.' },
  { id: '05', title: 'HUMANITARIAN RESPONSE', desc: 'Disaster-area mapping and evacuation planning.' }
];

export const OperationsGrid = () => {
  return (
    <section className="py-32 px-6 md:px-10 max-w-7xl mx-auto w-full" id="operations">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
        className="mb-16"
      >
        <h2 className="text-xs font-mono tracking-widest text-primary-bright mb-4">CAPABILITIES</h2>
        <h3 className="text-3xl font-bold tracking-wider text-white uppercase">Operational Profiles</h3>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {operations.map((op, idx) => (
          <motion.div
            key={op.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            className="group relative h-64 bg-bg-card border border-white/5 p-6 flex flex-col justify-end overflow-hidden hover:border-primary-bright/50 transition-colors"
          >
            {/* Abstract visual background */}
            <div className="absolute inset-0 opacity-10 group-hover:opacity-20 transition-opacity flex items-center justify-center">
               <svg width="100%" height="100%" className="text-primary-bright stroke-current" strokeWidth="1" fill="none">
                  {idx % 2 === 0 ? (
                    <circle cx="50%" cy="50%" r="40%" />
                  ) : (
                    <rect x="10%" y="10%" width="80%" height="80%" />
                  )}
                  <line x1="0" y1="50%" x2="100%" y2="50%" strokeDasharray="4 4" />
                  <line x1="50%" y1="0" x2="50%" y2="100%" strokeDasharray="4 4" />
               </svg>
            </div>
            
            <div className="relative z-10">
              <span className="text-[10px] font-mono text-primary-bright mb-2 block">{op.id}</span>
              <h4 className="text-lg font-bold text-white tracking-widest mb-2">{op.title}</h4>
              <p className="text-xs font-mono text-neutral-400">{op.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
