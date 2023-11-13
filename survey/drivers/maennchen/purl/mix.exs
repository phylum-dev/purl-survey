defmodule Driver.MixProject do
  use Mix.Project

  def project do
    [
      app: :driver,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      registered: [Driver]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:json, "~> 1.4"},
      {:purl, path: "repo"}
    ]
  end
end
