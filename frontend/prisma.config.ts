import dotenv from "dotenv";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { defineConfig } from "prisma/config";

// prisma.config.ts lives at frontend/, root .env is one level up.
// fileURLToPath(import.meta.url) gives the absolute path of this file
// regardless of CWD, so the root .env is always found correctly.
const root = path.resolve(fileURLToPath(import.meta.url), "..");
dotenv.config({ path: path.join(root, "..", ".env") });

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
  },
  datasource: {
    url: process.env["PRISMA_DATABASE_URL"],
  },
});
