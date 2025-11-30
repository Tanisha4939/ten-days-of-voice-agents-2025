import { Button } from '@/components/livekit/button';

function ShoppingBagIcon() {
  return (
    <div className="relative mb-8">
      {/* Pink gradient glow */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-32 w-32 rounded-full bg-gradient-to-r from-pink-300/40 via-pink-400/40 to-pink-500/40 animate-pulse" />
      </div>

      {/* Shopping bag */}
      <div className="relative flex items-center justify-center">
        <svg
          className="h-24 w-24 text-pink-500 drop-shadow-xl"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
          />
        </svg>

        {/* Cute emojis around the bag */}
        
      </div>
    </div>
  );
}

function MicIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
      />
    </svg>
  );
}

function SparkleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
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
  ...rest
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      {...rest}
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-pink-300 via-pink-100 to-white px-4 py-10"
    >
      {/* animated pink blobs in background */}
      <div className="pointer-events-none absolute inset-0 opacity-60">
        <div className="absolute -top-10 -left-10 h-40 w-40 rounded-full bg-pink-300 blur-3xl" />
        <div
          className="absolute bottom-10 right-4 h-48 w-48 rounded-full bg-pink-400 blur-3xl"
          style={{ animation: 'pulse 4s ease-in-out infinite' }}
        />
        <div
          className="absolute top-1/3 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full bg-pink-200 blur-3xl"
          style={{ animation: 'pulse 5s ease-in-out infinite 1s' }}
        />
      </div>

      <section className="relative z-10 w-full max-w-3xl rounded-3xl border border-pink-200/70 bg-white/80 px-6 py-9 text-center shadow-[0_18px_40px_rgba(255,83,150,0.35)] backdrop-blur">
        {/* top pill + sparkle */}
        <div className="mb-4 flex items-center justify-center gap-3">
          <span className="inline-flex items-center gap-2 rounded-full border border-pink-200 bg-pink-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-pink-600">
            <span className="h-2 w-2 rounded-full bg-pink-500 shadow-[0_0_0_4px_rgba(255,126,186,0.6)]" />
            SwiftCart · Voice Shopping BFF
          </span>
          <SparkleIcon className="h-5 w-5 text-pink-400" />
        </div>

        <ShoppingBagIcon />

        {/* heading */}
        <div className="mb-6">
          <h1 className="text-balance text-3xl font-extrabold leading-tight text-foreground sm:text-4xl">
            Shop like a{' '}
            <span className="bg-gradient-to-r from-pink-500 via-pink-400 to-pink-600 bg-clip-text text-transparent">
               Queen!!
            </span>
              
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
            Meet <span className="font-semibold text-pink-600">SwiftCart</span> – your
            super cute voice shopping assistant for all your e-commerce cravings.  
            Ask for products, compare options, and place orders… totally hands-free and fully pink.
          </p>
        </div>

        {/* value / mic block */}
        <div className="mx-auto mb-7 max-w-2xl rounded-2xl border border-pink-100 bg-pink-50/80 p-5 text-left shadow-sm">
          <div className="flex items-start gap-3">
            <MicIcon className="mt-1 h-7 w-7 text-pink-500" />
            <div>
              <p className="mb-1 text-sm font-semibold text-pink-900">
                Your personal shopping bestie
              </p>
              <p className="text-xs text-pink-700 leading-relaxed">
                Just say what you’re in the mood for –  
                “cute hoodies under ₹1500”, “a comfy black tee”, or  
                “what did I just buy?” – and I’ll handle the rest.
              </p>
            </div>
          </div>
        </div>

      

        {/* CTA */}
        <div className="mb-2 flex flex-col items-center">
          <Button
            variant="primary"
            size="lg"
            onClick={onStartCall}
            className="w-full max-w-xs rounded-full bg-gradient-to-r from-pink-500 via-pink-400 to-pink-600 text-sm font-bold uppercase tracking-[0.16em] text-white shadow-lg shadow-pink-300/70 hover:translate-y-[1px] hover:shadow-pink-400/80"
          >
            {startButtonText}
          </Button>
          <p className="mt-3 text-[11px] font-medium italic text-pink-700">
            🎤 Just talk naturally – SwiftCart understands you.
          </p>
        </div>
      </section>

      {/* docs link bottom */}
      <div className="pointer-events-none absolute bottom-4 left-0 flex w-full items-center justify-center">
        <p className="max-w-prose px-4 text-center text-[11px] leading-5 text-pink-700/85 md:text-xs">
          Need help getting set up? Check out the{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="pointer-events-auto underline decoration-pink-400 underline-offset-2 hover:text-pink-500"
          >
            Voice AI quickstart
          </a>
          .
        </p>
      </div>
    </div>
  );
};
