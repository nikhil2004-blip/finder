import { motion, AnimatePresence } from 'framer-motion';
import { X, Trash2, FileText, AlertCircle } from 'lucide-react';
import { useState } from 'react';

interface FileListModalProps {
    isOpen: boolean;
    onClose: () => void;
    files: any[];
    onDelete: (filename: string) => Promise<void>;
}

export const FileListModal = ({ isOpen, onClose, files, onDelete }: FileListModalProps) => {
    const [deleting, setDeleting] = useState<string | null>(null);

    const handleDelete = async (filename: string) => {
        setDeleting(filename);
        await onDelete(filename);
        setDeleting(null);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-50 w-full md:w-[600px] h-full md:h-[600px] bg-dark-card border border-zinc-800 md:rounded-2xl shadow-2xl overflow-hidden flex flex-col"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-6 border-b border-zinc-800 bg-zinc-900/50">
                            <h2 className="text-xl font-bold flex items-center gap-2">
                                <FileText className="w-5 h-5 text-brand-primary" />
                                Managed Files
                            </h2>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-white/10 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* File List */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
                            {files.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-full text-zinc-500 gap-4">
                                    <AlertCircle className="w-12 h-12 opacity-20" />
                                    <p>No processed files found</p>
                                </div>
                            ) : (
                                files.map((file) => (
                                    <motion.div
                                        layout
                                        key={file.filename}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                        className="flex items-center justify-between p-4 bg-zinc-900/40 border border-zinc-800/50 rounded-xl group hover:border-brand-primary/30 hover:bg-zinc-900/60 transition-all"
                                    >
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className="p-2 bg-zinc-800 rounded-lg group-hover:bg-brand-primary/20 transition-colors">
                                                <FileText className="w-4 h-4 text-zinc-400 group-hover:text-brand-primary" />
                                            </div>
                                            <div className="flex flex-col min-w-0">
                                                <span className="font-medium text-sm truncate text-zinc-200" title={file.filename}>
                                                    {file.filename}
                                                </span>
                                                <span className="text-xs text-zinc-500">
                                                    {(file.size / 1024).toFixed(1)} KB
                                                </span>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => handleDelete(file.filename)}
                                            disabled={deleting === file.filename}
                                            className="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors disabled:opacity-50"
                                            title="Delete File"
                                        >
                                            {deleting === file.filename ? (
                                                <motion.div
                                                    animate={{ rotate: 360 }}
                                                    transition={{ repeat: Infinity, duration: 1 }}
                                                    className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
                                                />
                                            ) : (
                                                <Trash2 className="w-4 h-4" />
                                            )}
                                        </button>
                                    </motion.div>
                                ))
                            )}
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-zinc-800 bg-zinc-900/30 text-xs text-center text-zinc-600">
                            {files.length} document{files.length !== 1 ? 's' : ''} stored locally
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
