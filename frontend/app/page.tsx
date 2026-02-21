import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-slate-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-slate-900 mb-6">
              AI-Powered Voice Ad Generation
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
              Create professional voice advertisements in minutes, not days.
              Powered by Claude AI and ElevenLabs voice synthesis.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/campaigns"
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Get Started
              </Link>
              <a
                href="https://github.com/b24repo/claude-code-voice-ad-generator"
                className="px-8 py-3 bg-slate-200 text-slate-900 font-semibold rounded-lg hover:bg-slate-300 transition"
              >
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">
            Why Voice Ads?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon="⚡"
              title="Lightning Fast"
              description="Generate complete ad copy and voice in under 2 minutes. What used to take days now takes minutes."
            />
            <FeatureCard
              icon="🤖"
              title="AI-Powered Copy"
              description="Claude AI understands your brand voice and generates compelling, on-brand ad copy automatically."
            />
            <FeatureCard
              icon="🎯"
              title="Cost Optimized"
              description="Smart model selection and response caching reduce API costs by 60% compared to naive approaches."
            />
            <FeatureCard
              icon="🔊"
              title="Natural Voices"
              description="Choose from dozens of natural-sounding voices powered by ElevenLabs. No robotic sound."
            />
            <FeatureCard
              icon="📊"
              title="Campaign Management"
              description="Organize multiple campaigns, track variants, and analyze performance all in one place."
            />
            <FeatureCard
              icon="💰"
              title="Transparent Pricing"
              description="Real-time cost tracking shows exactly what each ad generation costs. No surprises."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <Step
              number="1"
              title="Create Campaign"
              description="Define your product, brand voice, and target audience"
            />
            <Step
              number="2"
              title="Generate Ad Copy"
              description="Claude AI generates multiple ad variations in seconds"
            />
            <Step
              number="3"
              title="Preview Voices"
              description="Listen to natural voice renditions of your ad copy"
            />
            <Step
              number="4"
              title="Launch & Track"
              description="Download, edit, and deploy your voice ads to your platform"
            />
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">
            Built with Modern Tech
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <TechBadge name="Next.js 14" />
            <TechBadge name="FastAPI" />
            <TechBadge name="Claude API" />
            <TechBadge name="PostgreSQL" />
            <TechBadge name="Docker" />
            <TechBadge name="ElevenLabs" />
            <TechBadge name="TypeScript" />
            <TechBadge name="TailwindCSS" />
          </div>
          <p className="text-center text-slate-600 mt-8">
            Built with Claude Code - demonstrating AI-assisted full-stack development
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Ad Production?
          </h2>
          <p className="text-blue-100 mb-8">
            Join teams using AI to create ads 10x faster.
          </p>
          <Link
            href="/campaigns"
            className="inline-block px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition"
          >
            Start Creating Ads Free
          </Link>
        </div>
      </section>
    </div>
  )
}

interface FeatureCardProps {
  icon: string
  title: string
  description: string
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="p-6 rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-lg transition">
      <div className="text-3xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}

interface StepProps {
  number: string
  title: string
  description: string
}

function Step({ number, title, description }: StepProps) {
  return (
    <div className="relative">
      <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-lg font-bold mb-4">
        {number}
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
      {number !== '4' && (
        <div className="hidden md:block absolute top-6 left-12 w-full h-0.5 bg-gradient-to-r from-blue-600 to-transparent" />
      )}
    </div>
  )
}

interface TechBadgeProps {
  name: string
}

function TechBadge({ name }: TechBadgeProps) {
  return (
    <div className="p-4 bg-slate-100 rounded-lg text-center">
      <p className="font-semibold text-slate-900">{name}</p>
    </div>
  )
}