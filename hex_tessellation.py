from math import (
    ceil, floor, sin, tan, pi
)
from PIL import Image
import numpy as np
from random import randint
import itertools


def dist2(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


class PixelMap:
    def __init__(self, image_size):
        self._pixel_map = np.empty(image_size, dtype='int32')
        # top, right, bottom, left
        self._neighbors_map = np.full((image_size[0], image_size[1], 4), -1, dtype='int32')
        self.has_neighbor_set = False
        self.image_width = image_size[0]
        self.image_height = image_size[1]

    def set(self, pixel, segment_id):
        x, y = pixel
        if 0 <= x < self.image_width and 0 <= y < self.image_height:
            self._pixel_map[x, y] = segment_id
        if self.has_neighbor_set:
            self.set_neighbor(x, y-1, 2, segment_id)
            self.set_neighbor(x+1, y, 3, segment_id)
            self.set_neighbor(x, y+1, 0, segment_id)
            self.set_neighbor(x-1, y, 1, segment_id)

    def get(self, pixel):
        if 0 <= pixel[0] < self.image_width and 0 <= pixel[1] < self.image_height:
            return self._pixel_map[pixel]
        return -1
        
    def is_edge(self, pixel):
        if 0 <= pixel[0] < self.image_width and 0 <= pixel[1] < self.image_height:
            segment_id = self.get(pixel)
            return any([n != segment_id and n != -1 for n in self.get_neighbors(pixel)])   
        return False
    
    def get_neighbors(self, pixel):
        return self._neighbors_map[pixel]
        
    def set_neighbor(self, pixel, direction, segment_id):
        if (0 <= pixel[0] < self.image_width
                and 0 <= pixel[1] < self.image_height
                and 0 <= direction <= 3):
            self._neighbors_map[pixel[0], pixel[1], direction] = segment_id


class Segment:
    def __init__(self):
        self.pixels = []
        self.edges = []

    def add(self, pixel, edge=False, body=True):
        if edge:
            self.edges.append(pixel)
        if body:
            self.pixels.append(pixel)


class Tessellator:
    def __init__(self, image_size, cell_size):
        self.segment_list = []
        self.pixel_map = PixelMap(image_size)
        self.image_width = image_size[0]
        self.image_height = image_size[1]
        self.cell_size = cell_size
        self.tessellate()

    def tessellate(self):
        grid_width = self.cell_size * 3/2
        grid_height = self.cell_size * sin(pi/3)

        # 偶数列目の六角形の個数
        hex_cols_even = ceil((ceil(self.image_height / grid_height) - 1) / 2)
        # 奇数列目の六角形の個数
        hex_cols_odd = floor((ceil(self.image_height / grid_height) - 1) / 2)

        def get_hex_index(i, j):
            assert (i + j) % 2 == 0
            past_rows = i // 2 * (hex_cols_even + hex_cols_odd)
            if i % 2 == 1:
                past_rows += hex_cols_even
            return past_rows + j//2 + 1

        for x, y in itertools.product(range(self.image_width), range(self.image_height)):
            i = floor(x / grid_width)
            j = floor(y / grid_height)
            segment_index = -1
            if (i + j) % 2 == 0:
                topleft = (i * grid_width, j * grid_height)
                bottomright = ((i + 1) * grid_width, (j + 1) * grid_height)
                if (dist2((x, y), topleft) <= dist2((x, y), bottomright)):
                    segment_index = get_hex_index(i, j)
                else:
                    segment_index = get_hex_index(i+1, j+1)
            else:
                topright = ((i + 1) * grid_width, j * grid_height)
                bottomleft = (i * grid_width, (j + 1) * grid_height)
                if (dist2((x, y), topright) <= dist2((x, y), bottomleft)):
                    segment_index = get_hex_index(i+1, j)
                else:
                    segment_index = get_hex_index(i, j+1)

            while len(self.segment_list) <= segment_index:
                self.segment_list.append(Segment())
            self.segment_list[segment_index].add((x, y))
            self.pixel_map.set((x, y), segment_index)

            self.pixel_map.set_neighbor((x, y-1), 2, segment_index)
            self.pixel_map.set_neighbor((x+1, y), 3, segment_index)
            self.pixel_map.set_neighbor((x, y+1), 0, segment_index)
            self.pixel_map.set_neighbor((x-1, y), 1, segment_index)

            if self.pixel_map.is_edge((x-1, y)):
                left_segment_id = self.pixel_map.get((x-1, y))
                self.segment_list[left_segment_id].add((x-1, y), edge=True, body=False)

        for y in range(self.image_height):
            if self.pixel_map.is_edge((self.image_width-1, y)):
                left_segment_id = self.pixel_map.get((self.image_width-1, y))
                self.segment_list[left_segment_id].add((self.image_width-1, y), edge=True, body=False)


def run():
    width = 512
    height = 512
    size = 10

    image = Image.new('RGB', (width, height))
    pixels = image.load()
    tessellator = Tessellator((width, height), size)
    

    for i, segment in enumerate(tessellator.segment_list):
        if i < 256:
            color = (255 - i, 0, 255)
        elif 256 <= i < 512:
            color = (0, i - 256, 255)
        else:
            color = (0, 255, 255 - i + 512)
        c = randint(0, 255)
        # color = (c, c, 255)

        for x, y in segment.edges:
            pixels[x, y] = color

    image.show()


if __name__ == "__main__":
    run()
