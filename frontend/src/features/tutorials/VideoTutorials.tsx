import { useState } from 'react';
import { Play, BookOpen, FileText, CheckCircle } from 'lucide-react';

interface Tutorial {
    id: string;
    title: string;
    duration: string;
    category: 'basics' | 'installation' | 'maintenance' | 'advanced';
    thumbnail: string;
    videoUrl: string; // YouTube ID or local path
    description: string;
}

const TUTORIALS: Tutorial[] = [
    {
        id: '1',
        title: 'Introduction to RainForge',
        duration: '2:30',
        category: 'basics',
        thumbnail: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg', // Placeholder
        videoUrl: 'dQw4w9WgXcQ', // Using dummy ID for demo
        description: 'Learn the basics of the RainForge platform and how to navigate.'
    },
    {
        id: '2',
        title: 'How to Assess Your Roof',
        duration: '5:45',
        category: 'basics',
        thumbnail: 'https://img.youtube.com/vi/M7lc1UVf-VE/maxresdefault.jpg',
        videoUrl: 'M7lc1UVf-VE',
        description: 'Step-by-step guide to measuring your roof area and identifying surface types.'
    },
    {
        id: '3',
        title: 'First Flush Diverter Installation',
        duration: '8:15',
        category: 'installation',
        thumbnail: 'https://img.youtube.com/vi/ScMzIvxBSi4/maxresdefault.jpg',
        videoUrl: 'ScMzIvxBSi4',
        description: 'Detailed installation instructions for the first flush diverter system.'
    },
    {
        id: '4',
        title: 'Filter Maintenance Guide',
        duration: '4:20',
        category: 'maintenance',
        thumbnail: 'https://img.youtube.com/vi/MKJk_kR6kR8/maxresdefault.jpg',
        videoUrl: 'MKJk_kR6kR8',
        description: 'How to clean and unclog your rainwater filter for optimal performance.'
    },
    {
        id: '5',
        title: 'Trading Carbon Credits',
        duration: '6:10',
        category: 'advanced',
        thumbnail: 'https://img.youtube.com/vi/F2X3w5G1s1A/maxresdefault.jpg',
        videoUrl: 'F2X3w5G1s1A',
        description: 'Learn how to mint and trade carbon credits on the RainForge marketplace.'
    },
];

export default function VideoTutorials() {
    const [selectedVideo, setSelectedVideo] = useState<Tutorial | null>(null);
    const [filter, setFilter] = useState<string>('all');

    const filteredTutorials = filter === 'all'
        ? TUTORIALS
        : TUTORIALS.filter(t => t.category === filter);

    const categories = [
        { id: 'all', label: 'All Videos' },
        { id: 'basics', label: 'Basics' },
        { id: 'installation', label: 'Installation' },
        { id: 'maintenance', label: 'Maintenance' },
        { id: 'advanced', label: 'Advanced' },
    ];

    return (
        <div className="min-h-screen bg-slate-900 text-white p-6">
            <header className="mb-8 text-center max-w-3xl mx-auto">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500 mb-2">
                    📺 Video Knowledge Base
                </h1>
                <p className="text-gray-400">
                    Master rainwater harvesting with our expert-led video tutorials.
                </p>
            </header>

            {/* Category Filter */}
            <div className="flex flex-wrap justify-center gap-3 mb-8">
                {categories.map(cat => (
                    <button
                        key={cat.id}
                        onClick={() => setFilter(cat.id)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${filter === cat.id
                                ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/25'
                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
                {filteredTutorials.map(tutorial => (
                    <div
                        key={tutorial.id}
                        className="group bg-slate-800/50 border border-white/5 rounded-2xl overflow-hidden hover:border-cyan-500/30 transition-all hover:shadow-2xl hover:shadow-cyan-900/20 cursor-pointer"
                        onClick={() => setSelectedVideo(tutorial)}
                    >
                        <div className="relative aspect-video">
                            <img
                                src={tutorial.thumbnail}
                                alt={tutorial.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            />
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                                <div className="w-12 h-12 rounded-full bg-cyan-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                                    <Play className="w-5 h-5 text-white ml-1" fill="currentColor" />
                                </div>
                            </div>
                            <div className="absolute bottom-3 right-3 bg-black/80 px-2 py-1 rounded text-xs font-mono">
                                {tutorial.duration}
                            </div>
                        </div>

                        <div className="p-5">
                            <div className="flex items-center gap-2 mb-2">
                                <span className={`text-xs px-2 py-1 rounded-md bg-white/5 uppercase tracking-wider font-semibold 
                  ${tutorial.category === 'basics' ? 'text-blue-400' : ''}
                  ${tutorial.category === 'installation' ? 'text-green-400' : ''}
                  ${tutorial.category === 'maintenance' ? 'text-orange-400' : ''}
                  ${tutorial.category === 'advanced' ? 'text-purple-400' : ''}
                `}>
                                    {tutorial.category}
                                </span>
                            </div>

                            <h3 className="text-lg font-bold mb-2 group-hover:text-cyan-400 transition-colors line-clamp-1">
                                {tutorial.title}
                            </h3>
                            <p className="text-sm text-gray-400 line-clamp-2">
                                {tutorial.description}
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Video Modal */}
            {selectedVideo && (
                <div
                    className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
                    onClick={() => setSelectedVideo(null)}
                >
                    <div
                        className="bg-slate-900 rounded-2xl w-full max-w-4xl overflow-hidden border border-white/10 shadow-2xl animate-in zoom-in-95 duration-200"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="relative aspect-video bg-black">
                            <iframe
                                width="100%"
                                height="100%"
                                src={`https://www.youtube.com/embed/${selectedVideo.videoUrl}?autoplay=1`}
                                title={selectedVideo.title}
                                frameBorder="0"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                            ></iframe>
                        </div>

                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2">{selectedVideo.title}</h2>
                                    <p className="text-gray-400">{selectedVideo.description}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="p-2 hover:bg-white/10 rounded-full transition-colors"
                                >
                                    ✕
                                </button>
                            </div>

                            <div className="flex gap-4 pt-4 border-t border-white/10">
                                <button className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300">
                                    <BookOpen className="w-4 h-4" />
                                    View Transcript
                                </button>
                                <button className="flex items-center gap-2 text-sm text-gray-400 hover:text-white">
                                    <FileText className="w-4 h-4" />
                                    Related Docs
                                </button>
                                <button className="flex items-center gap-2 text-sm text-gray-400 hover:text-white ml-auto">
                                    <CheckCircle className="w-4 h-4" />
                                    Mark as Watched
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
