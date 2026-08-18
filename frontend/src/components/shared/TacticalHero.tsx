import { motion } from 'framer-motion';
import { ThreeDMap } from '../map/ThreeDMap';
import { useNavigate } from 'react-router-dom';

export const TacticalHero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative w-full flex items-center overflow-hidden pt-20" style={{ height: '100vh', minHeight: '600px' }} id="platform">
      <ThreeDMap />
      
      {/* Vignette overlay for text readability */}
      <div className="absolute inset-0 bg-gradient-to-r from-bg-main via-bg-main/70 to-transparent pointer-events-none z-0" />
      <div className="absolute inset-0 bg-gradient-to-t from-bg-main via-transparent to-transparent pointer-events-none z-0" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-10 w-full flex flex-col md:flex-row items-center justify-between">
        
        {/* Left Content */}
        <div className="w-full md:w-[65%] flex flex-col gap-8">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <h1 className="text-[clamp(2.5rem,5vw,5rem)] leading-[1.05] font-bold text-white tracking-tight uppercase">
              Battlefield Analytics & <br/>
              Tactical Mission <br/>
              <span className="text-primary-bright">Assistance Network</span>
            </h1>
          </motion.div>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="text-lg md:text-xl text-neutral-300 max-w-2xl font-light border-l-2 border-primary-bright pl-6"
          >
            AI-assisted command decision support for planning, simulation, risk analysis and mission understanding.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mt-4"
          >
            <button 
              onClick={() => navigate('/command')}
              className="px-8 py-4 bg-primary-dark text-white font-bold tracking-widest text-sm hover:bg-primary-bright transition-all border border-transparent hover:border-white/30 flex items-center gap-3 group">
              ENTER COMMAND DASHBOARD
              <span className="group-hover:translate-x-2 transition-transform">→</span>
            </button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="flex flex-wrap gap-4 mt-8"
          >
            <span className="px-3 py-1 bg-white/5 border border-white/10 text-xs font-mono tracking-wider text-accent-dark">HUMAN-IN-THE-LOOP</span>
            <span className="px-3 py-1 bg-white/5 border border-white/10 text-xs font-mono tracking-wider text-accent-dark">OFFLINE-FIRST</span>
            <span className="px-3 py-1 bg-white/5 border border-white/10 text-xs font-mono tracking-wider text-accent-dark">EXPLAINABLE AI</span>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
