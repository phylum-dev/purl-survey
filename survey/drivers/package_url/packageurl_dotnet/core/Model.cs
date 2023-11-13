using System.Collections.Generic;

public class Parts
{
    public string? Type { get; set; }
    public string? Name { get; set; }
    public string? Namespace { get; set; }
    public string? Version { get; set; }
    public SortedDictionary<string, string>? Qualifiers { get; set; }
    public string? Subpath { get; set; }
}

public class ErrorModel
{
    public string Error { get; set; } = "";
}
