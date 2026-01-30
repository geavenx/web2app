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
import re
import sys
from pathlib import Path

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


def list_apps():
    """List all web apps created by web2app."""
    applications_dir = Path(f"{Path.home()}/.local/share/applications")
    icon_dir = Path(f"{applications_dir}/icons")

    if not applications_dir.exists():
        print("No web apps found.")
        return

    webapps = []
    for desktop_file in applications_dir.glob("*.desktop"):
        try:
            content = desktop_file.read_text()
            # Check if this is a web2app-created file (has --app= in Exec line)
            if "--app=" not in content:
                continue

            # Parse name and URL
            name_match = re.search(r"^Name=(.+)$", content, re.MULTILINE)
            exec_match = re.search(r"--app=(\S+)", content)

            if name_match and exec_match:
                name = name_match.group(1)
                url = exec_match.group(1)
                icon_path = Path(f"{icon_dir}/{desktop_file.stem}.png")
                has_icon = icon_path.exists()
                webapps.append((name, url, has_icon))
        except Exception:
            continue

    if not webapps:
        print("No web apps found.")
        return

    print("Installed web apps:")
    for name, url, has_icon in webapps:
        icon_status = "" if has_icon else " (no icon)"
        print(f"  {name:20} {url}{icon_status}")
    print(f"\nTotal: {len(webapps)} web app(s)")


def usage(program_name: str):
    print(f"Usage: {program_name} <SUBCOMMAND> [ARGS]")
    print("Subcommands:")
    print("    add <name> <url> <icon_url> [--platform=<wayland|x11>] [--browser=<name>]")
    print("                                   add a new webapp")
    print("    list                           list all installed webapps")
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


if __name__ == "__main__":
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
        case "list":
            list_apps()
            exit(0)
        case "help":
            usage(program_name)
            exit(0)
        case _:
            print("[ERROR] unknown subcommand provided.\n")
            usage(program_name)
            exit(1)
