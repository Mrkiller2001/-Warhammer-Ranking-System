import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { gamesApi, campaignsApi } from '@/api/client'

function HomePage() {
  const { data: games } = useQuery({
    queryKey: ['games'],
    queryFn: async () => (await gamesApi.getAll()).data,
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns', 'active'],
    queryFn: async () => (await campaignsApi.getActive()).data,
  })

  return (
    <div>
      <h1>Warhammer Ranking System</h1>
      
      <div className="card">
        <h2>Welcome</h2>
        <p>
          Track your Warhammer games, manage campaigns, and view player rankings
          using the Glicko-2 rating system.
        </p>
      </div>

      <div className="card">
        <h2>Active Games ({games?.length || 0})</h2>
        {games?.map((game) => (
          <div key={game.id} style={{ marginBottom: '0.5rem' }}>
            <strong>{game.display_name}</strong>
          </div>
        ))}
      </div>

      <div className="card">
        <h2>Active Campaigns ({campaigns?.length || 0})</h2>
        {campaigns?.map((campaign) => (
          <div key={campaign.id} style={{ marginBottom: '0.5rem' }}>
            <strong>{campaign.name}</strong>
            {campaign.description && <p>{campaign.description}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}

export default HomePage
