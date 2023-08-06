# DESCRIPTION
This python script compares tls cipher suites of a server to baselines.

Cipher suites are retrieved with the testssl.sh shell script (https://github.com/drwetter/testssl.sh).

# INSTALLATION

## DO NOT INSTALL WITH PIP

## DO *NOT* INSTALL WITH SUDO PIP

This is a public Headmind Tool, so it is hosted on the public PyPI (Python Package Index).
Install it with pipx:

```sh
pipx install sslcompare
```

# USAGE
```sh
sslcompare https://headmind.com
sslcompare -b my/baseline/file.yaml https://potato:8443
sslcompare 128.0.0.56:2244
```
# Baseline files :

Each TLS cipher suite can be either :
- RECOMMENDED
- DEGRADED
- DEPRECATED

Baseline are YAML files.
The default baseline file is anssi.yaml (ANSSI recommendations).
If you followed the recommanded installation instructions (installing with pipx), the baseline should be:
~/.local/pipx/venvs/sslcompare/lib/python3.11/site-packages/sslcompare/anssi.yaml
