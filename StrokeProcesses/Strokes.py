# This is the version before 16.07.11

# The stroke is a single line with centre width. It functions from the base and should act enough to perform different
# material.
# Meanwhile, this level should leave some variables as interface for Machine learning.

import Implement_For_Stroke
import math
nos=0

# r, g, b: 0--1
# H: 0-360    S,V: 0-1
class Color(object):
    # Present color in two ways RGB & HSL
    # Consider the transform relationship between RGB & HSL;
    def __init__(self):
        self.H = 0            # Hue
        self.S = 0     # Perceived intensity of a specific color. C/V.
        self.V = 0      # Black at 0, to white at 1.
        self.R = 0
        self.G = 0
        self.B = 0
        self.alpha = 0          # From 0 to 1 to represent transparency

    def __init__(self, r=0, g=0, b=0):
        #rgb2hsv
        if r>1 or g>1 or b>1:
            r /= 255.0
            g /= 255.0
            b /= 255.0
        self.R = r
        self.G = g
        self.B = b
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx
        self.H = h
        self.S = s
        self.V = v

    def give_color(self, h, s, v):
        self.H = h
        self.S = s
        self.V = v
        self.get_color()

    def get_color(self):
        #hsv2rgb
        h = float(self.H)
        s = float(self.S)
        v = float(self.V)
        h60 = h / 60.0
        h60f = math.floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        elif hi == 5:
            r, g, b = v, p, q
        self.R, self.G, self.B = r, g, b
        return r, g, b


class Point(object):
    def __init__(self, x=0, y=0, z=Color(0, 0, 0)):
        self.x = x
        self.y = y
        self.color = z

# Description: How to draw the line
class Stroke(object):
    def __init__(self):
        self.exp_length = 200
        self.exp_width = 30
        # This is the size of the square we use to simulate the actual stroke for better calculation

        # This part defines a 2D array which store the color of each point.
        self.lists = []
        self.dicts = {}
        # This is container for all Points classes for the stroke Points.x y c[x][y]
        self.c = [[(0, 0, 0) for col in range(self.exp_width)] for row in range(self.exp_length)]
        # This is a 2D array that stores the color information of each point
        self.axis_line = []

        # This part contains basic parameters we need from the CURVES layer.
        self.length = 0               # This is length (set on x axis, don't care its position.)
        self.width = 0                # This is width (defined only on one side).
        self.color = 0                # This defines single color of the stroke.

        # Below part defines parameters we add to adjust the picture. Consider the interface for machine learning here.
        self.distort = 0
        self.shake = 0
        self.tapering = 0

        # distort controls the distort rate of this stroke and is the first step. We need to adjust axis line.
        # shape controls how smooth this stroke is
        # tapering controls width at different length and is the second step. Set width at corresponding x position.

        self.TransparencyProportions = 0
        self.FrictionProbability = 0  # This define loss color area in the stroke.
        self.ColorVariability = 0     # This controls color range.
        self.ShadeVariability = 0     # This controls shade range.

        self.OverlappingRegion = 0  # This controls the overlapped region.[0,1]
        # This controls transparency proportions. Take mass process on each point's Color class.

    def draw_strokes(self, x1=0, y1=0, x2=50, y2=50, width=15, color=0):
        #global nos
        #nos+=1
        #print 'Stroke', nos
        self.length = int(math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)))
        if self.length == 0:
            self.length = 1
        self.width = width
        self.color = color
        self.dicts = {}
        self.lists = []

        # Here we calculate the shape for exp_length and exp_width which performs better
        new_lists = self.shape_changing()
        lm = self.exp_length * 1.0 / self.length
        wm = self.exp_width * 1.0 / self.width
        new_lists = Implement_For_Stroke.resize_full_points(new_lists, lm, wm)      # Resize it to appropriate size

        # Here we calculate three sets of points for interpolation: up, mid, down
        np = max(self.ColorVariability, self.ShadeVariability) * self.length / 8.0   # num of points
        color_boundary = Implement_For_Stroke.color_rectangle(np, color,
                                                              self.ColorVariability, self.ShadeVariability)

        up = color_boundary[0]
        mid = color_boundary[1]
        down = color_boundary[2]
        leng = (self.length + self.width) * 1.0 / np

        # Calculate the color for each point in new_list
        for i in range(len(new_lists)):
            x_points = new_lists[i]
            k = range(x_points[0][1], x_points[1][1] + 1)
            xp = x_points[0][0] + width / 2.0
            pos = max(0, int(xp / leng))
            v1 = (xp - leng * pos) / leng                      # Calculate the band region it belongs to

            # Here we calculate the S value using two time interpolation to prevent sudden change of s on y direction.
            # a, b is the coefficient for the two times function.
            xx = up[pos][1] * (1 - v1) * 1.0 + up[pos + 1][1] * v1 * 1.0
            yy = mid[pos][1] * (1 - v1) * 1.0 + mid[pos + 1][1] * v1 * 1.0
            zz = down[pos][1] * (1 - v1) * 1.0 + down[pos + 1][1] * v1 * 1.0
            a = (xx + zz - yy * 2) * 2.0
            b = (xx - zz) * 1.0
            # Here we add al_len to distort the color band
            al_len = len(self.axis_line)

            for j in k:
                x = x_points[0][0]
                y = j
                v2 = (width * 1.0 / 2 - abs(j)) / width
                # Below is to process the condition: one of H is >360
                if j > 0:
                    a1 = up[pos]
                    a2 = up[pos + 1]
                else:
                    a1 = down[pos]
                    a2 = down[pos + 1]
                b1 = mid[pos]
                b2 = mid[pos + 1]
                aa1 = a1[0]
                aa2 = a2[0]
                bb1 = b1[0]
                bb2 = b2[0]
                if max(aa1, aa2, bb1, bb2) - min(aa1, aa2, bb1, bb2) > 180:
                    if aa1 < 90:
                        aa1 += 360
                    if aa2 < 90:
                        aa2 += 360
                    if bb1 < 90:
                        bb1 += 360
                    if bb2 < 90:
                        bb2 += 360
                c_h = (aa1 * (1 - v1) + aa2 * v1) * (1 - v2) + (bb1 * (1 - v1) + bb2 * v1) * v2
                if c_h > 360:
                    c_h -= 360

                k = 2.0 * j / width
                c_s = a * k * k + b * k + yy            # Two time interpolation
                if abs(k)>0.7:
                    c_s *= 1
                    #c_s *= (0.6/(abs(k)-1.3)+1)
                # One time interpolation for V
                c_v = (a1[2] * (1 - v1) + a2[2] * v1) * (1 - v2) + (b1[2] * (1 - v1) + b2[2] * v1) * v2

                c = Color(0.0, 0.0, 0.0)
                c.give_color(c_h, c_s, c_v)

                # Add the bias for y
                if lm * x < al_len:
                    y_bias = int(self.axis_line[int(lm * x) - 1][1] / wm)
                else:
                    y_bias = 0

                self.dicts[(x,y-y_bias)] = c

        x, y = x2 - x1, y2 - y1
        if x!=0 or y!=0:
            CT, ST = 1.0*x/math.sqrt(x*x+y*y), 1.0*y/math.sqrt(x*x+y*y)
            origin_point = [x1, y1]
            self.lists = Implement_For_Stroke.rotate(CT, ST, self.length+self.width, self.dicts, origin_point)
        return self.lists
    # This part draws stroke by firstly calculating boundary using shape_changing, then it use color_attribute to
    # get c[x][y] array. Finally we return the corresponding Points lists.

    def shape_changing(self):
        exp_length = self.exp_length
        exp_width = self.exp_width
        self.axis_line = Implement_For_Stroke.distort_axis_line(exp_length, self.distort, self.shake)
        points = Implement_For_Stroke.broaden_axis_line(self.axis_line, exp_length, exp_width, self.tapering, self.shake)
        full_points = Implement_For_Stroke.soften_points(points, exp_width, self.shake)
        return full_points
    # This part gives ways describing how to get wanted shape for the stroke.
    # The way is considering big stroke with 200*30.

    def boundary_process(self):
        pass
    # This part will give details in fulfilling three styles: pointillism, natural painting, Impressionism by
    # discussing how to deal with the boundary.
