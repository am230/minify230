import rpack
from .model import Model, Texcoord, Texture, Material, Color
from typing import Dict
from PIL import Image
import math


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

    def minify(self) -> Model:
        texture_bounds: Dict[str, Box2] = {}
        for mesh in self.model.meshes:
            texture_name = mesh.material.texture.name
            for face in mesh.faces:
                for vertex in face.vertexes:
                    texcoord = vertex.texcoord
                    if texture_name not in texture_bounds:
                        texture_bounds[texture_name] = Box2(texcoord, texcoord)
                    else:
                        box = Box2()
                        # box.min[0] = min(texture_bounds[texture_name].min[0], texcoord[0])
                        # box.min[1] = min(texture_bounds[texture_name].min[1], texcoord[1])
                        # box.max[0] = max(texture_bounds[texture_name].max[0], texcoord[0])
                        # box.max[1] = max(texture_bounds[texture_name].max[1], texcoord[1])
                        box.min = (min(texture_bounds[texture_name].min[0], texcoord[0]),
                                   min(texture_bounds[texture_name].min[1], texcoord[1]))
                        box.max = (max(texture_bounds[texture_name].max[0], texcoord[0]),
                                  max(texture_bounds[texture_name].max[1], texcoord[1]))
                        texture_bounds[texture_name] = box
        positions = rpack.pack([(math.ceil(b.width), math.ceil(b.height)) for b in texture_bounds.values()])
        combined_width = max(pos[0] + bb.width for pos, bb in zip(positions, texture_bounds.values()))
        combined_height = max(pos[1] + bb.height for pos, bb in zip(positions, texture_bounds.values()))
        combined_texture = Texture('combined.png', Image.new('RGBA', (math.ceil(combined_width), math.ceil(combined_height))))
        combined_material = Material('combined', Color(), Color(), combined_texture)
        texture_offsets = {}
        for index, position in enumerate(positions):
            texture_offsets[tuple(texture_bounds.keys())[index]] = position
        for texture in self.model.textures:
            texture_name = texture.name
            bound = texture_bounds[texture_name]
            offset = texture_offsets[texture_name]
            cropped = texture.image.crop((bound.min[0], bound.min[1], bound.max[0], bound.max[1]))
            combined_texture.image.paste(cropped, offset)
        self.model.textures = [combined_texture]
        for mesh in self.model.meshes:
            texture_name = mesh.material.texture.name
            bound = texture_bounds[texture_name]
            tex_offset = bound.min
            for face in mesh.faces:
                for vertex in face.vertexes:
                    # vertex.texcoord[0] -= tex_offset[0]
                    # vertex.texcoord[1] -= tex_offset[1]
                    # vertex.texcoord[0] += texture_offsets[texture_name][0]
                    # vertex.texcoord[1] += combined_height - texture_offsets[texture_name][1] - bound.height
                    vertex.texcoord = (vertex.texcoord[0] - tex_offset[0] + texture_offsets[texture_name][0],
                                      vertex.texcoord[1] - tex_offset[1] + combined_height - texture_offsets[texture_name][1] - bound.height)
        for mesh in self.model.meshes:
            mesh.material = combined_material
        self.model.materials = {combined_material.name: combined_material}
        return self.model
