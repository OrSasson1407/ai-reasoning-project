/**
 * AI Reasoning Project — State Management
 * Uses a lightweight observable pattern to manage the graph state in the UI.
 */
import { useState, useEffect } from 'react';
import { KnowledgeNode, Relation } from '../types';

export function useGraphStore() {
    const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
    const [relations, setRelations] = useState<Relation[]>([]);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

    // In a real application, this would fetch the full graph or a subgraph from the API
    const loadMockData = () => {
        setNodes([
            {
                entity_id: "1", label: "Water boils at 100C", node_type: "FACT" as any,
                confidence: 0.99, quarantine_flag: false, valid_from: new Date().toISOString(),
                source_ids: ["sys"], meta_tags: ["Physics"]
            }
        ]);
    };

    useEffect(() => {
        loadMockData();
    }, []);

    return {
        nodes,
        relations,
        selectedNodeId,
        setSelectedNodeId
    };
}
