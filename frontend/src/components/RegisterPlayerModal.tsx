import React, { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { playersApi } from '@/api/client'

interface RegisterPlayerModalProps {
  campaignId: number
  gameId: number
  onClose: () => void
}

const RegisterPlayerModal: React.FC<RegisterPlayerModalProps> = ({
  gameId,
  onClose,
}) => {
  const queryClient = useQueryClient()
  const [discordId, setDiscordId] = useState('')
  const [discordName, setDiscordName] = useState('')

  const { data: existingPlayers } = useQuery({
    queryKey: ['players', gameId],
    queryFn: async () => (await playersApi.getByGame(gameId)).data,
  })

  const registerMutation = useMutation({
    mutationFn: async () => {
      const response = await playersApi.create({
        discord_id: discordId,
        discord_name: discordName,
        game_id: gameId,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['players', gameId] })
      setDiscordId('')
      setDiscordName('')
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    registerMutation.mutate()
  }

  const playerExists = existingPlayers?.some((p) => p.discord_id === discordId)

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
          maxWidth: '500px',
          width: '100%',
          border: '2px solid #4caf50',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            background: 'linear-gradient(135deg, #4caf5022 0%, #4caf5044 100%)',
            padding: '24px',
            borderBottom: '2px solid #4caf50',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0, fontSize: '24px', color: '#4caf50' }}>
              👤 Register Player
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
          <div style={{ marginBottom: '20px', padding: '12px', backgroundColor: 'rgba(74, 144, 226, 0.2)', borderRadius: '8px', fontSize: '13px' }}>
            <strong>Note:</strong> Players need to be registered before they can participate in campaign battles. 
            You can find Discord IDs by right-clicking on a user in Discord with Developer Mode enabled.
          </div>

          <label style={{ display: 'block', marginBottom: '20px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Discord Username
            </div>
            <input
              type="text"
              value={discordName}
              onChange={(e) => setDiscordName(e.target.value)}
              placeholder="e.g., CommanderDante#1234"
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

          <label style={{ display: 'block', marginBottom: '24px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
              Discord ID
            </div>
            <input
              type="text"
              value={discordId}
              onChange={(e) => setDiscordId(e.target.value)}
              placeholder="e.g., 123456789012345678"
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: playerExists ? '2px solid #ff9800' : '1px solid #333',
                backgroundColor: '#2a2a3e',
                color: 'white',
                fontSize: '14px',
              }}
            />
            {playerExists && (
              <div style={{ marginTop: '8px', color: '#ff9800', fontSize: '12px' }}>
                ⚠️ This player is already registered for this game.
              </div>
            )}
          </label>

          {registerMutation.isError && (
            <div
              style={{
                padding: '12px',
                backgroundColor: 'rgba(244, 67, 54, 0.2)',
                border: '1px solid #f44336',
                borderRadius: '8px',
                marginBottom: '16px',
                color: '#f44336',
                fontSize: '13px',
              }}
            >
              Error registering player. They may already be registered or there was a server error.
            </div>
          )}

          {/* Existing Players */}
          {existingPlayers && existingPlayers.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px', opacity: 0.7 }}>
                Registered Players ({existingPlayers.length})
              </div>
              <div
                style={{
                  maxHeight: '150px',
                  overflowY: 'auto',
                  backgroundColor: 'rgba(0, 0, 0, 0.2)',
                  borderRadius: '8px',
                  padding: '8px',
                }}
              >
                {existingPlayers.map((player) => (
                  <div
                    key={player.id}
                    style={{
                      padding: '8px',
                      marginBottom: '4px',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: '4px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      fontSize: '13px',
                    }}
                  >
                    <span>{player.discord_name}</span>
                    <span style={{ opacity: 0.6, fontSize: '11px' }}>
                      {player.matches_played} battles
                    </span>
                  </div>
                ))}
              </div>
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
              disabled={registerMutation.isPending || playerExists}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: playerExists ? '#666' : '#4caf50',
                color: 'white',
                fontSize: '14px',
                fontWeight: 'bold',
                cursor: registerMutation.isPending || playerExists ? 'not-allowed' : 'pointer',
                opacity: registerMutation.isPending || playerExists ? 0.6 : 1,
              }}
            >
              {registerMutation.isPending ? 'Registering...' : '👤 Register Player'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RegisterPlayerModal
