#!/usr/bin/env node
/**
 * Regenera cotizacion.pdf (4 páginas JPEG) con pdf-lib para que pdf-lib pueda
 * escribir texto sin espejo. No usar el PDF directo de pdf_light.swift como plantilla.
 *
 * Uso: node scripts/rebuild-cotizacion-template.mjs [origen.pdf] [salida.pdf]
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { PDFDocument } = require('pdf-lib');

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const srcPdf = process.argv[2] || join(root, 'cotizacion.full.backup-addr.pdf');
const outPdf = process.argv[3] || join(root, 'cotizacion.pdf');
const rasterDpi = process.argv[4] || '200';
const jpegQuality = process.argv[5] || '0.92';
const tmpRaster = join(root, '.cotizacion-raster-tmp.pdf');
const swift = join(root, 'scripts', 'pdf_light.swift');

if (!existsSync(srcPdf)) {
  console.error('No existe:', srcPdf);
  process.exit(1);
}

const swiftRun = spawnSync('swift', [swift, srcPdf, tmpRaster, rasterDpi, jpegQuality], {
  cwd: root,
  stdio: 'inherit',
});
if (swiftRun.status !== 0) process.exit(swiftRun.status ?? 1);

const raw = readFileSync(tmpRaster);
const jpgs = [];
let i = 0;
while (i < raw.length) {
  const start = raw.indexOf(Buffer.from([0xff, 0xd8, 0xff]), i);
  if (start < 0) break;
  const end = raw.indexOf(Buffer.from([0xff, 0xd9]), start);
  if (end < 0) break;
  const blob = raw.subarray(start, end + 2);
  const isJfif = blob[3] === 0xe0 || blob[3] === 0xe1;
  if (isJfif && blob.length > 50_000) jpgs.push(blob);
  i = end + 2;
}
if (jpgs.length < 4) {
  console.error('Se esperaban 4 JPEG en el raster; encontrados:', jpgs.length);
  process.exit(1);
}

const doc = await PDFDocument.create();
for (const jpg of jpgs.slice(0, 4)) {
  const img = await doc.embedJpg(new Uint8Array(jpg));
  const page = doc.addPage([612, 792]);
  page.drawImage(img, { x: 0, y: 792, width: 612, height: -792 });
}

writeFileSync(outPdf, await doc.save({ useObjectStreams: false }));
console.log('OK', outPdf, `(${jpgs.length} páginas, ${(readFileSync(outPdf).length / 1024).toFixed(0)} KB)`);
