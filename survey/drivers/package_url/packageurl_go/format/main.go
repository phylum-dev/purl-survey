package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/package-url/packageurl-go"
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
		err = purl.Normalize()
		if err == nil {
			fmt.Println(purl)
		} else {
			parts := model.Error{
				Error: fmt.Sprint(err),
			}
			out, err := json.Marshal(parts)
			if err != nil {
				panic(err)
			}
			_, err = os.Stdout.Write(out)
			if err != nil {
				panic(err)
			}
			_, err = os.Stdout.WriteString("\n")
			if err != nil {
				panic(err)
			}
		}
	}
}
