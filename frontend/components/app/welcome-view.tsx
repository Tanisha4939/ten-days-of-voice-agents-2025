import * as React from "react";
import { Button } from "@/components/livekit/button";

function SpotlightIcon() {
  return (
    <div className="relative mb-8">
      {/* Golden halo */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="h-40 w-40 rounded-full bg-gradient-to-r from-[#CDA43433] via-[#E5C76B55] to-[#CDA43433] blur-md animate-pulse" />
      </div>

      

        {/* Emojis around mic */}
        
      </div>
    
  );
}

function TheaterIcon({ className }: { className?: string }) {
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
        d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<"div"> & WelcomeViewProps
>(({ startButtonText, onStartCall, ...props }, ref) => {
  const [name, setName] = React.useState("");

  const handleStart = () => {
    // optional: you can require name here if you want
    onStartCall();
  };

  return (
    <div
      ref={ref}
      {...props}
      className="min-h-screen bg-gradient-to-br from-[#021330] via-[#062055] to-[#0A2E6E] relative overflow-hidden flex items-center justify-center"
    >
      {/* Subtle navy lines / beams */}
      <div className="absolute inset-0 opacity-25 pointer-events-none">
        <div className="absolute -left-20 top-0 h-full w-40 bg-gradient-to-br from-[#0A2E6E] to-transparent rotate-6" />
        <div className="absolute -right-24 top-0 h-full w-40 bg-gradient-to-bl from-[#0A2E6E] to-transparent -rotate-6" />
      </div>

      {/* Golden spotlights */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute -top-32 left-1/3 h-80 w-80 rounded-full bg-[#CDA434] blur-3xl" />
        <div className="absolute -top-40 right-1/4 h-72 w-72 rounded-full bg-[#E5C76B] blur-3xl" />
      </div>

      <section className="relative z-10 flex flex-col items-center justify-center text-center px-4 py-12 w-full max-w-4xl">
        <SpotlightIcon />

        {/* Title */}
        <div className="mb-6">
          <div className="text-[10px] sm:text-xs tracking-[0.3em] uppercase text-[#F6E9C4]/80 mb-2 font-semibold animate-text-shimmer">
            Live from the navy & gold stage
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black bg-gradient-to-r from-[#F6E9C4] via-[#E5C76B] to-[#CDA434] bg-clip-text text-transparent mb-3 drop-shadow-[0_0_25px_rgba(0,0,0,0.8)]">
            IMPROV BATTLE
          </h1>
          <p className="text-lg sm:text-2xl text-[#D4C798] font-semibold">
            The Ultimate Voice Comedy Showdown!
          </p>
        </div>

        {/* How it works card */}
        <div className="bg-gradient-to-br from-[#102145]/95 via-[#141F3D]/95 to-[#11182F]/95 border border-[#CDA434] rounded-3xl p-6 max-w-2xl mb-8 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.6)] text-left">
          <div className="flex items-start gap-3 mb-3">
            <TheaterIcon className="h-7 w-7 text-[#E5C76B] flex-shrink-0 mt-1" />
            <div>
              <p className="text-[#F6E9C4] font-bold text-lg mb-2">
                🎟️ How It Works
              </p>
              <p className="text-[#D4C798] text-sm leading-relaxed">
                Your AI host will throw wild scenarios at you – act them out on
                the spot! Be a time-travelling tour guide, a barista with
                magical coffee, or a waiter whose food escaped the kitchen. The
                host will react, critique, and keep you on your toes through
                multiple improv rounds.
              </p>
            </div>
          </div>
        </div>

                {/* Name / stage name + START button inside same card */}
        <div className="w-full max-w-md mb-10">
          <div className="bg-[#0A2040]/80 border border-[#CDA434]/70 rounded-2xl p-5 pb-6 backdrop-blur-xl shadow-[0_18px_40px_rgba(0,0,0,0.7)] text-left flex flex-col gap-3">
            <div>
              <p className="text-sm font-semibold text-[#F6E9C4] mb-1">
                🎤 Enter your stage name
              </p>
              <p className="text-xs text-[#D4C798]/90 mb-3">
                This is how the host will welcome you on the Improv Battle stage.
              </p>
              <input
                type="text"
                placeholder="e.g. Tanisha the Time-Traveler"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-xl border border-[#CDA434]/60 bg-[#061735]/80 px-4 py-2 text-sm text-[#F6E9C4] placeholder:text-[#CDA434]/50 outline-none focus:ring-2 focus:ring-[#CDA434] focus:border-[#CDA434] transition"
              />
              <p className="mt-2 text-[11px] text-[#D4C798]/80">
                You can still tell the host your name later – this is just for the
                vibes ✨
              </p>
            </div>

            {/* START button – always visible, no conditions */}
            <div className="pt-2">
              <div className="bg-gradient-to-r from-[#CDA434] via-[#E5C76B] to-[#CDA434] p-[3px] rounded-full shadow-[0_0_30px_rgba(205,164,52,0.7)]">
                <Button
                  variant="primary"
                  size="lg"
                  
                  onClick={handleStart}
                  className="w-full font-black text-lg bg-[#CDA434] text-[#021330] hover:bg-[#E5C76B] rounded-full transition-all duration-300 hover:scale-105"
                >
                  {startButtonText}
                </Button>
              </div>
              <p className="mt-2 text-[11px] text-[#F6E9C4]/80 text-center">
                🎙️ Once you hit start, your AI host joins the stage.
              </p>
            </div>
          </div>
        </div>

      </section>
    </div>
  );
});

WelcomeView.displayName = "WelcomeView";
