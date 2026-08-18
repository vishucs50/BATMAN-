import { motion } from 'framer-motion';

const principles = [
  { id: '01', text: 'HUMAN SUPREMACY' },
  { id: '02', text: 'EXPLAINABILITY FIRST' },
  { id: '03', text: 'OFFLINE-FIRST' },
  { id: '04', text: 'INDIGENOUS INTELLIGENCE' },
  { id: '05', text: 'DOCTRINE-ALIGNED' },
  { id: '06', text: 'SIMULATION-DRIVEN' }
];

export const Principles = () => {
  return (
    <section className="py-40 px-6 md:px-10 bg-bg-secondary w-full border-y border-white/5" id="about">
      <div className="max-w-5xl mx-auto flex flex-col items-start gap-12">
        {principles.map((p, idx) => (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: idx * 0.1 }}
            className="flex items-baseline gap-8 group"
          >
            <span className="text-lg md:text-2xl font-mono text-neutral-500 group-hover:text-primary-bright transition-colors">
              {p.id}
            </span>
            <h2 className="text-3xl md:text-5xl lg:text-7xl font-bold tracking-tighter text-white group-hover:text-white transition-colors">
              {p.text}
            </h2>
          </motion.div>
        ))}
      </div>
    </section>
  );
};
