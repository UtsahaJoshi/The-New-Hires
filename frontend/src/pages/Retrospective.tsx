import { useState, useRef } from 'react';
import { Video, StopCircle, Upload, Play } from 'lucide-react';
import api from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function Retrospective() {
    const [step, setStep] = useState<'intro' | 'recording' | 'review' | 'done'>('intro');
    const [isRecording, setIsRecording] = useState(false);
    const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const navigate = useNavigate();

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }

            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;

            const chunks: BlobPart[] = [];
            mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
            mediaRecorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'video/webm' });
                setVideoBlob(blob);
                if (videoRef.current) {
                    videoRef.current.srcObject = null;
                    videoRef.current.src = URL.createObjectURL(blob);
                    videoRef.current.controls = true;
                    videoRef.current.play();
                }
                setStep('review');
            };

            mediaRecorder.start();
            setIsRecording(true);
            setStep('recording');
        } catch (err) {
            console.error("Error accessing camera", err);
            alert("Camera permission required!");
        }
    };

    const stopRecording = () => {
        mediaRecorderRef.current?.stop();
        mediaRecorderRef.current?.stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
    };

    const uploadVideo = async () => {
        if (!videoBlob) return;
        const formData = new FormData();
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        formData.append('file', videoBlob, `retro_${user.id}.webm`);

        try {
            await api.post(`/features/retrospectives/upload?user_id=${user.id}`, formData);
            setStep('done');
        } catch (error) {
            console.error("Upload failed", error);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center p-8 max-w-4xl mx-auto text-center h-full">
            {step === 'intro' && (
                <div className="space-y-6 animate-fade-in">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
                        Sprint Retrospective
                    </h1>
                    <p className="text-xl text-slate-600 max-w-lg mx-auto">
                        Congratulations on surviving your first sprint!
                        It's time for the "Testimonial" - a video record of your experience for the company archives.
                    </p>
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 max-w-md mx-auto">
                        <h3 className="text-white font-semibold mb-2">Prompt:</h3>
                        <p className="text-gray-400 italic">"What was your biggest challenge, and what did you learn about The New Hire culture?"</p>
                    </div>
                    <button
                        onClick={startRecording}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full text-lg flex items-center mx-auto space-x-2 transition-transform hover:scale-105"
                    >
                        <Video className="w-6 h-6" />
                        <span>Start Recording</span>
                    </button>
                </div>
            )}

            {step === 'recording' && (
                <div className="space-y-6 w-full max-w-2xl">
                    <div className="relative aspect-video bg-black rounded-2xl overflow-hidden border-4 border-red-500/50 shadow-2xl">
                        <video ref={videoRef} autoPlay muted className="w-full h-full object-cover transform scale-x-[-1]" />
                        <div className="absolute top-4 right-4 animate-pulse flex items-center space-x-2 bg-red-600 px-3 py-1 rounded-full">
                            <div className="w-3 h-3 bg-white rounded-full"></div>
                            <span className="text-white text-xs font-bold">REC</span>
                        </div>
                    </div>
                    <button
                        onClick={stopRecording}
                        className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-12 rounded-full text-lg flex items-center mx-auto space-x-2"
                    >
                        <StopCircle className="w-8 h-8" />
                        <span>Stop Recording</span>
                    </button>
                </div>
            )}

            {step === 'review' && (
                <div className="space-y-6 w-full max-w-2xl">
                    <h2 className="text-3xl font-bold text-slate-900">Review Your Testimonial</h2>
                    <div className="aspect-video bg-black rounded-2xl overflow-hidden border border-gray-700">
                        <video ref={videoRef} className="w-full h-full" />
                    </div>
                    <div className="flex justify-center space-x-4">
                        <button
                            onClick={startRecording}
                            className="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-3 px-6 rounded-lg transition-colors"
                        >
                            Retake
                        </button>
                        <button
                            onClick={uploadVideo}
                            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg flex items-center space-x-2 transition-transform hover:scale-105"
                        >
                            <Upload className="w-5 h-5" />
                            <span>Submit & Complete Onboarding</span>
                        </button>
                    </div>
                </div>
            )}

            {step === 'done' && (
                <div className="space-y-8 animate-fade-in">
                    <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-2xl animate-bounce">
                        <Play className="w-12 h-12 text-white fill-current" />
                    </div>
                    <div>
                        <h1 className="text-5xl font-extrabold text-slate-900 mb-4">You're Hired!</h1>
                        <p className="text-2xl text-slate-600">Welcome to the team, officially.</p>
                    </div>
                    <div className="bg-gray-800/50 p-8 rounded-2xl max-w-2xl mx-auto border border-gray-700">
                        <p className="text-gray-400 leading-relaxed">
                            You've completed the onboarding simulation. Your stats have been recorded.
                            Keep pushing code, stay reliable, and maybe one day you'll make it to Level 99.
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/')}
                        className="text-blue-600 hover:text-blue-800 underline text-lg"
                    >
                        Return to Dashboard
                    </button>
                </div>
            )}
        </div>
    );
}
