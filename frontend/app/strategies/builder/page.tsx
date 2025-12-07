"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import axios from "axios";

// TypeScript Interfaces
interface Condition {
    entity: string;
    context: string;
    metric: string;
    operator: string;
    value: number;
    last_n_games: number;
}

export default function StrategyBuilder() {
    const router = useRouter();

    // Form State
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [targetOutcome, setTargetOutcome] = useState("home_win");
    const [conditions, setConditions] = useState<Condition[]>([]);

    // Scope State (New)
    const [selectedLeagues, setSelectedLeagues] = useState<string[]>([]);
    const [selectedTeams, setSelectedTeams] = useState<string[]>([]);

    // Available Options
    const [availableLeagues, setAvailableLeagues] = useState<string[]>([]);
    const [availableTeams, setAvailableTeams] = useState<{ id: number, name: string, leagues: string[] }[]>([]);

    // Fetch Lists on Mount
    useEffect(() => {
        const fetchMetadata = async () => {
            try {
                // Fetch Leagues & Teams
                const res = await axios.get("http://localhost:8000/api/matches/filters/options");
                setAvailableLeagues(res.data.leagues || []);
                setAvailableTeams(res.data.teams || []);
            } catch (err) {
                console.error("Failed to fetch options", err);
            }
        }
        fetchMetadata();
    }, []);

    // Selection Helpers
    const toggleLeague = (league: string) => {
        if (selectedLeagues.includes(league)) {
            setSelectedLeagues(selectedLeagues.filter(l => l !== league));
        } else {
            setSelectedLeagues([...selectedLeagues, league]);
        }
        // Ideally we might clear selectedTeams if they no longer match, but keeping them is safer UI ux (e.g. user misclicked)
    }

    const toggleTeam = (teamName: string) => {
        if (selectedTeams.includes(teamName)) {
            setSelectedTeams(selectedTeams.filter(t => t !== teamName));
        } else {
            setSelectedTeams([...selectedTeams, teamName]);
        }
    }

    // Filter Logic
    const displayedTeams = availableTeams.filter(t => {
        if (selectedLeagues.length === 0) return true; // Show all if no league selected
        // Check if team belongs to ANY selected league
        // We handle potential data mismatch (t.leagues might be missing in old cache, safe fallback)
        const teamLeagues = t.leagues || [];
        return teamLeagues.some(l => selectedLeagues.includes(l));
    });

    // Sort Displayed
    displayedTeams.sort((a, b) => a.name.localeCompare(b.name));

    // ...

    // Condition Helpers
    const addCondition = () => {
        setConditions([
            ...conditions,
            {
                entity: "home_team",
                context: "home",
                metric: "goals_scored",
                operator: ">",
                value: 1.5,
                last_n_games: 5,
            },
        ]);
    };

    const removeCondition = (index: number) => {
        const newConditions = [...conditions];
        newConditions.splice(index, 1);
        setConditions(newConditions);
    };

    const updateCondition = (index: number, field: keyof Condition, val: any) => {
        const newConditions = [...conditions];
        newConditions[index] = { ...newConditions[index], [field]: val };
        setConditions(newConditions);
    };

    const handleSubmit = async () => {
        if (!name) return alert("Please name your strategy");
        // Warn if no logic but allow if scope is set
        if (conditions.length === 0 && selectedTeams.length === 0 && selectedLeagues.length === 0) {
            return alert("Defina pelo menos uma regra ou filtro (Liga/Equipa).");
        }

        try {
            await axios.post("http://localhost:8000/api/strategies/", {
                name,
                description,
                target_outcome: targetOutcome,
                is_active: true,
                conditions,
                leagues: selectedLeagues,
                teams: selectedTeams
            });
            router.push("/strategies");
        } catch (err) {
            console.error("Failed to save strategy", err);
            alert("Error saving strategy");
        }
    };

    return (
        <main className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold">Criar Nova Estratégia</h1>
                    <Link href="/strategies" className="text-slate-400 hover:text-white flex items-center gap-2">
                        ← Voltar
                    </Link>
                </div>

                {/* 1. Basic Info */}
                <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
                    <h3 className="text-lg font-bold mb-4 text-blue-400">1. Identidade</h3>
                    <div className="grid gap-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Nome da Estratégia</label>
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                placeholder="Ex: Benfica Home Power"
                                className="w-full bg-slate-900 text-white p-3 rounded border border-slate-700"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Descrição</label>
                            <textarea
                                value={description}
                                onChange={e => setDescription(e.target.value)}
                                placeholder="Ex: Apostar na vitória quando joga em casa e marcou muitos golos recentemente..."
                                className="w-full bg-slate-900 text-white p-3 rounded border border-slate-700 h-24"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Alvo da Aposta</label>
                            <select
                                value={targetOutcome}
                                onChange={e => setTargetOutcome(e.target.value)}
                                className="w-full bg-slate-900 text-white p-3 rounded border border-slate-700"
                            >
                                <option value="home_win">Home Win (Vitória Casa)</option>
                                <option value="away_win">Away Win (Vitória Fora)</option>
                                <option value="draw">Draw (Empate)</option>
                                <option value="over_2.5">Over 2.5 Goals</option>
                                <option value="under_2.5">Under 2.5 Goals</option>
                                <option value="btts_yes">Ambas Marcam (Sim)</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* 2. Scope (New) */}
                <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
                    <h3 className="text-lg font-bold mb-4 text-purple-400">2. Âmbito (Ligas e Equipas) <span className="text-xs text-slate-500 font-normal">(Opcional)</span></h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* League Selector */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Filtrar Ligas</label>
                            <div className="h-48 overflow-y-auto bg-slate-900 border border-slate-700 rounded p-2">
                                {availableLeagues.map(l => (
                                    <div key={l} className="flex items-center gap-2 mb-1 p-1 hover:bg-slate-800 rounded cursor-pointer" onClick={() => toggleLeague(l)}>
                                        <input
                                            type="checkbox"
                                            checked={selectedLeagues.includes(l)}
                                            onChange={() => { }} // Handled by div click
                                            className="rounded bg-slate-700 border-slate-500"
                                        />
                                        <span className="text-sm truncate">{l}</span>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-1 text-xs text-slate-500">
                                {selectedLeagues.length} ligas selecionadas.
                            </div>
                        </div>

                        {/* Team Selector */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Filtrar Equipas Específicas</label>
                            <div className="h-48 overflow-y-auto bg-slate-900 border border-slate-700 rounded p-2">
                                {displayedTeams
                                    .map(t => (
                                        <div key={t.id} className="flex items-center gap-2 mb-1 p-1 hover:bg-slate-800 rounded cursor-pointer" onClick={() => toggleTeam(t.name)}>
                                            <input
                                                type="checkbox"
                                                checked={selectedTeams.includes(t.name)}
                                                onChange={() => { }}
                                                className="rounded bg-slate-700 border-slate-500"
                                            />
                                            <span className="text-sm truncate">{t.name}</span>
                                        </div>
                                    ))}
                            </div>
                            <div className="mt-1 text-xs text-slate-500">
                                {displayedTeams.length} equipas disponíveis. ({selectedTeams.length} selecionadas)
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. Rules Builder */}
                <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-green-400">3. Regras (Condições)</h3>
                        <button
                            onClick={addCondition}
                            className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded"
                        >
                            + Adicionar Regra
                        </button>
                    </div>

                    {conditions.length === 0 ? (
                        <div className="text-center py-8 text-slate-500 border-2 border-dashed border-slate-700 rounded">
                            Nenhuma regra definida (Estratégia basear-se-á apenas no Âmbito se definido).
                        </div>
                    ) : (
                        <div className="grid gap-3">
                            {conditions.map((cond, idx) => (
                                <div key={idx} className="bg-slate-900 p-4 rounded border border-slate-700 flex flex-wrap gap-2 items-center">
                                    <span className="text-slate-500 font-mono text-xs mr-2">IF</span>

                                    {/* Entity */}
                                    <select
                                        onChange={e => updateCondition(idx, 'metric', e.target.value)}
                                        className="bg-slate-800 text-white text-sm p-1 rounded"
                                    >
                                        <option value="win_rate">Taxa de Vitória %</option>
                                        <option value="goals_scored">Golos Marcados (Média)</option>
                                        <option value="goals_conceded">Golos Sofridos (Média)</option>
                                    </select>

                                    {/* Operator */}
                                    <select
                                        value={cond.operator}
                                        onChange={e => updateCondition(idx, 'operator', e.target.value)}
                                        className="bg-slate-800 text-white text-sm p-1 rounded w-16 text-center"
                                    >
                                        <option value=">">{">"}</option>
                                        <option value="<">{"<"}</option>
                                    </select>

                                    {/* Value */}
                                    <input
                                        type="number"
                                        value={cond.value}
                                        onChange={e => updateCondition(idx, 'value', parseFloat(e.target.value))}
                                        className="bg-slate-800 text-white text-sm p-1 rounded w-20 text-center"
                                    />

                                    <span className="text-slate-500 text-xs">nos últimos</span>

                                    {/* Last N */}
                                    <select
                                        value={cond.last_n_games}
                                        onChange={e => updateCondition(idx, 'last_n_games', parseInt(e.target.value))}
                                        className="bg-slate-800 text-white text-sm p-1 rounded w-16"
                                    >
                                        <option value="3">3</option>
                                        <option value="5">5</option>
                                        <option value="10">10</option>
                                    </select>

                                    <span className="text-slate-500 text-xs">jogos.</span>

                                    <button
                                        onClick={() => removeCondition(idx)}
                                        className="ml-auto text-red-500 hover:text-red-400 font-bold px-2"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* 4. Logic Preview (Optional) */}
                {conditions.length > 0 && (
                    <div className="mb-6 p-4 bg-blue-900/20 border border-blue-900/50 rounded text-sm text-blue-200">
                        <strong>Lógica:</strong> {conditions.map(c => `[${c.entity} ${c.metric} ${c.operator} ${c.value}]`).join(" AND ")}
                    </div>
                )}

                <div className="flex gap-4">
                    <button
                        onClick={handleSubmit}
                        className="flex-1 bg-green-600 hover:bg-green-500 text-white p-4 rounded-lg font-bold text-lg transition-colors shadow-lg shadow-green-900/20"
                    >
                        Guardar Estratégia
                    </button>
                </div>

            </div>
        </main>
    );
}
