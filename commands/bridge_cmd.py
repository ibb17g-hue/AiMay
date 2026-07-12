from engine.colors import C
from engine.bridge import Bridge
from .registry import command


@command("BRIDGE")
def cmd_bridge(engine, args: list):
    """BRIDGE <name> origin:<x> capabilities:[...] scope:<x>"""
    name  = args[0]
    caps  = ["read"]
    scope = "*"
    origin = "Human"

    joined = " ".join(args[1:])
    if "capabilities:" in joined:
        start = joined.index("capabilities:") + len("capabilities:")
        caps_raw = joined[start:].split("]")[0].strip("[ ")
        caps = [c.strip(" ,") for c in caps_raw.split(",")]
    if "scope:" in joined:
        scope = joined.split("scope:")[1].strip().split()[0]

    bridge = Bridge(name, origin, caps, scope)
    engine.bridges[name] = bridge

    engine._log("BRIDGE", (
        f"{C.YELLOW}{name}{C.RESET} "
        f"origin:{C.GREEN}{origin}{C.RESET}  "
        f"capabilities:{C.MAGENTA}{caps}{C.RESET}  "
        f"scope:{C.GRAY}{scope}{C.RESET}  "
        f"state:{C.YELLOW}{bridge.state}{C.RESET}"
    ), C.YELLOW)
