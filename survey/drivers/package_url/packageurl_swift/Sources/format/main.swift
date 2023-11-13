import Foundation

import PackageURL

#if os(Linux)
    import Glibc
#else
    import Darwin.C
#endif

import Common

while let line = readLine() {
    let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
    if trimmed.isEmpty {
        continue
    }

    let raw = trimmed.data(using: .utf8)!
    let parts: Parts = try! JSONDecoder().decode(Parts.self, from: raw)

    let purl = PackageURL(
        type: parts.type,
        namespace: parts.namespace,
        name: parts.name,
        version: parts.version,
        qualifiers: parts.qualifiers,
        subpath: parts.subpath).canonicalized

    print(purl)

    // Workaround for Swift bug?
    fflush(stdout)
}
