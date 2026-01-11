import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { gamesApi, rankingsApi } from '@/api/client'

function RankingsPage() {
  const [selectedGameId, setSelectedGameId] = useState<number | null>(null)

  const { data: games } = useQuery({
    queryKey: ['games'],
    queryFn: async () => (await gamesApi.getAll()).data,
  })

  const { data: rankings, isLoading } = useQuery({
    queryKey: ['rankings', selectedGameId],
    queryFn: async () => (await rankingsApi.getByGame(selectedGameId!)).data,
    enabled: !!selectedGameId,
  })

  return (
    <div>
      <h1>Rankings</h1>

      <div className="card">
        <label>
          Select Game
          <select
            value={selectedGameId || ''}
            onChange={(e) => setSelectedGameId(Number(e.target.value))}
          >
            <option value="">-- Select a game --</option>
            {games?.map((game) => (
              <option key={game.id} value={game.id}>
                {game.display_name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {isLoading && <div>Loading rankings...</div>}

      {rankings && (
        <div className="card">
          <h2>{rankings.game_name} Rankings</h2>
          <p>Total Players: {rankings.total_players}</p>
          
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Rating</th>
                <th>RD</th>
                <th>Matches</th>
                <th>W-L</th>
                <th>Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {rankings.rankings.map((entry) => (
                <tr key={entry.discord_id}>
                  <td><strong>#{entry.rank}</strong></td>
                  <td>{entry.discord_name}</td>
                  <td><strong>{Math.round(entry.rating)}</strong></td>
                  <td>{Math.round(entry.rating_deviation)}</td>
                  <td>{entry.matches_played}</td>
                  <td>{entry.wins}-{entry.losses}</td>
                  <td>{entry.win_rate.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default RankingsPage
