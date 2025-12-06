export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div className="container mx-auto px-4 py-16">
                {/* Header */}
                <div className="text-center mb-16">
                    <h1 className="text-6xl font-bold text-white mb-4">
                        Bet<span className="text-primary-500">On</span>
                    </h1>
                    <p className="text-xl text-slate-300">
                        Sistema de Automação de Apostas Betfair
                    </p>
                </div>

                {/* Status Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Status do Sistema</h3>
                        <p className="text-2xl font-bold text-green-500">✓ Online</p>
                    </div>

                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Modo</h3>
                        <p className="text-2xl font-bold text-yellow-500">Paper Trading</p>
                    </div>

                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                        <h3 className="text-slate-400 text-sm font-medium mb-2">Banca</h3>
                        <p className="text-2xl font-bold text-white">€1,000.00</p>
                    </div>
                </div>

                {/* Quick Links */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <a
                        href="/dashboard"
                        className="bg-primary-600 hover:bg-primary-700 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">📊</div>
                        <h3 className="font-semibold">Dashboard</h3>
                    </a>

                    <a
                        href="/matches"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">⚽</div>
                        <h3 className="font-semibold">Jogos</h3>
                    </a>

                    <a
                        href="/bets"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🎯</div>
                        <h3 className="font-semibold">Apostas</h3>
                    </a>

                    <a
                        href="/strategies"
                        className="bg-slate-700 hover:bg-slate-600 text-white rounded-lg p-6 text-center transition-colors"
                    >
                        <div className="text-3xl mb-2">🧠</div>
                        <h3 className="font-semibold">Estratégias</h3>
                    </a>
                </div>

                {/* Setup Instructions */}
                <div className="mt-16 bg-slate-800/30 backdrop-blur-sm rounded-lg p-8 border border-slate-700">
                    <h2 className="text-2xl font-bold text-white mb-4">🚀 Próximos Passos</h2>
                    <ol className="space-y-3 text-slate-300">
                        <li className="flex items-start">
                            <span className="text-primary-500 font-bold mr-3">1.</span>
                            <span>Configurar credenciais Betfair no ficheiro <code className="bg-slate-900 px-2 py-1 rounded">.env</code></span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-primary-500 font-bold mr-3">2.</span>
                            <span>Obter API keys gratuitas (API-Football, TheOddsAPI)</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-primary-500 font-bold mr-3">3.</span>
                            <span>Executar script de inicialização da base de dados</span>
                        </li>
                        <li className="flex items-start">
                            <span className="text-primary-500 font-bold mr-3">4.</span>
                            <span>Testar em modo Paper Trading antes de apostas reais</span>
                        </li>
                    </ol>
                </div>

                {/* Footer */}
                <div className="mt-12 text-center text-slate-500 text-sm">
                    <p>BetOn v0.1.0 - Sistema em desenvolvimento</p>
                    <p className="mt-2">⚠️ Apostar responsavelmente. Nunca aposte mais do que pode perder.</p>
                </div>
            </div>
        </main>
    )
}
