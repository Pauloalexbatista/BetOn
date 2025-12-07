/**
 * Strategy Templates Library
 * Pre-defined betting strategies for quick start
 */

export interface StrategyTemplate {
    name: string;
    description: string;
    category: 'value' | 'goals' | 'form' | 'defensive' | 'special';
    target_outcome: string;
    conditions: Array<{
        entity: string;
        context: string;
        metric: string;
        operator: string;
        value: number;
        last_n_games: number;
    }>;
    leagues?: string[];
    teams?: string[];
}

export const STRATEGY_TEMPLATES: Record<string, StrategyTemplate> = {
    value_betting: {
        name: "Value Betting - Favoritos",
        description: "Aposta em favoritos com boa forma recente e odds atrativas",
        category: "value",
        target_outcome: "home_win",
        conditions: [
            {
                entity: "home_team",
                context: "home",
                metric: "win_rate",
                operator: ">",
                value: 60,
                last_n_games: 5
            },
            {
                entity: "home_team",
                context: "home",
                metric: "goals_scored",
                operator: ">",
                value: 1.5,
                last_n_games: 5
            }
        ]
    },

    btts_specialist: {
        name: "BTTS Specialist",
        description: "Ambas as equipas marcam - histórico forte de golos",
        category: "goals",
        target_outcome: "btts_yes",
        conditions: [
            {
                entity: "home_team",
                context: "overall",
                metric: "btts_percentage",
                operator: ">",
                value: 65,
                last_n_games: 10
            },
            {
                entity: "away_team",
                context: "overall",
                metric: "btts_percentage",
                operator: ">",
                value: 65,
                last_n_games: 10
            },
            {
                entity: "home_team",
                context: "overall",
                metric: "goals_scored",
                operator: ">",
                value: 1.2,
                last_n_games: 10
            }
        ]
    },

    over_goals: {
        name: "Over 2.5 Goals Hunter",
        description: "Jogos com muitos golos - equipas ofensivas",
        category: "goals",
        target_outcome: "over_2.5",
        conditions: [
            {
                entity: "home_team",
                context: "overall",
                metric: "goals_scored",
                operator: ">",
                value: 2.0,
                last_n_games: 5
            },
            {
                entity: "away_team",
                context: "overall",
                metric: "goals_scored",
                operator: ">",
                value: 1.5,
                last_n_games: 5
            },
            {
                entity: "home_team",
                context: "overall",
                metric: "goals_conceded",
                operator: ">",
                value: 1.0,
                last_n_games: 5
            }
        ]
    },

    defensive_fortress: {
        name: "Fortaleza Defensiva",
        description: "Under 2.5 - Equipas com defesas sólidas",
        category: "defensive",
        target_outcome: "under_2.5",
        conditions: [
            {
                entity: "home_team",
                context: "overall",
                metric: "goals_conceded",
                operator: "<",
                value: 0.8,
                last_n_games: 10
            },
            {
                entity: "away_team",
                context: "overall",
                metric: "goals_conceded",
                operator: "<",
                value: 1.0,
                last_n_games: 10
            },
            {
                entity: "home_team",
                context: "overall",
                metric: "clean_sheets_percentage",
                operator: ">",
                value: 40,
                last_n_games: 10
            }
        ]
    },

    away_underdog: {
        name: "Away Underdog Value",
        description: "Equipas visitantes com boa forma a surpreender",
        category: "value",
        target_outcome: "away_win",
        conditions: [
            {
                entity: "away_team",
                context: "away",
                metric: "win_rate",
                operator: ">",
                value: 50,
                last_n_games: 5
            },
            {
                entity: "away_team",
                context: "away",
                metric: "goals_scored",
                operator: ">",
                value: 1.3,
                last_n_games: 5
            },
            {
                entity: "home_team",
                context: "home",
                metric: "win_rate",
                operator: "<",
                value: 60,
                last_n_games: 5
            }
        ]
    },

    form_momentum: {
        name: "Momentum de Forma",
        description: "Equipas em excelente momento de forma",
        category: "form",
        target_outcome: "home_win",
        conditions: [
            {
                entity: "home_team",
                context: "overall",
                metric: "win_rate",
                operator: ">",
                value: 70,
                last_n_games: 3
            },
            {
                entity: "home_team",
                context: "overall",
                metric: "points_per_game",
                operator: ">",
                value: 2.5,
                last_n_games: 3
            }
        ]
    },

    draw_specialist: {
        name: "Draw Specialist",
        description: "Jogos equilibrados com tendência para empate",
        category: "special",
        target_outcome: "draw",
        conditions: [
            {
                entity: "home_team",
                context: "overall",
                metric: "draw_percentage",
                operator: ">",
                value: 35,
                last_n_games: 10
            },
            {
                entity: "away_team",
                context: "overall",
                metric: "draw_percentage",
                operator: ">",
                value: 35,
                last_n_games: 10
            },
            {
                entity: "home_team",
                context: "overall",
                metric: "win_rate",
                operator: "<",
                value: 55,
                last_n_games: 10
            }
        ]
    }
};

export const TEMPLATE_CATEGORIES = {
    value: { name: "Value Betting", icon: "💰", color: "green" },
    goals: { name: "Golos", icon: "⚽", color: "blue" },
    form: { name: "Forma", icon: "📈", color: "purple" },
    defensive: { name: "Defensiva", icon: "🛡️", color: "red" },
    special: { name: "Especial", icon: "✨", color: "yellow" }
};

export function getTemplatesByCategory(category: string): StrategyTemplate[] {
    return Object.values(STRATEGY_TEMPLATES).filter(t => t.category === category);
}

export function getAllTemplates(): StrategyTemplate[] {
    return Object.values(STRATEGY_TEMPLATES);
}
