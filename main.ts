/**
 * Deterministic runtime entrypoint for world-news-canvas-20261120 (v17).
 *
 * The 1024x1024 progressive 4:4:4 JPEG broadsheet for Friday, 20 November 2026
 * is pre-rendered offline by build_poster.py into ./entry.png. At runtime this
 * module validates the bundled artifact's magic header and byte budget, writes
 * it to ${MAKEFUN_OUTPUT_DIR:-/output}/entry.png using only Node built-ins, and
 * verifies the written file matches the source byte-for-byte.
 */

import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SIZE_CAP_BYTES = 1_048_576;
const ARTIFACT_NAME = 'entry.png';

function hasValidImageSignature(buf: Buffer): boolean {
  const jpegStart = buf.length >= 4 && buf[0] === 0xff && buf[1] === 0xd8 && buf[buf.length - 2] === 0xff && buf[buf.length - 1] === 0xd9;
  const pngStart = buf.length >= 8 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  return jpegStart || pngStart;
}

function shipBroadsheet(): void {
  const repoRoot = dirname(fileURLToPath(import.meta.url));
  const sourcePath = join(repoRoot, ARTIFACT_NAME);
  const payload = readFileSync(sourcePath);

  if (payload.byteLength === 0) {
    throw new Error(`${ARTIFACT_NAME} is empty`);
  }
  if (payload.byteLength > SIZE_CAP_BYTES) {
    throw new Error(`${ARTIFACT_NAME} exceeds ${SIZE_CAP_BYTES} bytes (${payload.byteLength})`);
  }
  if (!hasValidImageSignature(payload)) {
    throw new Error(`${ARTIFACT_NAME} failed JPEG/PNG signature verification`);
  }

  const targetDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
  mkdirSync(targetDir, { recursive: true });

  const destPath = join(targetDir, ARTIFACT_NAME);
  writeFileSync(destPath, payload);

  const writtenStat = statSync(destPath);
  const writtenBytes = readFileSync(destPath);
  if (writtenStat.size !== payload.byteLength || Buffer.compare(writtenBytes, payload) !== 0) {
    throw new Error(`Integrity mismatch after writing ${destPath}`);
  }
}

shipBroadsheet();
