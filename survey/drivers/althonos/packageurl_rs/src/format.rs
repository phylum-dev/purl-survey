use std::io::{self, Write};

use packageurl::{Error, PackageUrl};

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
                writeln!(out)?;
                out.flush()?;
                continue;
            }
        };
        let mut out = io::stdout().lock();
        match build(&parts) {
            Ok(purl) => writeln!(out, "{purl}")?,
            Err(error) => {
                serde_json::to_writer(
                    &mut out,
                    &json::Error {
                        error: format!("{error:?}"),
                    },
                )
                .unwrap();
                writeln!(out)?;
            }
        }
        out.flush()?;
    }

    Ok(())
}

fn build(parts: &json::Parts) -> Result<PackageUrl, Error> {
    let mut builder = PackageUrl::new(&parts.r#type, &parts.name)?;
    if let Some(namespace) = &parts.namespace {
        builder.with_namespace(namespace);
    }
    if let Some(version) = &parts.version {
        builder.with_version(version);
    }
    for (k, v) in parts.qualifiers.iter() {
        builder.add_qualifier(k, v)?;
    }
    if let Some(subpath) = &parts.subpath {
        builder.with_subpath(subpath)?;
    }
    Ok(builder)
}
