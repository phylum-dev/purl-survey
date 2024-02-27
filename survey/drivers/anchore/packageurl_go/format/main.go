package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/anchore/packageurl-go"
	"github.com/phylum-dev/purl-survey/model"
)

func main() {
	in := bufio.NewReader(os.Stdin)
	for {
		line, _ := in.ReadString('\n')
		if line == "" {
			break
		}
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		var parts model.Parts
		err := json.Unmarshal([]byte(line), &parts)
		if err != nil {
			panic(err)
		}
		purl := packageurl.PackageURL{
			Type:       parts.Type,
			Name:       parts.Name,
			Namespace:  parts.Namespace,
			Version:    parts.Version,
			Qualifiers: packageurl.QualifiersFromMap(parts.Qualifiers),
			Subpath:    parts.Subpath,
		}
		fmt.Println(purl)
	}
}
