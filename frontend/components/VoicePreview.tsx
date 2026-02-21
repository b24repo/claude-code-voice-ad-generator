'use client'

import { useState, useEffect } from 'react'

interface VoicePreviewProps {
  campaignId: string
  adId: string
}

interface VoiceOption {
  voiceId: string
  name: string
  description: string
}

export default function VoicePreview({
  campaignId,
  adId,
}: VoicePreviewProps) {
  const [selectedVoice, setSelectedVoice] = useState('alloy')
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const voices: VoiceOption[] = [
    { voiceId: 'alloy', name: 'Alloy', description: 'Neutral, clear' },
    { voiceId: 'echo', name: 'Echo', description: 'Warm, friendly' },
    { voiceId: 'fable', name: 'Fable', description: 'Energetic, young' },
    { voiceId: 'onyx', name: 'Onyx', description: 'Deep, professional' },
    { voiceId: 'nova', name: 'Nova', description: 'Bright, modern' },
  ]

  async function synthesizeVoice() {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/campaigns/${campaignId}/ads/${adId}/voice`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            voice_id: selectedVoice,
          }),
        }
      )

      if (!response.ok) {
        throw new Error('Failed to synthesize voice')
      }

      const data = await response.json()
      setAudioUrl(data.audio_url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <h3 className="font-semibold text-slate-900 mb-4">Voice Synthesis</h3>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg mb-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-4 mb-6">
        <label className="block text-sm font-medium text-slate-900">
          Select Voice
        </label>
        <div className="grid grid-cols-2 gap-2">
          {voices.map((voice) => (
            <button
              key={voice.voiceId}
              onClick={() => setSelectedVoice(voice.voiceId)}
              className={`p-3 rounded-lg border text-left transition ${
                selectedVoice === voice.voiceId
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-200 bg-white hover:border-blue-300'
              }`}
            >
              <div className="font-medium text-sm text-slate-900">
                {voice.name}
              </div>
              <div className="text-xs text-slate-500">
                {voice.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={synthesizeVoice}
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 mb-4"
      >
        {loading ? 'Synthesizing...' : 'Generate Voice'}
      </button>

      {audioUrl && (
        <div className="bg-slate-50 rounded-lg p-4">
          <p className="text-sm font-medium text-slate-900 mb-3">
            Preview
          </p>
          <audio
            src={audioUrl}
            controls
            className="w-full"
          />
          <a
            href={audioUrl}
            download
            className="mt-3 inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Audio
          </a>
        </div>
      )}

      <p className="text-xs text-slate-500 mt-4">
        Powered by ElevenLabs • Natural voice synthesis
      </p>
    </div>
  )
}