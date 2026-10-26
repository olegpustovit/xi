#!/usr/bin/env python3
"""Prove a yank inside tmux reaches the outer terminal as OSC52 even when tmux forwards nothing.

The outer PTY stands in for mosh/ssh. tmux runs with `set-clipboard off` and
`allow-passthrough off`, so neither tmux's own OSC52 nor DCS passthrough can carry the
sequence: only Xi's direct write to `#{client_tty}` can make `ESC ] 52 ; c ; ...` appear.
"""
from __future__ import annotations

import base64
import os
import pty
import select
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_for(master: int, captured: bytearray, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not select.select([master], [], [], 0.05)[0]:
            continue
        try:
            captured.extend(os.read(master, 65536))
        except OSError:
            return


if shutil.which("tmux") is None:
    raise SystemExit("tmux is required for the tmux OSC52 PTY check")

with tempfile.TemporaryDirectory(prefix="xi-tmux-osc52-pty-") as temporary:
    workspace = Path(temporary)
    source = workspace / "main.txt"
    source.write_text("one\ntwo\n", encoding="utf-8")
    tmux_conf = workspace / "tmux.conf"
    tmux_conf.write_text("set -s set-clipboard off\nset -g allow-passthrough off\nset -g status off\n", encoding="utf-8")
    socket = workspace / "tmux.sock"
    environment = os.environ.copy()
    environment.pop("TMUX", None)
    environment.update({"HOME": temporary, "TERM": "xterm-256color", "SSH_CONNECTION": "10.0.0.1 1 10.0.0.2 22"})
    xi = f"bun run {ROOT / 'apps/xi/src/main.ts'} {source}"

    master, slave = pty.openpty()
    child = subprocess.Popen(
        ["tmux", "-S", str(socket), "-f", str(tmux_conf), "new-session", xi],
        cwd=ROOT,
        env=environment,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    captured = bytearray()
    expected = b"\x1b]52;c;" + base64.b64encode(b"one\n") + b"\x07"
    try:
        read_for(master, captured, 4)
        os.write(master, b'"+yy')
        deadline = time.monotonic() + 5
        while expected not in captured and time.monotonic() < deadline:
            read_for(master, captured, 0.05)
        if expected not in captured:
            raise SystemExit(f"yank inside tmux never reached the outer terminal as OSC52: {captured[-3000:]!r}")
    finally:
        subprocess.run(["tmux", "-S", str(socket), "kill-server"], check=False, capture_output=True)
        if child.poll() is None:
            child.kill()
        child.wait()
        os.close(master)

print("tmux OSC52 PTY passed: yank reached the client tty with set-clipboard and passthrough off.")
