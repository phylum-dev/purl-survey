These files suppress errors for survey.suite.

overescape.json suppresses errors caused by implementations that escape characters when the spec says not to. This overescaping does not change the meaning of the PURL when it is parsed with conforming parsers, so it's mostly harmless.

purl-226.json suppresses errors caused by implementations that have fixed package-url/purl-spec#226.

type-rules.json suppresses errors caused by implementations not implementing type-specific rules.
