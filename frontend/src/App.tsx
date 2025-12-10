import { useState } from 'react';
import { Hero } from './components/Hero';
import { SearchInterface } from './components/SearchInterface';
import { motion } from 'framer-motion';

function App() {
  const [showSearch, setShowSearch] = useState(false);

  return (
    <div className="min-h-screen bg-dark-bg text-white selection:bg-brand-primary selection:text-white">
      {!showSearch ? (
        <motion.div
          key="hero"
        // exit prop removed as AnimatePresence is removed
        >
          <Hero onStart={() => setShowSearch(true)} />
        </motion.div>
      ) : (
        <motion.div
          key="search"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <SearchInterface onBack={() => setShowSearch(false)} />
        </motion.div>
      )}
    </div>
  );
}

export default App;
