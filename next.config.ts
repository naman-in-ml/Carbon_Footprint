import type { NextConfig } from "next";

// Optional deployed backend (e.g. a separate Vercel project or host).
// When unset, production leaves /api/* unhandled and the UI falls back to
// static demo data; development proxies to the local FastAPI server.
const backendOrigin = process.env.BACKEND_URL;

const nextConfig: NextConfig = {
  async rewrites() {
    if (backendOrigin) {
      return [
        { source: "/api/:path*", destination: `${backendOrigin}/api/:path*` },
      ];
    }
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    }
    return [];
  },
};

export default nextConfig;