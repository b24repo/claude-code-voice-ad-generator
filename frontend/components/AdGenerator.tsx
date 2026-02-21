'use client'

import { useState } from 'react'

interface AdGeneratorProps {
  campaignId: string
  productName: string
  brandTone: string
  onAdGenerated: () => void
}

export default function AdGenerator({
  campaignId,
  productName,
  brandTone,
  onAdGenerated,
}: AdGeneratorProps) {
  const [duration, setDuration] = useState(30)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null)

  async function handleGenerate() {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/campaigns/${campaignId}/ads/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product: productName,
            duration,
            tone: brandTone,
          }),
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to generate ad')
      }

      const data = await response.json()
      setEstimatedCost(data.cost)
      onAdGenerated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Generate Ad Copy</h2>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Product/Service
          </label>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-slate-700">{productName}</p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Brand Tone
          </label>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-slate-700 capitalize">{brandTone}</p>
          </div>
        </div>

        <div>
          <label htmlFor="duration" className="block text-sm font-medium text-slate-900 mb-2">
            Duration: {duration} seconds
          </label>
          <input
            id="duration"
            type="range"
            min="15"
            max="60"
            step="5"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>15s (social)</span>
            <span>30s (standard)</span>
            <span>60s (long form)</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Number of Variations
          </label>
          <select
            defaultValue="3"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="1">1 variation</option>
            <option value="2">2 variations</option>
            <option value="3">3 variations</option>
            <option value="5">5 variations</option>
          </select>
        </div>
      </div>

      {estimatedCost !== null && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg mb-6">
          <p className="text-sm text-green-800">
            Ad generated successfully! Cost: ${estimatedCost.toFixed(3)}
          </p>
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Generating...
          </span>
        ) : (
          'Generate Ad Copy'
        )}
      </button>

      <p className="text-xs text-slate-500 mt-4 text-center">
        Powered by Claude AI • Token usage tracked automatically
      </p>
    </div>
  )
}