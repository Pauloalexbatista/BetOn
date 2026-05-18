import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

const outfit = Outfit({ 
  subsets: ["latin"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "🏛️ Império BetOn - World Cup Quantitative Terminal",
  description: "Plataforma premium de simulação de apostas financeiras e análise de valor para o Campeonato do Mundo",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt" className={`${inter.variable} ${outfit.variable}`}>
      <body className="min-h-screen flex flex-col">
        {/* Top Premium Bar */}
        <header className="glass-panel rounded-none border-t-0 border-x-0 border-b border-borderBg py-4 px-6 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🏛️</span>
              <div>
                <h1 className="font-outfit font-bold text-xl tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-gold via-white to-emerald">
                  IMPÉRIO BETON
                </h1>
                <p className="text-[10px] uppercase tracking-widest text-emerald font-semibold font-outfit">
                  World Cup Quantitative Terminal
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald animate-pulse"></span>
                <span className="text-xs font-semibold text-gray-400">VPS Conectada</span>
              </div>
              <div className="text-xs bg-borderBg px-3 py-1.5 rounded-full border border-borderBg font-mono">
                Porta: <span className="text-gold font-bold">3002</span> ➔ <span className="text-emerald font-bold">8001</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="py-6 text-center text-xs text-gray-500 border-t border-borderBg border-opacity-30 mt-12">
          <p>© 2026 Império BetOn. Desenvolvido em parceria com Olímpia & Alex. Reservado ao Rei Paulo.</p>
        </footer>
      </body>
    </html>
  );
}
