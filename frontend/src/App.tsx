import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import HomePage from './pages/HomePage'
import GamesPage from './pages/GamesPage'
import RankingsPage from './pages/RankingsPage'
import CampaignsPage from './pages/CampaignsPage'
import RecordMatchPage from './pages/RecordMatchPage'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="nav">
          <Link to="/">Home</Link>
          <Link to="/games">Games</Link>
          <Link to="/rankings">Rankings</Link>
          <Link to="/campaigns">Campaigns</Link>
          <Link to="/record-match">Record Match</Link>
        </nav>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/rankings" element={<RankingsPage />} />
          <Route path="/campaigns" element={<CampaignsPage />} />
          <Route path="/record-match" element={<RecordMatchPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
