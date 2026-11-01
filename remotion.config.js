import fs from "fs";
import os from "os";
import path from "path";
import { Config } from "@remotion/cli/config";

// Remotion downloads its own Chrome from remotion.media, which cloud sessions can't reach.
// Use REMOTION_BROWSER_EXECUTABLE if set, else a headless Chrome already on the machine
// (Playwright's or HyperFrames'). Elsewhere nothing matches and Remotion uses its own.
function localChrome() {
  if (process.env.REMOTION_BROWSER_EXECUTABLE) return process.env.REMOTION_BROWSER_EXECUTABLE;
  const roots = ["/opt/pw-browsers", path.join(os.homedir(), ".cache", "hyperframes", "chrome", "chrome-headless-shell")];
  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    for (const dir of fs.readdirSync(root).sort().reverse()) {
      const bin = path.join(root, dir, "chrome-headless-shell-linux64", "chrome-headless-shell");
      if (fs.existsSync(bin)) return bin;
    }
  }
  return null;
}

const chrome = localChrome();
if (chrome) Config.setBrowserExecutable(chrome);
