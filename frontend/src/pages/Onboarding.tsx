import { useEffect, useState } from 'react';
import api from '../api/client';
import { CheckCircle, Circle } from 'lucide-react';

interface Task {
    id: number;
    task: string;
    completed: boolean;
    xp: number;
}

export default function Onboarding() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Fetch tasks
        const fetchTasks = async () => {
            // Mocking fetch as endpoint might throw 401 if not logged in
            // In real app, call api.get('/onboarding/checklist')
            const mockTasks = [
                { id: 1, task: "Clone the repository", completed: false, xp: 50 },
                { id: 2, task: "Install dependencies", completed: false, xp: 50 },
                { id: 3, task: "Run the application", completed: false, xp: 50 },
            ];
            setTasks(mockTasks);
        };
        fetchTasks();
    }, []);

    const generateRepo = async () => {
        setLoading(true);
        try {
            await api.post('/onboarding/generate-repo', { github_token: 'dummy' });
            alert("Repository generated! Check your GitHub.");
        } catch (e) {
            console.error(e);
            alert("Failed to generate repo (Are you using a valid token in backend?)");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Onboarding Checklist</h1>
                    <p className="text-gray-400">Complete these tasks to verify your environment.</p>
                </div>
                <button
                    onClick={generateRepo}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50"
                >
                    {loading ? 'Generating...' : 'Start Simulation (Generate Repo)'}
                </button>
            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                {tasks.map((task) => (
                    <div key={task.id} className="p-4 border-b border-gray-800 flex items-center justify-between hover:bg-gray-800/50 transition-colors">
                        <div className="flex items-center">
                            {task.completed ?
                                <CheckCircle className="w-6 h-6 text-green-500 mr-4" /> :
                                <Circle className="w-6 h-6 text-gray-500 mr-4" />
                            }
                            <span className={task.completed ? "text-gray-500 line-through" : "text-gray-200"}>
                                {task.task}
                            </span>
                        </div>
                        <span className="text-xs bg-gray-800 text-blue-400 px-2 py-1 rounded">
                            {task.xp} XP
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
