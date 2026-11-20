// world-news-canvas-20261120 — Friday, 20 November 2026 edition.
// The broadsheet is built offline by build_poster.py; this entrypoint ships the
// finished bytes and refuses anything the gate would reject. No network, no
// dependencies, and the same input always produces the same output file.

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1_048_576;
const image = new URL('./entry.png', import.meta.url);
const bytes = readFileSync(image);

if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes; the limit is ${MAX_BYTES}`);
}
const isJpeg = bytes[0] === 0xff && bytes[1] === 0xd8;
const isPng = bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47;
if (!isJpeg && !isPng) {
  throw new Error('entry.png must begin with JPEG or PNG magic bytes');
}

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outputDir, { recursive: true });
const output = join(outputDir, 'entry.png');
copyFileSync(image, output);

const copied = readFileSync(output);
if (copied.length !== bytes.length || !copied.equals(bytes)) {
  throw new Error('copied entry.png is not byte-identical to the source');
}
if (statSync(output).size === 0) {
  throw new Error('copied entry.png is empty');
}
