from combiner230.importers.wavefront import Wavefront
from combiner230 import Minifier
from pathlib import Path
from combiner230.profiler import profiler

@profiler
def test():
    model_in = Wavefront(Path('D:\\projects\\倉庫\\blender\\satellite.obj'))
    # model_in = Wavefront(Path('D:\\projects\\倉庫\\avaters\\tona\\tona.obj'))
    model_in.parse()

    model_out = Wavefront(Path('export\\combined.obj'), fast_export=False)
    model_out.export(Minifier(model_in.model).minify())

if __name__ == '__main__':
    test()