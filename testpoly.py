from matplotlib.path import Path
def poly2Pixels(points, w, h):
    rows = []
    path = Path(points)

    for y in xrange(h):
        row = []
        for x in xrange(w):
            row.append(path.contains_point((x,y)))
        rows.append(row)
    return rows