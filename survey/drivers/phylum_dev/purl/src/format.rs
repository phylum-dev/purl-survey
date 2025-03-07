use std::io::{self, Write};
use std::str::FromStr;

use purl::{GenericPurl, PackageType, PurlShape};

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
        let parts: json::Parts = match serde_json::from_str(line) {
            Ok(parts) => parts,
            Err(error) => {
                let mut out = io::stdout().lock();
                serde_json::to_writer(
                    &mut out,
                    &json::Error {
                        error: error.to_string(),
                    },
                )
                .unwrap();
                writeln!(io::stdout().lock())?;
                out.flush()?;
                continue;
            }
        };
        let purl = if let Ok(r#type) = PackageType::from_str(&parts.r#type) {
            build(r#type, &parts).map_err(|e| format!("{e:?}"))
        } else {
            build(parts.r#type.clone(), &parts).map_err(|e| format!("{e:?}"))
        };
        let mut out = io::stdout().lock();
        match purl {
            Ok(purl) => writeln!(out, "{purl}")?,
            Err(error) => {
                serde_json::to_writer(&mut out, &json::Error { error }).unwrap();
                writeln!(out)?;
            }
        }
        out.flush()?;
    }

    Ok(())
}

fn build<T>(r#type: T, parts: &json::Parts) -> Result<String, T::Error>
where
    T: PurlShape,
{
    let mut builder = GenericPurl::builder(r#type, &parts.name);
    if let Some(namespace) = &parts.namespace {
        builder = builder.with_namespace(namespace);
    }
    if let Some(version) = &parts.version {
        builder = builder.with_version(version);
    }
    for (k, v) in parts.qualifiers.iter() {
        builder = builder.with_qualifier(k, v)?;
    }
    if let Some(subpath) = &parts.subpath {
        builder = builder.with_subpath(subpath);
    }
    Ok(builder.build()?.to_string())
}
