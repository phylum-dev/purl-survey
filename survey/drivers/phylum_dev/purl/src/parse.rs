use std::io::{self, Write};
use std::str::FromStr;

use purl::{GenericPurl, PackageError, Purl};

mod json;

type StringPurl = GenericPurl<String>;

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
        let parts: Result<json::Parts, json::Error> = match Purl::from_str(line) {
            Ok(purl) => Ok((&purl).into()),
            Err(PackageError::UnsupportedType) => match StringPurl::from_str(line) {
                Ok(purl) => Ok((&purl).into()),
                Err(e) => Err(json::Error {
                    error: format!("{e:?}"),
                }),
            },
            Err(e) => Err(json::Error {
                error: format!("{e:?}"),
            }),
        };
        let mut out = io::stdout().lock();
        match parts {
            Ok(parts) => serde_json::to_writer(&mut out, &parts).unwrap(),
            Err(error) => serde_json::to_writer(&mut out, &error).unwrap(),
        }
        writeln!(out)?;
        out.flush()?;
    }

    Ok(())
}

impl<T> From<&GenericPurl<T>> for json::Parts
where
    T: ToString,
{
    fn from(value: &GenericPurl<T>) -> Self {
        Self {
            r#type: value.package_type().to_string(),
            namespace: value.namespace().map(ToOwned::to_owned),
            name: value.name().to_owned(),
            version: value.version().map(ToOwned::to_owned),
            qualifiers: value
                .qualifiers()
                .iter()
                .map(|(k, v)| (k.as_str().to_owned(), v.to_owned()))
                .collect(),
            subpath: value.subpath().map(ToOwned::to_owned),
        }
    }
}
