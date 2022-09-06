import os
import math
import random
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from dataclasses import dataclass, field
from typing import ClassVar
from collections import namedtuple

# convert ndjson to png files
def genIM(drawing: list, path: str):

    lw = 5 # length of width
    xmax, ymax = 0, 0
    xmin, ymin = math.inf, math.inf

    for i in range(0, len(drawing)):
        x = drawing[i][0]
        y = drawing[i][1]

        xmax = max([max(x), xmax])
        ymax = max([max(y), ymax])

        xmin = min([min(x), xmin])
        ymin = min([min(y), ymin])

    # First setup the figure
    ax = plt.axes(xlim=(xmax+lw, xmin-lw), ylim=(ymax+lw, ymin-lw))
    line, = ax.plot([], [], lw=lw, c='k')

    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Remove border
    ax.axis('off')

    line.set_data([], [])

    for data in drawing:
        x, y = data[0], data[1]
        line.set_data(x, y)
        line, = ax.plot([], [], lw=lw, c='k')

    # Plotting the Graph
    plt.plot()

    plt.savefig(path, transparent=True)

    plt.close()

    return None

# Draw specific class from ndjson file
def draw(obj_name: str, path: str, idx: int=0, nrows: int=100):
    df = pd.read_json((f'../simplified/{obj_name}.ndjson'), lines=True, nrows=nrows)
    genIM(df['drawing'][idx], path)
    return None

# Generate png format files from ndjson files
def genDataset(nrows: int=100):
    files = os.listdir('../simplified')

    # # Replace file's whitespace with underscore
    # for f in files:
    #     if ' ' in f:
    #         os.replace(f'../simplified/{f}', f'../simplified/{f.replace(" ", "_")}')

    prefix = '../temp'
    if not os.path.exists(prefix):
        os.mkdir(prefix)

    for f in files:
        # path of image
        fname = f[:-7]
        path = f'{prefix}/{fname}'
        if not os.path.exists(path):
            os.mkdir(path)

        # generate Image by data
        for i in range(nrows):
            draw(fname, f'{path}/{fname}_{i}.png', i, nrows)
            print(f'{path}/{fname}_{i}.png')
        
    return None


class CanvasObj:

    def __init__(self, catalog: str, pos=(-1, -1), scale: float=0.2, im=""):
        self.id = uuid.uuid4()
        self.catalog = catalog
        self.pos = pos
        self.scale = scale

        w, h = im.size
        self.w, self.h = int(w*scale), int(h*scale)
        self.im = im.resize((self.w, self.h))

    def config(self):
        print(f'id: {self.id}')
        print(f'catalog: {self.catalog}')
        print(f'position: {self.pos}')
        print(f'scale: {self.scale}')
        print(f'width: {self.w}, height: {self.h}')


@dataclass
class Canvas:

    def init(self, background: str='blank'):
        self.bg = background
        self.objs = []
        self.classes = {}
        self.inclasses = []
        self.max_nums = 500

        # Record used index for classes
        for f in os.listdir('../simplified'):
            self.classes[f[:-7]] = []
        
        self.edges = []
        return None

    def addObj(self, name: str, idx: int=0):
        if name not in self.inclasses:
            self.inclasses.append(name)

        while idx in self.classes[name]:
            idx = random.randint(0, self.max_nums-1)
        self.classes[name].append(idx)

        prefix = '../temp'
        path = f'{prefix}/{name}/{name}_{idx}.png'
        Im = Image.open(path)

        self.objs.append(CanvasObj(catalog=name, im=Im))
        return None
    
    def addEdge(self, edges: list):
        # print(f'edges: {edges}')

        for edge in edges:
            for a in edge['sobj']:
                for b in edge['pobj']:
                    self.edges.append([a, b, edge['adp']])
        return None

    def draw(self):
        bgIm = Image.open(f'../temp/background/{self.bg}.png')
        maxw, maxh = bgIm.size
        paintedObjs = []

        def intersection(a, b):
            dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
            dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
            if (dx>=0) and (dy>=0):
                return dx*dy

        Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')
        def conflict(paintedObj: list[CanvasObj], objT: CanvasObj):
            xTmin, yTmin = objT.pos
            rT = Rectangle(xTmin, yTmin, xTmin + objT.w, yTmin + objT.h)
            for obj in paintedObj:
                xmin, ymin = obj.pos
                r = Rectangle(xmin, ymin, xmin + obj.w, ymin + obj.h)

                if intersection(r, rT) != None:
                    return True
                
            return False

        def outOfbound(obj: CanvasObj):
            xmin, ymin = obj.pos
            xmax, ymax = xmin + obj.w, ymin + obj.h
            if xmax > maxw or ymax > maxh:
                return True
            return False

        def updown(objA: CanvasObj, objB: CanvasObj):
            ax, ay = objA.pos
            bx, by = objB.pos
            bx = ax
            by = ay + objA.h
            objB.pos = (bx, by)
            return None

        def leftright(objA: CanvasObj, objB: CanvasObj):
            ax, ay = objA.pos
            bx, by = objB.pos
            bx = ax + objA.w
            by = ay
            objB.pos = (bx, by)
            return None

        # Initial objs position
        for obj in self.objs:
            # while comflict, change position
            obj.pos = (random.randint(0, maxw), random.randint(0, maxh))
            while conflict(paintedObjs, obj) or outOfbound(obj):
                obj.pos = (random.randint(0, maxw), random.randint(0, maxh))
            # bgIm.paste(obj.im, obj.pos, obj.im)
            paintedObjs.append(obj)

        for edge in self.edges:
            A, B, adp = edge
            random.shuffle(paintedObjs)
            objA, objB = None, None
            for obj in paintedObjs:
                if obj.catalog == A:
                    objA = obj
                elif obj.catalog == B:
                    objB = obj

            if adp == 'up':
                updown(objA, objB)
            elif adp == 'down':
                updown(objB, objA)
            elif adp == 'left':
                leftright(objA, objB)
            elif adp == 'right':
                leftright(objB, objA)
        
        for obj in paintedObjs:
            bgIm.paste(obj.im, obj.pos, obj.im)

        outfile = 'output.png'
        bgIm.save(outfile)

        return bgIm

    def config(self):
        print(f'background: {self.bg}')
        print(f'objects in canvas: {self.objs}')
        # print(f'classes: {self.classes}')
        print(f'edges: {self.edges}')
        print(f'included classes: {self.inclasses}')


def main():
    random.seed(2022)
    # genDataset(500)
    canvas = Canvas()
    canvas.init()
    canvas.addObj('cat', random.randint(0, 499))
    canvas.addObj('dog', random.randint(0, 499))
    canvas.addObj('duck', random.randint(0, 499))
    canvas.addObj('table', random.randint(0, 499))

    clauses = [{'sobj': ['cat'], 'pobj': ['dog'], 'adp': 'right'}, {'sobj': ['duck'], 'pobj': ['table'], 'adp': 'up'}]
    canvas.addEdge(clauses)

    canvas.config()
    canvas.draw()

    # cobj = CanvasObj(catalog='dog', im=Image.open('../temp/background/blank.png'))
    # cobj.config()
    
    return None


if __name__ == "__main__":
  main()
