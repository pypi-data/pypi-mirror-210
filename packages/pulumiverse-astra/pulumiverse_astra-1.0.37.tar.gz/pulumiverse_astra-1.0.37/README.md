# Datastax Astra Provider

This provider lets you manage [Datastax Astra](https://astra.datastax.com/) resources.

## Installing

This package is available for several languages/platforms:

### Node.js (JavaScript/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

```bash
npm install @pulumiverse/astra
```

or `yarn`:

```bash
yarn add @pulumiverse/astra
```

### Python

To use from Python, install using `pip`:

```
$ pip install pulumiverse-astra
```

### Go

To use from Go, use `go get` to grab the latest version of the library:

```bash
go get github.com/pulumiverse/pulumi-astra/sdk/go/...
```

### .NET

To use from Dotnet, use `dotnet add package` to install into your project. You must specify the version if it is a pre-release version.


```
$ dotnet add package Pulumiverse.Astra
```

## Configuration

The following configuration points are available for the `astra` provider:

- `astra:token` - the API key to make changes in astra org. Please make sure that you grant it enough permissions for operations that you are going to perform. To create a token go into **organisation settings** -> **Token management**, select your role (I use **Administrator User** for full access) and press **Generate token**

## Reference

For detailed reference documentation, please visit [the Pulumi registry](https://www.pulumi.com/registry/packages/astra/api-docs/).
