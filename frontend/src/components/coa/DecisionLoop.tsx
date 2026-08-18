import { motion } from 'framer-motion';

const steps = [
  'OBSERVE',
  'UNDERSTAND',
  'PLAN',
  'SIMULATE',
  'SCORE',
  'EXPLAIN',
  'COMMANDER'
];

export const DecisionLoop = () => {
  return (
    <section className="py-32 px-6 md:px-10 bg-bg-secondary w-full" id="loop">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="mb-24 text-center md:text-left"
        >
          <h2 className="text-[clamp(3rem,6vw,6rem)] leading-none font-bold text-white tracking-tighter uppercase">
            From Signal <br />
            <span className="text-primary-bright">To Command.</span>
          </h2>
        </motion.div>

        <div className="flex flex-col items-center">
          {steps.map((step, index) => (
            <motion.div 
              key={step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-20%" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex flex-col items-center"
            >
              <div className={`px-8 py-4 bg-bg-card border w-[300px] text-center shadow-lg relative group overflow-hidden ${index === steps.length - 1 ? 'border-primary-bright bg-primary-dark/20' : 'border-white/10'}`}>
                <div className="absolute inset-0 bg-primary-bright/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                <span className={`relative z-10 text-xl font-bold tracking-widest ${index === steps.length - 1 ? 'text-primary-bright' : 'text-white'}`}>{step}</span>
              </div>
              
              {index < steps.length - 1 && (
                <div className="h-12 border-l border-primary-bright/50 my-2" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
