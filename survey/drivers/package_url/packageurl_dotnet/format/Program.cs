using System.Text;
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
    var parts = JsonSerializer.Deserialize<Parts>(line, options)!;
    try
    {
        var purl = new PackageURL(parts.Type, parts.Namespace, parts.Name, parts.Version, parts.Qualifiers, parts.Subpath);
        output.Write(Encoding.UTF8.GetBytes(purl.ToString()));
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
