'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import axios from 'axios'

export default function EditSingleStrategy() {
    const router = useRouter()
    const params = useParams()
    const strategyId = params.id

    // Form state
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [targetOutcome, setTargetOutcome] = useState('win')
    const [selectedLeagues, setSelectedLeagues] = useState<string[]>([])
    const [selectedTeams, setSelectedTeams] = useState<string[]>([])
    const [isActive, setIsActive] = useState(true)

    // Available data
    const [availableLeagues, setAvailableLeagues] = useState<string[]>([])
    const [availableTeams, setAvailableTeams] = useState<any[]>([])

    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            // Load strategy
            const stratRes = await axios.get(`http://localhost:8000/api/strategies/${strategyId}`)
            const strategy = stratRes.data

            setName(strategy.name)
            setDescription(strategy.description || '')
            setTargetOutcome(strategy.target_outcome)
            setSelectedLeagues(strategy.leagues || [])
            setSelectedTeams(strategy.teams || [])
            setIsActive(strategy.is_active)

            // Load teams
            const teamsRes = await axios.get('http://localhost:8000/api/analysis/pareto-teams')
            if (teamsRes.data.teams) {
                setAvailableTeams(teamsRes.data.teams)
                const leagues = [...new Set(teamsRes.data.teams.map((t: any) => t.leagues).flat())]
                setAvailableLeagues(leagues as string[])
            }
        } catch (err) {
            console.error('Error loading:', err)
            alert('Erro ao carregar estratégia')
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        if (!name) {
            alert('Dá um nome à estratégia')
            return
        }

        try {
            await axios.put(`http://localhost:8000/api/strategies/${strategyId}`, {
                name,
                description,
                target_outcome: targetOutcome,
                is_active: isActive,
                leagues: selectedLeagues.length > 0 ? selectedLeagues : null,
                teams: selectedTeams.length > 0 ? selectedTeams : null
            })
            alert('Estratégia atualizada!')
            router.push('/strategies')
        } catch (err) {
            console.error('Error saving:', err)
            alert('Erro ao gravar')
        }
    }

    const displayedTeams = availableTeams.filter(t => {
        if (selectedLeagues.length === 0) return true
        return t.leagues && t.leagues.some((l: string) => selectedLeagues.includes(l))
    })

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 p-8">
                <div className="text-white text-center">Carregando...</div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-900 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <button
                        onClick={() => router.push('/strategies')}
                        className="text-gray-400 hover:text-white mb-4"
                    >
                        ← Voltar
                    </button>
                    <h1 className="text-3xl font-bold text-white mb-2">Editar Estratégia - Simples</h1>
                    <p className="text-gray-400">Modifica a tua estratégia de apostas individuais</p>
                </div>

                {/* Form */}
                <div className="space-y-6">
                    {/* Basic Info */}
                    <div className="bg-gray-800 p-6 rounded-lg">
                        <h2 className="text-xl font-bold text-white mb-4">Informação Básica</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Nome</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Descrição</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-blue-500"
                                    rows={3}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Tipo de Aposta</label>
                                <select
                                    value={targetOutcome}
                                    onChange={(e) => setTargetOutcome(e.target.value)}
                                    className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="win">Vitória (Casa ou Fora)</option>
                                    <option value="home_win">Vitória Casa</option>
                                    <option value="away_win">Vitória Fora</option>
                                    <option value="draw">Empate</option>
                                    <option value="over_2.5">Mais de 2.5 Golos</option>
                                    <option value="under_2.5">Menos de 2.5 Golos</option>
                                    <option value="btts_yes">Ambas Marcam</option>
                                </select>
                            </div>

                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    checked={isActive}
                                    onChange={(e) => setIsActive(e.target.checked)}
                                    className="form-checkbox"
                                />
                                <label className="text-sm text-gray-300">Estratégia Ativa</label>
                            </div>
                        </div>
                    </div>

                    {/* Teams Selection */}
                    <div className="bg-gray-800 p-6 rounded-lg">
                        <h2 className="text-xl font-bold text-white mb-4">Equipas</h2>

                        {/* Leagues */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">Ligas</label>
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
                                <label className="block text-sm font-medium text-gray-300">Equipas ({selectedTeams.length})</label>
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
                                        onClick={() => setSelectedTeams(displayedTeams.map(t => t.name))}
                                        className="text-xs text-blue-400 hover:text-blue-300"
                                    >
                                        Todas
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
                            onClick={() => router.push('/strategies')}
                            className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded font-medium"
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={handleSave}
                            className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded font-medium"
                        >
                            Guardar Alterações
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
