from dataclasses import dataclass, field
from typing import Dict, List

from PIL.Image import Image


def Texcoord(u=0.0, v=0.0, w=1.0):
    return (float(u), float(v), float(w))


def Position(x=0.0, y=0.0, z=0.0, w=1.0):
    return (float(x), float(y), float(z), float(w))


def Color(red=1.0, green=1.0, blue=1.0, alpha=1.0):
    return (float(red), float(green), float(blue), float(alpha))


@dataclass
class Texture:
    name: str
    image: Image

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Material:
    name: str
    diffuse: tuple = field(default_factory=Color)
    ambient: tuple = field(default_factory=Color)
    texture: Texture = None


@dataclass
class Vertex:
    position: tuple = field(default_factory=Position)
    texcoord: tuple = field(default_factory=Texcoord)
    normal: tuple = field(default_factory=Position)


@dataclass
class Face:
    vertexes: List[Vertex]


@dataclass
class Mesh:
    material: Material
    faces: List[Face] = field(default_factory=list)


@dataclass
class Model:
    meshes: List[Mesh] = field(default_factory=list)
    materials: Dict[str, Material] = field(default_factory=dict)
    textures: List[Texture] = field(default_factory=list)
