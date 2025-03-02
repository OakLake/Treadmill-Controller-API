# Bluetooth Enabled Treadmill Controller

A bluetooth enabled treadmill might advertise itself as a Fitness Machine Service (FTMS), the FTMS is a protocol of communication and control defined by Bluetooth, this enables any Bluetooth enabled device to communicate and control the treadmill in a pre-defined way.

## Setup

```bash
uv sync
uv venv
source venv/bin/activate
```

## Launch app
### Launch TUI
```bash
uv run poe serve_tui
```
### Launch TUI as webapp
```bash
uv run poe serve_tui_webapp
```

### Launch API
```bash
uv run poe serve_api
```