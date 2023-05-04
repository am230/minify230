from minify230.importers.wavefront import Wavefront
from minify230.model import Model
from minify230 import Minifier
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

path = Path('LOD2')
temp = Path('temp')

def pre_process(obj: Path):
    a = Wavefront(obj)
    a.parse()
    dest = Wavefront(temp / obj.stem / 'combined.obj')
    if dest.base.exists():
        print('[*]', obj.name)
        return
    dest.base.mkdir(parents=True, exist_ok=True)
    dest.export(Minifier(a.model).minify())
    print('[+]', obj.name)

if __name__ == '__main__':
    combined = Model()

    for obj in path.glob('*/*.obj'):
        a = Wavefront(obj)
        a.model = combined
        a.parse()
        print('[+]', obj.name)


    Wavefront(Path('export10', 'combined.obj')).export(Minifier(combined).minify())

# a = Wavefront(Path('LOD2\\533926434\\533926434_bldg_6677.obj'))
# a = Wavefront(Path('cubes', 'untitled.obj'))
# a.parse()

# b = Wavefront(Path('test', 'export', 'untitled.obj'))
# b.export(Minifier(a.model).minify())
