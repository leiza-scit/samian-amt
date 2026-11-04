"""Step visuals: case figures (PF.1-4, PC.1-4, IC-PC.1) and model figures in the visuals style -> docs/visuals/."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "visuals"))


def main() -> int:
    import build
    import chain_pages
    import model_figs
    import afe_roundtrip_figs
    import roundtrip_figs
    model_figs.main()      # first: the overview page of build.main() shows a model figure
    roundtrip_figs.main()
    afe_roundtrip_figs.main()
    chain_pages.main()
    build.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
