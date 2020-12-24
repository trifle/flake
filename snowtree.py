#!/usr/bin/python3
import cairo, math, random, sys

# Set up Cairo for drawing. Origin is in upper-left corner.
SIDE = 1200
height = SIDE
width = SIDE
center = SIDE // 2
surface = cairo.SVGSurface("snowtree.svg", width, height)
ctx = cairo.Context(surface)
ctx.set_source_rgb(0.0, 0.0, 0.0)
ctx.translate(center, center)
refl = cairo.Matrix(
    -1.0, 0.0,
     0.0, 1.0,
     0.0, 0.0,
)

def stroke_path(ctx, path):
    for type, points in path:
        if type == cairo.PATH_MOVE_TO:
            ctx.move_to(*points)
        elif type == cairo.PATH_LINE_TO:
            ctx.line_to(*points)
        else:
            assert False

def mirror():
    path = ctx.copy_path()
    for r in [False, True]:
        ctx.save()
        if r:
            ctx.transform(refl)
        ctx.new_path()
        stroke_path(ctx, path)
        ctx.stroke()
        ctx.restore()

def flake():
    path = ctx.copy_path()
    for i in range(6):
        ctx.save()
        ctx.rotate(i * 2 * math.pi / 6)
        ctx.new_path()
        stroke_path(ctx, path)
        ctx.stroke()
        ctx.restore()

def maketree(scale, depth):
    if scale <= 1 or depth <= 0:
        return None

    def v(mu):
        return min(0.8, max(0.2, random.normalvariate(mu, 0.5)))


    uscale = v(0.7) * scale
    uadv = v(0.3) * uscale
    utree = maketree(uscale, depth - 1)

    rscale = v(0.7) * scale
    radv = v(0.3) * rscale
    rtree = maketree(rscale, depth - 1)

    return [(uadv, utree), (radv, rtree)]

def drawtree(tree):
    if tree is None:
        return

    def subtree(adv, tree, rotate=0.0):
        ctx.move_to(0, 0)
        ctx.save()
        if rotate != 0:
            ctx.rotate(rotate * 2 * math.pi / 6)
        ctx.translate(0, adv)
        ctx.line_to(0, 0)
        drawtree(tree)
        ctx.restore()

    u, r = tree
    uadv, utree = u
    radv, rtree = r
    ctx.move_to(0, 0)
    ctx.save()
    ctx.translate(0, uadv / 2)
    ctx.line_to(0, 0)
    subtree(uadv / 2, utree)
    subtree(radv, rtree, 1)
    subtree(radv, rtree, -1)
    ctx.restore()

if len(sys.argv) == 2:
    seed = bytes(sys.argv[1], encoding="utf-8")
else:
    seed = random.randrange(10000)
    print(seed)
random.seed(seed)

tree = maketree(500, 6)
ctx.move_to(0, 0)
drawtree(tree)
flake()
ctx.stroke()
surface.finish()
