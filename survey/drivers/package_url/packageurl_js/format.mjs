#!/usr/bin/env node

import { PackageURL } from "packageurl-js";
import { createInterface } from "node:readline";

const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false,
});

for await (let line of rl) {
    line = line.trim();
    if (line === "") {
        continue;
    }
    const parts = JSON.parse(line);
    try {
        const purl = new PackageURL(parts.type, parts.namespace, parts.name, parts.version, parts.qualifiers, parts.subpath);
        console.log(purl.toString());
    } catch (e) {
        console.log(JSON.stringify({"error": e.toString()}));
    }
}
