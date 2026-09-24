#!/usr/bin/env node
/**
 * Reemplaza una página de un PDF por una imagen JPEG a página completa (612×792).
 *
 * Uso: node scripts/replace-pdf-page.mjs <archivo.pdf> <nº página 1-based> <imagen.jpg>
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { PDFDocument } = require('pdf-lib');

const [pdfPath, pageArg, jpgPath] = process.argv.slice(2);
const pageIndex = Number(pageArg) - 1;

const src = await PDFDocument.load(readFileSync(pdfPath));
const out = await PDFDocument.create();
const total = src.getPageCount();
if (pageIndex < 0 || pageIndex >= total) {
  console.error(`Página fuera de rango (1-${total})`);
  process.exit(1);
}

const copied = await out.copyPages(src, [...Array(total).keys()]);
const img = await out.embedJpg(readFileSync(jpgPath));
copied.forEach((page, i) => {
  if (i !== pageIndex) {
    out.addPage(page);
    return;
  }
  const p = out.addPage([612, 792]);
  p.drawImage(img, { x: 0, y: 0, width: 612, height: 792 });
});

writeFileSync(pdfPath, await out.save({ useObjectStreams: false }));
console.log('OK', pdfPath, `(${(readFileSync(pdfPath).length / 1024).toFixed(0)} KB)`);
