/**
 * API client for backend communication
 */

import axios from 'axios';
import type {
  Game,
  Player,
  Match,
  Campaign,
  Planet,
  NarrativeEvent,
  Rankings,
  CreateGameRequest,
  CreatePlayerRequest,
  CreateMatchRequest,
  CreateCampaignRequest,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Games API
export const gamesApi = {
  getAll: () => apiClient.get<Game[]>('/games'),
  getById: (id: number) => apiClient.get<Game>(`/games/${id}`),
  getByName: (name: string) => apiClient.get<Game>(`/games/name/${name}`),
  create: (data: CreateGameRequest) => apiClient.post<Game>('/games', data),
};

// Players API
export const playersApi = {
  getById: (id: number) => apiClient.get<Player>(`/players/${id}`),
  getByDiscordId: (discordId: string, gameId: number) =>
    apiClient.get<Player>(`/players/discord/${discordId}/game/${gameId}`),
  getByGame: (gameId: number) => apiClient.get<Player[]>(`/players/game/${gameId}`),
  create: (data: CreatePlayerRequest) => apiClient.post<Player>('/players', data),
};

// Matches API
export const matchesApi = {
  getByGame: (gameId: number, limit: number = 50) =>
    apiClient.get<Match[]>(`/matches/game/${gameId}`, { params: { limit } }),
  create: (data: CreateMatchRequest) => apiClient.post<Match>('/matches', data),
};

// Campaigns API
export const campaignsApi = {
  getById: (id: number) => apiClient.get<Campaign>(`/campaigns/${id}`),
  getActive: () => apiClient.get<Campaign[]>('/campaigns/active'),
  create: (data: CreateCampaignRequest) => apiClient.post<Campaign>('/campaigns', data),
  update: (id: number, data: Partial<Campaign>) =>
    apiClient.patch<Campaign>(`/campaigns/${id}`, data),
  getPlanets: (campaignId: number) => apiClient.get<Planet[]>(`/campaigns/${campaignId}/planets`),
  getNarrative: (campaignId: number) => apiClient.get<NarrativeEvent[]>(`/campaigns/${campaignId}/narrative`),
};

// Rankings API
export const rankingsApi = {
  getByGame: (gameId: number) => apiClient.get<Rankings>(`/rankings/game/${gameId}`),
};

export default apiClient;
