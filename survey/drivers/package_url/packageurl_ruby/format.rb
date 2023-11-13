#!/usr/bin/env ruby

require 'json'

require_relative 'repo/lib/package_url'

STDIN.each_line {|line|
    line.chomp!
    return if line.empty?

    parts = JSON.parse(line)

    begin
        purl = PackageURL.new(
            type: parts["type"],
            name: parts["name"],
            namespace: parts["namespace"],
            version: parts["version"],
            qualifiers: parts["qualifiers"],
            subpath: parts["subpath"]
        )
        puts purl
    rescue => error
        puts JSON.generate({
            error: error.to_s,
        })
    end
    STDOUT.flush
}
