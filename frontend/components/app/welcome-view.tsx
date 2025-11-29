import { Button } from '@/components/livekit/button';

function OceanIcon() {
  return (
    <div className="relative mb-8">
      {/* Glow halo */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-32 w-32 rounded-full bg-gradient-to-br from-cyan-500/30 via-sky-500/20 to-emerald-400/30 blur-xl animate-pulse" />
      </div>

      {/* Island + wave emoji cluster */}
      <div className="relative flex items-center justify-center">
        <div className="h-24 w-24 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center shadow-[0_0_35px_rgba(56,189,248,0.55)]">
          <span className="text-4xl drop-shadow-md">🏝️</span>
        </div>

        {/* Floating bubbles / icons */}
        <div className="absolute -top-3 -right-2 text-2xl animate-bounce">🌊</div>
        <div
          className="absolute -bottom-1 -left-3 text-xl animate-bounce"
          style={{ animationDelay: '0.25s' }}
        >
          🐬
        </div>
        <div
          className="absolute top-1 left-10 text-lg animate-bounce"
          style={{ animationDelay: '0.5s' }}
        >
          🐚
        </div>
      </div>
    </div>
  );
}

function ShellIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
    >
      <path
        d="M12 3C8.5 3 4 5.5 4 11c0 4.5 3 8 8 8s8-3.5 8-8c0-5.5-4.5-8-8-8z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7 11c0 3 2.5 5 5 5s5-2 5-5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="min-h-screen bg-gradient-to-br from-slate-950 via-sky-950 to-slate-950 relative overflow-hidden"
    >
      {/* Soft moving water blobs */}
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <div className="absolute -top-32 -left-20 h-64 w-64 rounded-full bg-sky-500/25 blur-3xl animate-pulse" />
        <div
          className="absolute top-1/3 -right-24 h-72 w-72 rounded-full bg-cyan-400/25 blur-3xl animate-pulse"
          style={{ animationDelay: '0.7s' }}
        />
        <div
          className="absolute bottom-[-5rem] left-1/4 h-64 w-64 rounded-full bg-emerald-400/20 blur-3xl animate-pulse"
          style={{ animationDelay: '1.3s' }}
        />
      </div>

      {/* Tiny plankton dots */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-20 left-16 h-1 w-1 rounded-full bg-cyan-200/70 animate-pulse" />
        <div
          className="absolute top-40 right-24 h-1.5 w-1.5 rounded-full bg-sky-300/70 animate-pulse"
          style={{ animationDelay: '0.4s' }}
        />
        <div
          className="absolute bottom-28 left-1/3 h-1 w-1 rounded-full bg-teal-200/70 animate-pulse"
          style={{ animationDelay: '0.9s' }}
        />
        <div
          className="absolute top-1/3 right-1/4 h-1.5 w-1.5 rounded-full bg-cyan-100/80 animate-pulse"
          style={{ animationDelay: '1.4s' }}
        />
      </div>

      <section className="relative z-10 flex flex-col items-center justify-center text-center px-4 py-12">
        <OceanIcon />

        {/* Heading */}
        <div className="mb-4">
          <div className="text-xs md:text-sm uppercase tracking-[0.25em] text-cyan-300/80 mb-2 font-semibold">
            🌊 Welcome Explorer 🌊
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-300 via-sky-300 to-emerald-300 bg-clip-text text-transparent mb-3 drop-shadow-[0_0_25px_rgba(56,189,248,0.6)]">
            Ocean Game Master
          </h1>
          <p className="text-base md:text-lg text-sky-200/90">
            A voice-powered adventure across islands, reefs, and forgotten tides.
          </p>
        </div>

        {/* Intro card */}
        <div className="bg-gradient-to-br from-sky-900/50 via-cyan-900/60 to-slate-900/70 border border-cyan-500/30 rounded-2xl p-6 md:p-7 max-w-2xl mb-6 backdrop-blur-xl shadow-[0_0_35px_rgba(15,118,110,0.45)]">
          <div className="flex items-start gap-3 mb-3">
            <ShellIcon className="h-7 w-7 text-cyan-300 flex-shrink-0 mt-1" />
            <div className="text-left">
              <p className="text-cyan-100 text-sm md:text-base leading-relaxed mb-2">
                <span className="text-cyan-300 font-semibold">
                  The sea is listening to your voice...
                </span>
              </p>
              <p className="text-sky-100/90 text-xs md:text-sm leading-relaxed">
                Speak to your AI Game Master and explore a living ocean world. Discover secret
                grottoes, meet water spirits, and decide the fate of lost relics — all just by
                saying what you want to do next.
              </p>
            </div>
          </div>
        </div>

        {/* ✅ START BUTTON – moved up so hamesha visible rahe */}
        <div className="mb-8 flex flex-col items-center">
          <Button
            variant="primary"
            size="lg"
            onClick={onStartCall}
            className="w-72 md:w-80 font-semibold text-base md:text-lg bg-gradient-to-r from-cyan-500 via-sky-500 to-emerald-500 hover:from-cyan-400 hover:via-sky-400 hover:to-emerald-400 border border-cyan-300/60 shadow-[0_0_30px_rgba(56,189,248,0.6)] transition-all duration-300 hover:scale-[1.03] rounded-full"
          >
            {startButtonText || 'Begin Ocean Adventure'}
          </Button>
          <p className="text-sky-300/80 text-[11px] md:text-xs mt-3 italic">
            Click to connect, then say: “Start the story”.
          </p>
        </div>

        
        
      </section>
    </div>
  );
};
