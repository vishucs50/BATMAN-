import { Navbar } from '../components/shared/Navbar';
import { TacticalHero } from '../components/shared/TacticalHero';
import { IntelligenceStreams } from '../components/shared/IntelligenceStreams';
import { DecisionLoop } from '../components/coa/DecisionLoop';
import { COAVisualization } from '../components/coa/COAVisualization';
import { CommanderApproval } from '../components/coa/CommanderApproval';
import { IntelligenceArchitecture } from '../components/shared/IntelligenceArchitecture';
import { OperationsGrid } from '../components/shared/OperationsGrid';
import { Principles } from '../components/shared/Principles';
import { InnovationGrid } from '../components/shared/InnovationGrid';
import { Footer } from '../components/shared/Footer';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-bg-main font-sans text-neutral-100 selection:bg-primary-bright selection:text-white">
      <Navbar />
      
      {/* 1. Hero */}
      <TacticalHero />
      
      {/* 2. Mission Intelligence */}
      <IntelligenceStreams />
      
      {/* 3. BATMAN Decision Loop */}
      <DecisionLoop />
      
      {/* 4. Plan & 5. Simulate & 6. COA Scoring */}
      <COAVisualization />
      
      {/* 7. Human-in-the-Loop */}
      <CommanderApproval />
      
      {/* 8. Intelligence Architecture */}
      <IntelligenceArchitecture />
      
      {/* 9. Operational Capabilities */}
      <OperationsGrid />
      
      {/* 10. BATMAN Principles */}
      <Principles />
      
      {/* 11. Innovation Features */}
      <InnovationGrid />
      
      {/* 12. Footer */}
      <Footer />
    </main>
  );
}
