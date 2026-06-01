import React from 'react';
import { useGraphStore } from '../store/useGraphStore';

/**
 * AI Reasoning Project — Graph Visualizer
 * In a full implementation, this uses react-force-graph-2d or D3.js.
 * This is a structural placeholder for the canvas.
 */
export const GraphVisualizer: React.FC = () => {
    const { nodes } = useGraphStore();

    return (
        <div className="w-full h-full flex items-center justify-center">
            {nodes.length === 0 ? (
                <div className="text-gray-600 font-mono text-sm">Graph is empty. Seed knowledge to begin.</div>
            ) : (
                <div className="relative w-full h-full">
                    {/* Simulated Node rendered via absolute positioning for demonstration */}
                    {nodes.map((node, i) => (
                        <div 
                            key={node.entity_id} 
                            className={`absolute p-3 rounded-full flex items-center justify-center text-xs font-bold shadow-lg cursor-pointer transform hover:scale-110 transition-transform ${node.quarantine_flag ? 'bg-red-900 border-2 border-red-500 text-red-100' : 'bg-blue-900 border-2 border-blue-500 text-blue-100'}`}
                            style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)', width: '120px', height: '120px', textAlign: 'center' }}
                        >
                            <div>
                                <div className="mb-1">{node.label}</div>
                                <div className="text-[10px] opacity-70">CONF: {node.confidence.toFixed(2)}</div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
