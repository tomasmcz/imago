"""Image filters module.

All filters return a filtered copy of the image, the original image is
preserved.
"""

from PIL import Image, ImageFilter
import numpy as np

from . import pcf

def color_enhance(image):
    """Stretch all color channels to their full range."""
    image_l = image.load()
    min_r, min_g, min_b = 999, 999, 999
    max_r, max_g, max_b = -1, -1, -1

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            min_r = min(min_r, image_l[x, y][0])
            max_r = max(max_r, image_l[x, y][0])
            min_g = min(min_g, image_l[x, y][1])
            max_g = max(max_g, image_l[x, y][1])
            min_b = min(min_b, image_l[x, y][2])
            max_b = max(max_b, image_l[x, y][2])

    new_image = Image.new('RGB', image.size)
    new_image_l = new_image.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r, g, b = image_l[x, y]
            r = (r - min_r) * 255 / (max_r - min_r)
            g = (g - min_g) * 255 / (max_g - min_g)
            b = (b - min_b) * 255 / (max_b - min_b)
            new_image_l[x, y] = (r, g, b)

    return new_image

def edge_detection(image):
    """Edge detection (on BW images)."""
    new_image = image.filter(ImageFilter.GaussianBlur())
    # GaussianBlur is undocumented class, it might not work in future versions
    # of PIL
    new_image = Image.frombytes('L', image.size,
                             pcf.edge(image.size, image.tobytes()))
    return new_image

def peaks(image):
    """Peak filter (on BW images)."""
    image_l = image.load()
    new_image = Image.new('L', image.size)
    new_image_l = new_image.load()
    for x in range(2, image.size[0] - 2):
        for y in range(2, image.size[1] - 2):
            pix = (sum([sum([
                - image_l[a, b] 
                    for b in range(y - 2, y + 3)]) 
                    for a in range(x - 2, x + 3)])
                + (17 * image_l[x, y]))
            if pix > 255:
                pix = 255
            if pix < 0:
                pix = 0 
            new_image_l[x, y] = pix
    return new_image

def high_pass(image, height):
    """High pass filter (on BW images)."""
    image_l = image.load()
    new_image = Image.new('L', image.size)
    new_image_l = new_image.load()
    
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if image_l[x, y] < height:
                new_image_l[x, y] = 0
            else:
                new_image_l[x, y] = image_l[x, y]

    return new_image

def components(image, diameter):
    # TODO comment 
    # TODO refactor
    image_l = image.load()
    new_image_l = np.zeros(image.size, dtype=np.int)

    components = [None]
    comp_counter = 1

    if diameter == 1:
        for y in range(1, image.size[1] - 1):
            for x in range(1, image.size[0] - 1):
                if image_l[x, y]:
                    s = {0}
                    s.add(new_image_l[x - 1, y - 1])
                    s.add(new_image_l[x, y - 1])
                    s.add(new_image_l[x + 1, y - 1])
                    s.add(new_image_l[x - 1, y])
                    if len(s) == 1:
                        components.append(set())
                        new_image_l[x, y] = comp_counter
                        components[comp_counter].add((x, y))
                        comp_counter += 1
                    elif len(s) == 2:
                        s.remove(0)
                        c = s.pop()
                        new_image_l[x, y] = c
                        components[c].add((x, y))
                    else:
                        s.remove(0)
                        c1, c2 = s.pop(), s.pop()
                        components[c2].add((x, y))
                        for (x1, y1) in components[c2]:
                            new_image_l[x1, y1] = c1
                        components[c1] = components[c1] | components[c2]
                        components[c2] = None
    elif diameter == 2:
        for y in range(2, image.size[1] - 2):
            for x in range(2, image.size[0] - 2):
                if image_l[x, y]:

                    s = {0}
                    for (a, b) in [(a,b) for a in range(x - 2, x + 3) 
                              for b in range(y - 2, y + 1)]:
                        if not (b == y and a >= x):
                            s.add(new_image_l[a, b])

                    if len(s) == 1:
                        components.append(set())
                        new_image_l[x, y] = comp_counter
                        components[comp_counter].add((x, y))
                        comp_counter += 1
                    elif len(s) == 2:
                        s.remove(0)
                        c = s.pop()
                        new_image_l[x, y] = c
                        try:
                            components[c].add((x, y))
                        except AttributeError:
                            print(s, c)
                            raise AttributeError
                    else:
                        s.remove(0)
                        c1 = s.pop()
                        components[c1].add((x, y))
                        new_image_l[x, y] = c1
                        for c2 in s:
                            for (x1, y1) in components[c2]:
                                new_image_l[x1, y1] = c1
                            components[c1] = components[c1] | components[c2]
                            components[c2] = None
    else:
        pass #TODO error


    new_image = Image.new('L', image.size)
    new_image_l = new_image.load()

    for component in components:
        if component:
            x_c = 0
            y_c = 0
            c = 0
            for (x, y) in component:
                x_c += x
                y_c += y
                c += 1
            new_image_l[int(round(float(x_c)/c)), int(round(float(y_c)/c))] = 255

    return new_image

