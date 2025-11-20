import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 text-center">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gradient">
            Aura Audit AI
          </h1>
          <p className="mt-4 text-xl text-muted-foreground">
            Next-Generation Audit Platform Powered by AI
          </p>
        </div>

        {/* Features Grid */}
        <div className="mx-auto mt-12 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <FeatureCard
            title="Analytics"
            description="ML-powered journal entry testing and anomaly detection"
            icon="📊"
          />
          <FeatureCard
            title="Smart Mapping"
            description="AI-driven trial balance account normalization"
            icon="🎯"
          />
          <FeatureCard
            title="Quality Control"
            description="Automated compliance checks for PCAOB & AICPA standards"
            icon="✅"
          />
          <FeatureCard
            title="Engagement Management"
            description="Streamlined workflow for audit engagements"
            icon="📁"
          />
          <FeatureCard
            title="Real-time Collaboration"
            description="Team collaboration with live updates"
            icon="👥"
          />
          <FeatureCard
            title="Comprehensive Reports"
            description="Beautiful, compliant audit documentation"
            icon="📝"
          />
        </div>

        {/* CTA */}
        <div className="mt-12 flex justify-center gap-4">
          <Link
            href="/login"
            className="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-3 font-semibold text-white shadow-lg transition-all hover:shadow-xl hover:scale-105"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="rounded-lg border-2 border-primary bg-background px-8 py-3 font-semibold shadow-lg transition-all hover:bg-accent hover:shadow-xl"
          >
            Sign Up Free
          </Link>
        </div>

        {/* Stats */}
        <div className="mx-auto mt-16 grid max-w-4xl grid-cols-3 gap-8">
          <StatCard value="99.9%" label="Accuracy" />
          <StatCard value="10x" label="Faster" />
          <StatCard value="100%" label="Compliant" />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="elevated-card p-6 transition-all hover:scale-105">
      <div className="mb-3 text-4xl">{icon}</div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-primary">{value}</div>
      <div className="mt-1 text-sm text-muted-foreground">{label}</div>
    </div>
  );
}
