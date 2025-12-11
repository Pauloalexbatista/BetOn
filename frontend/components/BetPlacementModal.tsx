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
            }

            alert(`❌ Erro ao criar aposta:\n${msg}`)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full p-6 shadow-2xl">
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
