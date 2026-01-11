import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { gamesApi, campaignsApi } from '@/api/client'
import type { CreateCampaignRequest } from '@/types/api'

function CampaignsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateCampaignRequest>({
    name: '',
    description: '',
    game_id: 0,
  })

  const { data: games } = useQuery({
    queryKey: ['games'],
    queryFn: async () => (await gamesApi.getAll()).data,
  })

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns', 'active'],
    queryFn: async () => (await campaignsApi.getActive()).data,
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateCampaignRequest) => campaignsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      setShowForm(false)
      setFormData({ name: '', description: '', game_id: 0 })
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
        <h1>Campaigns</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Create Campaign'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2>Create New Campaign</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Campaign Name
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </label>
            <label>
              Description
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </label>
            <label>
              Game
              <select
                value={formData.game_id}
                onChange={(e) => setFormData({ ...formData, game_id: Number(e.target.value) })}
                required
              >
                <option value={0}>-- Select a game --</option>
                {games?.map((game) => (
                  <option key={game.id} value={game.id}>
                    {game.display_name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Campaign'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Active Campaigns</h2>
        {campaigns && campaigns.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Started</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td><strong>{campaign.name}</strong></td>
                  <td>{campaign.description || 'No description'}</td>
                  <td>{new Date(campaign.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No active campaigns</p>
        )}
      </div>
    </div>
  )
}

export default CampaignsPage
