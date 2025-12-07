/**
 * Strategy Validator
 * Intelligent validation for betting strategies
 */

export interface Condition {
    entity: string;
    context: string;
    metric: string;
    operator: string;
    value: number;
    last_n_games: number;
    _index?: number;
}

export interface ValidationResult {
    errors: ValidationError[];
    warnings: ValidationWarning[];
    suggestions: ValidationSuggestion[];
    isValid: boolean;
}

export interface ValidationError {
    type: 'conflict' | 'invalid_value' | 'missing_data';
    message: string;
    affectedConditions: number[];
}

export interface ValidationWarning {
    type: 'too_restrictive' | 'unusual_value' | 'low_coverage';
    message: string;
    severity: 'low' | 'medium' | 'high';
}

export interface ValidationSuggestion {
    message: string;
    action?: string;
}

// Typical ranges for metrics
const METRIC_RANGES: Record<string, { min: number; max: number; typical: [number, number] }> = {
    win_rate: { min: 20, max: 90, typical: [40, 70] },
    points_per_game: { min: 0.5, max: 3.0, typical: [1.2, 2.3] },
    draw_percentage: { min: 15, max: 50, typical: [25, 35] },
    loss_percentage: { min: 10, max: 60, typical: [20, 40] },
    goals_scored: { min: 0.3, max: 4.0, typical: [1.0, 2.5] },
    goals_conceded: { min: 0.2, max: 3.0, typical: [0.8, 1.8] },
    clean_sheets_percentage: { min: 15, max: 70, typical: [30, 50] },
    btts_percentage: { min: 30, max: 85, typical: [55, 70] },
    'over_2_5_percentage': { min: 30, max: 80, typical: [50, 65] },
    'under_2_5_percentage': { min: 30, max: 80, typical: [40, 60] },
    total_goals_avg: { min: 1.0, max: 4.5, typical: [2.0, 3.0] }
};

export class StrategyValidator {
    validate(conditions: Condition[]): ValidationResult {
        const errors: ValidationError[] = [];
        const warnings: ValidationWarning[] = [];
        const suggestions: ValidationSuggestion[] = [];

        if (conditions.length === 0) {
            return { errors, warnings, suggestions, isValid: true };
        }

        // Add indices for tracking
        const indexedConditions = conditions.map((c, idx) => ({ ...c, _index: idx }));

        // 1. Check for conflicts
        this.checkConflicts(indexedConditions, errors);

        // 2. Check for unusual values
        this.checkUnusualValues(indexedConditions, warnings, suggestions);

        // 3. Check complexity
        this.checkComplexity(indexedConditions, warnings);

        return {
            errors,
            warnings,
            suggestions,
            isValid: errors.length === 0
        };
    }

    private checkConflicts(conditions: Condition[], errors: ValidationError[]) {
        // Group conditions by metric
        const byMetric = new Map<string, Condition[]>();

        conditions.forEach(c => {
            if (!byMetric.has(c.metric)) {
                byMetric.set(c.metric, []);
            }
            byMetric.get(c.metric)!.push(c);
        });

        // Check each metric group for conflicts
        byMetric.forEach((group, metric) => {
            if (group.length < 2) return;

            // Separate by operator type
            const greaterOps = group.filter(c => c.operator === '>' || c.operator === '>=');
            const lessOps = group.filter(c => c.operator === '<' || c.operator === '<=');
            const equalOps = group.filter(c => c.operator === '==' || c.operator === '=');

            // Check for impossible range (> X and < Y where X >= Y)
            if (greaterOps.length > 0 && lessOps.length > 0) {
                const maxLowerBound = Math.max(...greaterOps.map(c => c.value));
                const minUpperBound = Math.min(...lessOps.map(c => c.value));

                if (maxLowerBound >= minUpperBound) {
                    errors.push({
                        type: 'conflict',
                        message: `Conflito em "${this.getMetricLabel(metric)}": impossível ter valor > ${maxLowerBound} E < ${minUpperBound}`,
                        affectedConditions: [...greaterOps, ...lessOps].map(c => c._index!)
                    });
                }
            }

            // Check for multiple equals (can only be one value)
            if (equalOps.length > 1) {
                const values = equalOps.map(c => c.value);
                const uniqueValues = new Set(values);
                if (uniqueValues.size > 1) {
                    errors.push({
                        type: 'conflict',
                        message: `Conflito em "${this.getMetricLabel(metric)}": múltiplos valores exatos (${Array.from(uniqueValues).join(', ')})`,
                        affectedConditions: equalOps.map(c => c._index!)
                    });
                }
            }
        });
    }

    private checkUnusualValues(
        conditions: Condition[],
        warnings: ValidationWarning[],
        suggestions: ValidationSuggestion[]
    ) {
        conditions.forEach(c => {
            const range = METRIC_RANGES[c.metric];
            if (!range) return;

            // Check if value is outside typical range
            if (c.value < range.typical[0] || c.value > range.typical[1]) {
                // Only warn if significantly outside
                if (c.value < range.min || c.value > range.max) {
                    warnings.push({
                        type: 'unusual_value',
                        message: `Valor ${c.value} para "${this.getMetricLabel(c.metric)}" é muito incomum`,
                        severity: 'high'
                    });
                } else {
                    warnings.push({
                        type: 'unusual_value',
                        message: `Valor ${c.value} para "${this.getMetricLabel(c.metric)}" está fora do típico`,
                        severity: 'medium'
                    });
                }

                suggestions.push({
                    message: `Valores típicos para "${this.getMetricLabel(c.metric)}": ${range.typical[0]}-${range.typical[1]}`,
                    action: 'adjust_value'
                });
            }
        });
    }

    private checkComplexity(conditions: Condition[], warnings: ValidationWarning[]) {
        const count = conditions.length;

        if (count > 7) {
            warnings.push({
                type: 'too_restrictive',
                message: `${count} condições é muito restritivo - poucos jogos esperados`,
                severity: 'high'
            });
        } else if (count > 5) {
            warnings.push({
                type: 'too_restrictive',
                message: `${count} condições pode ser restritivo`,
                severity: 'medium'
            });
        }

        // Check for very specific last_n_games
        const veryShortTerm = conditions.filter(c => c.last_n_games <= 3);
        if (veryShortTerm.length >= 3) {
            warnings.push({
                type: 'low_coverage',
                message: 'Múltiplas condições com poucos jogos (≤3) pode ser instável',
                severity: 'medium'
            });
        }
    }

    private getMetricLabel(metric: string): string {
        const labels: Record<string, string> = {
            'win_rate': 'Taxa de Vitória',
            'points_per_game': 'Pontos por Jogo',
            'goals_scored': 'Golos Marcados',
            'goals_conceded': 'Golos Sofridos',
            'btts_percentage': 'BTTS %',
            'over_2_5_percentage': 'Over 2.5 %',
            'clean_sheets_percentage': 'Clean Sheets %'
        };
        return labels[metric] || metric;
    }
}
