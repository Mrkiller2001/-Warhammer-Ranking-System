import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { gamesApi } from '@/api/client'
import type { CreateGameRequest } from '@/types/api'

function GamesPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateGameRequest>({
    name: '',
    display_name: '',
  })

  const { data: games, isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: async () => (await gamesApi.getAll()).data,
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateGameRequest) => gamesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['games'] })
      setShowForm(false)
      setFormData({ name: '', display_name: '' })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Games</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Game'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2>Create New Game</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Internal Name (lowercase, no spaces)
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                pattern="[a-z0-9-]+"
              />
            </label>
            <label>
              Display Name
              <input
                type="text"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                required
              />
            </label>
            <button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Game'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>All Games</h2>
        <table>
          <thead>
            <tr>
              <th>Display Name</th>
              <th>Internal Name</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {games?.map((game) => (
              <tr key={game.id}>
                <td><strong>{game.display_name}</strong></td>
                <td>{game.name}</td>
                <td>{new Date(game.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default GamesPage
