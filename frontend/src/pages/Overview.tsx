import { Activity, CheckCircle, Calendar, Users } from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../api/client';
import socket from '../api/socket';

interface UserStats {
    level: number;
    xp: number;
    truthfulness: number;
    effort: number;
    reliability: number;
    collaboration: number;
    quality: number;
}

export default function Overview() {
    const [stats, setStats] = useState<UserStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const userJson = localStorage.getItem('user');
                if (!userJson) return;
                const user = JSON.parse(userJson);

                const res = await api.get(`/gamification/me/stats?user_id=${user.id}`);
                setStats(res.data);
            } catch (error) {
                console.error("Failed to fetch stats", error);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();

        const onStatsUpdate = (data: any) => {
            setStats(prev => prev ? { ...prev, ...data } : data);
        };

        const onLevelUp = (data: any) => {
            console.log("Level UP!", data);
        };

        socket.on('stats_update', onStatsUpdate);
        socket.on('level_up', onLevelUp);

        return () => {
            socket.off('stats_update', onStatsUpdate);
            socket.off('level_up', onLevelUp);
        };
    }, []);

    if (loading) return <div className="text-center py-12">Loading...</div>;

    const metrics = [
        { key: 'Truthfulness', value: stats?.truthfulness ?? 0 },
        { key: 'Effort', value: stats?.effort ?? 0 },
        { key: 'Reliability', value: stats?.reliability ?? 0 },
        { key: 'Collaboration', value: stats?.collaboration ?? 0 },
        { key: 'Quality', value: stats?.quality ?? 0 },
    ];

    const recent = [
        { id: 1, title: 'New specific task assigned: Fix Login CSS', time: '2 mins ago' },
        { id: 2, title: 'New specific task assigned: Fix Login CSS', time: '2 mins ago' },
        { id: 3, title: 'New specific task assigned: Fix Login CSS', time: '2 mins ago' },
    ];

    const squad = [
        { id: 'ai', name: 'AI', status: 'online' },
        { id: 'sarah', name: 'Sarah (AI)', status: 'online' },
        { id: 'jd', name: 'John Doe', status: 'offline' },
    ];

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Main Content */}
            <section className="lg:col-span-2 space-y-6">
                {/* Player Card */}
                <div className="bg-white rounded-2xl p-6 shadow">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-indigo-500 to-pink-500 flex items-center justify-center text-white text-xl font-bold">
                                P1
                            </div>
                            <div>
                                <div className="flex items-baseline gap-3">
                                    <h2 className="text-lg font-semibold">Player 1</h2>
                                    <span className="text-sm text-slate-500">Level {stats?.level} • {stats?.xp} XP</span>
                                </div>
                                <p className="text-sm text-slate-500">Welcome Back, Player 1</p>
                            </div>
                        </div>

                        <div className="text-right max-w-md">
                            <p className="text-sm text-slate-500">Your performance metrics are being tracked in real-time.</p>
                            <p className="text-sm text-slate-400">Keep your stats high to survive the probationary period.</p>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
                        {metrics.map((m) => (
                            <div key={m.key} className="p-3 bg-slate-50 rounded-lg text-center">
                                <div className="text-xs text-slate-500">{m.key}</div>
                                <div className="text-2xl font-semibold mt-1">{m.value}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Level Progress Bar */}
                <div className="bg-white rounded-2xl p-6 shadow flex items-center gap-6">
                    <div className="flex-1">
                        <h4 className="font-semibold">Level {stats?.level} / 100 XP</h4>
                        <div className="mt-3 w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                            <div
                                className="h-3 rounded-full bg-indigo-500 transition-all"
                                style={{ width: `${(stats?.xp || 0) % 100}%` }}
                            />
                        </div>
                        <div className="text-xs text-slate-400 mt-2">{stats?.xp} XP</div>
                    </div>

                    <div className="w-48 text-center p-3 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-500">Total XP</div>
                        <div className="text-2xl font-bold">{stats?.xp || 0}</div>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-2xl p-6 shadow">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">Recent Activity</h3>
                        <div className="text-sm text-slate-500">Activity feed</div>
                    </div>

                    <ul className="divide-y">
                        {recent.map((r) => (
                            <li key={r.id} className="py-3 flex items-start gap-3">
                                <div className="flex-none w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                                    <Activity className="w-4 h-4 text-slate-600" />
                                </div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium">{r.title}</div>
                                    <div className="text-xs text-slate-400">{r.time}</div>
                                </div>
                                <div className="flex-none text-xs text-slate-400">#task</div>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Progress Bar */}
                <div className="bg-white rounded-2xl p-6 shadow flex items-center gap-6">
                    <div className="flex-1">
                        <h4 className="font-semibold">Level {stats?.level} / 100 XP</h4>
                        <div className="mt-3 w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                            <div
                                className="h-3 rounded-full bg-indigo-500 transition-all"
                                style={{ width: `${(stats?.xp || 0) % 100}%` }}
                            />
                        </div>
                        <div className="text-xs text-slate-400 mt-2">{stats?.xp} XP</div>
                    </div>

                    <div className="w-48 text-center p-3 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-500">Progress</div>
                        <div className="text-2xl font-bold">{stats?.xp || 0}</div>
                    </div>
                </div>
            </section>

            {/* Right Column - Sidebar */}
            <aside className="space-y-6">
                {/* Squad Status */}
                <div className="bg-white rounded-2xl p-4 shadow">
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold">Squad Status</h4>
                        <div className="text-xs text-slate-400">Realtime</div>
                    </div>

                    <ul className="space-y-3">
                        {squad.map((s) => (
                            <li key={s.id} className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                                    <Users className="w-4 h-4 text-slate-600" />
                                </div>
                                <div className="flex-1">
                                    <div className="text-sm font-medium">{s.name}</div>
                                    <div className="text-xs text-slate-400">{s.status}</div>
                                </div>
                                <div>
                                    {s.status === 'online' ? (
                                        <span className="inline-flex items-center gap-1 text-xs text-green-600">
                                            <CheckCircle className="w-3 h-3" /> Online
                                        </span>
                                    ) : (
                                        <span className="text-xs text-slate-400">Offline</span>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Onboarding Info */}
                <div className="bg-white rounded-2xl p-4 shadow text-sm text-slate-500">
                    <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4" />
                        <div>
                            <div className="font-medium text-slate-900">Onboarding</div>
                            <div className="text-xs">Day 1 — Welcome & orientation</div>
                        </div>
                    </div>
                </div>
            </aside>
        </div>
    );
}
