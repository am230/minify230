from combiner230.importers.wavefront import Wavefront
from combiner230 import Minifier
from pathlib import Path
model_in = Wavefront(Path('533926434\\533926434_bldg_6677.obj'))
# model_in = Wavefront(Path('D:\\projects\\倉庫\\avaters\\tona\\tona.obj'))
model_in.parse()

model_out = Wavefront(Path('export\\combined.obj'))
model_out.export(Minifier(model_in.model).minify())
