import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: pdf_light <in.pdf> <out.pdf> [dpi] [jpegQuality0-1]\n", stderr)
    exit(1)
}
let inPath = args[1]
let outPath = args[2]
let dpi = args.count > 3 ? (CGFloat(Double(args[3]) ?? 120)) : 120
let quality = args.count > 4 ? (CGFloat(Double(args[4]) ?? 0.45)) : 0.45

guard let provider = CGDataProvider(url: URL(fileURLWithPath: inPath) as CFURL),
      let src = CGPDFDocument(provider) else {
    fputs("open failed\n", stderr); exit(2)
}
let pageCount = src.numberOfPages
print("pages=\(pageCount) dpi=\(dpi) q=\(quality)")

guard pageCount > 0, let first = src.page(at: 1) else { exit(3) }
var mediaBox = first.getBoxRect(.mediaBox)

guard let ctx = CGContext(URL(fileURLWithPath: outPath) as CFURL, mediaBox: &mediaBox, nil) else {
    fputs("ctx failed\n", stderr); exit(4)
}

for i in 1...pageCount {
    guard let page = src.page(at: i) else { continue }
    let box = page.getBoxRect(.mediaBox)
    let wPx = Int(box.width * dpi / 72.0)
    let hPx = Int(box.height * dpi / 72.0)

    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let bitmap = CGContext(
        data: nil, width: wPx, height: hPx,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { continue }

    bitmap.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    bitmap.fill(CGRect(x: 0, y: 0, width: wPx, height: hPx))
    bitmap.saveGState()
    bitmap.translateBy(x: 0, y: CGFloat(hPx))
    bitmap.scaleBy(x: CGFloat(wPx) / box.width, y: -CGFloat(hPx) / box.height)
    bitmap.drawPDFPage(page)
    bitmap.restoreGState()

    guard let cgImage = bitmap.makeImage() else { continue }

    let tmpURL = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("p\(i).jpg")
    guard let dest = CGImageDestinationCreateWithURL(tmpURL as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else { continue }
    let opts: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: quality]
    CGImageDestinationAddImage(dest, cgImage, opts as CFDictionary)
    CGImageDestinationFinalize(dest)

    guard let jpgProvider = CGDataProvider(url: tmpURL as CFURL),
          let jpgSrc = CGImageSourceCreateWithDataProvider(jpgProvider, nil),
          let jpgImage = CGImageSourceCreateImageAtIndex(jpgSrc, 0, nil) else { continue }

    var pageBox = box
    ctx.beginPDFPage(nil)
    ctx.draw(jpgImage, in: pageBox)
    ctx.endPDFPage()

    let jpgSize = (try? FileManager.default.attributesOfItem(atPath: tmpURL.path)[.size] as? NSNumber)?.intValue ?? 0
    print("page \(i): \(wPx)x\(hPx) jpg=\(jpgSize) bytes")
    try? FileManager.default.removeItem(at: tmpURL)
}

ctx.closePDF()
let size = (try? FileManager.default.attributesOfItem(atPath: outPath)[.size] as? NSNumber)?.intValue ?? 0
print("out_bytes=\(size)")
