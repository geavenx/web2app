# web2app

Convert websites into Linux desktop applications.

`web2app` creates `.desktop` entry files that launch websites in app mode using a Chromium-based browser, making them appear as standalone applications in your system menu.

## Features

- Create web apps from any URL
- Auto-detect display server (Wayland/X11)
- Support for multiple browsers (Chromium, Chrome, Brave, Edge)
- Auto-fetch favicon when icon URL not provided
- List, update, and remove installed web apps
- URL validation with helpful error messages

## Requirements

- Python 3.10+
- A Chromium-based browser (Chromium, Google Chrome, Brave, Microsoft Edge)
- `requests` library

## Installation

### From source (recommended)

```bash
git clone https://github.com/geavenx/web2app.git
cd web2app
pip install .
```

### Manual

```bash
git clone https://github.com/geavenx/web2app.git
cd web2app
pip install requests
chmod +x web2app.py
```

## Usage

### Add a web app

```bash
# With manual icon URL
web2app add Gmail https://mail.google.com https://example.com/gmail-icon.png

# Auto-fetch favicon (icon URL optional)
web2app add Spotify https://open.spotify.com

# Specify browser and platform
web2app add Discord https://discord.com/app icon.png --browser=brave-browser --platform=x11
```

### List installed web apps

```bash
web2app list
```

Output:
```
Installed web apps:
  Gmail                https://mail.google.com
  Spotify              https://open.spotify.com

Total: 2 web app(s)
```

### Update a web app

```bash
# Change URL
web2app update Gmail --url=https://workspace.google.com/mail

# Change icon
web2app update Gmail --icon=https://new-icon.png

# Rename
web2app update Gmail --rename=GoogleMail

# Combine options
web2app update Gmail --url=https://new-url.com --rename=NewGmail
```

### Remove a web app

```bash
web2app remove Gmail
```

### Help

```bash
web2app help
```

## Options

### Add command options

| Option | Description |
|--------|-------------|
| `--platform=<wayland\|x11>` | Display server (auto-detected if not specified) |
| `--browser=<name>` | Browser to use (auto-detected if not specified) |

### Supported browsers

- `chromium` / `chromium-browser`
- `google-chrome` / `google-chrome-stable`
- `brave-browser` / `brave`
- `microsoft-edge` / `microsoft-edge-stable`

### Update command options

| Option | Description |
|--------|-------------|
| `--url=<new_url>` | Change the webapp URL |
| `--icon=<new_icon_url>` | Change the webapp icon |
| `--rename=<new_name>` | Rename the webapp |

## How it works

web2app creates a `.desktop` file in `~/.local/share/applications/` that launches your chosen browser in "app mode" (`--app=URL`). Icons are stored in `~/.local/share/applications/icons/`.

## Finding icons

- [Dashboard Icons](https://dashboardicons.com) - Large collection of app icons
- Most websites have favicons that are auto-fetched when you don't provide an icon URL

## License

MIT License - see [LICENSE](LICENSE) for details.
