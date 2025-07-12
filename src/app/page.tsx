import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Bot, Zap, Shield, Users, BarChart3, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { Header } from '@/components/layout/header'
import { HeroSection } from '@/components/sections/hero-section'
import { FeaturesSection } from '@/components/sections/features-section'
import { AgentShowcase } from '@/components/sections/agent-showcase'
import { StatsSection } from '@/components/sections/stats-section'
import { TestimonialsSection } from '@/components/sections/testimonials-section'
import { PricingSection } from '@/components/sections/pricing-section'
import { Footer } from '@/components/layout/footer'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <AgentShowcase />
        <StatsSection />
        <TestimonialsSection />
        <PricingSection />
      </main>
      
      <Footer />
    </div>
  )
}