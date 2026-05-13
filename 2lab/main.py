import math
from itertools import count, islice, chain
from functools import reduce, wraps

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def dist(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5


def polygon_area(poly):

    s = 0

    for i in range(len(poly)):

        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]

        s += x1 * y2 - x2 * y1

    return abs(s) / 2


def polygon_perimeter(poly):

    return sum(
        dist(poly[i], poly[(i + 1) % len(poly)])
        for i in range(len(poly))
    )


def polygon_sides(poly):

    return [
        dist(poly[i], poly[(i + 1) % len(poly)])
        for i in range(len(poly))
    ]


def take(n, iterator):
    return list(islice(iterator, n))



def draw(polygons, title, ax=None, fill=True, color=None):

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    polygons = list(polygons)

    for poly in polygons:

        patch = patches.Polygon(
            poly,
            closed=True,
            edgecolor="black",
            alpha=0.5,
            lw=1.5,
            fill=fill
        )

        ax.add_patch(patch)

    ax.autoscale()

    ax.set_aspect('equal')

    ax.set_title(title)

    ax.grid(True, linestyle=':', alpha=0.6)

    return ax


def gen_rectangle(w, h, step=10):

    for i in count():

        x = i * (w + step)

        yield (
            (x, 0),
            (x + w, 0),
            (x + w, h),
            (x, h)
        )


def gen_triangle(side, step=10):

    h = side * math.sqrt(3) / 2

    for i in count():

        x = i * (side + step)

        yield (
            (x, 0),
            (x + side / 2, h),
            (x + side, 0)
        )


def gen_hexagon(r, step=10):

    for i in count():

        cx = i * (2 * r + step)

        yield tuple(
            (
                cx + r * math.cos(math.radians(60 * k)),
                r * math.sin(math.radians(60 * k))
            )
            for k in range(6)
        )


def tr_translate(dx, dy):

    return lambda poly: tuple(
        (x + dx, y + dy)
        for x, y in poly
    )


def tr_rotate(angle):

    a = math.radians(angle)

    c = math.cos(a)
    s = math.sin(a)

    return lambda poly: tuple(
        (
            x * c - y * s,
            x * s + y * c
        )
        for x, y in poly
    )


def tr_symmetry(axis='x'):

    if axis == 'x':
        return lambda poly: tuple((x, -y) for x, y in poly)

    if axis == 'y':
        return lambda poly: tuple((-x, y) for x, y in poly)

    return lambda poly: tuple((-x, -y) for x, y in poly)


def tr_homothety(k):

    return lambda poly: tuple(
        (x * k, y * k)
        for x, y in poly
    )


def flt_convex_polygon(poly):
    return len(poly) >= 3


def flt_angle_point(point):
    return lambda poly: point in poly


def flt_square(limit):
    return lambda poly: polygon_area(poly) < limit


def flt_short_side(limit):
    return lambda poly: min(polygon_sides(poly)) < limit


def point_inside(poly, point):

    x, y = point
    inside = False

    for i in range(len(poly)):

        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]

        if ((y1 > y) != (y2 > y)) and \
                (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):

            inside = not inside

    return inside


def flt_point_inside(point):
    return lambda poly: point_inside(poly, point)


def flt_polygon_angles_inside(other):
    return lambda poly: any(point_inside(poly, p) for p in other)


def transform_decorator(transform):

    def outer(func):

        @wraps(func)
        def inner(*args, **kwargs):

            return map(transform, func(*args, **kwargs))

        return inner

    return outer


def filter_decorator(flt):

    def outer(func):

        @wraps(func)
        def inner(*args, **kwargs):

            return filter(flt, func(*args, **kwargs))

        return inner

    return outer


def agr_area(polygons):

    return reduce(
        lambda s, p: s + polygon_area(p),
        polygons,
        0
    )


def agr_perimeter(polygons):

    return reduce(
        lambda s, p: s + polygon_perimeter(p),
        polygons,
        0
    )


def agr_max_side(polygons):

    return reduce(
        lambda m, p: max(m, max(polygon_sides(p))),
        polygons,
        0
    )


def zip_polygons(*iters):

    for item in zip(*iters):

        yield tuple(chain.from_iterable(item))


def zip_tuple(a, b):
    return tuple(zip(a, b))


def count_2D(iterator):

    return sum(1 for _ in iterator)


def main():

    

    fig1, ax1 = plt.subplots(3, 1, figsize=(15, 18))

    rects = take(7, gen_rectangle(20, 10))
    tris = take(7, gen_triangle(20))
    hexs = take(7, gen_hexagon(10))

    draw(rects, '7 прямоугольников', ax1[0])
    draw(tris, '7 треугольников', ax1[1])
    draw(hexs, '7 шестиугольников', ax1[2])

    fig1.tight_layout()

    

    fig2, ax2 = plt.subplots(2, 2, figsize=(12, 12))

    ribbons = chain(
        map(tr_rotate(20), rects),
        map(tr_translate(0, 35), map(tr_rotate(20), rects)),
        map(tr_translate(0, 70), map(tr_rotate(20), rects))
    )

    draw(ribbons, 'Параллельные ленты', ax2[0, 0], fill=True)

    cross = chain(
        map(tr_rotate(45), rects),
        map(tr_rotate(-45), rects)
    )

    cross = map(tr_translate(40, 40), cross)

    draw(cross, 'Пересекающиеся ленты', ax2[0, 1], fill=True)

    sym = chain(
        tris,
        map(
            tr_translate(0, 60),
            map(tr_symmetry('x'), tris)
        )
    )

    draw(sym, 'Симметричные треугольники', ax2[1, 0], fill=True)

    base = ((0, 0), (15, 0), (15, 10), (0, 10))

    scaled = map(
        lambda k: tr_homothety(k)(base),
        [1, 1.5, 2, 2.5]
    )

    draw(scaled, 'Гомотетия', ax2[1, 1], fill=True)

    plt.subplots_adjust(hspace=0.3)

    

    filtered = list(
        filter(
            flt_square(250),
            rects
        )
    )[:6]

    print('Фигур после фильтрации:', len(filtered))

    

    @transform_decorator(tr_rotate(30))
    @filter_decorator(flt_short_side(25))
    def decorated():

        return gen_rectangle(15, 10)

    fig3, ax3 = plt.subplots(figsize=(7, 7))

    draw(
        take(5, decorated()),
        'Декораторы',
        ax3
    )

    

    test = take(10, gen_rectangle(20, 20))

    print('\nАгрегирующие функции')

    print('Общая площадь:',
          agr_area(test))

    print('Общий периметр:',
          agr_perimeter(test))

    print('Максимальная сторона:',
          agr_max_side(test))

    

    joined = list(
        zip_polygons(
            rects[:2],
            tris[:2]
        )
    )

    print('\nСклеенные полигоны:')

    for j in joined:
        print(j)

    fig4, ax4 = plt.subplots(figsize=(7, 7))

    draw(joined, 'zip_polygons', ax4)



    plt.show()


if __name__ == '__main__':
    main()