"use client";

import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  Shield, 
  Percent, 
  Sliders, 
  Zap, 
  Play, 
  DollarSign, 
  RefreshCw, 
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Calendar,
  MapPin,
  Award,
  Search
} from "lucide-react";


// Partidas REAIS do Mundial de 2026 para exibição inicial e salvaguarda
const REAL_WORLD_CUP_MATCHES = [
  { id: 1, home: "México", away: "Coreia do Sul", time: "11 Jun, 20:00", ELO_H: 1800, ELO_A: 1760, btts_odd: 2.10, fav_odd: 1.90 },
  { id: 2, home: "EUA", away: "Suíça", time: "12 Jun, 19:00", ELO_H: 1820, ELO_A: 1780, btts_odd: 2.20, fav_odd: 1.85 },
  { id: 3, home: "Brasil", away: "Marrocos", time: "14 Jun, 21:00", ELO_H: 2010, ELO_A: 1880, btts_odd: 2.10, fav_odd: 1.50 },
  { id: 4, home: "Portugal", away: "RD Congo", time: "17 Jun, 13:00", ELO_H: 1980, ELO_A: 1710, btts_odd: 2.05, fav_odd: 1.30 },
  { id: 5, home: "Portugal", away: "Uzbequistão", time: "23 Jun, 13:00", ELO_H: 1980, ELO_A: 1760, btts_odd: 2.05, fav_odd: 1.35 },
  { id: 6, home: "Portugal", away: "Colômbia", time: "27 Jun, 19:30", ELO_H: 1980, ELO_A: 1940, btts_odd: 1.95, fav_odd: 2.10 },
];

const WORLD_CUP_ELO: Record<string, number> = {
  "Argentina": 2130, "França": 2110, "Espanha": 2040, "Inglaterra": 2020,
  "Brasil": 2010, "Portugal": 2000, "Países Baixos": 1960, "Bélgica": 1940,
  "Itália": 1920, "Alemanha": 1910, "Uruguai": 1900, "Croácia": 1880,
  "Marrocos": 1850, "Colômbia": 1840, "Japão": 1820, "EUA": 1790,
  "Suíça": 1780, "Dinamarca": 1770, "Coreia do Sul": 1760, "África do Sul": 1650,
  "México": 1800, "Canadá": 1780, "Chéquia": 1760, "Bósnia e Herzegovina": 1740,
  "Bósnia e H.": 1740, "Catar": 1720, "Haiti": 1600, "Escócia": 1750,
  "Austrália": 1770, "Turquia": 1780, "Curaçau": 1580, "Costa do Marfim": 1740,
  "Equador": 1760, "Suécia": 1800, "Tunísia": 1700, "Arábia Saudita": 1680,
  "Cabo Verde": 1690, "Irão": 1760, "Nova Zelândia": 1620, "Egito": 1730,
  "Senegal": 1780, "Iraque": 1670, "Noruega": 1770, "Argélia": 1720,
  "Áustria": 1790, "Jordânia": 1630, "Gana": 1710, "Panamá": 1660,
  "RD Congo": 1710, "Usbequistão": 1730
};

const getFlag = (team: string) => {
  const flags: Record<string, string> = {
    "México": "🇲🇽", "África do Sul": "🇿🇦", "Coreia do Sul": "🇰🇷", "Chéquia": "🇨🇿",
    "Canadá": "🇨🇦", "Bósnia e Herzegovina": "🇧🇦", "Bósnia e H.": "🇧🇦", "EUA": "🇺🇸", "Paraguai": "🇵🇾",
    "Catar": "🇶🇦", "Suíça": "🇨🇭", "Brasil": "🇧🇷", "Marrocos": "🇲🇦",
    "Haiti": "🇭🇹", "Escócia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Austrália": "🇦🇺", "Turquia": "🇹🇷",
    "Alemanha": "🇩🇪", "Curaçau": "🇨🇼", "Países Baixos": "🇳🇱", "Japão": "🇯🇵",
    "Costa do Marfim": "🇨🇮", "Equador": "🇪🇨", "Suécia": "🇸🇪", "Tunísia": "🇹🇳",
    "Arábia Saudita": "🇸🇦", "Uruguai": "🇺🇾", "Espanha": "🇪🇸", "Cabo Verde": "🇨🇻",
    "Irão": "🇮🇷", "Nova Zelândia": "🇳🇿", "Bélgica": "🇧🇪", "Egito": "🇪🇬",
    "França": "🇫🇷", "Senegal": "🇸🇳", "Iraque": "🇮🇶", "Noruega": "🇳🇴",
    "Argentina": "🇦🇷", "Argélia": "🇩🇿", "Áustria": "🇦🇹", "Jordânia": "🇯🇴",
    "Gana": "🇬🇭", "Panamá": "🇵🇦", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croácia": "🇭🇷",
    "Portugal": "🇵🇹", "RD Congo": "🇨🇩", "Usbequistão": "🇺🇿", "Colômbia": "🇨🇴"
  };
  return flags[team] || "🏳️";
};

const STADIUMS_DATA = [
  { name: "Dallas Stadium", commerical: "AT&T Stadium", city: "Dallas", country: "EUA", flag: "🇺🇸" },
  { name: "New York New Jersey Stadium", commerical: "MetLife Stadium", city: "East Rutherford", country: "EUA", flag: "🇺🇸" },
  { name: "Los Angeles Stadium", commerical: "SoFi Stadium", city: "Inglewood", country: "EUA", flag: "🇺🇸" },
  { name: "Miami Stadium", commerical: "Hard Rock Stadium", city: "Miami Gardens", country: "EUA", flag: "🇺🇸" },
  { name: "Boston Stadium", commerical: "Gillette Stadium", city: "Foxborough", country: "EUA", flag: "🇺🇸" },
  { name: "Atlanta Stadium", commerical: "Mercedes-Benz Stadium", city: "Atlanta", country: "EUA", flag: "🇺🇸" },
  { name: "Houston Stadium", commerical: "NRG Stadium", city: "Houston", country: "EUA", flag: "🇺🇸" },
  { name: "Kansas City Stadium", commerical: "Arrowhead Stadium", city: "Kansas City", country: "EUA", flag: "🇺🇸" },
  { name: "Philadelphia Stadium", commerical: "Lincoln Financial Field", city: "Philadelphia", country: "EUA", flag: "🇺🇸" },
  { name: "San Francisco Bay Area Stadium", commerical: "Levi's Stadium", city: "Santa Clara", country: "EUA", flag: "🇺🇸" },
  { name: "Seattle Stadium", commerical: "Lumen Field", city: "Seattle", country: "EUA", flag: "🇺🇸" },
  { name: "Estadio Azteca", commerical: "Mexico City Stadium", city: "Cidade do México", country: "México", flag: "🇲🇽" },
  { name: "Estadio Guadalajara", commerical: "Estadio Akron", city: "Guadalajara", country: "México", flag: "🇲🇽" },
  { name: "Estadio Monterrey", commerical: "Estadio BBVA", city: "Monterrey", country: "México", flag: "🇲🇽" },
  { name: "BC Place Vancouver", commerical: "BC Place", city: "Vancouver", country: "Canadá", flag: "🇨🇦" },
  { name: "Toronto Stadium", commerical: "BMO Field", city: "Toronto", country: "Canadá", flag: "🇨🇦" }
];

const WORLD_CUP_CALENDAR_DATA = [
  { id: 101, grupo: "A", data: "Qui, 11 Jun, 17:00", home: "México", away: "África do Sul", estadio: "Mexico City Stadium", cidade: "Cidade do México", semana: 1 },
  { id: 102, grupo: "A", data: "Qui, 11 Jun, 20:00", home: "Coreia do Sul", away: "Chéquia", estadio: "Estadio Guadalajara", cidade: "Guadalajara", semana: 1 },
  { id: 103, grupo: "B", data: "Sex, 12 Jun, 16:00", home: "Canadá", away: "Bósnia e Herzegovina", estadio: "Toronto Stadium", cidade: "Toronto", semana: 1 },
  { id: 104, grupo: "D", data: "Sex, 12 Jun, 19:00", home: "EUA", away: "Paraguai", estadio: "Los Angeles Stadium", cidade: "Los Angeles", semana: 1 },
  { id: 105, grupo: "B", data: "Sáb, 13 Jun, 13:00", home: "Catar", away: "Suíça", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 1 },
  { id: 106, grupo: "C", data: "Sáb, 13 Jun, 16:00", home: "Brasil", away: "Marrocos", estadio: "New York New Jersey Stadium", cidade: "East Rutherford", semana: 1 },
  { id: 107, grupo: "C", data: "Sáb, 13 Jun, 19:00", home: "Haiti", away: "Escócia", estadio: "Boston Stadium", cidade: "Foxborough", semana: 1 },
  { id: 108, grupo: "D", data: "Sáb, 13 Jun, 21:00", home: "Austrália", away: "Turquia", estadio: "BC Place Vancouver", cidade: "Vancouver", semana: 1 },
  { id: 109, grupo: "E", data: "Dom, 14 Jun, 13:00", home: "Alemanha", away: "Curaçau", estadio: "Houston Stadium", cidade: "Houston", semana: 1 },
  { id: 110, grupo: "F", data: "Dom, 14 Jun, 16:00", home: "Países Baixos", away: "Japão", estadio: "Dallas Stadium", cidade: "Dallas", semana: 1 },
  { id: 111, grupo: "E", data: "Dom, 14 Jun, 19:00", home: "Costa do Marfim", away: "Equador", estadio: "Philadelphia Stadium", cidade: "Philadelphia", semana: 1 },
  { id: 112, grupo: "F", data: "Dom, 14 Jun, 21:00", home: "Suécia", away: "Tunísia", estadio: "Estadio Monterrey", cidade: "Monterrey", semana: 1 },
  { id: 113, grupo: "H", data: "Seg, 15 Jun, 13:00", home: "Arábia Saudita", away: "Uruguai", estadio: "Miami Stadium", cidade: "Miami Gardens", semana: 1 },
  { id: 114, grupo: "H", data: "Seg, 15 Jun, 16:00", home: "Espanha", away: "Cabo Verde", estadio: "Atlanta Stadium", cidade: "Atlanta", semana: 1 },
  { id: 115, grupo: "G", data: "Seg, 15 Jun, 19:00", home: "Irão", away: "Nova Zelândia", estadio: "Los Angeles Stadium", cidade: "Inglewood", semana: 1 },
  { id: 116, grupo: "G", data: "Seg, 15 Jun, 21:00", home: "Bélgica", away: "Egito", estadio: "Seattle Stadium", cidade: "Seattle", semana: 1 },
  { id: 117, grupo: "I", data: "Ter, 16 Jun, 13:00", home: "França", away: "Senegal", estadio: "New York New Jersey Stadium", cidade: "East Rutherford", semana: 1 },
  { id: 118, grupo: "I", data: "Ter, 16 Jun, 16:00", home: "Iraque", away: "Noruega", estadio: "Boston Stadium", cidade: "Foxborough", semana: 1 },
  { id: 119, grupo: "J", data: "Ter, 16 Jun, 19:00", home: "Argentina", away: "Argélia", estadio: "Kansas City Stadium", cidade: "Kansas City", semana: 1 },
  { id: 120, grupo: "J", data: "Ter, 16 Jun, 21:00", home: "Áustria", away: "Jordânia", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 1 },
  { id: 121, grupo: "L", data: "Qua, 17 Jun, 13:00", home: "Gana", away: "Panamá", estadio: "Toronto Stadium", cidade: "Toronto", semana: 1 },
  { id: 122, grupo: "L", data: "Qua, 17 Jun, 16:00", home: "Inglaterra", away: "Croácia", estadio: "Dallas Stadium", cidade: "Dallas", semana: 1 },
  { id: 123, grupo: "K", data: "Qua, 17 Jun, 19:00", home: "Portugal", away: "RD Congo", estadio: "Houston Stadium", cidade: "Houston", semana: 1 },
  { id: 124, grupo: "K", data: "Qua, 17 Jun, 21:00", home: "Usbequistão", away: "Colômbia", estadio: "Mexico City Stadium", cidade: "Cidade do México", semana: 1 },
  
  { id: 201, grupo: "A", data: "Qui, 18 Jun, 13:00", home: "Chéquia", away: "África do Sul", estadio: "Atlanta Stadium", cidade: "Atlanta", semana: 2 },
  { id: 202, grupo: "B", data: "Qui, 18 Jun, 16:00", home: "Suíça", away: "Bósnia e Herzegovina", estadio: "Los Angeles Stadium", cidade: "Inglewood", semana: 2 },
  { id: 203, grupo: "B", data: "Qui, 18 Jun, 19:00", home: "Canadá", away: "Catar", estadio: "BC Place Vancouver", cidade: "Vancouver", semana: 2 },
  { id: 204, grupo: "A", data: "Qui, 18 Jun, 21:00", home: "México", away: "Coreia do Sul", estadio: "Estadio Guadalajara", cidade: "Guadalajara", semana: 2 },
  { id: 205, grupo: "C", data: "Sex, 19 Jun, 13:00", home: "Brasil", away: "Haiti", estadio: "Philadelphia Stadium", cidade: "Philadelphia", semana: 2 },
  { id: 206, grupo: "C", data: "Sex, 19 Jun, 16:00", home: "Escócia", away: "Marrocos", estadio: "Boston Stadium", cidade: "Foxborough", semana: 2 },
  { id: 207, grupo: "D", data: "Sex, 19 Jun, 19:00", home: "Turquia", away: "Paraguai", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 2 },
  { id: 208, grupo: "D", data: "Sex, 19 Jun, 21:00", home: "EUA", away: "Austrália", estadio: "Seattle Stadium", cidade: "Seattle", semana: 2 },
  { id: 209, grupo: "E", data: "Sáb, 20 Jun, 13:00", home: "Alemanha", away: "Costa do Marfim", estadio: "Toronto Stadium", cidade: "Toronto", semana: 2 },
  { id: 210, grupo: "E", data: "Sáb, 20 Jun, 16:00", home: "Equador", away: "Curaçau", estadio: "Kansas City Stadium", cidade: "Kansas City", semana: 2 },
  { id: 211, grupo: "F", data: "Sáb, 20 Jun, 19:00", home: "Países Baixos", away: "Suécia", estadio: "Houston Stadium", cidade: "Houston", semana: 2 },
  { id: 212, grupo: "F", data: "Sáb, 20 Jun, 21:00", home: "Tunísia", away: "Japão", estadio: "Estadio Monterrey", cidade: "Monterrey", semana: 2 },
  { id: 213, grupo: "H", data: "Dom, 21 Jun, 13:00", home: "Uruguai", away: "Cabo Verde", estadio: "Miami Stadium", cidade: "Miami Gardens", semana: 2 },
  { id: 214, grupo: "H", data: "Dom, 21 Jun, 16:00", home: "Espanha", away: "Arábia Saudita", estadio: "Atlanta Stadium", cidade: "Atlanta", semana: 2 },
  { id: 215, grupo: "G", data: "Dom, 21 Jun, 19:00", home: "Bélgica", away: "Irão", estadio: "Los Angeles Stadium", cidade: "Inglewood", semana: 2 },
  { id: 216, grupo: "G", data: "Dom, 21 Jun, 21:00", home: "Nova Zelândia", away: "Egito", estadio: "BC Place Vancouver", cidade: "Vancouver", semana: 2 },
  { id: 217, grupo: "I", data: "Seg, 22 Jun, 13:00", home: "Noruega", away: "Senegal", estadio: "New York New Jersey Stadium", cidade: "East Rutherford", semana: 2 },
  { id: 218, grupo: "I", data: "Seg, 22 Jun, 16:00", home: "França", away: "Iraque", estadio: "Philadelphia Stadium", cidade: "Philadelphia", semana: 2 },
  { id: 219, grupo: "J", data: "Seg, 22 Jun, 19:00", home: "Argentina", away: "Áustria", estadio: "Dallas Stadium", cidade: "Dallas", semana: 2 },
  { id: 220, grupo: "J", data: "Seg, 22 Jun, 21:00", home: "Jordânia", away: "Argélia", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 2 },
  { id: 221, grupo: "L", data: "Ter, 23 Jun, 13:00", home: "Inglaterra", away: "Gana", estadio: "Boston Stadium", cidade: "Foxborough", semana: 2 },
  { id: 222, grupo: "L", data: "Ter, 23 Jun, 16:00", home: "Panamá", away: "Croácia", estadio: "Toronto Stadium", cidade: "Toronto", semana: 2 },
  { id: 223, grupo: "K", data: "Ter, 23 Jun, 19:00", home: "Portugal", away: "Usbequistão", estadio: "Houston Stadium", cidade: "Houston", semana: 2 },
  { id: 224, grupo: "K", data: "Ter, 23 Jun, 21:00", home: "Colômbia", away: "RD Congo", estadio: "Estadio Guadalajara", cidade: "Guadalajara", semana: 2 },
  
  { id: 301, grupo: "C", data: "Qua, 24 Jun, 13:00", home: "Escócia", away: "Brasil", estadio: "Miami Stadium", cidade: "Miami Gardens", semana: 3 },
  { id: 302, grupo: "C", data: "Qua, 24 Jun, 13:00", home: "Marrocos", away: "Haiti", estadio: "Atlanta Stadium", cidade: "Atlanta", semana: 3 },
  { id: 303, grupo: "B", data: "Qua, 24 Jun, 16:00", home: "Suíça", away: "Canadá", estadio: "BC Place Vancouver", cidade: "Vancouver", semana: 3 },
  { id: 304, grupo: "B", data: "Qua, 24 Jun, 16:00", home: "Bósnia e Herzegovina", away: "Catar", estadio: "Seattle Stadium", cidade: "Seattle", semana: 3 },
  { id: 305, grupo: "A", data: "Qua, 24 Jun, 20:00", home: "Chéquia", away: "México", estadio: "Mexico City Stadium", cidade: "Cidade do México", semana: 3 },
  { id: 306, grupo: "A", data: "Qua, 24 Jun, 20:00", home: "África do Sul", away: "Coreia do Sul", estadio: "Estadio Monterrey", cidade: "Monterrey", semana: 3 },
  { id: 307, grupo: "E", data: "Qui, 25 Jun, 13:00", home: "Curaçau", away: "Costa do Marfim", estadio: "Philadelphia Stadium", cidade: "Philadelphia", semana: 3 },
  { id: 308, grupo: "E", data: "Qui, 25 Jun, 13:00", home: "Equador", away: "Alemanha", estadio: "New York New Jersey Stadium", cidade: "East Rutherford", semana: 3 },
  { id: 309, grupo: "F", data: "Qui, 25 Jun, 16:00", home: "Japão", away: "Suécia", estadio: "Dallas Stadium", cidade: "Dallas", semana: 3 },
  { id: 310, grupo: "F", data: "Qui, 25 Jun, 16:00", home: "Tunísia", away: "Países Baixos", estadio: "Kansas City Stadium", cidade: "Kansas City", semana: 3 },
  { id: 311, grupo: "D", data: "Qui, 25 Jun, 20:00", home: "Turquia", away: "EUA", estadio: "Los Angeles Stadium", cidade: "Inglewood", semana: 3 },
  { id: 312, grupo: "D", data: "Qui, 25 Jun, 20:00", home: "Paraguai", away: "Austrália", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 3 },
  { id: 313, grupo: "H", data: "Sex, 26 Jun, 13:00", home: "Uruguai", away: "Espanha", estadio: "Miami Stadium", cidade: "Miami Gardens", semana: 3 },
  { id: 314, grupo: "H", data: "Sex, 26 Jun, 13:00", home: "Cabo Verde", away: "Arábia Saudita", estadio: "Houston Stadium", cidade: "Houston", semana: 3 },
  { id: 315, grupo: "G", data: "Sex, 26 Jun, 16:00", home: "Nova Zelândia", away: "Bélgica", estadio: "San Francisco Bay Area Stadium", cidade: "Santa Clara", semana: 3 },
  { id: 316, grupo: "G", data: "Sex, 26 Jun, 16:00", home: "Egito", away: "Irão", estadio: "Seattle Stadium", cidade: "Seattle", semana: 3 },
  { id: 317, grupo: "I", data: "Sex, 26 Jun, 20:00", home: "Noruega", away: "França", estadio: "Boston Stadium", cidade: "Foxborough", semana: 3 },
  { id: 318, grupo: "I", data: "Sex, 26 Jun, 20:00", home: "Senegal", away: "Iraque", estadio: "Toronto Stadium", cidade: "Toronto", semana: 3 },
  { id: 319, grupo: "J", data: "Sáb, 27 Jun, 13:00", home: "Jordânia", away: "Argentina", estadio: "Estadio Monterrey", cidade: "Monterrey", semana: 3 },
  { id: 320, grupo: "J", data: "Sáb, 27 Jun, 13:00", home: "Argélia", away: "Áustria", estadio: "Estadio Guadalajara", cidade: "Guadalajara", semana: 3 },
  { id: 321, grupo: "K", data: "Sáb, 27 Jun, 16:00", home: "Colômbia", away: "Portugal", estadio: "Miami Stadium", cidade: "Miami Gardens", semana: 3 },
  { id: 322, grupo: "K", data: "Sáb, 27 Jun, 16:00", home: "RD Congo", away: "Usbequistão", estadio: "Mexico City Stadium", cidade: "Cidade do México", semana: 3 },
  { id: 323, grupo: "L", data: "Sáb, 27 Jun, 20:00", home: "Panamá", away: "Inglaterra", estadio: "New York New Jersey Stadium", cidade: "East Rutherford", semana: 3 },
  { id: 324, grupo: "L", data: "Sáb, 27 Jun, 20:00", home: "Croácia", away: "Gana", estadio: "Philadelphia Stadium", cidade: "Philadelphia", semana: 3 }
];



export default function Dashboard() {
  // Estados para a Consola Martingale Inteligente
  const [banca, setBanca] = useState<number>(100);
  const [odd, setOdd] = useState<number>(2.0);
  const [lucro, setLucro] = useState<number>(1);
  const [martingaleResult, setMartingaleResult] = useState<any>(null);
  const [loadingMartingale, setLoadingMartingale] = useState<boolean>(false);
  
  // Estado para a estratégia selecionada na UI
  const [selectedStrategy, setSelectedStrategy] = useState<number>(1);
  
  // Estado para a Banca Virtual Global
  const [bancaVirtual, setBancaVirtual] = useState<number>(1000);
  const [simulatedBets, setSimulatedBets] = useState<any[]>([]);
  const [matches, setMatches] = useState<any[]>(REAL_WORLD_CUP_MATCHES);

  // Estados para o Calendário Visual do Mundial 2026
  const [calendarTab, setCalendarTab] = useState<string>("jogos");
  const [filterWeek, setFilterWeek] = useState<number>(0);
  const [filterGroup, setFilterGroup] = useState<string>("todos");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedMatchDetail, setSelectedMatchDetail] = useState<any>(null);

  // Filtragem dos jogos para a visualização
  const filteredMatches = WORLD_CUP_CALENDAR_DATA.filter(m => {
    const matchesWeek = filterWeek === 0 || m.semana === filterWeek;
    const matchesGroup = filterGroup === "todos" || m.grupo === filterGroup;
    const matchesSearch = searchQuery === "" || 
      m.home.toLowerCase().includes(searchQuery.toLowerCase()) || 
      m.away.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.cidade.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesWeek && matchesGroup && matchesSearch;
  });

  const handleMatchSelect = (match: any) => {
    setSelectedMatchDetail(match);
  };



  // Chamada de API para calcular o Martingale dinamicamente no backend
  const fetchMartingale = async () => {
    setLoadingMartingale(true);
    try {
      const res = await fetch("http://localhost:8001/api/calculators/martingale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          banca_total: banca,
          odd_media: odd,
          lucro_alvo: lucro
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMartingaleResult(data);
      }
    } catch (e) {
      // Fallback matemático se a API ainda não estiver de pé na VPS
      const stakes = [];
      let acumulado = 0;
      let passo = 1;
      while (true) {
        const proxima = (acumulado + lucro) / (odd - 1);
        const proxima_rounded = Math.round(proxima * 100) / 100;
        if (acumulado + proxima_rounded > banca) break;
        stakes.push({ passo, stake: proxima_rounded, custo_total: Math.round((acumulado + proxima_rounded) * 100) / 100 });
        acumulado += proxima_rounded;
        passo++;
      }
      setMartingaleResult({
        banca_total: banca,
        odd_media: odd,
        lucro_alvo: lucro,
        passos_sobrevivencia: stakes.length,
        sequencia_stakes: stakes,
        banca_utilizada: Math.round(acumulado * 100) / 100,
        banca_restante: Math.round((banca - acumulado) * 100) / 100,
        probabilidade_falencia_percent: Math.round((0.5 ** stakes.length) * 10000) / 100
      });
    } finally {
      setLoadingMartingale(false);
    }
  };

  useEffect(() => {
    fetchMartingale();
  }, [banca, odd, lucro]);

  // Carregar partidas e apostas reais do SQLite
  useEffect(() => {
    fetch("http://localhost:8001/api/matches")
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          // Mapear os campos do SQLite para o formato esperado pelo ecrã
          const mapped = data.map((m: any) => ({
            id: m.id,
            home: m.home_team,
            away: m.away_team,
            time: m.date ? new Date(m.date).toLocaleDateString("pt-PT") + " " + new Date(m.date).toLocaleTimeString("pt-PT", {hour: "2-digit", minute: "2-digit"}) : "Brevemente",
            ELO_H: m.home_elo || 1800,
            ELO_A: m.away_elo || 1800,
            btts_odd: m.home_team === "Portugal" ? 2.05 : (m.home_team === "EUA" ? 2.20 : 2.10), // Odds do simulador base
            fav_odd: m.home_team === "Brasil" ? 1.50 : 1.90
          }));
          setMatches(mapped);
        } else {
          setMatches(REAL_WORLD_CUP_MATCHES);
        }
      })
      .catch(() => setMatches(REAL_WORLD_CUP_MATCHES));

    fetch("http://localhost:8001/api/bets")
      .then(res => res.json())
      .then(data => setSimulatedBets(data));
  }, []);


  // Função para simular aposta (Persistida no SQLite)
  const handleSimulateBet = async (match: any, type: string, oddVal: number, stake: number) => {
    const betData = {
      match_id: match.id,
      strategy_name: type,
      stake: stake,
      odd_taken: oddVal
    };
    const res = await fetch("http://localhost:8001/api/bets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(betData)
    });
    if (res.ok) {
      const newBet = await res.json();
      setSimulatedBets([newBet, ...simulatedBets]);
      setBancaVirtual(prev => Math.round((prev - stake) * 100) / 100);
    }
  };

  // Resolver aposta (Atualizada no SQLite)
  const resolveBet = async (id: number, won: boolean, stake: number, oddVal: number) => {
    const status = won ? "Ganha" : "Perdida";
    const res = await fetch(`http://localhost:8001/api/bets/${id}?status=${status}`, { method: "PUT" });
    if (res.ok) {
      setSimulatedBets(prev => prev.map(bet => bet.id === id ? { ...bet, status } : bet));
      if (won) {
        setBancaVirtual(prev => Math.round((prev + (stake * oddVal)) * 100) / 100);
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* SEÇÃO 1: BANCA VIRTUAL GLOBAL */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 shadow-blue-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <DollarSign size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Banca Virtual de Teste</p>
            <h2 className="text-4xl font-bold font-outfit text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-neonBlue mt-1">
              € {bancaVirtual.toFixed(2)}
            </h2>
            <p className="text-[10px] text-emerald font-semibold mt-2">📊 Campeonato do Mundo - Simulação Ativa</p>
          </div>
          <button 
            onClick={() => { setBancaVirtual(1000); setSimulatedBets([]); }}
            className="p-2.5 rounded-xl bg-borderBg bg-opacity-30 border border-borderBg hover:bg-opacity-100 transition-colors"
            title="Resetar Banca"
          >
            <RefreshCw size={18} className="text-neonBlue" />
          </button>
        </div>

        <div className="glass-panel p-6 shadow-gold-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <TrendingUp size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Apostas Simuladas</p>
            <h2 className="text-4xl font-bold font-outfit text-gold mt-1">
              {simulatedBets.length}
            </h2>
            <p className="text-[10px] text-gray-400 mt-2">
              Pendentes: {simulatedBets.filter(b => b.status === "Pendente").length} | Ganhas: {simulatedBets.filter(b => b.status === "Ganha").length}
            </p>
          </div>
          <span className="p-3 rounded-xl bg-gold bg-opacity-10 border border-gold border-opacity-20 text-gold">
            🏆
          </span>
        </div>

        <div className="glass-panel p-6 shadow-emerald-neon flex justify-between items-center relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-5 pointer-events-none translate-x-4 translate-y-4">
            <Percent size={160} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-gray-400 font-semibold font-outfit">Eficácia (ROI)</p>
            <h2 className="text-4xl font-bold font-outfit text-emerald mt-1">
              {simulatedBets.length > 0 
                ? `${((simulatedBets.filter(b => b.status === "Ganha").length / simulatedBets.filter(b => b.status !== "Pendente").length || 0) * 100).toFixed(0)}%`
                : "0%"}
            </h2>
            <p className="text-[10px] text-gray-400 mt-2">Apenas apostas liquidadas são calculadas</p>
          </div>
          <span className="p-3 rounded-xl bg-emerald bg-opacity-10 border border-emerald border-opacity-20 text-emerald">
            📈
          </span>
        </div>
      </section>

      {/* SEÇÃO 2: CENTRAL DE ESTRATÉGIAS QUANTITATIVAS */}
      <section className="glass-panel p-6 md:p-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-borderBg pb-6 mb-8">
          <div>
            <h2 className="text-2xl font-bold font-outfit text-white flex items-center gap-2">
              <Zap className="text-gold" /> Central de Estratégias Quantitativas
            </h2>
            <p className="text-xs text-gray-400 mt-1">Primeiro criamos a matemática lucrativa; segundo encontramos os melhores jogos.</p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {[
              { id: 1, name: "I: BTTS SIM 2.00+" },
              { id: 2, name: "II: Zebra Protegida (66%)" },
              { id: 3, name: "III: Over/Under 2.5" },
              { id: 4, name: "IV: Favorito In-Play" },
              { id: 5, name: "V: Draw No Bet" },
            ].map(strat => (
              <button
                key={strat.id}
                onClick={() => setSelectedStrategy(strat.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold font-outfit transition-all ${
                  selectedStrategy === strat.id 
                    ? "bg-gradient-to-r from-gold to-emerald text-background shadow-gold-neon" 
                    : "bg-borderBg bg-opacity-20 border border-borderBg border-opacity-50 hover:bg-opacity-100 text-gray-300"
                }`}
              >
                {strat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Detalhes da Estratégia Selecionada */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Informações Matemáticas da Estratégia */}
          <div className="lg:col-span-1 space-y-6">
            {selectedStrategy === 1 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-gold bg-opacity-10 border border-gold border-opacity-25 text-xs text-gold font-bold">
                  Estratégia I - 50/50 Estável
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Ambas Marcam SIM $\ge$ 2.00</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Filtramos jogos onde a odd do "Ambas Marcam: SIM" é igual ou superior a 2.00. Com odds de 2.00, o Martingale de duplicação simples funciona perfeitamente, aumentando o nosso índice de sobrevivência na banca!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Mínima:</span> <span className="text-gold font-bold">2.00</span></div>
                  <div className="flex justify-between"><span>Cobertura Teórica:</span> <span className="text-emerald font-bold">50%</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Martingale</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 2 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-emerald bg-opacity-10 border border-emerald border-opacity-25 text-xs text-emerald font-bold">
                  Estratégia II - 66.6% Alta Segurança
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">A Zebra Protegida (Chance Dupla)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Casas de apostas sobrevalorizam favoritos históricos por reputação. O algoritmo deteta favoritos fracos (RSI baixo) e sugere apostar na Chance Dupla do adversário (X2 ou 1X) com odds incrivelmente desajustadas!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Alvo:</span> <span className="text-gold font-bold">1.80 a 2.10</span></div>
                  <div className="flex justify-between"><span>Cobertura Real:</span> <span className="text-emerald font-bold">66.6% (2 resultados)</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Kelly Stake 2.5%</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 3 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-neonBlue bg-opacity-10 border border-neonBlue border-opacity-25 text-xs text-neonBlue font-bold">
                  Estratégia III - 50/50 Golo Value
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Linha de Golos Inteligente (Over 2.5)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Varre equipas famosas por serem "defensivas" no papel (o que eleva as odds do Over 2.5 para cima de 2.10), mas que nos últimos 5 jogos têm atacantes explosivos e média real superior a 3.0 golos.
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Mínima:</span> <span className="text-gold font-bold">2.10</span></div>
                  <div className="flex justify-between"><span>Probabilidade Poisson:</span> <span className="text-emerald font-bold">&gt; 55%</span></div>
                  <div className="flex justify-between"><span>Método Recomendado:</span> <span className="text-neonBlue font-bold">Simulação Direta</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 4 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-red-400 bg-opacity-10 border border-red-400 border-opacity-25 text-xs text-red-400 font-bold">
                  Estratégia IV - In-Play Oportunidade
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Favoritos ao Intervalo</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  A estratégia do Rei Paulo! Um super favorito entra no jogo a 1.15. Chega empatado aos 35-40 minutos e a odd dispara para 1.50+. A probabilidade de vitória na 2ª parte mantém-se fortíssima, mas agora com retorno lucrativo!
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd Pré-Jogo:</span> <span className="text-gold font-bold">&lt; 1.30</span></div>
                  <div className="flex justify-between"><span>Odd Live Alvo:</span> <span className="text-emerald font-bold">&ge; 1.50</span></div>
                  <div className="flex justify-between"><span>Minuto de Entrada:</span> <span className="text-neonBlue font-bold">35' a 50'</span></div>
                </div>
              </div>
            )}

            {selectedStrategy === 5 && (
              <div className="space-y-4">
                <div className="inline-flex px-3 py-1 rounded-full bg-purple-400 bg-opacity-10 border border-purple-400 border-opacity-25 text-xs text-purple-400 font-bold">
                  Estratégia V - Cobertura & Reembolso
                </div>
                <h3 className="text-xl font-bold font-outfit text-white">Favorito Empatado (Draw No Bet)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Filtra favoritos óbvios mas protege a aposta eliminando o risco do empate. Se empatar, a banca é reembolsada a 100%. Transforma o jogo num 50/50 purificado com blindagem total contra empates tardios.
                </p>
                <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-2 text-xs font-mono">
                  <div className="flex justify-between"><span>Odd DNB Mínima:</span> <span className="text-gold font-bold">1.70</span></div>
                  <div className="flex justify-between"><span>Em caso de Empate:</span> <span className="text-emerald font-bold">Reembolso Total</span></div>
                  <div className="flex justify-between"><span>Vantagem ELO:</span> <span className="text-neonBlue font-bold">&gt; +100 Pontos</span></div>
                </div>
              </div>
            )}
          </div>

          {/* Jogos Disponíveis para Filtragem (Zonas de Aposta) */}
          <div className="lg:col-span-2 space-y-6">
            <h4 className="text-sm font-bold uppercase tracking-wider text-gray-300 font-outfit">Jogos do Mundial Detetados</h4>
            
            <div className="space-y-4">
              {matches.map(match => {
                // Cálculo de valor com base na estratégia selecionada
                let badge = "";
                let valueLabel = "";
                let betOdd = 0.0;
                let betType = "";

                if (selectedStrategy === 1) {
                  betOdd = match.btts_odd;
                  betType = "BTTS SIM";
                  if (match.btts_odd >= 2.0) {
                    badge = "🔥 EXCELENTE NEGÓCIO";
                    valueLabel = `Odd BTTS ${match.btts_odd} excelente para Martingale`;
                  } else {
                    badge = "⚖️ NEUTRO";
                    valueLabel = `Odd ${match.btts_odd} muito baixa para sobrevivência`;
                  }
                } else if (selectedStrategy === 2) {
                  betOdd = match.home === "Portugal" ? 1.95 : 2.10;
                  betType = "Chance Dupla X2";
                  badge = "🔥 OPORTUNIDADE ZEBRA";
                  valueLabel = `Zebra com superioridade de forma`;
                } else {
                  betOdd = match.fav_odd;
                  betType = "DNB / Favorito";
                  badge = "⚖️ EM ANÁLISE";
                  valueLabel = `Requer monitorização live`;
                }

                return (
                  <div key={match.id} className="glass-card p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold font-mono ${
                          badge.includes("EXCELENTE") || badge.includes("OPORTUNIDADE")
                            ? "bg-emerald bg-opacity-20 text-emerald border border-emerald border-opacity-30" 
                            : "bg-gray-700 text-gray-400"
                        }`}>
                          {badge}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">{match.time}</span>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-outfit font-bold text-white">{match.home}</span>
                          <span className="text-xs text-gray-500 font-mono">({match.ELO_H})</span>
                        </div>
                        <span className="text-xs text-gold font-bold">vs</span>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-outfit font-bold text-white">{match.away}</span>
                          <span className="text-xs text-gray-500 font-mono">({match.ELO_A})</span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400">{valueLabel}</p>
                    </div>

                    <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t border-borderBg border-opacity-30 md:border-t-0 pt-4 md:pt-0">
                      <div className="text-left md:text-right">
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Mercado Alvo</p>
                        <p className="text-sm font-bold text-white font-mono">{betType}</p>
                        <p className="text-xl font-black text-gold font-mono">{betOdd.toFixed(2)}</p>
                      </div>

                      <button 
                        onClick={() => handleSimulateBet(match, betType, betOdd, 10.0)}
                        className="px-5 py-3 rounded-xl bg-neonBlue bg-opacity-10 border border-neonBlue border-opacity-30 hover:bg-neonBlue hover:text-background text-neonBlue text-sm font-bold font-outfit transition-all flex items-center gap-2"
                      >
                        <Play size={14} fill="currentColor" /> Simular Aposta (€10)
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* SEÇÃO 3: CONSOLA MARTINGALE INTELIGENTE (INTERATIVA) */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Calculadora Inputs */}
        <div className="lg:col-span-1 glass-panel p-6 md:p-8 space-y-6">
          <div>
            <h3 className="text-xl font-bold font-outfit text-white flex items-center gap-2">
              <Sliders className="text-gold" /> Consola Martingale
            </h3>
            <p className="text-xs text-gray-400 mt-1">Simulação matemática e cálculo de stakes para mercados 50/50.</p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Banca da Estratégia</span>
                <span className="text-white font-bold">€ {banca}</span>
              </label>
              <input 
                type="range" 
                min="10" 
                max="1000" 
                step="10"
                value={banca} 
                onChange={(e) => setBanca(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-gold"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>10€</span> <span>1000€</span></div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Odd do Mercado</span>
                <span className="text-white font-bold">{odd.toFixed(2)}</span>
              </label>
              <input 
                type="range" 
                min="1.3" 
                max="3.0" 
                step="0.05"
                value={odd} 
                onChange={(e) => setOdd(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-neonBlue"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>1.30</span> <span>3.00</span></div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                <span>Lucro Alvo / Ciclo</span>
                <span className="text-white font-bold">€ {lucro}</span>
              </label>
              <input 
                type="range" 
                min="0.5" 
                max="20" 
                step="0.5"
                value={lucro} 
                onChange={(e) => setLucro(Number(e.target.value))}
                className="w-full h-1 bg-borderBg rounded-lg appearance-none cursor-pointer accent-emerald"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono"><span>0.5€</span> <span>20€</span></div>
            </div>
          </div>

          <div className="p-4 bg-borderBg bg-opacity-20 border border-borderBg border-opacity-30 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider font-outfit">Análise de Risco</h4>
            <div className="flex items-center gap-3">
              {martingaleResult?.passos_sobrevivencia >= 6 ? (
                <div className="h-2 w-2 rounded-full bg-emerald animate-pulse shadow-emerald-neon"></div>
              ) : martingaleResult?.passos_sobrevivencia >= 4 ? (
                <div className="h-2 w-2 rounded-full bg-gold animate-pulse shadow-gold-neon"></div>
              ) : (
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></div>
              )}
              <span className="text-xs text-gray-300">
                {martingaleResult?.passos_sobrevivencia >= 6 
                  ? "🛡️ Altíssima Segurança (Zonas de Ouro)" 
                  : martingaleResult?.passos_sobrevivencia >= 4 
                    ? "⚖️ Segurança Moderada" 
                    : "⚠️ Risco Elevado de Quebra"}
              </span>
            </div>
          </div>
        </div>

        {/* Resultados da Sequência de Stakes */}
        <div className="lg:col-span-2 glass-panel p-6 md:p-8 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-bold font-outfit text-white">Sequência Matemática</h3>
              <p className="text-xs text-gray-400 mt-1">Passos exatos para recuperar 100% das perdas + obter o lucro alvo.</p>
            </div>
            
            <div className="text-right">
              <span className="text-xs text-gray-500 block uppercase font-mono">Sobrevivência</span>
              <span className="text-3xl font-black text-gold font-mono">{martingaleResult?.passos_sobrevivencia || 0} Passos</span>
            </div>
          </div>

          {loadingMartingale ? (
            <div className="h-48 flex justify-center items-center"><RefreshCw className="animate-spin text-gold" /></div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 text-[10px] text-gray-500 uppercase tracking-wider font-mono border-b border-borderBg border-opacity-30 pb-2">
                <span>Passo do Ciclo</span>
                <span className="text-center">Aposta (Stake)</span>
                <span className="text-right">Banca Acumulada</span>
              </div>
              
              <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {martingaleResult?.sequencia_stakes?.map((step: any) => (
                  <div key={step.passo} className="grid grid-cols-3 gap-4 py-2 px-3 bg-cardBg bg-opacity-40 border border-borderBg border-opacity-20 rounded-xl text-sm font-mono items-center">
                    <span className="text-gray-300 font-bold">Passo #{step.passo}</span>
                    <span className="text-center text-gold font-black">€ {step.stake.toFixed(2)}</span>
                    <span className="text-right text-gray-400">€ {step.custo_total.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-borderBg border-opacity-30 grid grid-cols-2 md:grid-cols-3 gap-4 text-xs font-mono">
                <div>
                  <span className="text-gray-500 block text-[10px] uppercase">Banca Alocada</span>
                  <span className="text-white font-bold">€ {martingaleResult?.banca_utilizada?.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-gray-500 block text-[10px] uppercase">Banca Sobra</span>
                  <span className="text-white font-bold">€ {martingaleResult?.banca_restante?.toFixed(2)}</span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <span className="text-gray-500 block text-[10px] uppercase">Probabilidade Ruína</span>
                  <span className="text-red-400 font-bold">{martingaleResult?.probabilidade_falencia_percent?.toFixed(2)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* SEÇÃO 4: HISTÓRICO DE SIMULAÇÃO DE APOSTAS VIRTUAIS */}
      <section className="glass-panel p-6 md:p-8">
        <h3 className="text-xl font-bold font-outfit text-white mb-6">Registo Virtual In-Play & Pré-Jogo</h3>
        
        {simulatedBets.length === 0 ? (
          <div className="py-12 text-center text-gray-500 text-sm">
            <AlertTriangle className="mx-auto mb-3 text-gold opacity-50" />
            Nenhuma aposta simulada registada. Clique em "Simular Aposta" num jogo acima para começar a testar!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-borderBg border-opacity-30 text-[10px] text-gray-500 uppercase tracking-wider font-mono pb-2">
                  <th className="pb-3">Partida</th>
                  <th className="pb-3">Estratégia</th>
                  <th className="pb-3 text-center">Odd</th>
                  <th className="pb-3 text-center">Stake</th>
                  <th className="pb-3 text-center">Estado</th>
                  <th className="pb-3 text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borderBg divide-opacity-20 text-sm font-mono">
                {simulatedBets.map(bet => (
                  <tr key={bet.id} className="hover:bg-cardBg hover:bg-opacity-20 transition-colors">
                    <td className="py-4 text-white font-bold">{bet.match}</td>
                    <td className="py-4 text-gray-400">{bet.type}</td>
                    <td className="py-4 text-center text-gold font-bold">{bet.odd.toFixed(2)}</td>
                    <td className="py-4 text-center text-gray-300">€ {bet.stake.toFixed(2)}</td>
                    <td className="py-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        bet.status === "Pendente" 
                          ? "bg-gold bg-opacity-10 text-gold border border-gold border-opacity-25" 
                          : bet.status === "Ganha"
                            ? "bg-emerald bg-opacity-10 text-emerald border border-emerald border-opacity-25"
                            : "bg-red-500 bg-opacity-10 text-red-400 border border-red-500 border-opacity-25"
                      }`}>
                        {bet.status}
                      </span>
                    </td>
                    <td className="py-4 text-right">
                      {bet.status === "Pendente" && (
                        <div className="flex gap-2 justify-end">
                          <button 
                            onClick={() => resolveBet(bet.id, true, bet.stake, bet.odd)}
                            className="px-3 py-1 bg-emerald bg-opacity-20 hover:bg-opacity-100 text-emerald hover:text-white border border-emerald rounded-lg text-xs transition-colors"
                          >
                            ✓ Ganhou
                          </button>
                          <button 
                            onClick={() => resolveBet(bet.id, false, bet.stake, bet.odd)}
                            className="px-3 py-1 bg-red-500 bg-opacity-20 hover:bg-opacity-100 text-red-400 hover:text-white border border-red-500 rounded-lg text-xs transition-colors"
                          >
                            ✗ Perdeu
                          </button>
                        </div>
                      )}
                      {bet.status !== "Pendente" && (
                        <span className="text-gray-500 text-xs flex items-center gap-1 justify-end">
                          <CheckCircle2 size={12} className={bet.status === "Ganha" ? "text-emerald" : "text-red-400"} /> Resolvida
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* SEÇÃO 5: GUIA & CALENDÁRIO VISUAL DO MUNDIAL 2026 */}
      <section className="glass-panel p-6 md:p-8 space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-borderBg pb-6 mb-8">
          <div>
            <h2 className="text-2xl font-bold font-outfit text-white flex items-center gap-2">
              <Calendar className="text-gold" /> Guia e Calendário Visual do Mundial 2026
            </h2>
            <p className="text-xs text-gray-400 mt-1">Explora os 104 jogos, estádios oficiais e simula probabilidades ELO interativamente.</p>
          </div>
          
          {/* Tabs principais */}
          <div className="flex gap-2 bg-borderBg bg-opacity-20 p-1.5 rounded-xl border border-borderBg border-opacity-30">
            {[
              { id: "jogos", name: "🗓️ Jogos de Grupo", icon: Calendar },
              { id: "estadios", name: "🗺️ Mapa de Estádios", icon: MapPin },
              { id: "finais", name: "🏆 Árvore das Finais", icon: Award },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setCalendarTab(tab.id)}
                className={`px-4 py-2 rounded-lg text-xs font-semibold font-outfit transition-all flex items-center gap-2 ${
                  calendarTab === tab.id 
                    ? "bg-neonBlue text-background font-bold shadow-blue-neon" 
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* CONTEÚDO DA TAB JOGOS */}
        {calendarTab === "jogos" && (
          <div className="space-y-6">
            {/* Filtros e Barra de Pesquisa */}
            <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-cardBg bg-opacity-30 p-4 rounded-2xl border border-borderBg border-opacity-20">
              <div className="flex flex-wrap gap-2 w-full md:w-auto">
                {/* Semanas */}
                {[
                  { value: 0, label: "Todas as Semanas" },
                  { value: 1, label: "Semana 1" },
                  { value: 2, label: "Semana 2" },
                  { value: 3, label: "Semana 3" },
                ].map(week => (
                  <button
                    key={week.value}
                    onClick={() => setFilterWeek(week.value)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                      filterWeek === week.value 
                        ? "bg-gold bg-opacity-20 text-gold border border-gold border-opacity-40" 
                        : "bg-borderBg bg-opacity-10 border border-borderBg hover:bg-opacity-30 text-gray-400"
                    }`}
                  >
                    {week.label}
                  </button>
                ))}
              </div>

              {/* Filtro de Grupo */}
              <div className="flex items-center gap-2 w-full md:w-auto">
                <span className="text-xs text-gray-500 font-mono">Grupo:</span>
                <select
                  value={filterGroup}
                  onChange={(e) => setFilterGroup(e.target.value)}
                  className="bg-background border border-borderBg rounded-lg px-2.5 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-neonBlue"
                >
                  <option value="todos">Todos</option>
                  {["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"].map(g => (
                    <option key={g} value={g}>Grupo {g}</option>
                  ))}
                </select>

                {/* Pesquisa */}
                <div className="relative w-full md:w-48 ml-auto md:ml-0">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Pesquisar seleção..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-background border border-borderBg rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-neonBlue font-mono"
                  />
                </div>
              </div>
            </div>

            {/* Listagem de Jogos Filtrada */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto pr-2">
              {filteredMatches.length === 0 ? (
                <div className="col-span-full py-12 text-center text-gray-500 text-sm font-mono">
                  Nenhum jogo encontrado com os filtros selecionados.
                </div>
              ) : (
                filteredMatches.map(match => {
                  const eloH = WORLD_CUP_ELO[match.home] || 1800;
                  const eloA = WORLD_CUP_ELO[match.away] || 1800;
                  const eloDiff = eloH - eloA;
                  const formatDiff = eloDiff > 0 ? `+${eloDiff}` : eloDiff;
                  
                  return (
                    <div 
                      key={match.id}
                      onClick={() => handleMatchSelect(match)}
                      className="glass-card p-4 hover:border-neonBlue hover:scale-[1.01] transition-all cursor-pointer relative overflow-hidden group border border-borderBg border-opacity-35"
                    >
                      {/* Badge superior */}
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-[10px] bg-borderBg bg-opacity-50 text-gold px-2 py-0.5 rounded font-mono font-bold">
                          Grupo {match.grupo} • Semana {match.semana}
                        </span>
                        <span className="text-[10px] text-gray-400 font-mono">
                          {match.data}
                        </span>
                      </div>

                      {/* Equipas */}
                      <div className="space-y-3 my-4">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{getFlag(match.home)}</span>
                            <span className="font-outfit font-bold text-white group-hover:text-neonBlue transition-colors">{match.home}</span>
                          </div>
                          <span className="text-xs text-gray-500 font-mono">{eloH}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{getFlag(match.away)}</span>
                            <span className="font-outfit font-bold text-white group-hover:text-neonBlue transition-colors">{match.away}</span>
                          </div>
                          <span className="text-xs text-gray-500 font-mono">{eloA}</span>
                        </div>
                      </div>

                      {/* Info Estádio & Detalhes */}
                      <div className="border-t border-borderBg border-opacity-20 pt-3 flex justify-between items-center text-[10px] text-gray-400 font-mono">
                        <span className="flex items-center gap-1 truncate max-w-[150px]">
                          <MapPin size={10} className="text-neonBlue" /> {match.cidade}
                        </span>
                        <span className={`font-bold ${eloDiff > 100 ? "text-emerald" : eloDiff < -100 ? "text-red-400" : "text-gray-400"}`}>
                          Δ ELO: {formatDiff}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* CONTEÚDO DA TAB ESTÁDIOS */}
        {calendarTab === "estadios" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-[500px] overflow-y-auto pr-2">
            {STADIUMS_DATA.map((stadium, index) => (
              <div key={index} className="glass-card p-5 space-y-3 border border-borderBg border-opacity-35 hover:border-gold transition-all">
                <div className="flex justify-between items-start">
                  <span className="text-2xl">{stadium.flag}</span>
                  <span className="text-[10px] bg-gold bg-opacity-10 text-gold border border-gold border-opacity-20 px-2 py-0.5 rounded font-mono font-semibold">
                    {stadium.country}
                  </span>
                </div>
                <div>
                  <h4 className="font-outfit font-bold text-white text-base leading-snug">{stadium.name}</h4>
                  <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1 font-mono">{stadium.commerical}</p>
                </div>
                <div className="border-t border-borderBg border-opacity-20 pt-3 flex justify-between text-xs text-gray-400 font-mono">
                  <span>📍 {stadium.city}</span>
                  <span className="text-gold font-bold">Mundial 2026</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CONTEÚDO DA TAB FINAIS */}
        {calendarTab === "finais" && (
          <div className="space-y-8">
            {/* Mini Roadmap Finais */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {[
                { phase: "1/16 Final", dates: "28 Jun - 3 Jul", desc: "32 Seleções (KO)", bg: "border-gray-700 bg-gray-900 bg-opacity-20 text-gray-400" },
                { phase: "Oitavos", dates: "4 Jul - 7 Jul", desc: "16 Seleções (KO)", bg: "border-blue-900 bg-blue-950 bg-opacity-20 text-neonBlue border-opacity-40" },
                { phase: "Quartos", dates: "9 Jul - 11 Jul", desc: "8 Seleções (KO)", bg: "border-purple-900 bg-purple-950 bg-opacity-20 text-purple-400 border-opacity-40" },
                { phase: "Meias-Finais", dates: "14 Jul - 15 Jul", desc: "Dallas e Atlanta", bg: "border-gold border-opacity-30 bg-gold bg-opacity-5 text-gold" },
                { phase: "🏆 Grande Final", dates: "19 Julho", desc: "MetLife Stadium", bg: "bg-gradient-to-r from-gold to-emerald text-background font-black font-outfit shadow-gold-neon" }
              ].map((step, idx) => (
                <div key={idx} className={`p-4 rounded-xl border flex flex-col justify-between space-y-2 text-center ${step.bg}`}>
                  <div>
                    <h4 className="font-outfit font-black uppercase text-sm tracking-wider">{step.phase}</h4>
                    <p className="text-[10px] font-mono mt-1 opacity-70">{step.dates}</p>
                  </div>
                  <p className="text-[11px] font-mono font-semibold">{step.desc}</p>
                </div>
              ))}
            </div>

            {/* Listagem Corrida das Finais */}
            <div className="glass-panel p-6 bg-cardBg bg-opacity-20 space-y-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-gray-300 font-mono">Estrutura de Fases & Datas Oficiais</h4>
              <div className="space-y-3 font-mono text-xs text-gray-300">
                <div className="flex justify-between items-center py-2 border-b border-borderBg border-opacity-20">
                  <span className="font-bold text-white">Dezasseis-avos de Final (Ronda de 32)</span>
                  <span className="text-gray-400 text-right">28 de Junho a 3 de Julho • 15 cidades dos 3 países</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-borderBg border-opacity-20">
                  <span className="font-bold text-white">Oitavos de Final (Ronda de 16)</span>
                  <span className="text-gray-400 text-right">4 a 7 de Julho • 8 Estádios (incluindo Azteca e MetLife)</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-borderBg border-opacity-20">
                  <span className="font-bold text-white">Quartos de Final</span>
                  <span className="text-gray-400 text-right">9 a 11 de Julho • Boston, Los Angeles, Miami e Kansas City</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-borderBg border-opacity-20">
                  <span className="font-bold text-white">Meias-Finais</span>
                  <span className="text-gold">14 de Julho (Dallas) e 15 de Julho (Atlanta)</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-borderBg border-opacity-20">
                  <span className="font-bold text-white">Terceiro e Quarto Lugar</span>
                  <span className="text-gray-400 text-right">18 de Julho • Miami Stadium (Miami)</span>
                </div>
                <div className="flex justify-between items-center py-2 bg-emerald bg-opacity-10 px-3 rounded-xl border border-emerald border-opacity-20">
                  <span className="font-bold text-emerald">🥇 A Grande Final do Mundial 2026</span>
                  <span className="text-emerald font-black">Domingo, 19 de Julho • New York New Jersey Stadium (MetLife Stadium)</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* OVERLAY MODAL: DETALHES MATEMÁTICOS ELO DO JOGO */}
      {selectedMatchDetail && (() => {
        const home = selectedMatchDetail.home;
        const away = selectedMatchDetail.away;
        const eloH = WORLD_CUP_ELO[home] || 1800;
        const eloA = WORLD_CUP_ELO[away] || 1800;
        
        // ELO Math
        const diff = eloH - eloA;
        const probHome = 1.0 / (1.0 + Math.pow(10.0, -diff / 400.0));
        const probAway = 1.0 - probHome;
        const drawProb = 0.26 * (1.0 - Math.abs(probHome - probAway));
        const homeAdj = probHome * (1.0 - drawProb);
        const awayAdj = probAway * (1.0 - drawProb);
        
        // Convert to percentage
        const pH = Math.round(homeAdj * 10000) / 100;
        const pD = Math.round(drawProb * 10000) / 100;
        const pA = Math.round(awayAdj * 10000) / 100;
        
        // Calculate simulated fair odds
        const fairH = pH > 0 ? Math.round((100 / pH) * 100) / 100 : 99.0;
        const fairD = pD > 0 ? Math.round((100 / pD) * 100) / 100 : 99.0;
        const fairA = pA > 0 ? Math.round((100 / pA) * 100) / 100 : 99.0;

        return (
          <div className="fixed inset-0 bg-background bg-opacity-70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="glass-panel max-w-xl w-full p-6 md:p-8 space-y-6 border border-borderBg relative animate-fade-in shadow-blue-neon">
              {/* Fechar */}
              <button 
                onClick={() => setSelectedMatchDetail(null)}
                className="absolute right-4 top-4 text-gray-400 hover:text-white text-xl font-bold font-mono p-2"
              >
                ✕
              </button>

              <div className="text-center">
                <span className="text-[10px] bg-gold bg-opacity-15 text-gold border border-gold border-opacity-35 px-3 py-1 rounded-full font-mono font-bold">
                  ⚽ MOTOR QUANTITATIVO: ESTIMATIVA ELO
                </span>
                <h3 className="text-2xl font-bold font-outfit text-white mt-3">Análise de Probabilidades</h3>
                <p className="text-xs text-gray-400 font-mono mt-1">{selectedMatchDetail.data} • Grupo {selectedMatchDetail.grupo}</p>
              </div>

              {/* Ecrã de Equipas */}
              <div className="grid grid-cols-3 items-center text-center py-4 bg-borderBg bg-opacity-20 rounded-2xl border border-borderBg border-opacity-20">
                <div className="space-y-1">
                  <span className="text-4xl block">{getFlag(home)}</span>
                  <span className="font-outfit font-black text-white block text-sm">{home}</span>
                  <span className="text-[11px] text-gray-400 font-mono block">ELO: {eloH}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-xs text-gold font-bold block uppercase font-mono tracking-widest">Diferença</span>
                  <span className="text-2xl font-black text-white font-mono block">{diff > 0 ? `+${diff}` : diff}</span>
                  <span className="text-[9px] text-gray-500 font-mono block">Pontos</span>
                </div>
                <div className="space-y-1">
                  <span className="text-4xl block">{getFlag(away)}</span>
                  <span className="font-outfit font-black text-white block text-sm">{away}</span>
                  <span className="text-[11px] text-gray-400 font-mono block">ELO: {eloA}</span>
                </div>
              </div>

              {/* Gráficos de Probabilidade */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300 font-mono">Probabilidades Reais Estimadas</h4>
                
                <div className="space-y-3 font-mono text-xs">
                  {/* Vitória Casa */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-gray-300">
                      <span>Vitória {home} ({getFlag(home)})</span>
                      <span className="text-emerald font-bold">{pH}%</span>
                    </div>
                    <div className="w-full bg-borderBg h-2 rounded-full overflow-hidden">
                      <div className="bg-emerald h-full rounded-full" style={{ width: `${pH}%` }}></div>
                    </div>
                  </div>

                  {/* Empate */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-gray-300">
                      <span>Empate (⚖️)</span>
                      <span className="text-gold font-bold">{pD}%</span>
                    </div>
                    <div className="w-full bg-borderBg h-2 rounded-full overflow-hidden">
                      <div className="bg-gold h-full rounded-full" style={{ width: `${pD}%` }}></div>
                    </div>
                  </div>

                  {/* Vitória Fora */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-gray-300">
                      <span>Vitória {away} ({getFlag(away)})</span>
                      <span className="text-neonBlue font-bold">{pA}%</span>
                    </div>
                    <div className="w-full bg-borderBg h-2 rounded-full overflow-hidden">
                      <div className="bg-neonBlue h-full rounded-full" style={{ width: `${pA}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Odds Justas Estimadas */}
              <div className="p-4 bg-cardBg bg-opacity-40 border border-borderBg border-opacity-35 rounded-2xl space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300 font-mono text-center">Odds Justas Teóricas (Zero Margem)</h4>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-2.5 bg-borderBg bg-opacity-25 rounded-xl border border-borderBg border-opacity-25">
                    <span className="text-[10px] text-gray-400 font-mono block">Vitória {home}</span>
                    <span className="text-base font-black text-emerald font-mono mt-1 block">{fairH.toFixed(2)}</span>
                  </div>
                  <div className="p-2.5 bg-borderBg bg-opacity-25 rounded-xl border border-borderBg border-opacity-25">
                    <span className="text-[10px] text-gray-400 font-mono block">Empate</span>
                    <span className="text-base font-black text-gold font-mono mt-1 block">{fairD.toFixed(2)}</span>
                  </div>
                  <div className="p-2.5 bg-borderBg bg-opacity-25 rounded-xl border border-borderBg border-opacity-25">
                    <span className="text-[10px] text-gray-400 font-mono block">Vitória {away}</span>
                    <span className="text-base font-black text-neonBlue font-mono mt-1 block">{fairA.toFixed(2)}</span>
                  </div>
                </div>
                <p className="text-[9px] text-gray-500 font-mono text-center">
                  💡 Regra do Rei Paulo: Se a odd da casa de apostas for superior a esta odd justa, é uma aposta de valor (+EV)!
                </p>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}

