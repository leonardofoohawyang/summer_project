import os
import math
import random
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from dataclasses import dataclass

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
def draw(obj_name: str, path: str, idx: int=0):
    df = pd.read_json((f'../simplified/{obj_name}.ndjson'), lines=True, nrows=100)
    genIM(df['drawing'][idx], path)
    return None

# Generate png format files from ndjson files
def genDataset():
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
        for i in range(100):
            draw(fname, f'{path}/{fname}_{i}.png', i)
        
    return None


@dataclass
class Canvas:

    def init(self, background: str='blank', rate: float=0.3):
        self.bg = background
        self.objs = []
        self.classes = {}
        self.rate = rate
        self.wmax, self.hmax = 0, 0
        self.num_objs = 0
        # Record used index for classes
        for f in os.listdir('../simplified'):
            self.classes[f[:-7]] = []
        
        self.edges = []
        return None

    def addObj(self, name: str, idx: int=0):
        while idx in self.classes[name]:
            idx = random.randint(0, 99)
        self.classes[name].append(idx)
        prefix = '../temp'
        path = f'{prefix}/{name}/{name}_{idx}.png'
        Im = Image.open(path)
        w, h = Im.size
        Im = Im.resize((int(w*self.rate), int(h*self.rate)))
        self.wmax = max(self.wmax, int(w*self.rate))
        self.hmax = max(self.hmax, int(h*self.rate))
        obj = {
            'name': name,
            'img': Im,
            'x': 0,
            'y': 0,
            'id': self.num_objs,
            'on_canvas': False
        }
        
        self.num_objs += 1
        self.objs.append(obj)
        return None
    
    def addEdge(self, edges: list):
        print(f'edges: {edges}')

        for edge in edges:
            for a in edge['sobj']:
                for b in edge['pobj']:
                    self.edges.append([a, b, edge['adp']])
        return None

    def config(self):
        print(f'background: {self.bg}')
        print(f'Objects in canvas: {self.objs}')
        # print(f'Classes: {self.classes}')
        print(self.relations)
        return None

    def draw(self):
        bgIm = Image.open(f'../temp/background/{self.bg}.png')

        wbg, hbg = bgIm.size
        pos_x = [x for x in range(0, wbg, self.wmax)][:-1]
        pos_y = [y for y in range(0, hbg, self.hmax)][:-1]

        def paste_A_on_B(A, B, adp):
            print(f'A: {A}, B: {B}, adp: {adp}')

            x, y = None, None
            for obj in self.objs:
                if A == obj['name']:
                    if not obj['on_canvas']:
                        obj['on_canvas'] = True
                        x, y = random.choice(pos_x[2:-2]), random.choice(pos_y[2:-2])
                        obj['x'], obj['y'] = x, y
                    else:
                        x, y = obj['x'], obj['y']
                    
                    bgIm.paste(obj['img'], (x, y), obj['img'])

            for obj in self.objs:
                if B == obj['name']:
                    obj['on_canvas'] = True
                    bgIm.paste(obj['img'], (x, y + self.hmax), obj['img'])

            return None

        def paste_A_by_B(A, B, adp):
            print(f'A: {A}, B: {B}, adp: {adp}')

            x, y = None, None
            for obj in self.objs:
                if A == obj['name']:
                    if not obj['on_canvas']:
                        obj['on_canvas'] = True
                        x, y = random.choice(pos_x[2:-2]), random.choice(pos_y[2:-2])
                        obj['x'], obj['y'] = x, y
                    else:
                        x, y = obj['x'], obj['y']

                    bgIm.paste(obj['img'], (x, y), obj['img'])

            for obj in self.objs:
                if B == obj['name']:
                    obj['on_canvas'] = True
                    bgIm.paste(obj['img'], (x + self.wmax, y), obj['img'])

            return None
        
        # print(self.edges)
        # print(self.objs)
        for edge in self.edges:
            A, B, adp = edge
            if adp == 'up':
                paste_A_on_B(A, B, adp)
            elif adp == 'down':
                paste_A_on_B(B, A, adp)
            elif adp == 'left':
                paste_A_by_B(A, B, adp)
            else:
                paste_A_by_B(B, A, adp)
        
        for obj in self.objs:
            if not obj['on_canvas']:
                obj['on_canvas'] = True
                bgIm.paste(obj['img'], (random.choice(pos_x[2:-2]), random.choice(pos_y[2:-2])), obj['img'])
        

        # outfile = 'output.png'
        # bgIm.save(outfile)

        return bgIm


def main():
    # genDataset()
    canvas = Canvas()
    canvas.init(rate=0.25)
    canvas.addObj('cat', random.randint(0, 99))
    canvas.addObj('dog', random.randint(0, 99))
    canvas.addObj('duck', random.randint(0, 99))
    # canvas.config()
    canvas.draw()
    return None


if __name__ == "__main__":
  main()
