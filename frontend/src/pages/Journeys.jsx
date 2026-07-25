import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, MapPin, Calendar, LogOut, Loader2, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import api from '../utils/api.js'
// Destination to currency map for automatic currency deduction
const destinationToCurrencyMap = {
  // Cities
  'bangkok': 'THB', 'phuket': 'THB', 'pattaya': 'THB', 'krabi': 'THB', 'chiang mai': 'THB',
  'singapore': 'SGD',
  'tokyo': 'JPY', 'osaka': 'JPY', 'kyoto': 'JPY', 'hiroshima': 'JPY',
  'london': 'GBP', 'manchester': 'GBP', 'edinburgh': 'GBP',
  'paris': 'EUR', 'rome': 'EUR', 'berlin': 'EUR', 'barcelona': 'EUR', 'madrid': 'EUR', 'amsterdam': 'EUR', 'munich': 'EUR', 'vienna': 'EUR', 'athens': 'EUR', 'dublin': 'EUR',
  'new york': 'USD', 'los angeles': 'USD', 'san francisco': 'USD', 'chicago': 'USD', 'miami': 'USD', 'las vegas': 'USD',
  'sydney': 'AUD', 'melbourne': 'AUD', 'brisbane': 'AUD',
  'toronto': 'CAD', 'vancouver': 'CAD', 'montreal': 'CAD',
  'mumbai': 'INR', 'delhi': 'INR', 'bangalore': 'INR', 'goa': 'INR',
  
  // Countries
  'thailand': 'THB',
  'japan': 'JPY',
  'united kingdom': 'GBP', 'uk': 'GBP', 'gb': 'GBP',
  'france': 'EUR', 'italy': 'EUR', 'germany': 'EUR', 'spain': 'EUR', 'netherlands': 'EUR', 'austria': 'EUR', 'greece': 'EUR', 'ireland': 'EUR', 'europe': 'EUR',
  'united states': 'USD', 'usa': 'USD', 'us': 'USD',
  'australia': 'AUD',
  'canada': 'CAD',
  'india': 'INR'
}

function detectCurrencies(destinationsStr, homeCurrency = 'INR') {
  const dests = destinationsStr.toLowerCase();
  const currencies = new Set();
  
  for (const [key, value] of Object.entries(destinationToCurrencyMap)) {
    if (dests.includes(key)) {
      currencies.add(value);
    }
  }
  
  if (currencies.size === 0) {
    currencies.add(homeCurrency);
  }
  
  return Array.from(currencies);
}

export default function Journeys() {
  const [pingStatus, setPingStatus] = useState('checking')
  const [journeys, setJourneys] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newJourney, setNewJourney] = useState({
    title: '',
    destinations: '',
    total_budget: '',
    start_date: '',
    end_date: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)

  const navigate = useNavigate()
  const { logout, user } = useAuth()

  // Fetch Journeys from Backend
  const fetchJourneys = async () => {
    try {
      setLoading(true)
      const res = await api.get('/api/journeys')
      setJourneys(res.data || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching journeys:', err)
      setError(err.message || 'Failed to load journeys. Please ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  // Handshake Ping on mount
  useEffect(() => {
    api.get('/api/ping')
      .then((res) => {
        // If using standard wrap
        const status = res.status === 'ok' ? 'ok' : res.data?.status || 'ok'
        if (status === 'ok') {
          setPingStatus('connected')
        } else {
          setPingStatus('error')
        }
      })
      .catch((err) => {
        console.error('Ping handshake error:', err)
        setPingStatus('disconnected')
      })
      
    fetchJourneys()
  }, [])

  // Handle Journey Submission
  const handleCreateJourney = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setSubmitError(null)

    // Form validation/parsing
    const destinationsArray = newJourney.destinations
      .split(',')
      .map((d) => d.trim())
      .filter(Boolean)

    if (destinationsArray.length === 0) {
      setSubmitError('Please specify at least one destination.')
      setSubmitting(false)
      return
    }
    
    // Automatically detect currencies based on input destinations
    const currenciesArray = detectCurrencies(newJourney.destinations, user?.home_currency || 'INR')

    try {
      await api.post('/api/journeys', {
        title: newJourney.title,
        destinations: destinationsArray,
        currencies: currenciesArray,
        total_budget: parseFloat(newJourney.total_budget),
        start_date: new Date(newJourney.start_date).toISOString(),
        end_date: new Date(newJourney.end_date).toISOString(),
      })

      // Reset form, close modal, reload list
      setNewJourney({
        title: '',
        destinations: '',
        total_budget: '',
        start_date: '',
        end_date: ''
      })
      setIsModalOpen(false)
      fetchJourneys()
    } catch (err) {
      console.error('Error creating journey:', err)
      setSubmitError(err.message || 'Failed to create journey. Please check inputs.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-[#f3f4f6] p-6 lg:p-10 relative overflow-hidden">
      <div className="absolute top-[-20%] right-[-20%] w-[50%] h-[50%] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="max-w-6xl mx-auto z-10 relative">
        {/* Top Navbar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10 pb-6 border-b border-gray-800">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-1">Your Journeys</h1>
            <p className="text-gray-400 text-sm">Select a trip to manage your expenses and budget pacing</p>
          </div>

          <div className="flex items-center gap-4">
            {/* Handshake connection status badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold glass">
              {pingStatus === 'checking' && (
                <>
                  <span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
                  <span className="text-yellow-500">Checking connection...</span>
                </>
              )}
              {pingStatus === 'connected' && (
                <>
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  <span className="text-green-500">Backend: Connected</span>
                </>
              )}
              {pingStatus === 'disconnected' && (
                <>
                  <span className="w-2 h-2 rounded-full bg-red-500"></span>
                  <span className="text-red-500">Backend: Offline</span>
                </>
              )}
              {pingStatus === 'error' && (
                <>
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                  <span className="text-red-500">Backend: Connection Error</span>
                </>
              )}
            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg flex items-center gap-2 shadow-lg shadow-brand-500/20 active:scale-[0.98] transition-all cursor-pointer font-semibold"
            >
              <Plus size={18} />
              <span>New Journey</span>
            </button>

            <button
              onClick={logout}
              className="px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/50 text-red-400 font-medium rounded-lg flex items-center gap-2 active:scale-[0.98] transition-all cursor-pointer"
            >
              <LogOut size={18} />
              <span>Log Out</span>
            </button>
          </div>
        </div>

        {/* Loading and Error States */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 text-brand-500 animate-spin mb-4" />
            <p className="text-gray-400 text-sm">Loading your journeys...</p>
          </div>
        ) : error ? (
          <div className="glass border-red-500/20 rounded-xl p-8 text-center max-w-md mx-auto">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Failed to load journeys</h3>
            <p className="text-gray-400 text-sm mb-6">{error}</p>
            <button
              onClick={fetchJourneys}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium text-sm transition-all"
            >
              Retry
            </button>
          </div>
        ) : journeys.length === 0 ? (
          <div className="glass border-gray-850 rounded-xl p-12 text-center max-w-md mx-auto">
            <MapPin className="w-12 h-12 text-brand-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">No Journeys Found</h3>
            <p className="text-gray-400 text-sm mb-6">Create your first journey to start tracking budgets, local currency rates, and split bills.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg inline-flex items-center gap-2 shadow-lg shadow-brand-500/20 transition-all cursor-pointer"
            >
              <Plus size={18} />
              <span>Create Journey</span>
            </button>
          </div>
        ) : (
          /* Journeys List */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fadeIn">
            {journeys.map((j) => {
              const formattedStartDate = new Date(j.start_date).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
              })
              const formattedEndDate = new Date(j.end_date).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
              })

              return (
                <div
                  key={j.id}
                  onClick={() => navigate(`/journeys/${j.id}`)}
                  className="glass rounded-xl p-6 hover:border-brand-500/30 transition-all cursor-pointer relative group flex flex-col justify-between h-48 border border-gray-850"
                >
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-white group-hover:text-brand-400 transition-colors line-clamp-1">{j.title}</h3>
                      <span className={`px-2 py-0.5 rounded text-2xs font-semibold uppercase ${j.is_active ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
                        {j.is_active ? 'Active' : 'Past'}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-gray-400 text-sm mb-3">
                      <MapPin size={14} className="text-brand-500 shrink-0" />
                      <span className="line-clamp-1">{j.destinations.join(' → ')}</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-4 border-t border-gray-800/60">
                    <div className="flex items-center gap-2 text-gray-400 text-xs">
                      <Calendar size={14} />
                      <span>{formattedStartDate} to {formattedEndDate}</span>
                    </div>

                    <div className="text-right">
                      <p className="text-2xs text-gray-500 uppercase font-semibold">Budget</p>
                      <p className="text-lg font-bold text-white">INR {j.total_budget.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Modern Glassmorphic Create Journey Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
          <div className="glass border border-gray-800 rounded-2xl w-full max-w-lg p-6 relative overflow-hidden shadow-2xl">
            {/* Top Glow Decor */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-500 to-indigo-500"></div>

            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">Create New Journey</h2>
              <button 
                onClick={() => setIsModalOpen(false)} 
                className="text-gray-400 hover:text-white transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            {submitError && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg text-sm mb-4 flex items-start gap-2 animate-shake">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{submitError}</span>
              </div>
            )}

            <form onSubmit={handleCreateJourney} className="space-y-4">
              <div>
                <label className="block text-gray-400 text-xs font-semibold uppercase mb-1">Trip Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Southeast Asia Adventure"
                  value={newJourney.title}
                  onChange={(e) => setNewJourney({ ...newJourney, title: e.target.value })}
                  className="w-full bg-gray-950/60 border border-gray-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 text-sm placeholder:text-gray-600 transition-colors"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-xs font-semibold uppercase mb-1">Destinations (comma separated)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bangkok, Singapore, Tokyo"
                  value={newJourney.destinations}
                  onChange={(e) => setNewJourney({ ...newJourney, destinations: e.target.value })}
                  className="w-full bg-gray-950/60 border border-gray-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 text-sm placeholder:text-gray-600 transition-colors"
                />
                <span className="text-2xs text-gray-500 mt-1 block">Currencies will be automatically detected (e.g. Bangkok → THB, Singapore → SGD).</span>
              </div>

              <div>
                <label className="block text-gray-400 text-xs font-semibold uppercase mb-1">Total Budget (INR)</label>
                <input
                  type="number"
                  required
                  min="1"
                  placeholder="e.g. 150000"
                  value={newJourney.total_budget}
                  onChange={(e) => setNewJourney({ ...newJourney, total_budget: e.target.value })}
                  className="w-full bg-gray-950/60 border border-gray-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 text-sm placeholder:text-gray-600 transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-xs font-semibold uppercase mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={newJourney.start_date}
                    onChange={(e) => setNewJourney({ ...newJourney, start_date: e.target.value })}
                    className="w-full bg-gray-950/60 border border-gray-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 text-sm transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-xs font-semibold uppercase mb-1">End Date</label>
                  <input
                    type="date"
                    required
                    value={newJourney.end_date}
                    onChange={(e) => setNewJourney({ ...newJourney, end_date: e.target.value })}
                    className="w-full bg-gray-950/60 border border-gray-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500 text-sm transition-colors"
                  />
                </div>
              </div>

              <div className="flex gap-3 justify-end pt-4 border-t border-gray-800/60 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-850 hover:bg-gray-800 hover:border-gray-700 text-gray-400 font-medium rounded-lg text-sm transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-brand-500 hover:bg-brand-600 disabled:bg-brand-700 text-white font-medium rounded-lg text-sm shadow-lg shadow-brand-500/20 transition-all flex items-center gap-2 cursor-pointer font-semibold"
                >
                  {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>{submitting ? 'Creating...' : 'Create Trip'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
