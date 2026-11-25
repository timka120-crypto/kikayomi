"""Shot registry and small helpers shared by the shot modules."""
import math
from contextlib import contextmanager

from engine import Cam, clamp, lerp, ease

SHOTS = {}


def shot(n):
    def deco(fn):
        SHOTS[n] = fn
        return fn
    return deco


class Stage:
    """A camera plus canvas: `with st.at(z):` draws in the plane at depth z."""
    def __init__(self, c, W, H, **cam):
        self.c, self.W, self.H = c, W, H
        self.cam = Cam(W=W, H=H, **cam)

    @contextmanager
    def at(self, z):
        self.cam.begin(self.c, z)
        try:
            yield self.c
        finally:
            self.c.restore()


def track(t, d, a, b, fn=ease):
    return lerp(a, b, fn(t / d))
