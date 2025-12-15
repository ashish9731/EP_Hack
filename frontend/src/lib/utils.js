import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const getScoreLabel = (score) => {
  if (score >= 85) return { label: "Executive-Ready", color: "text-accent" };
  if (score >= 70) return { label: "Strong", color: "text-green-600" };
  if (score >= 55) return { label: "Developing", color: "text-yellow-600" };
  return { label: "Needs Improvement", color: "text-red-600" };
};

export const formatTimestamp = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};