#!/usr/bin/python3
import cairo, math, random, sys

# Page is 4 inches square at 72 dpi.
SIDE = 4 * 72
width = SIDE
height = SIDE
surface = cairo.SVGSurface("snowtree.svg", width, height)
ctx = cairo.Context(surface)
ctx.set_source_rgb(0.0, 0x88/255, 0xaa/255)
# Move origin to center of page.
center = SIDE // 2
ctx.translate(center, center)

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

def stroke_path(ctx, path):
    for type, points in path:
        if type == cairo.PATH_MOVE_TO:
            ctx.move_to(*points)
        elif type == cairo.PATH_LINE_TO:
            ctx.line_to(*points)
        else:
            assert False

def flake():
    path = ctx.copy_path()
    ctx.new_path()
    for i in range(6):
        ctx.save()
        ctx.rotate(i * 2 * math.pi / 6)
        stroke_path(ctx, path)
        ctx.restore()

def max_xy():
    m = 0
    path = ctx.copy_path()
    for type, points in path:
        if type == cairo.PATH_MOVE_TO or type == cairo.PATH_LINE_TO:
            for c in points:
                m = max(m, abs(c))
    return m

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

side = max_xy()
path = ctx.copy_path()
ctx.new_path()
# Scale to take up 90% of page.
nside = 0.95 * 0.5 * SIDE / side
ctx.scale(nside, nside)
stroke_path(ctx, path)
ctx.stroke()

surface.finish()
