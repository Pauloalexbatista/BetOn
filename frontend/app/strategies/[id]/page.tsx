'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

interface Strategy {
    id: number
    name: string
    description: string
    target_outcome: string
    strategy_type: string
    is_active: boolean
    created_at: string
}

interface Match {
    id: number
    date: string
    home: string
    away: string
    odds: number
    result: boolean
    round: string
}

export default function StrategyDetailPage({ params }: { params: { id: string } }) {
    const router = useRouter()
    const [strategy, setStrategy] = useState<Strategy | null>(null)
    const [stats, setStats] = useState<any>(null)
    const [matches, setMatches] = useState<Match[]>([])
    const [upcoming, setUpcoming] = useState<Match[]>([])
    const [activeTab, setActiveTab] = useState<'historico' | 'proximos'>('historico')
    const [loading, setLoading] = useState(true)
    const [selectedMatchForBet, setSelectedMatchForBet] = useState<Match | null>(null)

    useEffect(() => {
        loadStrategyData()
    }, [params.id])

    const loadStrategyData = async () => {
        try {
            setLoading(true)

            // Load strategy details + historical matches
            const histResponse = await axios.get(`http://localhost:8000/api/strategies/${params.id}/matches`)
            setStrategy(histResponse.data.strategy)
            setStats(histResponse.data.stats)
            setMatches(histResponse.data.matches)

            // Load upcoming matches
            const upcomingResponse = await axios.get(`http://localhost:8000/api/strategies/${params.id}/upcoming`)
            setUpcoming(upcomingResponse.data.upcoming)

        } catch (err) {
            console.error('Error loading strategy:', err)
            alert('Erro ao carregar estratégia')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 p-8">
                <div className="text-white text-center">Carregando...</div>
            </div>
        )
    }

    if (!strategy) {
        return (
            <div className="min-h-screen bg-gray-900 p-8">
                <div className="text-white text-center">Estratégia não encontrada</div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-900 p-8">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-8">
                <button
                    onClick={() => router.push('/strategies')}
                    className="text-gray-400 hover:text-white mb-4 flex items-center"
                >
                    ← Voltar às Estratégias
                </button>

                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">{strategy.name}</h1>
                        <div className="flex items-center gap-3">
                            <span className={`px-3 py-1 rounded text-sm ${strategy.strategy_type === 'single'
                                ? 'bg-blue-500/20 text-blue-400'
                                : 'bg-purple-500/20 text-purple-400'
                                }`}>
                                {strategy.strategy_type === 'single' ? 'Aposta Simples' : 'Acumulador'}
                            </span>
                            <span className={`px-3 py-1 rounded text-sm ${strategy.is_active
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-red-500/20 text-red-400'
                                }`}>
                                {strategy.is_active ? 'Ativa' : 'Inativa'}
                            </span>
                        </div>
                        {strategy.description && (
                            <p className="text-gray-400 mt-2">{strategy.description}</p>
                        )}
                    </div>

                    {/* Edit Button */}
                    <button
                        onClick={() => {
                            const editPath = strategy.strategy_type === 'single'
                                ? `/strategies/single/edit/${strategy.id}`
                                : `/strategies/accumulator/edit/${strategy.id}`
                            router.push(editPath)
                        }}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium flex items-center gap-2"
                    >
                        ✏️ Editar
                    </button>
                </div>
            </div>

            {/* Strategy Configuration Summary */}
            <div className="max-w-7xl mx-auto mb-8">
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h2 className="text-lg font-bold text-white mb-4">📋 Configuração da Estratégia</h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {/* Target Outcome */}
                        <div>
                            <div className="text-sm text-gray-400 mb-1">Tipo de Aposta</div>
                            <div className="text-white font-medium">
                                {strategy.target_outcome === 'win' && '🎯 Vitória (Casa ou Fora)'}
                                {strategy.target_outcome === 'home_win' && '🏠 Vitória Casa'}
                                {strategy.target_outcome === 'away_win' && '✈️ Vitória Fora'}
                                {strategy.target_outcome === 'draw' && '🤝 Empate'}
                                {strategy.target_outcome === 'over_2.5' && '⬆️ Mais de 2.5 Golos'}
                                {strategy.target_outcome === 'under_2.5' && '⬇️ Menos de 2.5 Golos'}
                                {strategy.target_outcome === 'btts_yes' && '⚽ Ambas Marcam'}
                            </div>
                        </div>

                        {/* Leagues */}
                        {(strategy as any).leagues && (strategy as any).leagues.length > 0 && (
                            <div>
                                <div className="text-sm text-gray-400 mb-1">Ligas Selecionadas</div>
                                <div className="text-white font-medium">
                                    {(strategy as any).leagues.join(', ')}
                                </div>
                            </div>
                        )}

                        {/* Teams */}
                        {(strategy as any).teams && (strategy as any).teams.length > 0 && (
                            <div className="md:col-span-2 lg:col-span-1">
                                <div className="text-sm text-gray-400 mb-1">Equipas Selecionadas ({(strategy as any).teams.length})</div>
                                <div className="text-white font-medium text-sm max-h-20 overflow-y-auto">
                                    {(strategy as any).teams.join(', ')}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* No filters warning */}
                    {!(strategy as any).leagues && !(strategy as any).teams && (
                        <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded">
                            <div className="text-yellow-300 text-sm">
                                ⚠️ Nenhum filtro de liga ou equipa aplicado - estratégia aplica-se a todos os jogos
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Stats Cards */}
            {
                stats && (
                    <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <div className="text-gray-400 text-sm">Jogos Encontrados</div>
                            <div className="text-3xl font-bold text-white mt-2">{stats.total_matches}</div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <div className="text-gray-400 text-sm">Win Rate</div>
                            <div className="text-3xl font-bold text-green-400 mt-2">{stats.win_rate}%</div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <div className="text-gray-400 text-sm">ROI</div>
                            <div className={`text-3xl font-bold mt-2 ${stats.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {stats.roi > 0 ? '+' : ''}{stats.roi}%
                            </div>
                        </div>
                        <div className="bg-gray-800 p-6 rounded-lg">
                            <div className="text-gray-400 text-sm">Lucro Total</div>
                            <div className={`text-3xl font-bold mt-2 ${stats.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                €{stats.total_profit}
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Tabs */}
            <div className="max-w-7xl mx-auto mb-6">
                <div className="flex gap-4 border-b border-gray-700">
                    <button
                        onClick={() => setActiveTab('historico')}
                        className={`px-6 py-3 font-medium transition-colors ${activeTab === 'historico'
                            ? 'text-white border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white'
                            }`}
                    >
                        Jogos Históricos ({matches.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('proximos')}
                        className={`px-6 py-3 font-medium transition-colors ${activeTab === 'proximos'
                            ? 'text-white border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white'
                            }`}
                    >
                        Próximos Jogos ({upcoming.length})
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto">
                {activeTab === 'historico' && (
                    <div className="bg-gray-800 rounded-lg overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-700">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Data</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Jogo</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Jornada</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Odds</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Resultado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {matches.map(match => (
                                    <tr key={match.id} className="hover:bg-gray-700/50">
                                        <td className="px-6 py-4 text-sm text-gray-300">
                                            {new Date(match.date).toLocaleDateString('pt-PT')}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-white">
                                            {match.home} vs {match.away}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-400">
                                            {match.round}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-white font-mono">
                                            @{match.odds}
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            <span className={`px-3 py-1 rounded text-xs font-medium ${match.result
                                                ? 'bg-green-500/20 text-green-400'
                                                : 'bg-red-500/20 text-red-400'
                                                }`}>
                                                {match.result ? 'WON' : 'LOST'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {matches.length === 0 && (
                            <div className="text-center py-12 text-gray-400">
                                Nenhum jogo histórico encontrado
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'proximos' && (
                    <div className="bg-gray-800 rounded-lg overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-700">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Data</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Jogo</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Jornada</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Odds</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Ação</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {upcoming.map(match => (
                                    <tr key={match.id} className="hover:bg-gray-700/50">
                                        <td className="px-6 py-4 text-sm text-gray-300">
                                            {new Date(match.date).toLocaleDateString('pt-PT')}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-white">
                                            {match.home} vs {match.away}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-400">
                                            {match.round}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-white font-mono">
                                            @{match.odds}
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            <button
                                                onClick={() => setSelectedMatchForBet(match)}
                                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition-colors"
                                            >
                                                Enviar p/ Aposta
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {upcoming.length === 0 && (
                            <div className="text-center py-12 text-gray-400">
                                Nenhum jogo futuro encontrado
                            </div>
                        )}
                    </div>
                )}
            </div>

            {selectedMatchForBet && (
                <BetPlacementModal
                    isOpen={!!selectedMatchForBet}
                    onClose={() => setSelectedMatchForBet(null)}
                    match={selectedMatchForBet}
                    strategy={strategy}
                    onSuccess={() => {
                        // Refresh stats if needed
                    }}
                />
            )}
        </div >
    )
}

import BetPlacementModal from '@/components/BetPlacementModal'
