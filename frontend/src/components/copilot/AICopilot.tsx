/**
 * AI Copilot Chat Component
 * Floating chat widget with GPT-4 powered assistant
 */

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Sparkles, Loader2, Mic, Paperclip } from 'lucide-react';
import { copilotAPI } from '../../services/unbeatableAPI';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    suggestions?: string[];
    actions?: { type: string; label: string; path?: string }[];
}

interface AICopilotProps {
    userId: string;
    currentPage?: string;
    projectId?: number;
}

const AICopilot: React.FC<AICopilotProps> = ({ userId, currentPage, projectId }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (isOpen && messages.length === 0) {
            // Add welcome message
            setMessages([{
                id: 'welcome',
                role: 'assistant',
                content: '👋 Hi! I\'m your RainForge AI assistant. I can help you with:\n\n• 🌧️ Rainwater harvesting assessments\n• 💰 Subsidy eligibility\n• 🔧 Finding installers\n• 📊 Project status\n\nHow can I help you today?',
                timestamp: new Date(),
                suggestions: ['Calculate my water potential', 'Check subsidies', 'Find installers']
            }]);
        }
    }, [isOpen]);

    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await copilotAPI.chat(userId, text, sessionId || undefined, {
                page: currentPage,
                project_id: projectId
            });

            const data = response.data;
            setSessionId(data.session_id);

            const assistantMessage: Message = {
                id: Date.now().toString() + '-assistant',
                role: 'assistant',
                content: data.response.message,
                timestamp: new Date(),
                suggestions: data.response.suggestions,
                actions: data.response.actions
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Copilot error:', error);
            setMessages(prev => [...prev, {
                id: Date.now().toString() + '-error',
                role: 'assistant',
                content: '😔 Sorry, I encountered an error. Please try again.',
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        sendMessage(suggestion);
    };

    const handleActionClick = (action: { type: string; path?: string }) => {
        if (action.type === 'navigate' && action.path) {
            window.location.href = action.path;
        }
    };

    const formatMessage = (content: string) => {
        // Convert markdown-like formatting
        return content.split('\n').map((line, i) => (
            <React.Fragment key={i}>
                {line.startsWith('**') && line.endsWith('**')
                    ? <strong>{line.slice(2, -2)}</strong>
                    : line.startsWith('• ')
                        ? <span className="block ml-2">{line}</span>
                        : line
                }
                {i < content.split('\n').length - 1 && <br />}
            </React.Fragment>
        ));
    };

    return (
        <>
            {/* Floating Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group z-50"
                >
                    <MessageCircle className="w-6 h-6 text-white" />
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />
                    <Sparkles className="w-4 h-4 text-yellow-300 absolute -top-2 -left-2 animate-bounce" />
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50 border border-gray-200">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h3 className="text-white font-semibold">RainForge AI</h3>
                                <p className="text-white/70 text-xs">Powered by GPT-4</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors"
                        >
                            <X className="w-4 h-4 text-white" />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[85%] ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white rounded-2xl rounded-br-md'
                                    : 'bg-white text-gray-800 rounded-2xl rounded-bl-md shadow-sm'
                                    } p-3`}>
                                    <div className="text-sm whitespace-pre-wrap">
                                        {formatMessage(msg.content)}
                                    </div>

                                    {/* Suggestions */}
                                    {msg.suggestions && msg.suggestions.length > 0 && (
                                        <div className="mt-3 flex flex-wrap gap-2">
                                            {msg.suggestions.map((s, i) => (
                                                <button
                                                    key={i}
                                                    onClick={() => handleSuggestionClick(s)}
                                                    className="text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors"
                                                >
                                                    {s}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    {/* Actions */}
                                    {msg.actions && msg.actions.length > 0 && (
                                        <div className="mt-3 flex flex-wrap gap-2">
                                            {msg.actions.map((action, i) => (
                                                <button
                                                    key={i}
                                                    onClick={() => handleActionClick(action)}
                                                    className="text-xs bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-full hover:opacity-90 transition-opacity"
                                                >
                                                    {action.label}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white rounded-2xl rounded-bl-md shadow-sm p-4">
                                    <div className="flex items-center gap-2 text-gray-500">
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        <span className="text-sm">Thinking...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 bg-white border-t border-gray-100">
                        <div className="flex items-center gap-2 bg-gray-100 rounded-full px-4 py-2">
                            <button className="text-gray-400 hover:text-gray-600 transition-colors">
                                <Paperclip className="w-5 h-5" />
                            </button>
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
                                placeholder="Ask me anything..."
                                className="flex-1 bg-transparent outline-none text-sm"
                            />
                            <button className="text-gray-400 hover:text-gray-600 transition-colors">
                                <Mic className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => sendMessage(input)}
                                disabled={!input.trim() || isLoading}
                                className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center disabled:opacity-50"
                            >
                                <Send className="w-4 h-4 text-white" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default AICopilot;
