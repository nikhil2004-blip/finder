import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadFile } from '../services/api';

interface FileUploadProps {
    onUploadComplete: () => void;
}

export const FileUpload = ({ onUploadComplete }: FileUploadProps) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    };

    const processFile = async (file: File) => {
        setIsUploading(true);
        setUploadStatus('idle');
        try {
            await uploadFile(file);
            setUploadStatus('success');
            setTimeout(onUploadComplete, 1500); // Wait a bit before refreshing list/showing success
        } catch (error) {
            console.error(error);
            setUploadStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await processFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await processFile(e.target.files[0]);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto my-8">
            <motion.div
                layout
                className={`relative border-2 border-dashed rounded-2xl p-8 transition-colors ${isDragging
                        ? 'border-brand-primary bg-brand-primary/10'
                        : 'border-zinc-700 hover:border-zinc-500 bg-zinc-900/50'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.xlsx,.xls"
                    onChange={handleChange}
                />

                <div className="flex flex-col items-center justify-center text-center gap-4">
                    <AnimatePresence mode="wait">
                        {isUploading ? (
                            <motion.div
                                key="uploading"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.8 }}
                                className="flex flex-col items-center"
                            >
                                <Loader2 className="w-12 h-12 text-brand-primary animate-spin mb-2" />
                                <p className="text-zinc-400">Processing document...</p>
                            </motion.div>
                        ) : uploadStatus === 'success' ? (
                            <motion.div
                                key="success"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.8 }}
                                className="flex flex-col items-center"
                            >
                                <CheckCircle className="w-12 h-12 text-green-500 mb-2" />
                                <p className="text-green-400">Upload Complete!</p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="idle"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.8 }}
                                className="flex flex-col items-center"
                            >
                                <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mb-2">
                                    <Upload className="w-8 h-8 text-zinc-400" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-medium text-white">Drag & drop your file</h3>
                                    <p className="text-sm text-zinc-500 mt-1">PDF or Excel up to 10MB</p>
                                </div>
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="mt-4 px-6 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-primary/90 transition-colors"
                                >
                                    Browse Files
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
};
