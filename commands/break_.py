from engine.colors import C
from engine.dissonance import Dissonance
from .registry import command


@command("BREAK")
def cmd_break(engine, args: list):
    """BREAK <a> <b>"""
    expr = " ".join(args)

    if engine.current:
        ds = Dissonance(
            source=engine.current.name, target=expr,
            reason="explicit BREAK", pattern=Dissonance.DECLARED,
        )
        engine.dissonances.append(ds)

    engine._log("BREAK", (
        f"{C.RED}⊗{C.RESET} резонанс {C.RED}{expr}{C.RESET} "
        f"— зв'язок не створено, Dissonance на ребрі"
    ), C.RED)
