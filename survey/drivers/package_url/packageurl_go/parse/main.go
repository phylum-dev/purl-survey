package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/matt-phylum/purl-driver/model"
	"github.com/package-url/packageurl-go"
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
		purl, err := packageurl.FromString(line)
		if err == nil {
			parts := model.Parts{
				Type:       purl.Type,
				Name:       purl.Name,
				Namespace:  purl.Namespace,
				Version:    purl.Version,
				Qualifiers: purl.Qualifiers.Map(),
				Subpath:    purl.Subpath,
			}
			out, err := json.Marshal(parts)
			if err != nil {
				panic(err)
			}
			_, err = os.Stdout.Write(out)
			if err != nil {
				panic(err)
			}
		} else {
			error := model.Error{
				Error: fmt.Sprint(err),
			}
			out, err := json.Marshal(error)
			if err != nil {
				panic(err)
			}
			_, err = os.Stdout.Write(out)
			if err != nil {
				panic(err)
			}
		}
		_, err = os.Stdout.WriteString("\n")
		if err != nil {
			panic(err)
		}
	}
}
