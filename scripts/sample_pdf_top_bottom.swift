import Foundation
import CoreGraphics

let path = CommandLine.arguments[1]
let pageIndex = Int(CommandLine.arguments[2]) ?? 1
guard let provider = CGDataProvider(url: URL(fileURLWithPath: path) as CFURL),
      let doc = CGPDFDocument(provider),
      let page = doc.page(at: pageIndex) else {
    fputs("open fail\n", stderr)
    exit(1)
}
let box = page.getBoxRect(.mediaBox)
let w = 40, h = 80
let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(
    data: nil, width: w, height: h,
    bitsPerComponent: 8, bytesPerRow: 0, space: cs,
    bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
) else { exit(2) }
ctx.setFillColor(gray: 0.5, alpha: 1)
ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
ctx.saveGState()
ctx.translateBy(x: 0, y: CGFloat(h))
ctx.scaleBy(x: CGFloat(w) / box.width, y: -CGFloat(h) / box.height)
ctx.drawPDFPage(page)
ctx.restoreGState()
guard let img = ctx.makeImage(), let data = img.dataProvider?.data as Data? else { exit(3) }
let b = [UInt8](data)
func px(_ y: Int) -> String {
    let i = y * w * 4
    return "\(b[i]),\(b[i+1]),\(b[i+2])"
}
print("top=\(px(0)) bottom=\(px(h-1))")
