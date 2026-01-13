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
  narrative_seed: number;
  is_active: boolean;
  created_at: string;
  ended_at: string | null;
}

export interface Planet {
  id: number;
  campaign_id: number;
  name: string;
  planet_type: string;
  position: number;
  color: string;
  size: number;
  description: string;
  strategic_value: string;
  games_played: number;
  is_contested: boolean;
  current_controller: string | null;
  created_at: string;
}

export interface NarrativeEvent {
  id: number;
  campaign_id: number;
  event_type: string;
  title: string;
  description: string;
  planet_id: number | null;
  game_id: number | null;
  created_at: string;
}

export interface CampaignGame {
  id: number;
  campaign_id: number;
  planet_id: number;
  attacker_id: number;
  defender_id: number;
  attacker_score: number;
  defender_score: number;
  attacker_req: number;
  defender_req: number;
  winner_id: number | null;
  mission_type: string;
  notes: string | null;
  played_at: string;
  attacker_name: string;
  defender_name: string;
  winner_name: string | null;
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
