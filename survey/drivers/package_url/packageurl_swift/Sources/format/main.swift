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
    if let parts: Parts = try? JSONDecoder().decode(Parts.self, from: raw) {
        let purl = PackageURL(
            type: parts.type,
            namespace: parts.namespace,
            name: parts.name,
            version: parts.version,
            qualifiers: parts.qualifiers,
            subpath: parts.subpath).canonicalized

        print(purl)
    } else {
        let e = Error(error: "invalid input JSON")
        let data = try! JSONEncoder().encode(e)
        print(String(data: data, encoding: .utf8)!)
    }

    // Workaround for Swift bug?
    fflush(stdout)
}
