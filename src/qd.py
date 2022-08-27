import os
import random
import math
import json
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from dataclasses import dataclass

## Reference:
# https://colab.research.google.com/github/zaidalyafeai/Notebooks/blob/master/Strokes_QuickDraw.ipynb#scrollTo=av_gNHXIPHvu

@dataclass
class QuickDraw:
  video_name: str
  
  def create_spec_animation(self, obj_name: str):

    files = os.listdir('../simplified')

    drawing = []
    if f'{obj_name}.ndjson' in files:
      print(f'{obj_name} is in the files.')
      contents = open(f'../simplified/{obj_name}.ndjson', "r").read()
      data = contents.split('\n')

      idx = random.randint(0, len(data))
      drawing = json.loads(data[idx])['drawing']
    else:
      print(f'{obj_name} is not in the files.')
      print("Random generate an animation!")
      contents = open(f'../simplified/{random.choice(files)}', "r").read()
      data = contents.split('\n')

      idx = random.randint(0, len(data))
      drawing = json.loads(data[idx])['drawing']
      
    self.create_animation(drawing)
    return None

  def init(self):
    self.categories = []
    self.drawings = {}

    files = os.listdir('../simplified')

    # print(f'Number of species: {len(files)}')
    # print(files)

    i = 0

    for file in files:
      obj = file.split(".ndjson")[0]
      self.categories.append(obj)
      # print(obj)

      contents = open(f'../simplified/{file}', "r").read()
      data = contents.split('\n')

      #load k samples for each class
      samples = []
      k = 5
      for h in data[:k]:
        samples.append(json.loads(h)['drawing'])

      self.drawings[obj] = samples

      i += 1

      if i == 10:
        break

    return None

  def create_animation(self, drawing, fps = 30, idx = 0, lw = 5):
    seq_length = 0

    xmax = 0
    ymax = 0

    xmin = math.inf
    ymin = math.inf

    #retreive min,max and the length of the drawing
    for k in range(0, len(drawing)):
      x = drawing[k][0]
      y = drawing[k][1]

      seq_length += len(x)
      xmax = max([max(x), xmax])
      ymax = max([max(y), ymax])

      xmin = min([min(x), xmin])
      ymin = min([min(y), ymin])

    i = 0
    j = 0

    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = plt.axes(xlim=(xmax+lw, xmin-lw), ylim=(ymax+lw, ymin-lw))
    ax.set_facecolor("white")
    line, = ax.plot([], [], lw=lw)

    #remove the axis
    ax.grid = False
    ax.set_xticks([])
    ax.set_yticks([])

    # initialization function: plot the background of each frame
    def init():
        line.set_data([], [])
        return line,

    # animation function.  This is called sequentially
    def animate(frame):
      nonlocal i, j, line
      x = drawing[i][0]
      y = drawing[i][1]
      line.set_data(x[0:j], y[0:j])

      if j >= len(x):
        i +=1
        j = 0
        line, = ax.plot([], [], lw=lw)

      else:
        j += 1
      return line,

    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                  frames= seq_length + len(drawing), blit=True)
    plt.close()

    # save the animation as an mp4.
    anim.save(self.video_name, fps=fps, extra_args=['-vcodec', 'libx264'])

  def draw(self, obj_name='random'):
    if obj_name == 'random':
      rdmPick = random.choice(self.categories)
      print(f'Random draw {rdmPick}!')
      drawing = random.choice(self.drawings[rdmPick])
    else:
      print(f'Draw {obj_name}!')
      drawing = random.choice(self.drawings[obj_name])

    self.create_animation(drawing)
    return None

if __name__ == "__main__":
  qd = QuickDraw('video.mp4')
  qd.create_spec_animation('abc')