public struct Parts: Codable {
    public let type: String
    public let name: String
    public let namespace: String?
    public let version: String?
    public let qualifiers: [String: String]?
    public let subpath: String?

    public init(
        type: String,
        name: String,
        namespace: String? = nil,
        version: String? = nil,
        qualifiers: [String: String]? = nil,
        subpath: String? = nil)
    {
        self.type = type
        self.name = name
        self.namespace = namespace
        self.version = version
        self.qualifiers = qualifiers
        self.subpath = subpath
    }
}

public struct Error: Encodable {
    public let error: String

    public init(
        error: String)
    {
        self.error = error
    }
}
