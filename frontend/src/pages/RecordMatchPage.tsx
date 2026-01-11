import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { gamesApi, playersApi, matchesApi } from '@/api/client'
import type { CreateMatchRequest } from '@/types/api'

function RecordMatchPage() {
  const queryClient = useQueryClient()
  const [selectedGameId, setSelectedGameId] = useState<number | null>(null)
  const [formData, setFormData] = useState<CreateMatchRequest>({
    game_id: 0,
    winner_discord_id: '',
    loser_discord_id: '',
    winner_score: undefined,
    loser_score: undefined,
    notes: '',
  })

  const { data: games } = useQuery({
    queryKey: ['games'],
    queryFn: async () => (await gamesApi.getAll()).data,
  })

  const { data: players } = useQuery({
    queryKey: ['players', selectedGameId],
    queryFn: async () => (await playersApi.getByGame(selectedGameId!)).data,
    enabled: !!selectedGameId,
  })

  const recordMutation = useMutation({
    mutationFn: (data: CreateMatchRequest) => matchesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] })
      queryClient.invalidateQueries({ queryKey: ['rankings'] })
      queryClient.invalidateQueries({ queryKey: ['players'] })
      alert('Match recorded successfully!')
      setFormData({
        game_id: selectedGameId || 0,
        winner_discord_id: '',
        loser_discord_id: '',
        winner_score: undefined,
        loser_score: undefined,
        notes: '',
      })
    },
  })

  const handleGameChange = (gameId: number) => {
    setSelectedGameId(gameId)
    setFormData({ ...formData, game_id: gameId })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.winner_discord_id === formData.loser_discord_id) {
      alert('Winner and loser must be different players')
      return
    }
    recordMutation.mutate(formData)
  }

  return (
    <div>
      <h1>Record Match</h1>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <label>
            Game
            <select
              value={selectedGameId || ''}
              onChange={(e) => handleGameChange(Number(e.target.value))}
              required
            >
              <option value="">-- Select a game --</option>
              {games?.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.display_name}
                </option>
              ))}
            </select>
          </label>

          {selectedGameId && players && (
            <>
              <label>
                Winner
                <select
                  value={formData.winner_discord_id}
                  onChange={(e) => setFormData({ ...formData, winner_discord_id: e.target.value })}
                  required
                >
                  <option value="">-- Select winner --</option>
                  {players.map((player) => (
                    <option key={player.discord_id} value={player.discord_id}>
                      {player.discord_name} (Rating: {Math.round(player.rating)})
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Loser
                <select
                  value={formData.loser_discord_id}
                  onChange={(e) => setFormData({ ...formData, loser_discord_id: e.target.value })}
                  required
                >
                  <option value="">-- Select loser --</option>
                  {players.map((player) => (
                    <option key={player.discord_id} value={player.discord_id}>
                      {player.discord_name} (Rating: {Math.round(player.rating)})
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Winner Score (optional)
                <input
                  type="number"
                  value={formData.winner_score || ''}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    winner_score: e.target.value ? Number(e.target.value) : undefined 
                  })}
                  min="0"
                />
              </label>

              <label>
                Loser Score (optional)
                <input
                  type="number"
                  value={formData.loser_score || ''}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    loser_score: e.target.value ? Number(e.target.value) : undefined 
                  })}
                  min="0"
                />
              </label>

              <label>
                Notes (optional)
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                />
              </label>

              <button type="submit" disabled={recordMutation.isPending}>
                {recordMutation.isPending ? 'Recording...' : 'Record Match'}
              </button>
            </>
          )}
        </form>
      </div>
    </div>
  )
}

export default RecordMatchPage
