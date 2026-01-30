#!/usr/bin/env python3

# source code: https://github.com/geavenx/web2app

# The files in this repository are licensed under the MIT license unless otherwise
# specified in the file header.
#
# MIT License
#
# Copyright (c) 2025 Vitor Cardoso vitordonnangeloc@proton.me
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.models import MissingSchema

# Supported Chromium-based browsers in order of preference
SUPPORTED_BROWSERS = [
    "helium-browser",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "brave-browser",
    "brave",
    "microsoft-edge",
    "microsoft-edge-stable",
]


def detect_browser() -> str | None:
    """Auto-detect the first available Chromium-based browser."""
    for browser in SUPPORTED_BROWSERS:
        if shutil.which(browser):
            return browser
    return None


def detect_display_server() -> str:
    """Auto-detect the display server (wayland or x11)."""
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        return "wayland"
    return "x11"


def validate_url(url: str, url_type: str = "URL") -> bool:
    """Validate that a URL has proper format (http:// or https://)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            print(f"[ERROR] invalid {url_type}: '{url}'")
            print(f"-> {url_type} must start with http:// or https://")
            return False
        if not parsed.netloc:
            print(f"[ERROR] invalid {url_type}: '{url}'")
            print(f"-> {url_type} is missing a domain")
            return False
        return True
    except Exception:
        print(f"[ERROR] failed to parse {url_type}: '{url}'")
        return False


def validate_icon_url(url: str) -> bool:
    """Validate that an icon URL points to an image."""
    if not validate_url(url, "icon URL"):
        return False

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        valid_types = [
            "image/png",
            "image/x-icon",
            "image/ico",
            "image/jpeg",
            "image/svg+xml",
            "image/webp",
        ]

        if not any(t in content_type for t in valid_types):
            print(
                f"[WARNING] icon URL may not be a valid image (Content-Type: {content_type})"
            )
            print("-> continuing anyway, but the icon might not display correctly")

        return True
    except requests.RequestException as err:
        print(f"[WARNING] could not verify icon URL: {err}")
        print("-> continuing anyway, but the icon might not work")
        return True  # Allow to continue, download_file will catch actual errors


def download_file(url: str, file_path: Path):
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)
    except requests.HTTPError as err:
        print(f"[ERROR] failed to download file: {file_path}.\nerror trace: {err}\n")
        exit(1)
    except MissingSchema as err:
        print(f"[ERROR] failed to parse icon url: {url}.\nerror trace: {err}\n")
        exit(1)


def write_desktop_file(
        url: str, name: str, file_path: Path, icon_path: Path, platform: str, browser: str
):
    platform_flag = f"--ozone-platform={platform}" if platform else ""
    content = f"""
[Desktop Entry]
Version=1.0
Name={name}
Comment={name}
Exec={browser} --new-window {platform_flag} --app={url} --name={name} --class={name}
>>>>>>> f03086e (feat: support multiple Chromium-based browsers)
Terminal=false
Type=Application
Icon={icon_path}
StartupNotify=true"""

    with open(file_path, "w") as f:
        f.write(content)

    file_path.chmod(0o755)


def create_app(name: str, url: str, icon_url: str, platform: str | None = None, browser: str | None = None):

    # Validate URLs before proceeding
    if not validate_url(url, "webapp URL"):
        exit(1)
    if not validate_icon_url(icon_url):
        exit(1)

    if platform is None:
        platform = detect_display_server()

    if browser is None:
        browser = detect_browser()
        if browser is None:
            print("[ERROR] no supported browser found.")
            print("-> supported browsers: " + ", ".join(SUPPORTED_BROWSERS))
            exit(1)

    applications_dir = Path(f"{Path.home()}/.local/share/applications")
    icon_dir = Path(f"{applications_dir}/icons")
    icon_dir.mkdir(exist_ok=True, parents=True)

    desktop_file = Path(f"{applications_dir}/{name}.desktop")
    icon_path = Path(f"{icon_dir}/{name}.png")

    download_file(icon_url, icon_path)
    write_desktop_file(url, name, desktop_file, icon_path, platform, browser)


def remove_app(name: str):
    applications_dir = Path(f"{Path.home()}/.local/share/applications")
    icon_dir = Path(f"{applications_dir}/icons")
    icon_dir.mkdir(exist_ok=True, parents=True)

    desktop_file = Path(f"{applications_dir}/{name}.desktop")
    icon_path = Path(f"{icon_dir}/{name}.png")

    if not desktop_file.exists():
        print(f"[ERROR] webapp with name '{name}' does not exist.")
        print("-> tip: make sure that the case is matching.")
        exit(1)

    if not icon_path.exists():
        print(f"[WARNING] webapp icon with name '{name}' not found.")
        desktop_file.unlink()
        return

    desktop_file.unlink()
    icon_path.unlink()


def usage(program_name: str):
    print(f"Usage: {program_name} <SUBCOMMAND> [ARGS]")
    print("Subcommands:")
    print("    add <name> <url> <icon_url> [--platform=<wayland|x11>] [--browser=<name>]")
    print("                                   add a new webapp")
    print("    remove <name>                  remove a webapp")
    print("    help                           prints this usage message to stdout.")
    print("\nOptions:")
    print(
        "    --platform=<wayland|x11>       display server (auto-detected if not specified)"
    )
    print(
        "    --browser=<name>               browser to use (auto-detected if not specified)"
    )
    print(
        "                                   supported: " + ", ".join(SUPPORTED_BROWSERS)
    )
    print("\nFYI: `<icon_url>` must be a png file, use: https://dashboardicons.com")


def main():
    argv = sys.argv
    program_name, *argv = argv

    if len(argv) < 1:
        print("[ERROR] no subcommand provided.\n")
        usage(program_name)
        exit(1)

    subcommand, *argv = argv
    match subcommand:
        case "add":
            # Parse optional --platform flag
            platform = None
            browser = None
            positional_args = []
            for arg in argv:
                if arg.startswith("--platform="):
                    platform = arg.split("=", 1)[1]
                    if platform not in ("wayland", "x11"):
                        print(
                            f"[ERROR] invalid platform '{platform}'. Must be 'wayland' or 'x11'.\n"
                        )
                        usage(program_name)
                        exit(1)

                if arg.startswith("--browser="):
                    browser = arg.split("=", 1)[1]
                else:
                    positional_args.append(arg)

            if len(positional_args) < 3:
                print("[ERROR] not enough arguments provided.\n")
                usage(program_name)
                exit(1)
            if len(positional_args) > 3:
                print("[ERROR] too many arguments provided.\n")
                usage(program_name)
                exit(1)
            name, url, icon_url = positional_args
            create_app(name, url, icon_url, platform, browser)
            print(f"{program_name}: web-app '{name}' created successfully.")
            exit(0)

        case "remove":
            if len(argv) < 1:
                print("[ERROR] not enough arguments provided.\n")
                usage(program_name)
                exit(1)
            if len(argv) > 1:
                print("[ERROR] too many arguments provided.\n")
                usage(program_name)
                exit(1)
            name = argv[0]
            remove_app(name)
            print(f"{program_name}: web-app '{name}' deleted successfully.")
            exit(0)
        case "help":
            usage(program_name)
            exit(0)
        case _:
            print("[ERROR] unknown subcommand provided.\n")
            usage(program_name)
            exit(1)


if __name__ == "__main__":
    main()
