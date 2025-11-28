'use client';

import type { HTMLAttributes } from 'react';
import { Button } from '@/components/livekit/button';

export type WelcomeViewProps = {
  startButtonText?: string;
  onStartCall?: () => void;
} & HTMLAttributes<HTMLDivElement>;

function MultiCuisineIcon() {
  return (
    <div className="relative mb-6">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-28 w-28 rounded-full bg-gradient-to-tr from-primary/30 via-accent/25 to-primary/10 animate-pulse" />
      </div>

      <div className="relative flex items-center justify-center">
        <div className="h-20 w-20 rounded-full bg-card shadow-xl border border-border flex items-center justify-center text-3xl">
          <span role="img" aria-label="multi cuisine plate">
            🍕🍜🌮
          </span>
        </div>

        <div className="absolute -top-3 -right-2 text-2xl animate-bounce">🍛</div>
        <div className="absolute -bottom-2 -left-1 text-xl animate-[float_3s_ease-in-out_infinite]">🍝</div>
        <div className="absolute -bottom-4 right-4 text-xl animate-[float_4s_ease-in-out_infinite]">🌯</div>
      </div>
    </div>
  );
}

export function WelcomeView({
  startButtonText = '🎙️ Start talking to your Menu Agent',
  onStartCall,
  className,
  ...rest
}: WelcomeViewProps) {
  const rootClassName = [
    'h-full w-full flex items-center justify-center bg-background text-foreground',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div {...rest} className={rootClassName}>
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.14),_transparent_55%),radial-gradient(circle_at_bottom,_rgba(0,0,0,0.48),_transparent_65%)] opacity-70" />

      <div className="relative z-10 max-w-3xl w-full px-6 py-12">
        <div className="glass-panel p-8 md:p-12 flex flex-col items-center text-center space-y-6">

          <MultiCuisineIcon />

          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/70 border border-border/60 px-4 py-1 text-xs font-medium text-secondary-foreground">
            👩‍🍳 Your AI-powered Multi-Cuisine Menu Guide
          </div>

          <h1 className="text-3xl md:text-5xl font-semibold tracking-tight leading-tight">
            Explore menus from{' '}
            <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Italian, Chinese, Mexican & Indian
            </span>
          </h1>

          <p className="text-sm md:text-base text-muted-foreground max-w-xl">
            Ask your voice agent to suggest perfect food combos, dinner ideas, restaurant-style dishes or quick meals.
          </p>

          <Button
            size="lg"
            className="rounded-full px-6 md:px-10 py-3 text-base shadow-md shadow-primary/30"
            onClick={onStartCall}
          >
            {startButtonText}
          </Button>

          <div className="flex flex-wrap justify-center gap-3 pt-2">
            <span className="cuisine-pill">Italian • 🍕</span>
            <span className="cuisine-pill">Chinese • 🍜</span>
            <span className="cuisine-pill">Mexican • 🌮</span>
            <span className="cuisine-pill">Indian • 🍛</span>
          </div>

          <p className="text-xs text-muted-foreground pt-1">
            Trusted by food lovers for smart recommendations & personalized dining suggestions.
          </p>
        </div>
      </div>
    </div>
  );
}
