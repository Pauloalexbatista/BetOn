# BetOn Frontend

Interface web para o sistema BetOn.

## Setup

1. **Instalar dependências**
```bash
npm install
```

2. **Executar em desenvolvimento**
```bash
npm run dev
```

Aplicação disponível em: `http://localhost:3000`

## Estrutura

```
frontend/
├── app/                # Next.js App Router
│   ├── dashboard/     # Dashboard principal
│   ├── matches/       # Gestão de jogos
│   ├── bets/          # Gestão de apostas
│   ├── strategies/    # Configuração de estratégias
│   └── settings/      # Configurações
├── components/        # Componentes React
└── lib/              # Utilitários e API client
```

## Páginas

- `/` - Landing page
- `/dashboard` - Dashboard principal (em desenvolvimento)
- `/matches` - Lista de jogos (em desenvolvimento)
- `/bets` - Gestão de apostas (em desenvolvimento)
- `/strategies` - Estratégias (em desenvolvimento)

## Desenvolvimento

O frontend comunica com o backend via proxy configurado em `next.config.js`.
Certifica-te que o backend está a correr em `http://localhost:8000`.
