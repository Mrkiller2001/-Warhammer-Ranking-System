import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { gamesApi, campaignsApi } from '@/api/client'
import type { CreateCampaignRequest, Planet, NarrativeEvent } from '@/types/api'
import CampaignSolarSystem from '@/components/CampaignSolarSystem'

function CampaignsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState<any | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'system'>('list')
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

  const handleCampaignClick = (campaign: any) => {
    setSelectedCampaign(campaign)
    setViewMode('system')
  }

  const handlePlanetClick = (planet: Planet) => {
    console.log('Planet clicked:', planet)
    // Future: Show planet details or start a battle
  }

  // Load planets and narrative for selected campaign
  const { data: planets } = useQuery({
    queryKey: ['planets', selectedCampaign?.id],
    queryFn: async () => selectedCampaign ? (await campaignsApi.getPlanets(selectedCampaign.id)).data : [],
    enabled: !!selectedCampaign
  })

  const { data: narrative } = useQuery({
    queryKey: ['narrative', selectedCampaign?.id],
    queryFn: async () => selectedCampaign ? (await campaignsApi.getNarrative(selectedCampaign.id)).data : [],
    enabled: !!selectedCampaign
  })

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

      {selectedCampaign && viewMode === 'system' && planets && planets.length > 0 ? (
        <>
          <div className="card" style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2>{selectedCampaign.name}</h2>
                <p>{selectedCampaign.description || 'No description'}</p>
              </div>
              <button onClick={() => setViewMode('list')}>Back to List</button>
            </div>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <h2>Campaign Galaxy</h2>
            <p style={{ marginBottom: '20px', opacity: 0.8 }}>
              Each planet represents a battleground in this crusade. Click planets to view details.
            </p>
            <CampaignSolarSystem 
              campaignId={selectedCampaign.id}
              planets={planets} 
              onPlanetClick={handlePlanetClick}
            />
          </div>

          {narrative && narrative.length > 0 && (
            <div className="card" style={{ marginTop: '20px' }}>
              <h2>Campaign Narrative</h2>
              <div style={{ maxHeight: '400px', overflowY: 'auto', padding: '10px' }}>
                {narrative.map((event) => (
                  <div 
                    key={event.id} 
                    style={{ 
                      marginBottom: '20px', 
                      padding: '15px',
                      backgroundColor: event.event_type === 'campaign_start' ? '#1a1a2e' : '#2a2a3e',
                      borderRadius: '8px',
                      borderLeft: event.event_type === 'battle' ? '4px solid #e24a4a' : 
                                  event.event_type === 'conquest' ? '4px solid #4ae24a' : 
                                  '4px solid #4a90e2'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>{event.title}</h3>
                      <span style={{ fontSize: '12px', opacity: 0.6 }}>
                        {new Date(event.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p style={{ margin: '0', fontSize: '14px', whiteSpace: 'pre-line' }}>
                      {event.description}
                    </p>
                    <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.7, fontStyle: 'italic' }}>
                      {event.event_type === 'campaign_start' && '🌟 Campaign Beginning'}
                      {event.event_type === 'battle' && '⚔️ Battle Report'}
                      {event.event_type === 'conquest' && '🏆 Conquest Update'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : viewMode === 'list' ? (
        <>
          {campaigns && campaigns.length > 0 && (
            <div className="card">
              <h2>Active Campaigns</h2>
              <p style={{ marginBottom: '15px', opacity: 0.8 }}>
                Select a campaign to view its solar system and narrative.
              </p>
              <div style={{ display: 'grid', gap: '15px' }}>
                {campaigns.map((campaign) => (
                  <div 
                    key={campaign.id}
                    onClick={() => handleCampaignClick(campaign)}
                    style={{
                      padding: '20px',
                      backgroundColor: '#1a1a2e',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      border: '2px solid transparent',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.borderColor = '#4a90e2'}
                    onMouseLeave={(e) => e.currentTarget.style.borderColor = 'transparent'}
                  >
                    <h3 style={{ margin: '0 0 8px 0' }}>{campaign.name}</h3>
                    <p style={{ margin: '0 0 8px 0', opacity: 0.8 }}>
                      {campaign.description || 'No description'}
                    </p>
                    <div style={{ fontSize: '12px', opacity: 0.6 }}>
                      Started: {new Date(campaign.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {campaigns && campaigns.length === 0 && (
            <div className="card">
              <h2>No Active Campaigns</h2>
              <p>Create a new campaign to begin your crusade!</p>
            </div>
          )}
        </>
      ) : null}
    </div>
  )
}

export default CampaignsPage
