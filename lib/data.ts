import fs from "fs";
import path from "path";
import type { InternData } from "./types";

export function getInternData(): InternData {
  const p = path.join(process.cwd(), "public/data/intern_data.json");
  const raw = fs.readFileSync(p, "utf-8");
  return JSON.parse(raw) as InternData;
}
