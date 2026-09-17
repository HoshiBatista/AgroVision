interface Cloud {
  top: string;
  size: number;
  duration: number;
  delay: number;
  opacity: number;
}

const CLOUDS: Cloud[] = [
  { top: "8%", size: 180, duration: 60, delay: 0, opacity: 0.85 },
  { top: "22%", size: 120, duration: 45, delay: 8, opacity: 0.7 },
  { top: "40%", size: 220, duration: 75, delay: 3, opacity: 0.6 },
  { top: "58%", size: 140, duration: 52, delay: 12, opacity: 0.5 },
  { top: "72%", size: 260, duration: 90, delay: 6, opacity: 0.45 },
];

function CloudShape({ opacity }: { opacity: number }) {
  return (
    <svg viewBox="0 0 200 100" className="h-full w-full" style={{ opacity }}>
      <g fill="white">
        <ellipse cx="60" cy="65" rx="45" ry="30" />
        <ellipse cx="100" cy="50" rx="50" ry="38" />
        <ellipse cx="140" cy="66" rx="42" ry="28" />
        <rect x="55" y="66" width="95" height="26" rx="13" />
      </g>
    </svg>
  );
}

/** A layer of slow, semi-transparent drifting clouds. */
export function CloudScene() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-sky-300 via-sky-200 to-sky-50" />
      {CLOUDS.map((cloud, index) => (
        <div
          key={index}
          className="absolute animate-drift"
          style={{
            top: cloud.top,
            width: cloud.size,
            height: cloud.size * 0.5,
            animationDuration: `${cloud.duration}s`,
            animationDelay: `-${cloud.delay}s`,
          }}
        >
          <CloudShape opacity={cloud.opacity} />
        </div>
      ))}
    </div>
  );
}
