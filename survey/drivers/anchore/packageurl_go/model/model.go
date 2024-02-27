package model

type Parts struct {
	Type       string            `json:"type"`
	Name       string            `json:"name"`
	Namespace  string            `json:"namespace"`
	Version    string            `json:"version"`
	Qualifiers map[string]string `json:"qualifiers"`
	Subpath    string            `json:"subpath"`
}

type Error struct {
	Error string `json:"error"`
}
