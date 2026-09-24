import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
let path = args[1]
let pageIndex = Int(args[2]) ?? 1
let out = args[3]
let scale = CGFloat(Double(args.count > 4 ? args[4] : "2") ?? 2)

guard let provider = CGDataProvider(url: URL(fileURLWithPath: path) as CFURL),
      let doc = CGPDFDocument(provider),
      let page = doc.page(at: pageIndex) else {
    fputs("open fail\n", stderr)
    exit(1)
}
let box = page.getBoxRect(.mediaBox)
let w = Int(box.width * scale), h = Int(box.height * scale)
guard let ctx = CGContext(
    data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
    space: CGColorSpaceCreateDeviceRGB(),
    bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
) else { exit(2) }
ctx.setFillColor(gray: 1, alpha: 1)
ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
ctx.scaleBy(x: scale, y: scale)
ctx.drawPDFPage(page)
guard let img = ctx.makeImage(),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: out) as CFURL, UTType.png.identifier as CFString, 1, nil) else { exit(3) }
CGImageDestinationAddImage(dest, img, nil)
CGImageDestinationFinalize(dest)
print("OK \(out) \(w)x\(h)")
