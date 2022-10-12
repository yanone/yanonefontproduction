import logging

from ufo2ft.filters import BaseFilter
from fontTools.pens.boundsPen import ControlBoundsPen

logger = logging.getLogger(__name__)


def _find_anchor(glyph, name):
    for anchor in glyph.anchors:
        if anchor.name == name:
            return anchor


def get_controlPointBounds(glyph):
    try:
        pen = ControlBoundsPen(None)
        glyph.draw(pen)
        return pen.bounds
    except Exception:
        return None


def move_top(target, source, glyph=None):
    if target and source:
        target.x = min(target.x, source.x)
        target.y = max(target.y, source.y)
        return True
    return False


def move_bottom(target, source):
    if target and source:
        target.x = min(target.x, source.x)
        target.y = min(target.y, source.y)
        return True
    return False


class MarkPosFilter(BaseFilter):

    _kwargs = {"a": 0}

    def __call__(self, font, glyphSet=None):
        if super().__call__(font, glyphSet):
            modified = self.context.modified
            if modified:
                logger.info("Adjusted mark positions: %i" % len(modified))
            return modified

    def filter(self, glyph):

        modified = False

        # Adjust anchors positions

        # for target_anchor_name in _anchors_startswith_name(glyph, "top"):
        if _find_anchor(glyph, "top") and _find_anchor(glyph, "mark_top"):
            _find_anchor(glyph, "top").y = max(
                _find_anchor(glyph, "top").y, _find_anchor(glyph, "mark_top").y
            )
            if (
                abs(_find_anchor(glyph, "top").x - _find_anchor(glyph, "mark_top").x)
                > 100
            ):
                _find_anchor(glyph, "top").x = _find_anchor(glyph, "mark_top").x
                _find_anchor(glyph, "top").y = _find_anchor(glyph, "mark_top").y
            modified = True

        if _find_anchor(glyph, "bottom") and _find_anchor(glyph, "mark_bottom"):
            _find_anchor(glyph, "bottom").y = min(
                _find_anchor(glyph, "bottom").y, _find_anchor(glyph, "mark_bottom").y
            )
            modified = True

        # Adjust anchor.y where topthreedots acnhor exists.
        # TODO: make this work for top* instead of just topthreedots
        if (
            _find_anchor(glyph, "topthreedots")
            and len(glyph.components) >= 2
            and _find_anchor(
                self.context.font[glyph.components[1].baseGlyph], "_topthreedots"
            )
        ):
            # print(glyph, _find_anchor(glyph, "top").y)
            _find_anchor(glyph, "top").x = _find_anchor(glyph, "topthreedots").x
            _find_anchor(glyph, "top").y += (
                _find_anchor(self.context.font[glyph.components[1].baseGlyph], "top").y
                - _find_anchor(
                    self.context.font[glyph.components[1].baseGlyph], "_top"
                ).y
                - 150
            )
        # Ligatures
        if glyph.components:
            for i in range(len(glyph.components)):

                if _find_anchor(glyph, f"top_{i+1}") and _find_anchor(
                    glyph, f"mark_top_{i+1}"
                ):
                    _find_anchor(glyph, f"top_{i+1}").x = _find_anchor(
                        glyph, f"mark_top_{i+1}"
                    ).x
                    _find_anchor(glyph, f"top_{i+1}").y = _find_anchor(
                        glyph, f"mark_top_{i+1}"
                    ).y
                    modified = True

                if _find_anchor(glyph, f"bottom_{i+1}") and _find_anchor(
                    glyph, f"mark_bottom_{i+1}"
                ):
                    _find_anchor(glyph, f"bottom_{i+1}").x = _find_anchor(
                        glyph, f"mark_bottom_{i+1}"
                    ).x
                    _find_anchor(glyph, f"bottom_{i+1}").y = _find_anchor(
                        glyph, f"mark_bottom_{i+1}"
                    ).y
                    modified = True

        return modified
