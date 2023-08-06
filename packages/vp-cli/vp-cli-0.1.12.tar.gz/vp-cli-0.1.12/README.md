# vp_cli
[![vp-cli](https://github.com/corsis-tech/vp-cli/actions/workflows/build-vp-cli.yml/badge.svg)](https://github.com/corsis-tech/vp-cli/actions/workflows/build-vp-cli.yml)

Command Line interface for VantagePoint

## Installation and Documentation
The full documentation is available [here](https://vantagepointsecurity.gitlab.io/platform-components/utilities/vp_cli)

## Development
- In-container development environment

```console
$ make shell
```
Use [.env](https://gitlab.com/vantagepointsecurity/platform-components/utilities/vp_cli/-/blob/staging/.env) file to set development environment

- To install cli (Also works inside development container)
```console
$ make install
```

- Running tests
```console
$ tox
```
Use `tox.ini` to set the test environment [here](https://gitlab.com/vantagepointsecurity/platform-components/utilities/vp_cli/-/blob/staging/tox.ini#L4)

- To build `.deb`, `.rpm` and `.tar.gz` packages

```console
$ make build_all
```
This will build and place the artifacts in `build` dir

- To build and push to artifactory
```
$ make release
```

- To clean up and uninstall cli

```console
$ make clean
```

- Documentation

Updates to documentation are made in the [docs](https://gitlab.com/vantagepointsecurity/platform-components/utilities/vp_cli/-/tree/staging/docs) directory.
To generate html
```console
$ cd docs
$ make html # this will generate html in the docs/build dir
```


