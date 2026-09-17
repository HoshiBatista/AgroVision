import { motion } from "framer-motion";

function Sheep({ delay }: { delay: number }) {
  return (
    <motion.div
      initial={{ y: 0 }}
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay }}
      className="text-4xl drop-shadow-md sm:text-5xl"
      aria-hidden
    >
      🐑
    </motion.div>
  );
}

/** A small flock of gently bobbing sheep grazing on a meadow strip. */
export function SheepFlock() {
  return (
    <div className="relative mt-10 h-28 w-full">
      <div className="absolute bottom-0 h-14 w-full rounded-t-[100%] bg-gradient-to-t from-meadow-600 to-meadow-400" />
      <div className="absolute bottom-6 flex w-full items-end justify-center gap-6">
        {[0, 0.6, 1.2, 1.8, 2.4].map((delay) => (
          <Sheep key={delay} delay={delay} />
        ))}
      </div>
    </div>
  );
}
