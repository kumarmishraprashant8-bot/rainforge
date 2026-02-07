/**
 * Keyboard Shortcuts / Command Palette
 * Power-user feature with Ctrl+K activation
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search, Command, Home, Upload, Activity, Camera,
  LayoutDashboard, ShoppingBag, Globe, Settings, X,
  Zap, FileText, Map, ArrowRight
} from 'lucide-react';

interface CommandItem {
  id: string;
  title: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void;
  keywords?: string[];
  category: 'navigation' | 'action' | 'settings';
}

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const commands: CommandItem[] = [
    // Navigation
    { id: 'home', title: 'Go to Home', icon: <Home size={18} />, action: () => navigate('/'), category: 'navigation', keywords: ['landing', 'main'] },
    { id: 'intake', title: 'New Assessment', icon: <Zap size={18} />, action: () => navigate('/intake'), category: 'navigation', keywords: ['assess', 'start', 'new'] },
    { id: 'bulk', title: 'Bulk Upload', icon: <Upload size={18} />, action: () => navigate('/bulk'), category: 'navigation', keywords: ['csv', 'batch', 'import'] },
    { id: 'portfolio', title: 'Portfolio Dashboard', icon: <LayoutDashboard size={18} />, action: () => navigate('/portfolio'), category: 'navigation', keywords: ['dashboard', 'projects'] },
    { id: 'marketplace', title: 'Marketplace', icon: <ShoppingBag size={18} />, action: () => navigate('/marketplace'), category: 'navigation', keywords: ['installers', 'quotes', 'bidding'] },
    { id: 'monitoring', title: 'IoT Monitoring', icon: <Activity size={18} />, action: () => navigate('/monitoring'), category: 'navigation', keywords: ['iot', 'sensors', 'live'] },
    { id: 'verification', title: 'Verification', icon: <Camera size={18} />, action: () => navigate('/verification'), category: 'navigation', keywords: ['photo', 'verify', 'proof'] },
    { id: 'public', title: 'Public Dashboard', icon: <Globe size={18} />, action: () => navigate('/public'), category: 'navigation', keywords: ['transparency', 'stats', 'public'] },

    // Actions
    { id: 'report', title: 'Generate Report', description: 'Create PDF report', icon: <FileText size={18} />, action: () => console.log('Generate report'), category: 'action', keywords: ['pdf', 'export', 'download'] },
    { id: 'map', title: 'View Map', description: 'Open map view', icon: <Map size={18} />, action: () => console.log('Open map'), category: 'action', keywords: ['location', 'geo'] },
  ];

  const filteredCommands = query
    ? commands.filter(cmd => {
      const searchStr = `${cmd.title} ${cmd.description || ''} ${cmd.keywords?.join(' ') || ''}`.toLowerCase();
      return searchStr.includes(query.toLowerCase());
    })
    : commands;

  // Keyboard shortcut to open
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && filteredCommands[selectedIndex]) {
      filteredCommands[selectedIndex].action();
      setIsOpen(false);
    }
  }, [filteredCommands, selectedIndex]);

  if (!isOpen) return null;

  const groupedCommands = {
    navigation: filteredCommands.filter(c => c.category === 'navigation'),
    action: filteredCommands.filter(c => c.category === 'action'),
    settings: filteredCommands.filter(c => c.category === 'settings'),
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[200] animate-fade-in"
        onClick={() => setIsOpen(false)}
      />

      {/* Palette */}
      <div className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-lg z-[201] animate-scale-in">
        <div className="glass rounded-2xl overflow-hidden border border-white/20 shadow-2xl">
          {/* Search Input */}
          <div className="flex items-center gap-3 p-4 border-b border-white/10">
            <Search className="text-gray-400" size={20} />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(0);
              }}
              onKeyDown={handleKeyDown}
              placeholder="Search commands..."
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none text-lg"
            />
            <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-400 bg-white/5 rounded border border-white/10">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div className="max-h-80 overflow-y-auto p-2">
            {filteredCommands.length === 0 ? (
              <div className="p-8 text-center text-gray-400">
                No commands found
              </div>
            ) : (
              <>
                {groupedCommands.navigation.length > 0 && (
                  <>
                    <div className="px-3 py-2 text-xs font-medium text-gray-500 uppercase">Navigation</div>
                    {groupedCommands.navigation.map((cmd, idx) => (
                      <CommandItemComponent
                        key={cmd.id}
                        command={cmd}
                        isSelected={filteredCommands.indexOf(cmd) === selectedIndex}
                        onSelect={() => {
                          cmd.action();
                          setIsOpen(false);
                        }}
                      />
                    ))}
                  </>
                )}
                {groupedCommands.action.length > 0 && (
                  <>
                    <div className="px-3 py-2 text-xs font-medium text-gray-500 uppercase mt-2">Actions</div>
                    {groupedCommands.action.map((cmd) => (
                      <CommandItemComponent
                        key={cmd.id}
                        command={cmd}
                        isSelected={filteredCommands.indexOf(cmd) === selectedIndex}
                        onSelect={() => {
                          cmd.action();
                          setIsOpen(false);
                        }}
                      />
                    ))}
                  </>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10 text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white/5 rounded">↑</kbd>
                <kbd className="px-1.5 py-0.5 bg-white/5 rounded">↓</kbd>
                to navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white/5 rounded">↵</kbd>
                to select
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Command size={12} />
              <span>K to toggle</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const CommandItemComponent: React.FC<{
  command: CommandItem;
  isSelected: boolean;
  onSelect: () => void;
}> = ({ command, isSelected, onSelect }) => {
  return (
    <button
      onClick={onSelect}
      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${isSelected ? 'bg-cyan-500/20 text-white' : 'text-gray-300 hover:bg-white/5'
        }`}
    >
      <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-cyan-500/30' : 'bg-white/5'}`}>
        {command.icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{command.title}</div>
        {command.description && (
          <div className="text-xs text-gray-500 truncate">{command.description}</div>
        )}
      </div>
      {isSelected && <ArrowRight size={16} className="text-cyan-400" />}
    </button>
  );
};

// Keyboard shortcut hint component
export const KeyboardHint: React.FC = () => {
  return (
    <button
      onClick={() => {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }));
      }}
      className="hidden md:flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-colors"
    >
      <Search size={14} />
      <span>Search</span>
      <kbd className="px-1.5 py-0.5 text-xs bg-white/5 rounded">⌘K</kbd>
    </button>
  );
};

export default CommandPalette;
