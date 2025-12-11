'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function AccumulatorStrategyBuilder() {
    const router = useRouter()

    // Form state
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [targetOutcome, setTargetOutcome] = useState('win')
    const [minLegs, setMinLegs] = useState(2)
    const [maxLegs, setMaxLegs] = useState(3)
    const [selectedLeagues, setSelectedLeagues] = useState<string[]>([])
    const [selectedTeams, setSelectedTeams] = useState<string[]>([])

    // Available data
    const [availableLeagues, setAvailableLeagues] = useState<string[]>([])
    const [availableTeams, setAvailableTeams] = useState<any[]>([])

    // Preview
    const [preview, setPreview] = useState<any>(null)
    const [loadingPreview, setLoadingPreview] = useState(false)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            const teamsRes = await axios.get('http://localhost:8000/api/analysis/pareto-teams')
            if (teamsRes.data.teams) {
                setAvailableTeams(teamsRes.data.teams)
                const leagues = [...new Set(teamsRes.data.teams.map((t: any) => t.leagues).flat())]
                setAvailableLeagues(leagues as string[])
            }
        } catch (err) {
            console.error('Error loading data:', err)
        }
    }

    const runPreview = async () => {
        if (selectedTeams.length < 2) {
            alert('Seleciona pelo menos 2 equipas para criar acumuladores')
            return
        }

        try {
            setLoadingPreview(true)
            const res = await axios.post('http://localhost:8000/api/strategies/preview', {
                conditions: [],
                target_outcome: targetOutcome,
                leagues: selectedLeagues.length > 0 ? selectedLeagues : null,
                teams: selectedTeams,
                limit: 200
            })
            setPreview(res.data)
        } catch (err) {
            console.error('Error running preview:', err)
            alert('Erro ao gerar preview')
        } finally {
            setLoadingPreview(false)
        }
    }

    const handleSave = async () => {
        if (!name) {
            alert('Dá um nome à estratégia')
            return
        }

        if (selectedTeams.length < 2) {
            alert('Seleciona pelo menos 2 equipas')
            return
        }

        try {
            await axios.post('http://localhost:8000/api/strategies/', {
                name,
                description,
                target_outcome: targetOutcome,
                strategy_type: 'accumulator',
                is_active: true,
                conditions: [],
                leagues: selectedLeagues.length > 0 ? selectedLeagues : null,
                teams: selectedTeams
            })
            alert('Estratégia de acumuladores criada!')
            router.push('/strategies')
        } catch (err) {
            console.error('Error saving strategy:', err)
            alert('Erro ao gravar estratégia')
        }
    }

    const displayedTeams = availableTeams.filter(t => {
        if (selectedLeagues.length === 0) return true
        return t.leagues && t.leagues.some((l: string) => selectedLeagues.includes(l))
    })

    return (
        <div className="min-h-screen bg-gray-900 p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <button
                        onClick={() => router.push('/strategies')}
                        className="text-gray-400 hover:text-white mb-4"
                    >
                        ← Voltar
                    </button>
                    <h1 className="text-3xl font-bold text-white mb-2">Nova Estratégia - Acumuladores</h1>
                    <p className="text-gray-400">Cria uma estratégia para apostas múltiplas agrupadas por jornada</p>
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left: Configuration */}
                    <div className="space-y-6">
                        {/* Basic Info */}
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <h2 className="text-xl font-bold text-white mb-4">Informação Básica</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Nome da Estratégia</label>
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-purple-500"
                                        placeholder="Ex: Big 3 Acumuladores"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Descrição (opcional)</label>
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-purple-500"
                                        placeholder="Descreve a tua estratégia..."
                                        rows={3}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Tipo de Aposta</label>
                                    <select
                                        value={targetOutcome}
                                        onChange={(e) => setTargetOutcome(e.target.value)}
                                        className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-purple-500"
                                    >
                                        <option value="win">Vitória (Casa ou Fora)</option>
                                        <option value="home_win">Vitória Casa</option>
                                        <option value="away_win">Vitória Fora</option>
                                        <option value="over_2.5">Mais de 2.5 Golos</option>
                                        <option value="btts_yes">Ambas Marcam</option>
                                    </select>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Mínimo Legs</label>
                                        <input
                                            type="number"
                                            min="2"
                                            max="10"
                                            value={minLegs}
                                            onChange={(e) => setMinLegs(parseInt(e.target.value))}
                                            className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-purple-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Máximo Legs</label>
                                        <input
                                            type="number"
                                            min="2"
                                            max="10"
                                            value={maxLegs}
                                            onChange={(e) => setMaxLegs(parseInt(e.target.value))}
                                            className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-purple-500"
                                        />
                                    </div>
                                </div>

                                <div className="bg-purple-900/20 border border-purple-500/30 p-4 rounded">
                                    <div className="flex items-start gap-2">
                                        <span className="text-purple-400">ℹ️</span>
                                        <div className="text-sm text-purple-300">
                                            <strong>Acumuladores</strong> agrupam jogos da mesma jornada/semana.
                                            Quanto mais legs, maior o risco mas maior a odd combinada.
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Teams Selection */}
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <h2 className="text-xl font-bold text-white mb-4">Selecionar Equipas (mínimo 2)</h2>

                            {/* Leagues Filter */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-300 mb-2">Filtrar por Liga</label>
                                <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto">
                                    {availableLeagues.map(league => (
                                        <label key={league} className="flex items-center gap-2 p-2 hover:bg-gray-700 rounded cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={selectedLeagues.includes(league)}
                                                onChange={() => {
                                                    if (selectedLeagues.includes(league)) {
                                                        setSelectedLeagues(selectedLeagues.filter(l => l !== league))
                                                    } else {
                                                        setSelectedLeagues([...selectedLeagues, league])
                                                    }
                                                }}
                                                className="form-checkbox"
                                            />
                                            <span className="text-white text-sm">{league}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Teams */}
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <label className="block text-sm font-medium text-gray-300">Equipas ({selectedTeams.length} selecionadas)</label>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => {
                                                const top20Count = Math.max(1, Math.ceil(displayedTeams.length * 0.2))
                                                setSelectedTeams(displayedTeams.slice(0, top20Count).map(t => t.name))
                                            }}
                                            className="text-xs text-yellow-400 hover:text-yellow-300"
                                        >
                                            Top 20%
                                        </button>
                                        <button
                                            onClick={() => setSelectedTeams(displayedTeams.slice(0, 3).map(t => t.name))}
                                            className="text-xs text-purple-400 hover:text-purple-300"
                                        >
                                            Top 3
                                        </button>
                                        <button
                                            onClick={() => setSelectedTeams([])}
                                            className="text-xs text-red-400 hover:text-red-300"
                                        >
                                            Limpar
                                        </button>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto border border-gray-700 rounded p-2">
                                    {displayedTeams.map(team => (
                                        <label key={team.id} className="flex items-center gap-2 p-2 hover:bg-gray-700 rounded cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={selectedTeams.includes(team.name)}
                                                onChange={() => {
                                                    if (selectedTeams.includes(team.name)) {
                                                        setSelectedTeams(selectedTeams.filter(t => t !== team.name))
                                                    } else {
                                                        setSelectedTeams([...selectedTeams, team.name])
                                                    }
                                                }}
                                                className="form-checkbox"
                                            />
                                            <span className="text-white text-sm">{team.name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-4">
                            <button
                                onClick={runPreview}
                                disabled={loadingPreview}
                                className="flex-1 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded font-medium disabled:opacity-50"
                            >
                                {loadingPreview ? 'A calcular...' : 'Ver Preview'}
                            </button>
                            <button
                                onClick={handleSave}
                                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded font-medium"
                            >
                                Guardar Estratégia
                            </button>
                        </div>
                    </div>

                    {/* Right: Preview */}
                    <div>
                        {preview && (
                            <div className="bg-gray-800 p-6 rounded-lg sticky top-8">
                                <h2 className="text-xl font-bold text-white mb-4">Preview - Acumuladores</h2>

                                {/* Stats */}
                                <div className="grid grid-cols-2 gap-4 mb-6">
                                    <div className="bg-gray-700 p-4 rounded">
                                        <div className="text-gray-400 text-sm">Acumuladores</div>
                                        <div className="text-2xl font-bold text-white">{preview.accumulators?.length || 0}</div>
                                    </div>
                                    <div className="bg-gray-700 p-4 rounded">
                                        <div className="text-gray-400 text-sm">Jogos Total</div>
                                        <div className="text-2xl font-bold text-white">{preview.matches_found}</div>
                                    </div>
                                    <div className="bg-gray-700 p-4 rounded">
                                        <div className="text-gray-400 text-sm">Win Rate</div>
                                        <div className="text-2xl font-bold text-green-400">{preview.win_rate}%</div>
                                    </div>
                                    <div className="bg-gray-700 p-4 rounded">
                                        <div className="text-gray-400 text-sm">ROI</div>
                                        <div className={`text-2xl font-bold ${preview.roi_estimate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {preview.roi_estimate > 0 ? '+' : ''}{preview.roi_estimate}%
                                        </div>
                                    </div>
                                </div>

                                {/* Recent Accumulators */}
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-3">Acumuladores Recentes</h3>
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {preview.accumulators?.slice(0, 10).map((acca: any, idx: number) => (
                                            <div key={idx} className={`p-3 rounded border ${acca.is_win
                                                ? 'bg-green-900/20 border-green-500/30'
                                                : 'bg-red-900/20 border-red-500/30'
                                                }`}>
                                                <div className="flex justify-between items-start mb-2">
                                                    <span className="text-white font-medium text-sm">{acca.date}</span>
                                                    <span className={`text-xs font-bold ${acca.is_win ? 'text-green-400' : 'text-red-400'}`}>
                                                        {acca.is_win ? `+€${Math.abs(acca.profit)}` : `-€${Math.abs(acca.profit)}`}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-400 mb-1">
                                                    {acca.legs} Legs • Odd: @{acca.combined_odds}
                                                </div>
                                                <div className="space-y-1">
                                                    {acca.matches?.map((match: any, mIdx: number) => (
                                                        <div key={mIdx} className="text-xs text-gray-300">
                                                            • {match.home} vs {match.away}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {!preview && (
                            <div className="bg-gray-800 p-12 rounded-lg text-center">
                                <div className="text-gray-400">Clica em "Ver Preview" para ver os acumuladores</div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
