import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader, FileText as FileIcon } from 'lucide-react';
import { searchFiles, listFiles, deleteFile, type SearchResult } from '../services/api';
import { ResultsGrid } from './ResultsGrid';
import { FileUpload } from './FileUpload';
import { FileListModal } from './FileListModal';

import { ArrowLeft } from 'lucide-react';
import Hyperspeed, { hyperspeedPresets } from './react-bits/Hyperspeed';
import { Squares } from './react-bits/Squares';

interface SearchInterfaceProps {
    onBack: () => void;
}

export const SearchInterface = ({ onBack }: SearchInterfaceProps) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [debouncedQuery, setDebouncedQuery] = useState('');

    // File Management State
    const [totalDocs, setTotalDocs] = useState(0);
    const [isManagerOpen, setIsManagerOpen] = useState(false);
    const [fileList, setFileList] = useState<any[]>([]);

    const refreshFiles = () => {
        listFiles().then(files => {
            setFileList(files);
            setTotalDocs(files.length);
        }).catch(console.error);
    };

    const handleDeleteFile = async (filename: string) => {
        try {
            await deleteFile(filename);
            refreshFiles();
            // Optional: clear results if they belonged to deleted file
            if (results.some(r => r.file_name === filename)) {
                // simple approach: just clear all results or re-search
                setResults(prev => prev.filter(r => r.file_name !== filename));
            }
        } catch (error) {
            console.error("Failed to delete file", error);
        }
    };

    // Fetch total docs on mount
    useEffect(() => {
        refreshFiles();
    }, []);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(query);
        }, 300);
        return () => clearTimeout(timer);
    }, [query]);

    // Perform search
    useEffect(() => {
        const doSearch = async () => {
            if (!debouncedQuery.trim()) {
                setResults([]);
                return;
            }
            setLoading(true);
            try {
                const res = await searchFiles(debouncedQuery);
                setResults(res);
            } catch (error) {
                console.error("Search failed", error);
            } finally {
                setLoading(false);
            }
        };
        doSearch();
    }, [debouncedQuery]);

    return (
        <div className="relative min-h-screen bg-dark-bg text-white overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 z-0">
                <Hyperspeed effectOptions={hyperspeedPresets.one} />
            </div>
            <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
                <Squares
                    direction="diagonal"
                    speed={0.1}
                    squareSize={50}
                    borderColor="#8B5CF6"
                    hoverFillColor="#222"
                />
            </div>

            {/* Content Container */}
            <div className="relative z-10 container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-6">
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        <span>Back to Home</span>
                    </button>

                    <button
                        onClick={() => setIsManagerOpen(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-colors backdrop-blur-sm cursor-pointer group"
                    >
                        <FileIcon className="w-4 h-4 text-brand-primary group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium text-zinc-300">
                            Total Processed Docs: <span className="text-white font-bold">{totalDocs}</span>
                        </span>
                    </button>
                </div>

                {/* Upload Section */}
                <div className="mb-12">
                    <FileUpload onUploadComplete={() => {
                        if (query) setDebouncedQuery(query + " ");
                        refreshFiles();
                    }} />
                </div>

                {/* Search Input */}
                <div className="max-w-3xl mx-auto mb-12 sticky top-4 z-20">
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-brand-primary to-brand-secondary rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                        <div className="relative bg-dark-card border border-zinc-800 rounded-xl flex items-center p-2 shadow-2xl backdrop-blur-md bg-opacity-90">
                            <Search className="w-6 h-6 text-zinc-400 ml-3" />
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Search globally across all documents..."
                                className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-zinc-500 text-lg sm:text-lg px-4 py-3"
                            />
                            {loading && <Loader className="w-5 h-5 text-brand-primary animate-spin mr-3" />}
                        </div>
                    </div>
                </div>

                {/* Results */}
                <ResultsGrid results={results} />

                {!loading && query && results.length === 0 && (
                    <div className="text-center text-zinc-500 mt-12 bg-black/40 backdrop-blur-sm p-4 rounded-xl inline-block mx-auto">
                        <p>No results found for "{query}"</p>
                    </div>
                )}
            </div>

            {/* File Manager Modal */}
            <FileListModal
                isOpen={isManagerOpen}
                onClose={() => setIsManagerOpen(false)}
                files={fileList}
                onDelete={handleDeleteFile}
            />
        </div>
    );
};
