import React, { useState, useEffect } from "react";
import { api, NodeResponse } from "./api";
import { Brain, ShieldAlert, Zap, Plus, GitMerge } from "lucide-react";

function App() {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());
  const [backendStatus, setBackendStatus] = useState<string>("CONNECTING...");
  const [error, setError] = useState<string | null>(null);

  const [newLabel, setNewLabel] = useState("");
  const [newConf, setNewConf] = useState(0.9);
  const [newType, setNewType] = useState("FACT");
  const [infMode, setInfMode] = useState<"DEDUCTIVE" | "INDUCTIVE" | "ABDUCTIVE">("DEDUCTIVE");
  const [infLabel, setInfLabel] = useState("");

  useEffect(() => {
    api.checkHealth()
      .then((res) => setBackendStatus(`ONLINE (${res.integrity})`))
      .catch(() => setBackendStatus("OFFLINE"));
  }, []);

  const handleAddNode = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newNode = await api.addNode(newType, newLabel, newConf);
      setNodes([...nodes, newNode]); 
      setNewLabel(""); 
      setError(null);
    } catch (err: any) { 
      setError(err.response?.data?.detail || "Failed to add node"); 
    }
  };

  const handleInference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedNodes.size === 0) return setError("Select at least 1 premise first.");
    try {
      const result = await api.deriveKnowledge(Array.from(selectedNodes), infMode, infLabel, "CLAIM");
      if (result.conclusion_node_id) {
        alert(`Success! Derived new node ID: ${result.conclusion_node_id}`);
      }
      setSelectedNodes(new Set()); 
      setInfLabel(""); 
      setError(null);
    } catch (err: any) { 
      setError(err.response?.data?.detail || "Inference Failed (Constraint Violation)"); 
    }
  };

  const toggleNodeSelection = (id: string) => {
    const newSet = new Set(selectedNodes);
    newSet.has(id) ? newSet.delete(id) : newSet.add(id);
    setSelectedNodes(newSet);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="flex items-center justify-between border-b border-slate-700 pb-4 mb-8">
        <div className="flex items-center gap-3">
          <Brain className="text-blue-400 w-8 h-8" />
          <h1 className="text-2xl font-bold tracking-wider">COGNITIVE ENGINE v1.0</h1>
        </div>
        <div className={`px-4 py-1 rounded-full text-xs font-bold ${backendStatus.includes("ONLINE") ? "bg-emerald-900 text-emerald-400" : "bg-red-900 text-red-400"}`}>
          ENGINE: {backendStatus}
        </div>
      </header>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded mb-6 flex items-center gap-3">
          <ShieldAlert className="w-5 h-5" />{error}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="space-y-8">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Plus className="w-5 h-5 text-blue-400"/> Inject Fact</h2>
            <form onSubmit={handleAddNode} className="space-y-4">
              <input type="text" placeholder="e.g., The system requires a database" value={newLabel} onChange={(e) => setNewLabel(e.target.value)} required className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm focus:border-blue-500 outline-none"/>
              <div className="flex gap-4">
                <select value={newType} onChange={(e) => setNewType(e.target.value)} className="w-1/2 bg-slate-900 border border-slate-600 rounded p-2 text-sm outline-none">
                  <option value="FACT">FACT</option>
                  <option value="HYPOTHESIS">HYPOTHESIS</option>
                  <option value="RULE">RULE</option>
                </select>
                <input type="number" step="0.05" min="0" max="1" value={newConf} onChange={(e) => setNewConf(parseFloat(e.target.value))} className="w-1/2 bg-slate-900 border border-slate-600 rounded p-2 text-sm outline-none"/>
              </div>
              <button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 rounded transition-colors">Commit to Memory</button>
            </form>
          </div>
          
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Zap className="w-5 h-5 text-purple-400"/> Trigger Inference</h2>
            <form onSubmit={handleInference} className="space-y-4">
              <div className="text-xs text-slate-400 mb-2">Select {selectedNodes.size} premises from the graph to combine.</div>
              <select value={infMode} onChange={(e: any) => setInfMode(e.target.value)} className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm outline-none">
                <option value="DEDUCTIVE">DEDUCTIVE (Strict)</option>
                <option value="INDUCTIVE">INDUCTIVE (Pattern)</option>
                <option value="ABDUCTIVE">ABDUCTIVE (Guess)</option>
              </select>
              <input type="text" placeholder="Hypothesized Conclusion..." value={infLabel} onChange={(e) => setInfLabel(e.target.value)} required className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm focus:border-purple-500 outline-none"/>
              <button type="submit" className="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 rounded transition-colors">Synthesize Knowledge</button>
            </form>
          </div>
        </div>
        
        <div className="lg:col-span-2 bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><GitMerge className="w-5 h-5 text-emerald-400"/> Active Memory Graph</h2>
          {nodes.length === 0 ? (
            <div className="text-center text-slate-500 py-12 border-2 border-dashed border-slate-700 rounded-lg">Engine Memory is empty. Inject facts to begin.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {nodes.map(node => (
                <div key={node.entity_id} onClick={() => toggleNodeSelection(node.entity_id)} className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${selectedNodes.has(node.entity_id) ? "border-purple-500 bg-purple-900/40" : "border-slate-600 bg-slate-900 hover:border-slate-400"}`}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold px-2 py-1 rounded bg-slate-700 text-slate-300">{node.node_type}</span>
                    <span className={`text-xs font-mono font-bold ${node.confidence > 0.8 ? "text-emerald-400" : "text-amber-400"}`}>Conf: {node.confidence.toFixed(2)}</span>
                  </div>
                  <p className="text-sm">{node.label}</p>
                  {node.quarantine_flag && <div className="mt-2 text-xs text-red-400 font-bold flex items-center gap-1"><ShieldAlert className="w-3 h-3"/> QUARANTINED</div>}
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
