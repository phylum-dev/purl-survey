use std::io::{self, Write};
use std::str::FromStr;

use packageurl::PackageUrl;

mod json;

fn main() -> io::Result<()> {
    let mut line = String::new();
    loop {
        line.clear();
        io::stdin().read_line(&mut line)?;
        if line.is_empty() {
            break;
        }
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let mut out = io::stdout().lock();
        match PackageUrl::from_str(line) {
            Ok(purl) => serde_json::to_writer(&mut out, &json::Parts::from(&purl)).unwrap(),
            Err(e) => serde_json::to_writer(
                &mut out,
                &json::Error {
                    error: format!("{e:?}"),
                },
            )
            .unwrap(),
        }
        writeln!(out)?;
        out.flush()?;
    }

    Ok(())
}

impl From<&PackageUrl<'_>> for json::Parts {
    fn from(value: &PackageUrl<'_>) -> Self {
        Self {
            r#type: value.ty().to_owned(),
            namespace: value.namespace().map(ToOwned::to_owned),
            name: value.name().to_owned(),
            version: value.version().map(ToOwned::to_owned),
            qualifiers: value
                .qualifiers()
                .iter()
                .map(|(k, v)| ((**k).to_owned(), (**v).to_owned()))
                .collect(),
            subpath: value.subpath().map(ToOwned::to_owned),
        }
    }
}
