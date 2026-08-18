import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const streams = [
  {
    id: '01',
    title: 'TERRAIN',
    tags: 'GIS • Elevation • Weather • Infrastructure',
    visual: 'Terrain Raster & Trafficability Model Active'
  },
  {
    id: '02',
    title: 'THREAT',
    tags: 'Sensor Fusion • Probability • Risk',
    visual: 'Probability Zones & Confidence Values Active'
  },
  {
    id: '03',
    title: 'FORCE',
    tags: 'Readiness • Logistics • Communications',
    visual: 'Unit Status & Supply Indicators Active'
  },
  {
    id: '04',
    title: 'MISSION',
    tags: 'Doctrine • Constraints • Mission Memory',
    visual: 'Mission Graph & Constraint Validations Active'
  }
];

export const IntelligenceStreams = () => {
  const [activeStream, setActiveStream] = useState(streams[0].id);

  return (
    <section className="py-32 px-6 md:px-10 max-w-7xl mx-auto w-full" id="capabilities">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
        className="mb-20"
      >
        <h2 className="text-[clamp(3rem,6vw,6rem)] leading-none font-bold text-white tracking-tighter uppercase">
          From Information <br />
          <span className="text-neutral-500">To Decision Advantage.</span>
        </h2>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
        <div className="flex flex-col gap-6 border-l border-white/10 pl-6">
          {streams.map((stream) => (
            <motion.div
              key={stream.id}
              onMouseEnter={() => setActiveStream(stream.id)}
              className={`cursor-pointer transition-all duration-300 ${
                activeStream === stream.id ? 'opacity-100 scale-[1.02]' : 'opacity-40 hover:opacity-70'
              }`}
            >
              <div className="flex items-baseline gap-4 mb-2">
                <span className="text-sm font-mono text-primary-bright font-bold">{stream.id}</span>
                <h3 className="text-3xl font-bold tracking-wide uppercase text-white">{stream.title}</h3>
              </div>
              <p className="text-sm font-mono text-neutral-400 pl-8">{stream.tags}</p>
            </motion.div>
          ))}
        </div>

        <div className="h-[400px] bg-bg-card border border-white/5 relative overflow-hidden flex items-center justify-center group">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,0,238,0.1)_0%,transparent_70%)]" />
          
          <AnimatePresence mode="wait">
            {streams.map((stream) => (
              activeStream === stream.id && (
                <motion.div
                  key={stream.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.4 }}
                  className="relative z-10 flex flex-col items-center justify-center p-8 text-center"
                >
                  <div className="w-32 h-32 mb-6 border border-primary-bright/30 rounded-full flex items-center justify-center">
                     <span className="text-[10px] font-mono text-primary-bright tracking-widest text-center animate-pulse">
                        [STREAM {stream.id}]
                     </span>
                  </div>
                  <h4 className="text-xl font-bold text-white mb-2">{stream.title} ANALYSIS</h4>
                  <p className="text-sm font-mono text-neutral-400 max-w-xs">{stream.visual}</p>
                </motion.div>
              )
            ))}
          </AnimatePresence>

          <div className="absolute bottom-4 right-4 text-[10px] font-mono text-neutral-500">
            PROCESSING: ACTIVE
          </div>
        </div>
      </div>
    </section>
  );
};
