from combiner230.importers.wavefront import Wavefront
from combiner230 import Minifier
from pathlib import Path
from combiner230.profiler import profiler

@profiler
def test():
    model_in = Wavefront(Path('533926434\\533926434_bldg_6677.obj'))
    model_in.parse()

    model_out = Wavefront(Path('export\\combined.obj'))
    model_out.export(Minifier(model_in.model).minify())

if __name__ == '__main__':
    test()