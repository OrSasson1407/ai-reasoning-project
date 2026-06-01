import React, { useEffect, useState } from 'react';
import { ApiClient } from '../api/client';
import { InferencePanel } from './InferencePanel';
import { GraphVisualizer } from './GraphVisualizer';

export const Dashboard: React.FC = () => {
    const [status, setStatus] = useState<string>('Connecting...');

    useEffect(() => {
        ApiClient.getHealth()
            .then(res => setStatus(`Gateway: ${res.status.toUpperCase()}`))
            .catch(() => setStatus('Gateway: OFFLINE'));
    }, []);

    return (
        <div className="flex h-screen bg-gray-900 text-white font-sans">
            {/* Sidebar / Tools */}
            <div className="w-1/3 border-r border-gray-700 p-6 flex flex-col gap-6 overflow-y-auto">
                <div>
                    <h1 className="text-2xl font-bold tracking-wider text-blue-400">AI REASONING</h1>
                    <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest">Oversight Console v2.0</p>
                    <div className="mt-4 text-xs font-mono bg-gray-800 p-2 rounded text-green-400">
                        {status}
                    </div>
                </div>

                <div className="border-t border-gray-700 pt-6">
                    <h2 className="text-sm font-bold text-gray-300 mb-4 uppercase">Layer 4 Engine</h2>
                    <InferencePanel />
                </div>
            </div>

            {/* Main Graph View */}
            <div className="w-2/3 relative bg-black">
                <div className="absolute top-4 left-4 z-10 bg-gray-800/80 p-2 rounded text-xs font-mono text-gray-300">
                    Live Knowledge Graph (T3)
                </div>
                <GraphVisualizer />
            </div>
        </div>
    );
};
