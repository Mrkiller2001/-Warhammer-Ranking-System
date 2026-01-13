import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { campaignsApi, playersApi } from '@/api/client'
import type { Planet } from '@/types/api'

interface RecordCampaignGameModalProps {
  campaignId: number
  gameId: number
  planets: Planet[]
  onClose: () => void
}

interface CampaignGameForm {
  planet_id: number
  attacker_discord_id: string
  defender_discord_id: string
  attacker_score: number
  defender_score: number
  mission_type: string
  notes: string
}

const RecordCampaignGameModal: React.FC<RecordCampaignGameModalProps> = ({
  campaignId,
  gameId,
  planets,
  onClose,
}) => {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<CampaignGameForm>({
    planet_id: planets[0]?.id || 0,
    attacker_discord_id: '',
    defender_discord_id: '',
    attacker_score: 0,
    defender_score: 0,
    mission_type: 'standard',
    notes: '',
  })

  // Get players for the game
  const { data: players } = useQuery({
    queryKey: ['players', gameId],
    queryFn: async () => (await playersApi.getByGame(gameId)).data,
  })

  const recordGameMutation = useMutation({
    mutationFn: async (data: CampaignGameForm) => {
      const response = await campaignsApi.recordGame({
        campaign_id: campaignId,
        planet_id: data.planet_id,
        attacker_discord_id: data.attacker_discord_id,
        defender_discord_id: data.defender_discord_id,
        attacker_score: data.attacker_score,
        defender_score: data.defender_score,
        mission_type: data.mission_type,
        notes: data.notes,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planets'] })
      queryClient.invalidateQueries({ queryKey: ['planetGames'] })
      queryClient.invalidateQueries({ queryKey: ['narrative'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    recordGameMutation.mutate(formData)
  }

  const selectedPlanet = planets.find((p) => p.id === formData.planet_id)

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#1a1a2e',
          borderRadius: '12px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          border: '2px solid #4a90e2',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            background: 'linear-gradient(135deg, #4a90e222 0%, #4a90e244 100%)',
            padding: '24px',
            borderBottom: '2px solid #4a90e2',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0, fontSize: '24px', color: '#4a90e2' }}>
              ⚔️ Record Campaign Battle
            </h2>
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontSize: '24px',
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
          {/* Planet Selection */}
          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Battlefield Planet
            </div>
            <select
              value={formData.planet_id}
              onChange={(e) =>
                setFormData({ ...formData, planet_id: Number(e.target.value) })
              }
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
              }}
            >
              {planets.map((planet) => (
                <option key={planet.id} value={planet.id}>
                  {planet.name} - {planet.planet_type} ({planet.games_played} battles)
                </option>
              ))}
            </select>
            {selectedPlanet && (
              <div
                style={{
                  marginTop: '8px',
                  padding: '8px',
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  borderRadius: '6px',
                  fontSize: '12px',
                  opacity: 0.8,
                  borderLeft: `3px solid ${selectedPlanet.color}`,
                }}
              >
                {selectedPlanet.description}
              </div>
            )}
          </label>

          {/* Attacker */}
          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              ⚔️ Attacker
            </div>
            <select
              value={formData.attacker_discord_id}
              onChange={(e) =>
                setFormData({ ...formData, attacker_discord_id: e.target.value })
              }
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
              }}
            >
              <option value="">-- Select Attacker --</option>
              {players?.map((player) => (
                <option key={player.id} value={player.discord_id}>
                  {player.discord_name} (Rating: {Math.round(player.rating)})
                </option>
              ))}
            </select>
          </label>

          {/* Defender */}
          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              🛡️ Defender
            </div>
            <select
              value={formData.defender_discord_id}
              onChange={(e) =>
                setFormData({ ...formData, defender_discord_id: e.target.value })
              }
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
              }}
            >
              <option value="">-- Select Defender --</option>
              {players?.map((player) => (
                <option key={player.id} value={player.discord_id}>
                  {player.discord_name} (Rating: {Math.round(player.rating)})
                </option>
              ))}
            </select>
          </label>

          {/* Scores */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <label style={{ display: 'block' }}>
              <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
                Attacker Score
              </div>
              <input
                type="number"
                min="0"
                value={formData.attacker_score}
                onChange={(e) =>
                  setFormData({ ...formData, attacker_score: Number(e.target.value) })
                }
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #333',
                  backgroundColor: '#2a2a3e',
                  color: 'white',
                  fontSize: '14px',
                }}
              />
            </label>

            <label style={{ display: 'block' }}>
              <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
                Defender Score
              </div>
              <input
                type="number"
                min="0"
                value={formData.defender_score}
                onChange={(e) =>
                  setFormData({ ...formData, defender_score: Number(e.target.value) })
                }
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #333',
                  backgroundColor: '#2a2a3e',
                  color: 'white',
                  fontSize: '14px',
                }}
              />
            </label>
          </div>

          {/* Mission Type */}
          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Mission Type
            </div>
            <select
              value={formData.mission_type}
              onChange={(e) =>
                setFormData({ ...formData, mission_type: e.target.value })
              }
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
              }}
            >
              <option value="standard">Standard Mission</option>
              <option value="secure">Secure Objective</option>
              <option value="assassinate">Assassinate</option>
              <option value="raid">Raid</option>
              <option value="breakthrough">Breakthrough</option>
              <option value="conquest">Conquest</option>
            </select>
          </label>

          {/* Notes */}
          <label style={{ display: 'block', marginBottom: '24px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Battle Notes (Optional)
            </div>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              placeholder="Describe key moments, heroic actions, or narrative details..."
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
                resize: 'vertical',
              }}
            />
          </label>

          {recordGameMutation.isError && (
            <div
              style={{
                padding: '12px',
                backgroundColor: 'rgba(244, 67, 54, 0.2)',
                border: '1px solid #f44336',
                borderRadius: '8px',
                marginBottom: '16px',
                color: '#f44336',
              }}
            >
              Error recording battle. Please try again.
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: '1px solid #333',
                backgroundColor: 'transparent',
                color: 'white',
                fontSize: '14px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={recordGameMutation.isPending}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: '#4a90e2',
                color: 'white',
                fontSize: '14px',
                fontWeight: 'bold',
                cursor: recordGameMutation.isPending ? 'not-allowed' : 'pointer',
                opacity: recordGameMutation.isPending ? 0.6 : 1,
              }}
            >
              {recordGameMutation.isPending ? 'Recording...' : '⚔️ Record Battle'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RecordCampaignGameModal
