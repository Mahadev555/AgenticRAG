import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  distDir: "../backend/static", // Custom build directory (for Next.js build)
  output: "export", // Ensure static export mode
  trailingSlash: true, // Optional: Ensures proper file resolution
};

export default nextConfig;
