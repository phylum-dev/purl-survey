import Foundation

import PackageURL

#if os(Linux)
    import Glibc
#else
    import Darwin.C
#endif

import Common

while var line = readLine() {
    line = line.trimmingCharacters(in: .whitespacesAndNewlines)
    if line.isEmpty {
        continue
    }

    guard var purl = PackageURL(line) else {
        // No explanation given.
        let e = Error(error: "")
        let data = try! JSONEncoder().encode(e)
        print(String(data: data, encoding: .utf8)!)

        // Workaround for Swift bug?
        fflush(stdout)
        continue
    }
    purl = purl.canonicalized
    let parts = Parts(
        type: purl.type,
        name: purl.name,
        namespace: purl.namespace,
        version: purl.version,
        qualifiers: purl.qualifiers,
        subpath: purl.subpath
    )
    let data = try! JSONEncoder().encode(parts)
    print(String(data: data, encoding: .utf8)!)

    // Workaround for Swift bug?
    fflush(stdout)
}
