import React, { useState } from 'react';
import { ApiClient } from '../api/client';
import { ReasoningMode, NodeType } from '../types';

export const InferencePanel: React.FC = () => {
    const [premise, setPremise] = useState('');
    const [label, setLabel] = useState('');
    const [mode, setMode] = useState<ReasoningMode>(ReasoningMode.DEDUCTIVE);
    const [log, setLog] = useState<string[]>([]);

    const handleDerive = async () => {
        try {
            setLog(prev => [`Requesting ${mode} derivation...`, ...prev]);
            const premiseIds = premise.split(',').map(s => s.trim());
            
            const result = await ApiClient.runInference(premiseIds, mode, label, NodeType.CLAIM);
            
            setLog(prev => [
                `SUCCESS: Conclusion generated.`,
                `Trace ID: ${result.reasoning_trace_id}`,
                `Confidence: ${(result.confidence * 100).toFixed(1)}%`,
                ...prev
            ]);
        } catch (error: any) {
            setLog(prev => [`[ERROR] ${error.message}`, ...prev]);
        }
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
                <label className="text-xs text-gray-400">Premise Node IDs (comma separated)</label>
                <input 
                    className="bg-gray-800 border border-gray-600 rounded p-2 text-sm focus:border-blue-500 focus:outline-none"
                    value={premise} onChange={e => setPremise(e.target.value)} placeholder="uuid-1, uuid-2"
                />
            </div>

            <div className="flex flex-col gap-1">
                <label className="text-xs text-gray-400">Reasoning Modality</label>
                <select 
                    className="bg-gray-800 border border-gray-600 rounded p-2 text-sm focus:border-blue-500 focus:outline-none"
                    value={mode} onChange={e => setMode(e.target.value as ReasoningMode)}
                >
                    <option value={ReasoningMode.DEDUCTIVE}>Deductive (High Certainty)</option>
                    <option value={ReasoningMode.INDUCTIVE}>Inductive (Pattern Match - Capped)</option>
                    <option value={ReasoningMode.ABDUCTIVE}>Abductive (Hypothesis - Capped)</option>
                </select>
            </div>

            <div className="flex flex-col gap-1">
                <label className="text-xs text-gray-400">Proposed Conclusion Label</label>
                <input 
                    className="bg-gray-800 border border-gray-600 rounded p-2 text-sm focus:border-blue-500 focus:outline-none"
                    value={label} onChange={e => setLabel(e.target.value)} placeholder="e.g., Therefore, X is Y"
                />
            </div>

            <button 
                onClick={handleDerive}
                className="mt-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded transition-colors"
            >
                Execute Derivation
            </button>

            {/* Audit Log Output */}
            <div className="mt-4 h-48 bg-black border border-gray-700 rounded p-3 overflow-y-auto font-mono text-xs">
                {log.map((entry, i) => (
                    <div key={i} className={`mb-1 ${entry.includes('ERROR') ? 'text-red-400' : 'text-gray-300'}`}>
                        {entry}
                    </div>
                ))}
                {log.length === 0 && <span className="text-gray-600">Waiting for inference tasks...</span>}
            </div>
        </div>
    );
};
