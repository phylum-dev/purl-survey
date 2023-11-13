#!/usr/bin/env ruby

require 'json'

require_relative 'repo/lib/package_url'

STDIN.each_line {|line|
    line.chomp!
    return if line.empty?

    begin
        purl = PackageURL.parse(line)

        puts JSON.generate({
            type: purl.type,
            name: purl.name,
            namespace: purl.namespace,
            version: purl.version,
            qualifiers: purl.qualifiers,
            subpath: purl.subpath,
        })
    rescue => error
        puts JSON.generate({
            error: error.to_s,
        })
    end
    STDOUT.flush
}
