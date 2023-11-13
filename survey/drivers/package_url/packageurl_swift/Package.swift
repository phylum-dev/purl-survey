// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "packageurl_swift",
    dependencies: [
        .package(name: "PackageURL", path: "repo"),
    ],
    targets: [
        .target(
            name: "Common", path: "Sources/Common"),
        .executableTarget(
            name: "format",
            dependencies: ["PackageURL", "Common"]),
        .executableTarget(
            name: "parse",
            dependencies: ["PackageURL", "Common"]),
    ]
)
