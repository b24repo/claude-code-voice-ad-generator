'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Campaign {
  id: string
  name: string
  product: string
  tone: string
  createdAt: string
  adCount: number
  totalTokens: number
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchCampaigns()
  }, [])

  async function fetchCampaigns() {
    try {
      setLoading(true)
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/campaigns`
      )
      if (!response.ok) throw new Error('Failed to fetch campaigns')
      const data = await response.json()
      setCampaigns(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Campaigns</h1>
            <p className="text-slate-600 mt-2">Manage your voice ad campaigns</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
          >
            {showForm ? 'Cancel' : 'New Campaign'}
          </button>
        </div>

        {showForm && (
          <CreateCampaignForm
            onSuccess={() => {
              setShowForm(false)
              fetchCampaigns()
            }}
          />
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-slate-200 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-5xl mb-4">📭</div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              No campaigns yet
            </h3>
            <p className="text-slate-600 mb-6">
              Create your first campaign to get started generating voice ads
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
            >
              Create Campaign
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign) => (
              <Link key={campaign.id} href={`/campaigns/${campaign.id}`}>
                <div className="p-6 bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-lg transition cursor-pointer">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {campaign.name}
                      </h3>
                      <p className="text-sm text-slate-600">{campaign.product}</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {campaign.tone}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">
                        Ads
                      </p>
                      <p className="text-2xl font-bold text-slate-900">
                        {campaign.adCount}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide">
                        Tokens Used
                      </p>
                      <p className="text-2xl font-bold text-slate-900">
                        {campaign.totalTokens.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Created {formatDate(campaign.createdAt)}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface CreateCampaignFormProps {
  onSuccess: () => void
}

function CreateCampaignForm({ onSuccess }: CreateCampaignFormProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const formData = new FormData(e.currentTarget)
    const data = {
      name: formData.get('name'),
      product: formData.get('product'),
      tone: formData.get('tone'),
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/campaigns`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        }
      )

      if (!response.ok) {
        throw new Error(await response.text())
      }

      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="p-6 bg-white rounded-lg border border-slate-200 mb-8"
    >
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        Create New Campaign
      </h2>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Campaign Name
          </label>
          <input
            type="text"
            name="name"
            required
            placeholder="e.g., Summer 2024 Campaign"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Product/Service
          </label>
          <input
            type="text"
            name="product"
            required
            placeholder="e.g., Premium Coffee"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Brand Tone
          </label>
          <select
            name="tone"
            required
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="energetic">Energetic</option>
            <option value="luxury">Luxury</option>
            <option value="playful">Playful</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Campaign'}
      </button>
    </form>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}