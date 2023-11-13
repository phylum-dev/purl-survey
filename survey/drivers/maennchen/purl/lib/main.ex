defmodule Driver do
  def run() do
    f = case Enum.at(System.argv(), 0) do
      "parse" -> &parse/1
      "format" -> &format/1
    end
    
    IO.stream()
    |> Stream.map(&String.trim/1)
    |> Stream.reject(fn l -> l == "" end)
    |> Stream.map(f)
    |> Stream.each(&IO.puts/1)
    |> Stream.run()
  end

  defp parse(purl) do
    case Purl.new(purl) do
      {:ok, purl} ->
        JSON.encode!(
          type: purl.type,
          name: purl.name,
          namespace: Enum.join(purl.namespace, "/"),
          version: purl.version,
          qualifiers: purl.qualifiers,
          subpath: Enum.join(purl.subpath, "/")
        )

      {:error, error} ->
        JSON.encode!(error: Exception.message(error))
    end
  end

  defp format(parts) do
    parts = JSON.decode!(parts)
    namespace = case parts["namespace"] do
      nil -> []
      ns -> String.split(ns, "/")
    end
    subpath = case parts["subpath"] do
      nil -> []
      sp -> String.split(sp, "/")
    end

    %Purl{
      type: parts["type"],
      name: parts["name"],
      namespace: namespace,
      version: parts["version"],
      qualifiers: parts["qualifiers"] || %{},
      subpath: subpath,
    }
  end
end
