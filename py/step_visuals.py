"""Step visuals: the eight vagueness / uncertainty case figures (PF.1-3, PC.1-4, IC-PC.1) -> visuals/site/."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "visuals"))


def main() -> int:
    import build
    build.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
