/**
 * API types matching backend models
 */

export interface Game {
  id: number;
  name: string;
  display_name: string;
  created_at: string;
}

export interface Player {
  id: number;
  discord_id: string;
  discord_name: string;
  game_id: number;
  rating: number;
  rating_deviation: number;
  volatility: number;
  matches_played: number;
  wins: number;
  losses: number;
  last_match_date: string | null;
  created_at: string;
}

export interface Match {
  id: number;
  game_id: number;
  winner_id: number;
  loser_id: number;
  winner_score: number | null;
  loser_score: number | null;
  notes: string | null;
  played_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description: string | null;
  game_id: number;
  is_active: boolean;
  created_at: string;
  ended_at: string | null;
}

export interface RankingEntry {
  rank: number;
  discord_id: string;
  discord_name: string;
  rating: number;
  rating_deviation: number;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
}

export interface Rankings {
  game_id: number;
  game_name: string;
  rankings: RankingEntry[];
  total_players: number;
  generated_at: string;
}

// Request types
export interface CreateGameRequest {
  name: string;
  display_name: string;
}

export interface CreatePlayerRequest {
  discord_id: string;
  discord_name: string;
  game_id: number;
}

export interface CreateMatchRequest {
  game_id: number;
  winner_discord_id: string;
  loser_discord_id: string;
  winner_score?: number;
  loser_score?: number;
  notes?: string;
}

export interface CreateCampaignRequest {
  name: string;
  description?: string;
  game_id: number;
}
