using System.Text.Json;

using PackageUrl;

var output = Console.OpenStandardOutput();
var options = new JsonSerializerOptions {
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
};

while (true)
{
    var line = Console.ReadLine();
    if (line is null)
    {
        break;
    }
    if (line == "")
    {
        continue;
    }
    try
    {
        var purl = new PackageURL(line);
        var parts = new Parts
        {
            Type = purl.Type!,
            Name = purl.Name!,
            Namespace = purl.Namespace,
            Version = purl.Version,
            Qualifiers = purl.Qualifiers!,
            Subpath = purl.Subpath,
        };
        JsonSerializer.Serialize(output, parts, options);
    }
    catch (MalformedPackageUrlException e)
    {
        var error = new ErrorModel
        {
            Error = e.ToString(),
        };
        JsonSerializer.Serialize(output, error, options);
    }
    output.WriteByte((byte)'\n');
    output.Flush();
}
