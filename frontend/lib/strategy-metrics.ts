/**
 * Available Metrics for Strategy Builder
 * Organized by category for better UX
 */

export interface MetricDefinition {
    value: string;
    label: string;
    description: string;
    unit?: string;
    defaultOperator?: string;
    defaultValue?: number;
}

export interface MetricCategory {
    name: string;
    icon: string;
    metrics: MetricDefinition[];
}

export const AVAILABLE_METRICS: Record<string, MetricCategory> = {
    form: {
        name: "Forma & Performance",
        icon: "📊",
        metrics: [
            {
                value: "win_rate",
                label: "Taxa de Vitória",
                description: "Percentagem de vitórias",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 60
            },
            {
                value: "points_per_game",
                label: "Pontos por Jogo",
                description: "Média de pontos conquistados",
                unit: "pts",
                defaultOperator: ">",
                defaultValue: 2.0
            },
            {
                value: "draw_percentage",
                label: "Taxa de Empates",
                description: "Percentagem de empates",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 30
            },
            {
                value: "loss_percentage",
                label: "Taxa de Derrotas",
                description: "Percentagem de derrotas",
                unit: "%",
                defaultOperator: "<",
                defaultValue: 30
            }
        ]
    },

    attack: {
        name: "Ataque",
        icon: "⚽",
        metrics: [
            {
                value: "goals_scored",
                label: "Golos Marcados",
                description: "Média de golos marcados por jogo",
                unit: "golos",
                defaultOperator: ">",
                defaultValue: 1.5
            },
            {
                value: "goals_first_half",
                label: "Golos 1ª Parte",
                description: "Média de golos na primeira parte",
                unit: "golos",
                defaultOperator: ">",
                defaultValue: 0.8
            },
            {
                value: "goals_second_half",
                label: "Golos 2ª Parte",
                description: "Média de golos na segunda parte",
                unit: "golos",
                defaultOperator: ">",
                defaultValue: 1.0
            },
            {
                value: "scoring_frequency",
                label: "Frequência de Golos",
                description: "% de jogos com pelo menos 1 golo",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 70
            }
        ]
    },

    defense: {
        name: "Defesa",
        icon: "🛡️",
        metrics: [
            {
                value: "goals_conceded",
                label: "Golos Sofridos",
                description: "Média de golos sofridos por jogo",
                unit: "golos",
                defaultOperator: "<",
                defaultValue: 1.0
            },
            {
                value: "clean_sheets_percentage",
                label: "Clean Sheets",
                description: "% de jogos sem sofrer golos",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 40
            },
            {
                value: "defensive_solidity",
                label: "Solidez Defensiva",
                description: "Índice de solidez (0-100)",
                unit: "pts",
                defaultOperator: ">",
                defaultValue: 70
            }
        ]
    },

    goals_markets: {
        name: "Mercados de Golos",
        icon: "🎯",
        metrics: [
            {
                value: "btts_percentage",
                label: "BTTS (Ambas Marcam)",
                description: "% de jogos com ambas a marcar",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 60
            },
            {
                value: "over_2.5_percentage",
                label: "Over 2.5 Goals",
                description: "% de jogos com +2.5 golos",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 60
            },
            {
                value: "over_1.5_percentage",
                label: "Over 1.5 Goals",
                description: "% de jogos com +1.5 golos",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 75
            },
            {
                value: "under_2.5_percentage",
                label: "Under 2.5 Goals",
                description: "% de jogos com -2.5 golos",
                unit: "%",
                defaultOperator: ">",
                defaultValue: 60
            },
            {
                value: "total_goals_avg",
                label: "Total de Golos (Média)",
                description: "Média total de golos por jogo",
                unit: "golos",
                defaultOperator: ">",
                defaultValue: 2.5
            }
        ]
    },

    home_away: {
        name: "Casa/Fora",
        icon: "🏠",
        metrics: [
            {
                value: "home_advantage",
                label: "Vantagem em Casa",
                description: "Diferença de performance casa vs fora",
                unit: "pts",
                defaultOperator: ">",
                defaultValue: 1.0
            },
            {
                value: "away_form",
                label: "Forma Fora",
                description: "Performance como visitante",
                unit: "pts",
                defaultOperator: ">",
                defaultValue: 1.5
            }
        ]
    }
};

export const OPERATORS = [
    { value: ">", label: "> (maior que)", symbol: ">" },
    { value: ">=", label: ">= (maior ou igual)", symbol: ">=" },
    { value: "<", label: "< (menor que)", symbol: "<" },
    { value: "<=", label: "<= (menor ou igual)", symbol: "<=" },
    { value: "==", label: "= (igual a)", symbol: "=" }
];

export function getAllMetrics(): MetricDefinition[] {
    return Object.values(AVAILABLE_METRICS).flatMap(cat => cat.metrics);
}

export function getMetricByValue(value: string): MetricDefinition | undefined {
    return getAllMetrics().find(m => m.value === value);
}

export function getMetricCategories(): string[] {
    return Object.keys(AVAILABLE_METRICS);
}
