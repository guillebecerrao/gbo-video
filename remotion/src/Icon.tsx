import React from "react";
import { IconName } from "./types";

// Minimal line icons (stroke = currentColor). No stock stickers, no emojis.
export const Icon: React.FC<{ name: IconName; size?: number }> = ({ name, size = 72 }) => {
  const common = {
    width: size, height: size, viewBox: "0 0 48 48", fill: "none",
    stroke: "currentColor", strokeWidth: 3, strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (name) {
    case "clock":
      return (<svg {...common}><circle cx="24" cy="24" r="18" /><path d="M24 13v12l8 5" /></svg>);
    case "coins":
      return (<svg {...common}><ellipse cx="24" cy="12" rx="14" ry="5" /><path d="M10 12v8c0 2.8 6.3 5 14 5s14-2.2 14-5v-8" /><path d="M10 20v8c0 2.8 6.3 5 14 5s14-2.2 14-5v-8" /><path d="M10 28v8c0 2.8 6.3 5 14 5s14-2.2 14-5v-8" /></svg>);
    case "people":
      return (<svg {...common}><circle cx="17" cy="16" r="6" /><circle cx="33" cy="18" r="5" /><path d="M5 40c0-7 5.4-12 12-12s12 5 12 12" /><path d="M29 30c1.2-.6 2.6-1 4-1 5.5 0 10 4.2 10 10" /></svg>);
    case "server":
      return (<svg {...common}><rect x="8" y="7" width="32" height="14" rx="3" /><rect x="8" y="27" width="32" height="14" rx="3" /><path d="M15 14h.01M15 34h.01M22 14h12M22 34h12" /></svg>);
    case "globe":
      return (<svg {...common}><circle cx="24" cy="24" r="18" /><ellipse cx="24" cy="24" rx="8" ry="18" /><path d="M6 24h36M9 15h30M9 33h30" /></svg>);
    case "briefcase":
      return (<svg {...common}><rect x="6" y="15" width="36" height="25" rx="4" /><path d="M18 15v-4a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v4M6 26h36" /></svg>);
    case "chart":
      return (<svg {...common}><path d="M8 40h34" /><rect x="11" y="26" width="6" height="12" rx="1.5" /><rect x="21" y="18" width="6" height="20" rx="1.5" /><rect x="31" y="10" width="6" height="28" rx="1.5" /></svg>);
    case "speech":
      return (<svg {...common}><path d="M8 10h32a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H22l-9 7v-7H8a3 3 0 0 1-3-3V13a3 3 0 0 1 3-3z" /><path d="M14 19h20M14 25h12" /></svg>);
  }
};
