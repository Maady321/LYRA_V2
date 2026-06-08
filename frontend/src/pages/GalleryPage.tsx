import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  RefreshCw,
  ExternalLink,
  Trash2,
  Maximize2,
  Calendar,
  Folder,
  Copy,
  Check,
  Sparkles,
  X
} from 'lucide-react';
import type { GalleryImage } from '../services/api';

export default function GalleryPage() {
  const {
    galleryImages,
    galleryLoading,
    fetchGalleryImages,
    openImageNatively,
    deleteGalleryImage
  } = useAppStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null);
  const [copiedText, setCopiedText] = useState(false);

  const filteredImages = galleryImages.filter((img) =>
    img.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
    img.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCopyPrompt = (prompt: string) => {
    navigator.clipboard.writeText(prompt);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleDelete = (filename: string, prompt: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to permanently delete the image for "${prompt}"?`)) {
      deleteGalleryImage(filename);
      if (selectedImage?.filename === filename) {
        setSelectedImage(null);
      }
    }
  };

  const formatDate = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Unknown date';
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#050811] overflow-y-auto px-8 py-6 select-none font-sans">
      
      {/* Gallery Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/40 pb-6 mb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2.5">
            <Sparkles className="w-6 h-6 text-brandPurple animate-pulse" />
            <span>CREATION ARCHIVE</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1.5">
            Your local, sandboxed repository of AI-generated visual assets.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search by prompt..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-64 bg-darkSurface/50 border border-slate-800/70 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brandPurple/50 focus:shadow-[0_0_15px_rgba(168,85,247,0.1)] transition-all"
            />
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          </div>

          {/* Sync Refresh Button */}
          <button
            onClick={fetchGalleryImages}
            disabled={galleryLoading}
            className="p-2 bg-darkSurface/40 border border-slate-800/60 hover:border-brandPurple/30 text-slate-400 hover:text-slate-200 rounded-xl transition-all flex items-center justify-center hover:scale-[1.03]"
            title="Scan workspace directory"
          >
            <RefreshCw className={`w-4.5 h-4.5 ${galleryLoading ? 'animate-spin text-brandPurple' : ''}`} />
          </button>
        </div>
      </div>

      {/* Grid Content */}
      {galleryLoading && galleryImages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center py-20">
          <RefreshCw className="w-8 h-8 text-brandPurple animate-spin mb-3" />
          <span className="text-xs text-slate-400">Scanning local directory...</span>
        </div>
      ) : filteredImages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center py-20 px-4 text-center">
          <div className="w-16 h-16 rounded-full bg-slate-900/40 border border-slate-800/60 flex items-center justify-center mb-4 text-slate-500">
            <Folder className="w-7 h-7" />
          </div>
          <h3 className="text-sm font-bold text-slate-300">No creations found</h3>
          <p className="text-xs text-slate-500 max-w-sm mt-2 leading-relaxed">
            {searchQuery
              ? `No results matched your search parameter "${searchQuery}".`
              : "You haven't generated any pictures yet. Try asking Lyra: 'create an image of a futuristic floating island' in the chat!"}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-1">
          {filteredImages.map((img) => (
            <motion.div
              key={img.filename}
              layoutId={`card-${img.filename}`}
              onClick={() => setSelectedImage(img)}
              className="group relative bg-[#0b0f19]/40 backdrop-blur-md border border-slate-800/50 hover:border-brandPurple/30 rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-[0_0_25px_rgba(168,85,247,0.1)] flex flex-col"
            >
              {/* Image Thumbnail Container */}
              <div className="aspect-square w-full bg-slate-950 overflow-hidden relative">
                <img
                  src={img.url}
                  alt={img.prompt}
                  className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                
                {/* Floating Micro Hover controls */}
                <div className="absolute inset-0 bg-[#05070d]/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      openImageNatively(img.filename);
                    }}
                    className="p-2.5 bg-slate-900/90 border border-slate-800 hover:border-brandBlue/35 text-slate-300 hover:text-brandBlue rounded-xl transition-all transform scale-90 group-hover:scale-100 duration-300"
                    title="Open natively in Windows"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setSelectedImage(img)}
                    className="p-2.5 bg-slate-900/90 border border-slate-800 hover:border-brandPurple/35 text-slate-300 hover:text-brandPurple rounded-xl transition-all transform scale-90 group-hover:scale-100 duration-300"
                    title="View details"
                  >
                    <Maximize2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => handleDelete(img.filename, img.prompt, e)}
                    className="p-2.5 bg-slate-900/90 border border-slate-800 hover:border-red-500/35 text-slate-300 hover:text-red-400 rounded-xl transition-all transform scale-90 group-hover:scale-100 duration-300"
                    title="Delete permanently"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Title / Description area */}
              <div className="p-4 flex-1 flex flex-col justify-between gap-2 border-t border-slate-900 bg-slate-950/20">
                <h4 className="text-xs font-bold text-slate-200 line-clamp-2 leading-snug">
                  {img.prompt}
                </h4>
                <div className="flex items-center justify-between mt-1 text-[9px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {img.filename.split('_').pop()?.split('.')[0]?.length === 10
                      ? formatDate(img.timestamp)
                      : 'Saved Locally'}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Glassmorphic Lightbox Modal Detail Overlay */}
      <AnimatePresence>
        {selectedImage && (
          <div className="fixed inset-0 z-50 bg-[#04060b]/90 backdrop-blur-xl flex items-center justify-center p-6 md:p-10">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0b0f19]/80 border border-slate-800/80 rounded-3xl overflow-hidden max-w-4xl w-full flex flex-col md:flex-row shadow-[0_0_50px_rgba(0,0,0,0.5)] z-50 h-[80vh] md:h-auto max-h-[85vh]"
            >
              {/* Left Column: Big Image Display */}
              <div className="flex-1 bg-slate-950 flex items-center justify-center relative min-h-[300px] md:min-h-0 md:aspect-square overflow-hidden max-h-[45vh] md:max-h-[85vh]">
                <img
                  src={selectedImage.url}
                  alt={selectedImage.prompt}
                  className="w-full h-full object-contain max-h-[45vh] md:max-h-[85vh]"
                />
                
                {/* Dismiss X button */}
                <button
                  onClick={() => setSelectedImage(null)}
                  className="absolute top-4 right-4 p-2 bg-slate-950/70 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 rounded-full backdrop-blur-sm transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Right Column: Metadata Panel details */}
              <div className="w-full md:w-80 p-6 flex flex-col justify-between border-t md:border-t-0 md:border-l border-slate-800/70 overflow-y-auto max-h-[35vh] md:max-h-none">
                <div className="space-y-4">
                  <div>
                    <span className="text-[9px] font-bold text-brandPurple uppercase tracking-widest leading-none">Generative Prompt</span>
                    <h3 className="text-sm font-bold text-slate-100 mt-1 leading-snug break-words">
                      {selectedImage.prompt}
                    </h3>
                  </div>

                  <hr className="border-slate-800/50" />

                  {/* Creation metrics */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-medium">Filename:</span>
                      <span className="text-slate-300 font-mono text-[10px] truncate max-w-[160px]" title={selectedImage.filename}>
                        {selectedImage.filename}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-medium">Created:</span>
                      <span className="text-slate-300 font-semibold">{formatDate(selectedImage.timestamp)}</span>
                    </div>

                    <div className="flex flex-col gap-1.5 text-xs">
                      <span className="text-slate-500 font-medium">Workspace Path:</span>
                      <span className="bg-[#05070d] border border-slate-900 rounded-lg p-2 font-mono text-[9px] text-slate-400 break-all select-all select-text">
                        {selectedImage.filepath}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Operations Buttons */}
                <div className="space-y-2 mt-6">
                  {/* Native Open */}
                  <button
                    onClick={() => openImageNatively(selectedImage.filename)}
                    className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-brandBlue/10 hover:bg-brandBlue/15 border border-brandBlue/20 hover:border-brandBlue/45 text-brandBlue hover:text-cyan-300 rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(6,182,212,0.02)]"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Launch Natively</span>
                  </button>

                  <div className="flex gap-2">
                    {/* Copy prompt */}
                    <button
                      onClick={() => handleCopyPrompt(selectedImage.prompt)}
                      className="flex-1 flex items-center justify-center gap-2 py-2 px-3 bg-slate-900 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-all"
                    >
                      {copiedText ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy Prompt</span>
                        </>
                      )}
                    </button>

                    {/* Delete permanently */}
                    <button
                      onClick={(e) => handleDelete(selectedImage.filename, selectedImage.prompt, e)}
                      className="p-2 bg-red-950/20 hover:bg-red-950/30 border border-red-900/30 hover:border-red-500/40 text-red-400 rounded-xl transition-all"
                      title="Delete permanently"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
