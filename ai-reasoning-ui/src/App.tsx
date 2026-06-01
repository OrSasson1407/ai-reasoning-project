import React, { useState, useEffect } from 'react';
import { api } from './api';
import type { NodeResponse } from './api';
import { Brain, ShieldAlert, Zap, Plus, GitMerge, Database, Activity } from 'lucide-react';

function App() {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());
  const [backendStatus, setBackendStatus] = useState<string>('SYNCHRONIZING...');

  useEffect(() => {
    api.checkHealth().then(() => setBackendStatus('ONLINE')).catch(() => setBackendStatus('OFFLINE'));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-black text-white p-8">
      <header className="mb-10 flex items-center justify-between">
        <div className="flex items-center gap-5">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-xl shadow-blue-500/20">
            <Brain className="h-9 w-9 text-white"/>
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tight">Cognitive Engine</h1>
            <p className="text-slate-400 text-sm">Autonomous Knowledge Synthesis Platform</p>
          </div>
        </div>
        <div className="px-6 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-xl text-xs font-bold tracking-widest uppercase">
          ENGINE: {backendStatus}
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="glass-card flex items-center gap-4">
          <Database className="text-blue-400 w-8 h-8"/> 
          <div><h3 className="text-xs text-slate-400 uppercase tracking-wider">Total Nodes</h3><p className="text-2xl font-bold">{nodes.length}</p></div>
        </div>
        <div className="glass-card flex items-center gap-4">
          <Activity className="text-purple-400 w-8 h-8"/> 
          <div><h3 className="text-xs text-slate-400 uppercase tracking-wider">Active Selection</h3><p className="text-2xl font-bold">{selectedNodes.size}</p></div>
        </div>
        <div className="glass-card flex items-center gap-4">
          <Zap className="text-emerald-400 w-8 h-8"/> 
          <div><h3 className="text-xs text-slate-400 uppercase tracking-wider">System Status</h3><p className="text-2xl font-bold">{backendStatus}</p></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-card">
            <div className="flex items-center gap-3 mb-6"><div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center"><Plus className="w-5 h-5 text-blue-400"/></div><div><h3 className="font-bold">Inject Knowledge</h3><p className="text-xs text-slate-400">Store new facts into memory</p></div></div>
            {/* Standard inputs would go here */}
          </div>
        </div>
        <div className="lg:col-span-8">
          {nodes.length === 0 ? (
            <div className="h-[400px] flex flex-col items-center justify-center text-center border border-white/5 rounded-3xl bg-white/[0.02]">
              <Brain className="w-16 h-16 text-slate-700 mb-4"/>
              <h3 className="text-xl font-bold">Memory Graph Empty</h3>
              <p className="text-slate-500 max-w-sm">Inject facts into the cognitive engine to visualize the network.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {nodes.map(node => (
                <div key={node.entity_id} className="glass-card border-white/10 hover:border-cyan-500/50 transition-all cursor-pointer">
                  <p className="text-sm font-medium">{node.label}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
export default App;
