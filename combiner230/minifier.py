import math
from typing import Dict

import rpack
from PIL import Image

from .model import Color, Material, Model, Texcoord, Texture
from .profiler import profiler


class Box2:
    def __init__(self, min: tuple = None, max: tuple = None):
        self.min = min or Texcoord()
        self.max = max or Texcoord()

    @property
    def width(self):
        return self.max[0] - self.min[0]

    @property
    def height(self):
        return self.max[1] - self.min[1]

    def __contains__(self, other: Texcoord):
        return self.min[0] <= other[0] <= self.max[0] and self.min[1] <= other[1] <= self.max[1]

    def __or__(self, other: Texcoord):
        return Texcoord(min(self.min[0], other[0]), min(self.min[1], other[1]), max(self.max[0], other[0]), max(self.max[1], other[1]))

    def __ior__(self, other: Texcoord):
        self.min = self.min.min(other)
        self.max = self.max.max(other)


class Minifier:
    def __init__(self, model: Model):
        self.model = model

    @profiler
    def minify(self) -> Model:
        texture_bounds: Dict[str, Box2] = {}
        for mesh in self.model.meshes:
            if mesh.material.texture is None:
                continue
            texture_name = mesh.material.texture.name
            if texture_name not in texture_bounds:
                box = Box2(mesh.faces[0].vertexes[0].texcoord, mesh.faces[0].vertexes[0].texcoord)
                texture_bounds[texture_name] = box
            else:
                box = texture_bounds[texture_name]
            for face in mesh.faces:
                for vertex in face.vertexes:
                    texcoord = vertex.texcoord
                    box.min = (min(box.min[0], texcoord[0]), min(box.min[1], texcoord[1]))
                    box.max = (max(box.max[0], texcoord[0]), max(box.max[1], texcoord[1]))
        texture_sizes = [(math.ceil(b.width), math.ceil(b.height)) for b in texture_bounds.values()]
        positions = rpack.pack(texture_sizes)
        max_right = 0
        max_bottom = 0
        for pos, size in zip(positions, texture_sizes):
            max_right = max(max_right, pos[0] + size[0])
            max_bottom = max(max_bottom, pos[1] + size[1])
        combined_texture = Texture('combined.png', Image.new('RGBA', (math.ceil(max_right), math.ceil(max_bottom))))
        combined_material = Material('combined', Color(), Color(), combined_texture)
        texture_offsets = {name: pos for name, pos in zip(texture_bounds.keys(), positions)}
        for texture in self.model.textures:
            texture_name = texture.name
            bound = texture_bounds[texture_name]
            offset = texture_offsets[texture_name]
            cropped = texture.image.crop((bound.min[0], bound.min[1], bound.max[0], bound.max[1]))
            combined_texture.image.paste(cropped, offset)
        for mesh in self.model.meshes:
            if mesh.material.texture is None:
                continue
            texture_name = mesh.material.texture.name
            bound = texture_bounds[texture_name]
            tex_offset = bound.min
            tex_offset_x, tex_offset_y = texture_offsets[texture_name]
            tex_offset_y = max_bottom - tex_offset_y - bound.height
            for face in mesh.faces:
                for vertex in face.vertexes:
                    vertex.texcoord = (vertex.texcoord[0] - tex_offset[0] + tex_offset_x,
                                       vertex.texcoord[1] - tex_offset[1] + tex_offset_y)
            mesh.material = combined_material
        self.model.textures = [combined_texture]
        self.model.materials = {combined_material.name: combined_material}
        return self.model
