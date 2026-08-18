import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export const Navbar = () => {
  const navigate = useNavigate();
  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 md:px-10 py-4 bg-bg-main/80 backdrop-blur-md border-b border-white/5"
    >
      <div className="flex flex-col">
        <span className="text-xl font-bold tracking-wider text-white">BATMAN</span>
        <span className="text-[10px] tracking-widest text-neutral-400 hidden lg:block uppercase">Battlefield Analytics & Tactical Mission Assistance Network</span>
      </div>
      
      <div className="hidden md:flex items-center space-x-8 text-xs font-mono tracking-widest text-neutral-300">
        <a href="#platform" className="hover:text-white transition-colors">PLATFORM</a>
        <a href="#capabilities" className="hover:text-white transition-colors">CAPABILITIES</a>
        <a href="#architecture" className="hover:text-white transition-colors">ARCHITECTURE</a>
        <a href="#operations" className="hover:text-white transition-colors">OPERATIONS</a>
        <a href="#about" className="hover:text-white transition-colors">ABOUT</a>
      </div>

      <div>
        <button 
          onClick={() => navigate('/command')}
          className="px-5 py-2.5 text-xs font-bold tracking-widest text-white bg-primary-dark hover:bg-primary-bright transition-colors flex items-center gap-2 group border border-primary-bright/30">
          ENTER SYSTEM
          <span className="group-hover:translate-x-1 transition-transform">→</span>
        </button>
      </div>
    </motion.nav>
  );
};
