import { useState } from 'react';
import { MessageSquare, X, Send } from 'lucide-react';

export default function FloatingChat() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<any[]>([]);
    const [input, setInput] = useState('');

    const toggleChat = () => setIsOpen(!isOpen);

    const sendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        // For now, just add to local state
        // In production, this would call the API
        setMessages(prev => [...prev, {
            id: Date.now(),
            content: input,
            sender_name: 'You',
            timestamp: new Date().toISOString()
        }]);
        setInput('');
    };

    return (
        <>
            {/* Floating Button */}
            <button
                onClick={toggleChat}
                className="fixed bottom-6 right-6 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg flex items-center justify-center transition-colors z-50"
            >
                {isOpen ? (
                    <X className="w-6 h-6" />
                ) : (
                    <>
                        <MessageSquare className="w-6 h-6" />
                        {messages.length > 0 && (
                            <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                {messages.length}
                            </span>
                        )}
                    </>
                )}
            </button>

            {/* Chat Panel */}
            {isOpen && (
                <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-xl shadow-2xl border border-slate-200 flex flex-col z-50">
                    {/* Header */}
                    <div className="p-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
                        <h3 className="font-semibold text-slate-900 flex items-center">
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Team Chat
                        </h3>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.length === 0 ? (
                            <div className="text-center text-slate-500 text-sm mt-8">
                                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-30" />
                                <p>No messages yet</p>
                                <p className="text-xs mt-1">Start a conversation!</p>
                            </div>
                        ) : (
                            messages.map((msg) => (
                                <div key={msg.id} className="flex items-start">
                                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex-shrink-0 mr-2 flex items-center justify-center text-xs font-bold text-indigo-600">
                                        {msg.sender_name[0]}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-baseline">
                                            <span className="font-medium text-slate-900 text-sm mr-2">{msg.sender_name}</span>
                                            <span className="text-xs text-slate-400">
                                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                        <p className="text-slate-700 text-sm mt-0.5">{msg.content}</p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-slate-200 bg-slate-50 rounded-b-xl">
                        <form onSubmit={sendMessage} className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Type a message..."
                                className="w-full bg-white border border-slate-300 rounded-lg py-2 pl-3 pr-10 text-slate-900 text-sm placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim()}
                                className="absolute right-2 top-2 p-1 text-indigo-600 hover:bg-indigo-50 rounded transition-colors disabled:opacity-30"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
