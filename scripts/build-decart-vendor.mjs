import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { build } from "esbuild";


const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const vendorDirectory = join(projectRoot, "static", "vendor");
const sdkPackagePath = fileURLToPath(
  import.meta.resolve("@decartai/sdk/package.json")
);
const sdkDirectory = dirname(sdkPackagePath);
const workerSource = join(
  sdkDirectory,
  "dist",
  "realtime",
  "browser",
  "frame-metadata-worker.js"
);

await mkdir(vendorDirectory, { recursive: true });

await build({
  entryPoints: ["@decartai/sdk"],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: ["firefox115"],
  outfile: join(vendorDirectory, "decart-sdk.js"),
  legalComments: "none",
  sourcemap: false,
});

const bundlePath = join(vendorDirectory, "decart-sdk.js");
const bundle = await readFile(bundlePath, "utf8");
await writeFile(bundlePath, bundle.replace(/[ \t]+$/gm, ""), "utf8");

await copyFile(
  workerSource,
  join(vendorDirectory, "frame-metadata-worker.js")
);
