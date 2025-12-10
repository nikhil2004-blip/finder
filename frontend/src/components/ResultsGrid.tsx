import { motion } from 'framer-motion';
import type { SearchResult } from '../services/api';
import { FileText, MapPin } from 'lucide-react';

interface ResultsGridProps {
    results: SearchResult[];
}

export const ResultsGrid = ({ results }: ResultsGridProps) => {
    if (results.length === 0) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
            {results.map((result, index) => (
                <motion.div
                    key={`${result.file_name}-${index}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-dark-card border border-zinc-800 rounded-xl p-6 hover:border-brand-primary/50 transition-colors group cursor-pointer"
                >
                    <div className="flex items-start justify-between mb-4">
                        <div className="p-2 bg-zinc-800 rounded-lg group-hover:bg-brand-primary/20 transition-colors">
                            <FileText className="w-6 h-6 text-zinc-400 group-hover:text-brand-primary" />
                        </div>
                        <span className="text-xs text-zinc-500 bg-zinc-900 px-2 py-1 rounded">
                            Score: {Math.round(result.score * 100)}%
                        </span>
                    </div>

                    <p className="text-sm text-zinc-300 line-clamp-3 mb-4 font-medium leading-relaxed">
                        "{result.text}"
                    </p>

                    <div className="flex items-center gap-2 text-xs text-zinc-500 mt-auto pt-4 border-t border-zinc-800">
                        <span className="truncate max-w-[150px]" title={result.file_name}>
                            {result.file_name}
                        </span>
                        <span className="w-1 h-1 bg-zinc-600 rounded-full" />
                        <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            Page {result.page_number}
                        </span>
                        {result.metadata?.row && (
                            <>
                                <span className="w-1 h-1 bg-zinc-600 rounded-full" />
                                <span>R{result.metadata.row}</span>
                            </>
                        )}
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
