A simple script `wait-for-docker` to wait for Docker daemon to be active.

## Installation

With `pipx`:

```bash
pipx install wait-for-docker
```

With `pip`:

```bash
python3 -m pip install wait-for-docker
```

## Usage

```bash
wait-for-docker && command_which_uses_docker
```

The command waits until Docker daemon gets active. There's no configuration.
