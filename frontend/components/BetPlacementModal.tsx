import { useState, useEffect } from 'react'
import axios from 'axios'

interface BetPlacementModalProps {
    isOpen: boolean
    onClose: () => void
    match: any
    strategy: any
    onSuccess: () => void
}

export default function BetPlacementModal({ isOpen, onClose, match, strategy, onSuccess }: BetPlacementModalProps) {
    const [loading, setLoading] = useState(false)
    const [bankroll, setBankroll] = useState<any>(null)
    const [stake, setStake] = useState<string>('')
    const [warning, setWarning] = useState<string | null>(null)

    const [showKelly, setShowKelly] = useState(false)
    const [kellyProb, setKellyProb] = useState<number>(55)
    const [kellyResult, setKellyResult] = useState<any>(null)

    useEffect(() => {
        if (isOpen) {
            fetchBankroll()
        }
    }, [isOpen])

    const fetchBankroll = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/bets/stats/summary')
            setBankroll(res.data.bankroll)

            // Suggest 1% stake
            const suggested = (res.data.bankroll.current * 0.01).toFixed(2)
            setStake(suggested)
        } catch (err) {
            console.error(err)
        }
    }

    const calculateKelly = async () => {
        try {
            const probDecimal = kellyProb / 100
            const res = await axios.post('http://localhost:8000/api/bankroll/kelly', {
                odds: match.odds,
                probability: probDecimal
            })
            setKellyResult(res.data)
        } catch (err) {
            console.error("Kelly calc error", err)
        }
    }

    const applyKelly = () => {
        if (kellyResult?.recommended_stake) {
            setStake(kellyResult.recommended_stake.toString())
            validateStake(kellyResult.recommended_stake)
        }
    }

    const validateStake = (val: number) => {
        if (!bankroll) return

        const newExposure = bankroll.exposure + val
        const exposurePercent = (newExposure / bankroll.current) * 100

        if (exposurePercent > 15) {
            setWarning(`⚠️ Aviso: Exposição total passará para ${exposurePercent.toFixed(1)}% da banca!`)
        } else if (val > bankroll.available) {
            setWarning(`❌ Saldo insuficiente! Disponível: €${bankroll.available}`)
        } else {
            setWarning(null)
        }
    }

    const handleCreateBet = async () => {
        if (!stake || isNaN(parseFloat(stake))) return

        try {
            setLoading(true)

            // Determine market and selection
            // Default fallback if strategy usage is simple
            const market = strategy.target_outcome === 'win' ? '1x2' : (strategy.target_outcome || '1x2')

            // Improve selection logic:
            // If strategy lists specific teams, we need to know WHICH team we are backing in this match
            // For now, let's assume the selection is the Strategy's target outcome (e.g. 'Home', 'Away', 'Draw' or specific logic)
            // BUT, since our current test strategy is "Win" for specific teams, we need to know if the team is Home or Away.

            // Simplification for the prototype:
            // Always send what is in strategy.target_outcome, OR if it is 'win', send 'Home' (placeholder)
            //Ideally, the backend or a helper should determine this.

            // Let's rely on what the backend expects.
            // Based on previous code, backend expects strings.
            const selection = strategy.target_outcome || 'Home'

            await axios.post('http://localhost:8000/api/bets/', {
                match_id: match.id,
                strategy_id: strategy.id,
                market: market,
                selection: selection,
                odds: match.odds,
                stake: parseFloat(stake),
                is_paper_trade: true
            })
            onSuccess()
            onClose()
            alert('🎉 Aposta colocada com sucesso!')
        } catch (err: any) {
            console.error(err)
            let msg = 'Erro desconhecido'

            if (err.response?.data?.detail) {
                const detail = err.response.data.detail
                if (Array.isArray(detail)) {
                    // Pydantic validation error
                    msg = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
                } else {
                    msg = detail
                }
            } else {
                msg = err.message
                // Handle Network Error specifically for better generic messaging
                if (msg === 'Network Error') {
                    msg = 'Erro de conexão com o servidor. Verifica se o backend (Docker) está a correr.'
                }
            }

            alert(`❌ Erro ao criar aposta:\n${msg}`)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
                <h3 className="text-xl font-bold text-white mb-1">Confirmar Aposta</h3>
                <p className="text-gray-400 text-sm mb-6">{match.home} vs {match.away}</p>

                {/* Bankroll Info Card */}
                {bankroll && (
                    <div className="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
                        <div className="flex justify-between mb-2">
                            <span className="text-gray-400 text-sm">Banca Atual</span>
                            <span className="text-white font-mono">€{bankroll.current}</span>
                        </div>
                        <div className="flex justify-between mb-2">
                            <span className="text-gray-400 text-sm">Em Jogo (Exposição)</span>
                            <span className="text-yellow-400 font-mono">
                                €{bankroll.exposure} ({bankroll.exposure_percent}%)
                            </span>
                        </div>
                        <div className="flex justify-between pt-2 border-t border-gray-700">
                            <span className="text-gray-400 text-sm">Disponível</span>
                            <span className="text-green-400 font-mono">€{bankroll.available}</span>
                        </div>
                    </div>
                )}

                {/* Kelly Calculator Toggle */}
                <div className="mb-4">
                    <button
                        onClick={() => setShowKelly(!showKelly)}
                        className="text-xs flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-bold uppercase tracking-wider transition-colors"
                    >
                        {showKelly ? '▼ Esconder Calculadora Kelly' : '▶ Mostrar Calculadora Kelly'}
                    </button>

                    {showKelly && (
                        <div className="mt-2 bg-gray-800/50 p-3 rounded border border-gray-700 animate-in fade-in slide-in-from-top-2">
                            <div className="flex gap-2 mb-2 items-center">
                                <div className="w-1/2">
                                    <label className="text-[10px] uppercase text-gray-500 font-bold block mb-1">Odd Atual</label>
                                    <input type="number" disabled value={match.odds} className="w-full bg-gray-900 border border-gray-700 text-gray-400 rounded px-2 py-1 text-sm" />
                                </div>
                                <div className="w-1/2">
                                    <label className="text-[10px] uppercase text-emerald-500 font-bold block mb-1">Probabilidade (%)</label>
                                    <input
                                        type="number"
                                        value={kellyProb}
                                        onChange={e => setKellyProb(parseFloat(e.target.value))}
                                        className="w-full bg-gray-900 border border-emerald-900/50 focus:border-emerald-500 text-white rounded px-2 py-1 text-sm outline-none"
                                    />
                                </div>
                            </div>
                            <button
                                onClick={calculateKelly}
                                className="w-full bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold py-1.5 rounded transition mb-2"
                            >
                                Calcular Stake Ideal
                            </button>

                            {kellyResult && (
                                <div className="bg-gray-900 p-2 rounded border border-gray-700 flex justify-between items-center">
                                    <div>
                                        <div className="text-[10px] text-gray-400 uppercase">Sugerido ({kellyResult.formatted_fraction})</div>
                                        <div className="text-emerald-400 font-mono font-bold">€{kellyResult.recommended_stake}</div>
                                    </div>
                                    <button
                                        onClick={applyKelly}
                                        className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded font-bold"
                                    >
                                        Usar
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Stake Input */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Valor da Aposta Suggestão: 1% (€{(bankroll?.current * 0.01).toFixed(2)})
                    </label>
                    <div className="relative">
                        <span className="absolute left-3 top-2 text-gray-500">€</span>
                        <input
                            type="number"
                            value={stake}
                            onChange={(e) => {
                                setStake(e.target.value)
                                validateStake(parseFloat(e.target.value))
                            }}
                            className="w-full bg-gray-950 border border-gray-700 rounded-lg py-2 pl-8 pr-4 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                    </div>
                    {warning && (
                        <p className="mt-2 text-xs text-yellow-500 bg-yellow-900/20 p-2 rounded border border-yellow-900/50">
                            {warning}
                        </p>
                    )}
                </div>

                {/* Buttons */}
                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleCreateBet}
                        disabled={loading || !!warning && warning.includes('insuficiente')}
                        className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Processando...' : 'Confirmar Aposta'}
                    </button>
                </div>
            </div>
        </div>
    )
}
