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

import sys
from pathlib import Path

import requests


def download_file(url: str, file_path: Path):
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)
    except requests.HTTPError as err:
        print(f"[ERROR] failed to download file: {file_path}\n{err}")
        exit(1)


def write_desktop_file(url: str, name: str, file_path: Path, icon_path: Path):
    content = f"""
[Desktop Entry]
Version=1.0
Name={name}
Comment={name}
Exec=chromium --new-window --ozone-platform=wayland --app={url} --name={name} --class={name}
Terminal=false
Type=Application
Icon={icon_path}
StartupNotify=true"""

    with open(file_path, "w") as f:
        f.write(content)

    file_path.chmod(0o755)


def create_app(name: str, url: str, icon_url: str):
    applications_dir = Path(f"{Path.home()}/.local/share/applications")
    icon_dir = Path(f"{applications_dir}/icons")
    icon_dir.mkdir(exist_ok=True, parents=True)

    desktop_file = Path(f"{applications_dir}/{name}.desktop")
    icon_path = Path(f"{icon_dir}/{name}.png")

    download_file(icon_url, icon_path)
    write_desktop_file(url, name, desktop_file, icon_path)


def remove_app(name: str):
    applications_dir = Path(f"{Path.home()}/.local/share/applications")
    icon_dir = Path(f"{applications_dir}/icons")
    icon_dir.mkdir(exist_ok=True, parents=True)

    desktop_file = Path(f"{applications_dir}/{name}.desktop")
    icon_path = Path(f"{icon_dir}/{name}.png")

    if not desktop_file.exists():
        print(f"[ERROR] webapp with name '{name}' does not exit.")
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
    print("    add <name> <url> <icon_url>        add a new webapp")
    print("    remove <name>                      remove a webapp")
    print("    help                               prints this usage message to stdout.")
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
            if len(argv) < 3:
                print("[ERROR] not enough arguments provided.\n")
                usage(program_name)
                exit(1)
            if len(argv) > 3:
                print("[ERROR] too many arguments provided.\n")
                usage(program_name)
                exit(1)
            name, url, icon_url = argv
            create_app(name, url, icon_url)
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
