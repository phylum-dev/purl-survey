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
    try {
        const purl = PackageURL.fromString(line);
        console.log(JSON.stringify({
            "type": purl.type,
            "name": purl.name,
            "namespace": purl.namespace,
            "version": purl.version,
            "qualifiers": purl.qualifiers,
            "subpath": purl.subpath,
        }))
    } catch (e) {
        console.log(JSON.stringify({"error": e.toString()}));
    }
}
