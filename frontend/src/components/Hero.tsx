import { useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Search as SearchIcon, FileText, Zap } from 'lucide-react';
import { BlurText } from './react-bits/BlurText';
import Hyperspeed, { hyperspeedPresets } from './react-bits/Hyperspeed';
import { Squares } from './react-bits/Squares';
import VariableProximity from './react-bits/VariableProximity';

interface HeroProps {
    onStart: () => void;
}

export const Hero = ({ onStart }: HeroProps) => {
    const containerRef = useRef<HTMLDivElement>(null);

    return (
        <div ref={containerRef} className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-dark-bg text-white">
            {/* React Bits Background - Hyperspeed */}
            <Hyperspeed effectOptions={hyperspeedPresets.one} />

            {/* Grid Overlay */}
            <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
                <Squares
                    direction="diagonal"
                    speed={0.1}
                    squareSize={50}
                    borderColor="#8B5CF6"
                    hoverFillColor="#222"
                />
            </div>

            {/* Background Gradients (Kept for depth) */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-brand-primary/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-secondary/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="z-10 text-center px-4"
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                    className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm"
                >
                    <Zap className="w-4 h-4 text-brand-accent" />
                    <span className="text-sm font-medium text-brand-accent">Powered by AI & OCR</span>
                </motion.div>

                <div className="mb-6 relative z-10">
                    {/* Split title for emphasis */}
                    <BlurText
                        text="Search Your Documents"
                        delay={50}
                        className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-neutral-200 to-neutral-400 justify-center drop-shadow-2xl"
                    />
                    <br className="hidden md:block" />

                    <div style={{ position: 'relative', display: 'inline-block' }}>
                        <VariableProximity
                            label="Instantly"
                            className="text-5xl md:text-7xl font-bold text-violet-400 mt-2 cursor-default drop-shadow-[0_0_15px_rgba(139,92,246,0.5)]"
                            fromFontVariationSettings="'wght' 700, 'wdth' 100"
                            toFontVariationSettings="'wght' 900, 'wdth' 125"
                            containerRef={containerRef}
                            radius={100}
                            falloff="gaussian"
                        />
                    </div>
                </div>

                <p className="text-xl text-gray-200 mb-10 max-w-2xl mx-auto leading-relaxed drop-shadow-md bg-black/30 backdrop-blur-[2px] rounded-xl p-4">
                    Upload PDF or Excel files. Our intelligent engine extracts text and enables fuzzy search to find exactly what you need, even with typos.
                </p>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onStart}
                    className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full text-lg font-semibold shadow-lg shadow-brand-primary/20 transition-all hover:bg-brand-primary hover:text-white cursor-pointer z-50"
                >
                    <Upload className="w-5 h-5" />
                    Start Uploading
                    <span className="absolute inset-0 rounded-full ring-2 ring-white/20 group-hover:ring-white/40 transition-all" />
                </motion.button>
            </motion.div>
        </div>
    );
};
