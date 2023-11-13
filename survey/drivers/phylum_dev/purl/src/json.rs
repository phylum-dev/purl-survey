use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct Parts {
    pub r#type: String,
    pub namespace: Option<String>,
    pub name: String,
    pub version: Option<String>,
    #[serde(default)]
    pub qualifiers: BTreeMap<String, String>,
    pub subpath: Option<String>,
}

#[derive(Serialize)]
pub struct Error {
    pub error: String,
}
