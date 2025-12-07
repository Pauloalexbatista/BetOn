/**
 * Template Selector Component
 * Displays strategy templates organized by category
 */

import { STRATEGY_TEMPLATES, TEMPLATE_CATEGORIES, StrategyTemplate } from "@/lib/strategy-templates";

interface TemplateSelectorProps {
    onSelectTemplate: (template: StrategyTemplate) => void;
    onClose: () => void;
}

export default function TemplateSelector({ onSelectTemplate, onClose }: TemplateSelectorProps) {
    const templates = Object.values(STRATEGY_TEMPLATES);
    const categories = Object.entries(TEMPLATE_CATEGORIES);

    return (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
            <div className="flex justify-between items-center mb-4">
                <div>
                    <h3 className="text-lg font-bold text-blue-400">🎯 Templates Rápidos</h3>
                    <p className="text-sm text-slate-400">Comece com uma estratégia pré-definida</p>
                </div>
                <button
                    onClick={onClose}
                    className="text-slate-400 hover:text-white text-sm"
                >
                    ✕ Fechar
                </button>
            </div>

            {/* Category Tabs */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                {categories.map(([key, cat]) => (
                    <button
                        key={key}
                        className="px-4 py-2 rounded bg-slate-700 hover:bg-slate-600 text-sm whitespace-nowrap transition-colors"
                        style={{
                            borderBottom: `2px solid ${cat.color === 'green' ? '#10b981' : cat.color === 'blue' ? '#3b82f6' : cat.color === 'purple' ? '#a855f7' : cat.color === 'red' ? '#ef4444' : '#eab308'}`
                        }}
                    >
                        {cat.icon} {cat.name}
                    </button>
                ))}
            </div>

            {/* Templates Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template, idx) => {
                    const category = TEMPLATE_CATEGORIES[template.category];
                    return (
                        <button
                            key={idx}
                            onClick={() => onSelectTemplate(template)}
                            className="text-left p-4 bg-slate-900 hover:bg-slate-750 rounded border border-slate-700 hover:border-blue-500 transition-all group"
                        >
                            <div className="flex items-start gap-2 mb-2">
                                <span className="text-2xl">{category.icon}</span>
                                <div className="flex-1">
                                    <h4 className="font-bold text-white group-hover:text-blue-400 transition-colors">
                                        {template.name}
                                    </h4>
                                    <p className="text-xs text-slate-400 mt-1">
                                        {template.description}
                                    </p>
                                </div>
                            </div>

                            <div className="mt-3 flex flex-wrap gap-1">
                                <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300">
                                    {template.conditions.length} condições
                                </span>
                                <span className="text-xs px-2 py-1 rounded bg-blue-900/30 text-blue-300">
                                    {template.target_outcome.replace('_', ' ')}
                                </span>
                            </div>
                        </button>
                    );
                })}
            </div>

            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-900/50 rounded text-sm text-blue-200">
                💡 <strong>Dica:</strong> Pode personalizar qualquer template após selecioná-lo!
            </div>
        </div>
    );
}
