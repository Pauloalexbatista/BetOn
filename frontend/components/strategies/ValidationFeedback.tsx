/**
 * Validation Feedback Component
 * Displays validation errors, warnings, and suggestions
 */

"use client";

import { ValidationResult } from '@/lib/strategy-validator';

interface ValidationFeedbackProps {
    validation: ValidationResult;
}

export default function ValidationFeedback({ validation }: ValidationFeedbackProps) {
    const hasIssues = validation.errors.length > 0 ||
        validation.warnings.length > 0 ||
        validation.suggestions.length > 0;

    if (!hasIssues) {
        return null;
    }

    return (
        <div className="space-y-3 mb-6">
            {/* Errors */}
            {validation.errors.map((error, idx) => (
                <div
                    key={`error-${idx}`}
                    className="bg-red-900/20 border-2 border-red-500 rounded-lg p-4 animate-in fade-in slide-in-from-top-2 duration-300"
                >
                    <div className="flex items-start gap-3">
                        <span className="text-red-400 text-2xl flex-shrink-0">❌</span>
                        <div className="flex-1">
                            <p className="font-bold text-red-300 mb-1">Erro - Impossível Guardar</p>
                            <p className="text-sm text-red-200">{error.message}</p>
                            {error.affectedConditions.length > 0 && (
                                <p className="text-xs text-red-300 mt-2">
                                    Afeta condições: {error.affectedConditions.map(i => `#${i + 1}`).join(', ')}
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            ))}

            {/* Warnings */}
            {validation.warnings.map((warning, idx) => {
                const isHigh = warning.severity === 'high';
                const isMedium = warning.severity === 'medium';

                return (
                    <div
                        key={`warning-${idx}`}
                        className={`border-2 rounded-lg p-4 animate-in fade-in slide-in-from-top-2 duration-300 ${isHigh
                                ? 'bg-orange-900/20 border-orange-500'
                                : isMedium
                                    ? 'bg-yellow-900/20 border-yellow-500'
                                    : 'bg-yellow-900/10 border-yellow-600'
                            }`}
                    >
                        <div className="flex items-start gap-3">
                            <span className={`text-2xl flex-shrink-0 ${isHigh ? 'text-orange-400' : 'text-yellow-400'
                                }`}>
                                ⚠️
                            </span>
                            <div className="flex-1">
                                <p className={`font-bold mb-1 ${isHigh ? 'text-orange-300' : 'text-yellow-300'
                                    }`}>
                                    Aviso {isHigh ? '(Alta Prioridade)' : ''}
                                </p>
                                <p className={`text-sm ${isHigh ? 'text-orange-200' : 'text-yellow-200'
                                    }`}>
                                    {warning.message}
                                </p>
                            </div>
                        </div>
                    </div>
                );
            })}

            {/* Suggestions */}
            {validation.suggestions.length > 0 && (
                <div className="bg-blue-900/20 border border-blue-500 rounded-lg p-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex items-start gap-3">
                        <span className="text-blue-400 text-2xl flex-shrink-0">💡</span>
                        <div className="flex-1">
                            <p className="font-bold text-blue-300 mb-2">Sugestões</p>
                            <ul className="space-y-1">
                                {validation.suggestions.map((suggestion, idx) => (
                                    <li key={idx} className="text-sm text-blue-200">
                                        • {suggestion.message}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

            {/* Summary */}
            {validation.errors.length === 0 && validation.warnings.length > 0 && (
                <div className="text-center text-xs text-slate-400 pt-2">
                    Pode guardar, mas considere os avisos acima
                </div>
            )}
        </div>
    );
}
