"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import axios from "axios";

interface FilterOptions {
    leagues: string[];
    seasons: string[];
    teams: { id: number, name: string }[];
    rounds?: string[]; // Optional for now
}

export default function UniversalFilter() {
    const router = useRouter();
    const searchParams = useSearchParams();

    // State
    const [league, setLeague] = useState(searchParams.get("league") || "");
    const [season, setSeason] = useState(searchParams.get("season") || "");
    const [team, setTeam] = useState(searchParams.get("team_name") || "");
    const [round, setRound] = useState(searchParams.get("round") || "");
    const [fromDate, setFromDate] = useState(searchParams.get("start_date") || "");
    const [toDate, setToDate] = useState(searchParams.get("end_date") || "");
    const [status, setStatus] = useState(searchParams.get("status") || "");

    const [options, setOptions] = useState<FilterOptions>({ leagues: [], seasons: [], teams: [] });

    // Sync state with URL when it changes (e.g. defaults set by parent)
    useEffect(() => {
        setLeague(searchParams.get("league") || "");
        setSeason(searchParams.get("season") || "");
        setTeam(searchParams.get("team_name") || "");
        setRound(searchParams.get("round") || "");
        setFromDate(searchParams.get("start_date") || "");
        setToDate(searchParams.get("end_date") || "");
        setStatus(searchParams.get("status") || "");
    }, [searchParams]);

    // Fetch Options (with context)
    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const params = new URLSearchParams();
                if (league) params.append("league", league);
                if (season) params.append("season", season);

                const res = await axios.get(`http://localhost:8000/api/matches/filters/options?${params.toString()}`);
                setOptions(res.data);
            } catch (err) {
                console.error("Failed to load options", err);
            }
        };
        fetchOptions();
    }, [league, season]);

    const applyFilters = () => {
        const params = new URLSearchParams();
        if (league) params.set("league", league);
        if (season) params.set("season", season);
        if (team) params.set("team_name", team);
        if (round) params.set("round", round);
        if (fromDate) params.set("start_date", fromDate);
        if (toDate) params.set("end_date", toDate);
        if (status) params.set("status", status);

        router.push(`?${params.toString()}`);
    };

    const clearFilters = () => {
        setLeague("");
        setSeason("");
        setTeam("");
        setRound("");
        setFromDate("");
        setToDate("");
        setStatus("");
        router.push("?");
    };

    return (
        <div className="bg-slate-800 p-4 rounded-lg shadow-md mb-6 border border-slate-700">
            <div className="flex flex-col md:flex-row gap-4 items-end">
                {/* League Selector */}
                <div className="flex-1 min-w-[200px]">
                    <label className="block text-xs text-slate-400 mb-1">League</label>
                    <select
                        value={league}
                        onChange={(e) => { setLeague(e.target.value); setTeam(""); }}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    >
                        <option value="">All Leagues</option>
                        {options.leagues.map(l => <option key={l} value={l}>{l}</option>)}
                    </select>
                </div>

                {/* Season Selector */}
                <div className="w-24">
                    <label className="block text-xs text-slate-400 mb-1">Season</label>
                    <select
                        value={season}
                        onChange={(e) => setSeason(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    >
                        <option value="">All</option>
                        {options.seasons.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>

                {/* Round Selector (Dropdown) */}
                <div className="w-24">
                    <label className="block text-xs text-slate-400 mb-1">Jornada</label>
                    <select
                        value={round}
                        onChange={(e) => setRound(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    >
                        <option value="">Todas</option>
                        {options.rounds?.map(r => (
                            <option key={r} value={r}>{r}</option>
                        ))}
                    </select>
                </div>

                {/* Team Selector (Dropdown) */}
                <div className="flex-1 min-w-[200px]">
                    <label className="block text-xs text-slate-400 mb-1">Team</label>
                    <select
                        value={team}
                        onChange={(e) => setTeam(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    >
                        <option value="">All Teams {league ? "(Filtered)" : ""}</option>
                        {options.teams?.map(t => (
                            <option key={t.id} value={t.name}>{t.name}</option>
                        ))}
                    </select>
                </div>

                {/* Status Selector */}
                <div className="w-32">
                    <label className="block text-xs text-slate-400 mb-1">Status</label>
                    <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    >
                        <option value="">All</option>
                        <option value="finished">Finished</option>
                        <option value="scheduled">Scheduled</option>
                    </select>
                </div>

                {/* Date Selector */}
                <div className="w-40">
                    <label className="block text-xs text-slate-400 mb-1">From</label>
                    <input
                        type="date"
                        value={fromDate}
                        onChange={(e) => setFromDate(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    />
                </div>

                {/* Date To Selector */}
                <div className="w-40">
                    <label className="block text-xs text-slate-400 mb-1">To</label>
                    <input
                        type="date"
                        value={toDate}
                        onChange={(e) => setToDate(e.target.value)}
                        className="w-full bg-slate-900 text-white rounded p-2 border border-slate-700 focus:border-blue-500 outline-none"
                    />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                    <button
                        onClick={applyFilters}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-medium transition-colors"
                    >
                        Filter
                    </button>
                    <button
                        onClick={clearFilters}
                        className="bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-2 rounded transition-colors"
                        title="Clear Filters"
                    >
                        x
                    </button>
                </div>
            </div>
        </div>
    );
}
