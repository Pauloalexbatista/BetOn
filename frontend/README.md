# BetOn Frontend
Web Interface for BetOn.

## Setup
1. **Install Dependencies**
```bash
npm install
```

2. **Run Dev Server**
```bash
npm run dev
```
App: `http://localhost:3000`

## Structure
```
frontend/
├── app/                
│   ├── page.tsx        # Dashboard (Update Games Button)
│   ├── matches/        # Matches List (Interactive Tables, Universal Filter)
│   ├── bets/           # Betting History (Universal Filter)
│   ├── standings/      # League Tables (Time Travel)
│   └── strategies/     # Strategy Builder (Next Phase)
├── components/         # Shared Components (UniversalFilter)
└── lib/                # API Client
```

## Pages
- `/` - **Dashboard**: Overview and System Controls (Update Button).
- `/matches` - **Matches**: Browse historical and upcoming games with deep filters.
- `/bets` - **Bets**: Analysis of betting history.
- `/standings` - **Standings**: Dynamic league tables with evolution charts.

## Development
The frontend proxies requests to backend at `http://localhost:8000`.
