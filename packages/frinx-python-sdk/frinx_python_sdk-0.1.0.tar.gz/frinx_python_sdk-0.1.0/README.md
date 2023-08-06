# Frinx Python SDK

Some basic information about package ["TODO]


## Development

### Poetry useful commands

#### Virtual Environment activate
```shell
# Add dependency
poetry env use /path/to/python
# If you have the python executable in your PATH you can use it:
poetry env use python3.10

# Show env info
poetry env info
```

#### Add dependency
```shell
poetry init --python
```

#### Dependency management
```shell
# Add dependency
poetry add django@^4.0.0

# Remove dependency
poetry remove django
```

#### Package build
```shell
poetry build

# Verbose output
poetry build -vvv
```
