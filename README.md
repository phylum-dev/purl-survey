# purl-survey

This repository contains code for exercising several PURL implementations.

- [althonos/packageurl.rs](https://github.com/althonos/packageurl.rs)
- [anchore/packageurl-go](https://github.com/anchore/packageurl-go)
- [giterlizzi/perl-URI-PackageURL](https://github.com/giterlizzi/perl-URI-PackageURL)
- [iseki0/PUrlKt](https://github.com/iseki0/PUrlKt)
- [maennchen/purl](https://github.com/maennchen/purl)
- [package-url/packageurl-dotnet](https://github.com/package-url/packageurl-dotnet)
- [package-url/packageurl-go](https://github.com/package-url/packageurl-go)
- [package-url/packageurl-java](https://github.com/package-url/packageurl-java)
- [package-url/packageurl-js](https://github.com/package-url/packageurl-js)
- [package-url/packageurl-php](https://github.com/package-url/packageurl-php)
- [package-url/packageurl-python](https://github.com/package-url/packageurl-python)
- [package-url/packageurl-ruby](https://github.com/package-url/packageurl-ruby)
- [package-url/packageurl-swift](https://github.com/package-url/packageurl-swift)
- [phylum-dev/purl](https://github.com/phylum-dev/purl)
- [sonatype/package-url-java](https://github.com/sonatype/package-url-java)

For each supported implementation, there are two small programs that read lines from stdin and write lines to stdout:

`parse`
: Parses a PURL and outputs a JSON description

`format`
: Parses a JSON description and outputs a PURL

These programs are in survey/drivers.

## Usage

```shell
# Create a virtual environment
python3 -m venv env
# Activate the virtual environment (command is different on Windows)
. env/bin/activate
# Install requirements into virtual environment.
pip install -r requirements.txt
# Build drivers for implementations.
python -m survey.build
```

### survey.parse

> Parse PURL to JSON

```
$ python -m survey.parse
pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
althonos/packageurl.rs: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
anchore/packageurl-go: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
giterlizzi/perl-URI-PackageURL: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
iseki0/PUrlKt: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
maennchen/purl: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-dotnet: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-go: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-java: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-js: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-php: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-python: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-ruby: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
package-url/packageurl-swift: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
phylum-dev/purl: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
sonatype/package-url-java: {"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
```

(press ^D to close stdin and exit)

### survey.format

> Format JSON to PURL

```
$ python -m survey.format
{"type": "deb", "name": "curl", "namespace": "debian", "version": "7.50.3-1", "qualifiers": {"arch": "i386", "distro": "jessie"}}
althonos/packageurl.rs: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
anchore/packageurl-go: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
giterlizzi/perl-URI-PackageURL: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
iseki0/PUrlKt: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
maennchen/purl: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-dotnet: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-go: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-java: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-js: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-php: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-python: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-ruby: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
package-url/packageurl-swift: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
phylum-dev/purl: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
sonatype/package-url-java: pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie
```

(press ^D to close stdin and exit)

### survey.check

> Parse PURL to JSON and format it back to PURL, ensuring that every PURL parses the same for all implementations.

```
$ python -m survey.check
pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?repository_url=repo.spring.io%2Frelease
pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?repository_url=repo.spring.io%2Frelease parsed to {"type": "maven", "name": "batik-anim", "namespace": "org.apache.xmlgraphics", "version": "1.9.1", "qualifiers": {"repository_url": "repo.spring.io/release"}}
Formatted as "pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?repository_url=repo.spring.io/release" by althonos/packageurl.rs, giterlizzi/perl-URI-PackageURL, maennchen/purl, phylum-dev/purl, iseki0/PUrlKt, sonatype/package-url-java, package-url/packageurl-python, package-url/packageurl-swift, package-url/packageurl-dotnet, package-url/packageurl-php
pkg:maven/org.apache.xmlgraphics/batik-anim@1.9.1?repository_url=repo.spring.io/release parsed to {"type": "maven", "name": "batik-anim", "namespace": "org.apache.xmlgraphics", "version": "1.9.1", "qualifiers": {"repository_url": "repo.spring.io/release"}}
```

(press ^D to close stdin and exit)

### survey.suite

> Run the PURL spec test suite.

Results are output as JSON.

```
$ python -m survey.suite
[
  {
    "implementation": "althonos/packageurl.rs",
    "code": "unexpected_success",
    "test": "invalid swift purl without name",
    "reason": "Expected an error for invalid purl pkg:swift/github.com/Alamofire/@5.4.3",
    "expected": "[error]",
    "actual": {
      "type": "swift",
      "name": "Alamofire",
      "namespace": "github.com",
      "version": "5.4.3"
    }
  },
…
```
