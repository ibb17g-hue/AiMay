"""
AiMay Engine v0.2
=================
Виконує .aim файли команда за командою. На відміну від v0.1:
  - команди — плагіни (commands/*.py, реєстрація через @command)
  - пам'ять Intent — ContextGraph, не dict
  - простір — AiMaySpaceSimulator з персистентним станом між командами
  - FORK/CHECK пов'язані через реальний BFS-резонанс, не хардкод
  - Bridge — двофазний (PENDING → FULFILLED)
"""

import re
import sys
import time
from datetime import datetime
from typing import Optional

from .colors import C
from .intent import Intent
from .bridge import Bridge
from .dissonance import Dissonance
from .space_simulator import AiMaySpaceSimulator
import commands  # реєструє всі плагіни через побічний ефект імпорту


class AiMayEngine:
    VERSION = "0.2.0"

    def __init__(self, seed: int = None):
        self.intents:     dict[str, Intent] = {}
        self.bridges:     dict[str, Bridge] = {}
        self.dissonances: list[Dissonance]  = []
        self.log_lines:   list[str]         = []
        self.current:     Optional[Intent]  = None
        self.space = AiMaySpaceSimulator(seed=seed)
        self.last_fork_results: list[tuple[str, float]] = []  # (candidate_id, score), спадання
        self._start_time = time.time()

    # ── Логування ────────────────────────────────────────────────────────

    def _log(self, cmd: str, msg: str, color: str = C.WHITE):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
        tag = f"{color}{C.BOLD}[{cmd:6}]{C.RESET}"
        line = f"  {C.GRAY}{ts}{C.RESET}  {tag}  {msg}"
        print(line)
        self.log_lines.append(f"[{cmd:6}] {msg}")

    def _separator(self, title: str = ""):
        if title:
            print(f"\n  {C.CYAN}{'─'*20} {title} {'─'*20}{C.RESET}\n")
        else:
            print(f"  {C.GRAY}{'─'*54}{C.RESET}")

    # ── Парсер ───────────────────────────────────────────────────────────

    def _parse_line(self, line: str):
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            return

        parts = re.findall(r'"[^"]*"|\S+', line)
        cmd  = parts[0].upper()
        args = parts[1:]

        handler = commands.COMMAND_REGISTRY.get(cmd)
        if handler:
            handler(self, args)
        else:
            self._log("WARN", f"{C.YELLOW}невідома команда: {cmd}{C.RESET}", C.YELLOW)

    # ── Запуск ───────────────────────────────────────────────────────────

    def run_file(self, path: str):
        try:
            with open(path, encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"\n  {C.RED}Файл не знайдено: {path}{C.RESET}\n")
            sys.exit(1)

        self._print_header(path)
        for line in source.splitlines():
            self._parse_line(line)
        self._print_summary()

    def run_source(self, source: str, header: str = ""):
        if header:
            self._separator(header)
        for line in source.splitlines():
            self._parse_line(line)

    def _print_header(self, source: str):
        print(f"\n  {C.CYAN}{C.BOLD}{'═'*54}{C.RESET}")
        print(f"  {C.CYAN}{C.BOLD}  AiMay Engine v{self.VERSION}{C.RESET}")
        print(f"  {C.GRAY}  {source}{C.RESET}")
        print(f"  {C.CYAN}{C.BOLD}{'═'*54}{C.RESET}\n")

    def _print_summary(self):
        elapsed = round(time.time() - self._start_time, 3)

        print(f"\n  {C.CYAN}{'─'*54}{C.RESET}")
        print(f"  {C.BOLD}Підсумок виконання:{C.RESET}")
        print(f"    Intents створено : {C.GREEN}{len(self.intents)}{C.RESET}")

        fulfilled = sum(1 for i in self.intents.values() if i.status == Intent.FULFILLED)
        suspended = sum(1 for i in self.intents.values() if i.status == Intent.SUSPENDED)
        print(f"    Fulfilled        : {C.GREEN}{fulfilled}{C.RESET}")
        if suspended:
            print(f"    Suspended        : {C.YELLOW}{suspended}{C.RESET}")

        open_bridges = sum(1 for b in self.bridges.values() if b.is_open())
        print(f"    Bridges          : {C.YELLOW}{len(self.bridges)}{C.RESET}"
              f"{'  (' + str(open_bridges) + ' ще PENDING!)' if open_bridges else ''}")
        print(f"    Dissonances      : "
              f"{C.RED if self.dissonances else C.GRAY}{len(self.dissonances)}{C.RESET}")
        print(f"    Час виконання    : {C.GRAY}{elapsed}s{C.RESET}")

        if self.intents:
            print(f"\n  {C.BOLD}Граф Intent:{C.RESET}")
            for name, intent in self.intents.items():
                status_color = C.GREEN if intent.status == Intent.FULFILLED else C.YELLOW
                bonds = (f"  bonds:{[f'{a}↔{b}' for a, b, _ in intent.bonds]}"
                         if intent.bonds else "")
                mem = (f"  memory:{list(intent.context.nodes.keys())}"
                       if intent.context.nodes else "")
                print(f"    {C.CYAN}{name}{C.RESET} "
                      f"[{status_color}{intent.status}{C.RESET}]"
                      f"{C.GRAY}{bonds}{mem}{C.RESET}")

        if self.dissonances:
            print(f"\n  {C.BOLD}Dissonances на ребрах графа:{C.RESET}")
            for ds in self.dissonances:
                print(f"    {C.RED}{ds}{C.RESET}")

        print(f"\n  {C.CYAN}{'═'*54}{C.RESET}\n")
