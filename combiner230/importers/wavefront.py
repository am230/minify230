from pathlib import Path
from typing import List

from PIL import Image
from ..profiler import profiler

from ..model import (Color, Face, Material, Mesh, Model, Position, Texcoord,
                     Texture, Vertex)


class Wavefront:

    def __init__(self, path: Path, fast_export: bool = False):
        self.base = path.parent
        self.obj = path
        self.material = self.base / Path('material.mtl')
        self.model = Model()
        self.fast_export = fast_export

    def get(self, path: str) -> Path:
        return self.base / path

    @profiler
    def parse(self) -> Model:
        mesh = None
        lines = self.obj.read_text(encoding='utf-8').splitlines()
        positions: List[tuple] = []
        texcoords: List[tuple] = []
        normals: List[tuple] = []
        meshes: List[Mesh] = []

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            args = line.split(' ')
            match args:
                case ['mtllib', *path]:
                    self.load_material(self.get(line[line.index(' ') + 1:]))
                case ['o', name]:
                    # mesh_group = VertexGroup()
                    pass
                case ['v', x, y, z, *w]:
                    positions.append(Position(x, y, z, *w))
                case ['vt', u, *vw]:
                    texcoords.append(Texcoord(u, *vw))
                case ['vn', *xyz]:
                    normals.append(Position(*xyz))
                case ['usemtl', name]:
                    mesh = Mesh(self.model.materials[name])
                    meshes.append(mesh)
                case ['f', *face]:
                    if mesh is None:
                        continue
                    vertexes = []
                    if '/' in line:
                        for pos, tex, *norm in [face.split('/') for face in face]:
                            vertex = Vertex(positions[int(pos) - 1],
                                            texcoords[int(tex) - 1])
                            if norm:
                                vertex.normal = normals[int(*norm) - 1]
                            vertexes.append(vertex)
                        mesh.faces.append(Face(vertexes))
                    else:
                        for pos_index in face:
                            vertexes.append(Vertex(positions[int(pos_index) - 1]))
                        mesh.faces.append(Face(vertexes))
        # uv to pixel
        for mesh in meshes:
            if mesh.material.texture is None:
                continue
            for face in mesh.faces:
                for vertex in face.vertexes:
                    vertex.texcoord = (vertex.texcoord[0] * mesh.material.texture.image.width,
                                       vertex.texcoord[1] * mesh.material.texture.image.height)
        self.model.meshes.extend(meshes)
        return self.model

    @profiler
    def export(self, model: Model) -> None:
        self.base.mkdir(parents=True, exist_ok=True)
        for texture in model.textures:
            texture.image.save(self.base / texture.name)
        self.export_material(model)
        if self.fast_export:
            self.export_model_fast(self.obj, self.material, model)
        else:
            self.export_model(self.obj, self.material, model)

    def export_material(self, model: Model):
        lines = []
        for name, material in model.materials.items():
            lines.append(f'newmtl {name}')
            lines.append(f'Kd {material.diffuse[0]} {material.diffuse[1]} {material.diffuse[2]} {material.diffuse[3]}')
            lines.append(f'Ka {material.ambient[0]} {material.ambient[1]} {material.ambient[2]} {material.ambient[3]}')
            lines.append(f'map_Kd {material.texture.name}')
        self.material.write_text('\n'.join(lines), encoding='utf-8')

    @profiler
    def export_model_fast(self, obj: Path, material: Path, model: Model):
        lines = [f'mtllib {material.relative_to(self.base)}', f'o {obj.name}']
        index = 1
        for mesh in model.meshes:
            lines.append(f"usemtl {mesh.material.name}")
            for face in mesh.faces:
                for vertex in face.vertexes:
                    lines.append(f'v {vertex.position[0]} {vertex.position[1]} {vertex.position[2]} {vertex.position[3]}')
                    lines.append(f'vt {vertex.texcoord[0] / mesh.material.texture.image.width} {vertex.texcoord[1] / mesh.material.texture.image.height}')
                    lines.append(f'vn {vertex.normal[0]} {vertex.normal[1]} {vertex.normal[2]}')
                lines.append('f')
                for _ in face.vertexes:
                    lines[-1] += (f' {index}/{index}/{index}')
                    index += 1
        obj.write_text('\n'.join(lines), encoding='utf-8')

    @profiler
    def export_model(self, obj: Path, material: Path, model: Model):
        lines = [f'mtllib {material.relative_to(self.base)}', f'o {obj.name}']

        positions, texcoords, normals = [], [], []

        for mesh in model.meshes:
            for face in mesh.faces:
                for vertex in face.vertexes:
                    positions.append(vertex.position)
                    if mesh.material.texture is not None:
                        vertex.texcoord = (vertex.texcoord[0] / mesh.material.texture.image.width, vertex.texcoord[1] / mesh.material.texture.image.height)
                    texcoords.append(vertex.texcoord)
                    normals.append(vertex.normal)

        position_dict = {pos: i + 1 for i, pos in enumerate(set(positions))}
        texcoord_dict = {tex: i + 1 for i, tex in enumerate(set(texcoords))}
        normal_dict = {norm: i + 1 for i, norm in enumerate(set(normals))}

        v_lines = [f'v {pos[0]} {pos[1]} {pos[2]}' for pos in position_dict]
        vt_lines = [f'vt {tex[0]} {tex[1]}' for tex in texcoord_dict]
        vn_lines = [f'vn {norm[0]} {norm[1]} {norm[2]}' for norm in normal_dict]
        f_lines = []

        material = None
        for mesh in model.meshes:
            if mesh.material != material:
                f_lines.append(f'usemtl {mesh.material.name}')
                material = mesh.material
            for face in mesh.faces:
                vertexes = []
                for vertex in face.vertexes:
                    vertexes.append(f'{position_dict[vertex.position]}/{texcoord_dict[vertex.texcoord]}/{normal_dict[vertex.normal]}')
                f_lines.append(f'f {" ".join(vertexes)}')

        lines.extend(v_lines)
        lines.extend(vt_lines)
        lines.extend(vn_lines)
        lines.extend(f_lines)
        obj.write_text('\n'.join(lines), encoding='utf-8')

    @profiler
    def load_material(self, path: Path) -> None:
        lines = path.read_text(encoding='utf-8').splitlines()
        for line in lines:
            if line.startswith('#'):
                continue
            args = line.split(' ')
            match args:
                case ['newmtl', name]:
                    material = Material(name)
                    self.model.materials[name] = material
                case ['Kd', *color]:
                    material.diffuse = Color(*color)
                case ['Ka', *color]:
                    material.ambient = Color(*color)
                case ['map_Kd', *path]:
                    material.texture = self.load_texture(self.get(line[line.index(' ') + 1:]))

    def load_texture(self, path: Path) -> Texture:
        texture = Texture(path.name, Image.open(path))
        self.model.textures.append(texture)
        return texture
