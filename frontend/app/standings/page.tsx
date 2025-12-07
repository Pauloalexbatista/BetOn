"use client";

import { useState, useEffect } from "react";
import UniversalFilter from "@/components/shared/UniversalFilter";
import { useSearchParams } from "next/navigation";

interface TableRow {
    position: number;
    team: string;
    team_id: number;
    played: number;
    won: number;
    drawn: number;
    lost: number;
    gf: number;
    ga: number;
    gd: number;
    points: number;
}

export default function StandingsPage() {
    const searchParams = useSearchParams();
    const [standings, setStandings] = useState<TableRow[]>([]);
    const [loading, setLoading] = useState(false);

    // Defaults if filter is empty
    const league = searchParams.get("league") || "Primeira Liga";
    const season = searchParams.get("season") || "2025/2026";
    const date = searchParams.get("start_date"); // Using start_date as the "As of" date for now

    useEffect(() => {
        fetchStandings();
    }, [league, season, date]);

    const fetchStandings = async () => {
        setLoading(true);
        try {
            let url = `http://localhost:8000/api/analysis/standings?league=${league}&season=${season}`;
            if (date) url += `&date=${date}`;

            const res = await fetch(url);
            const data = await res.json();
            setStandings(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white p-8">
            <div className="container mx-auto">
                <h1 className="text-3xl font-bold mb-6">League Standings (Time Machine)</h1>

                {/* Universal Filter */}
                <div className="mb-8">
                    <UniversalFilter />
                    <p className="text-sm text-slate-400 mt-2">
                        * Pick a "From Date" to see the table as it was on that specific day!
                    </p>
                </div>

                {/* Table */}
                <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden border border-slate-700">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-slate-900 text-slate-300 uppercase text-xs font-semibold">
                                <tr>
                                    <th className="p-4">Pos</th>
                                    <th className="p-4">Team</th>
                                    <th className="p-4 text-center">P</th>
                                    <th className="p-4 text-center text-green-400">W</th>
                                    <th className="p-4 text-center text-gray-400">D</th>
                                    <th className="p-4 text-center text-red-400">L</th>
                                    <th className="p-4 text-center">GF</th>
                                    <th className="p-4 text-center">GA</th>
                                    <th className="p-4 text-center">GD</th>
                                    <th className="p-4 text-center font-bold text-lg">Pts</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700">
                                {loading ? (
                                    <tr><td colSpan={10} className="p-8 text-center">Loading Table...</td></tr>
                                ) : standings.length === 0 ? (
                                    <tr><td colSpan={10} className="p-8 text-center text-slate-500">No standings found for this period.</td></tr>
                                ) : (
                                    standings.map((row) => (
                                        <tr key={row.team_id} className="hover:bg-slate-700/50 transition-colors">
                                            <td className="p-4 font-mono text-slate-400">#{row.position}</td>
                                            <td className="p-4 font-bold text-white">{row.team}</td>
                                            <td className="p-4 text-center text-slate-300">{row.played}</td>
                                            <td className="p-4 text-center font-medium text-green-400">{row.won}</td>
                                            <td className="p-4 text-center font-medium text-slate-400">{row.drawn}</td>
                                            <td className="p-4 text-center font-medium text-red-400">{row.lost}</td>
                                            <td className="p-4 text-center text-slate-500">{row.gf}</td>
                                            <td className="p-4 text-center text-slate-500">{row.ga}</td>
                                            <td className="p-4 text-center font-medium text-slate-300">
                                                {row.gd > 0 ? `+${row.gd}` : row.gd}
                                            </td>
                                            <td className="p-4 text-center font-bold text-xl text-primary-400">{row.points}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
