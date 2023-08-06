from bytez.tasks.language_modelling._models.blinkdl_rwkv_lm import BlinkdlRwkvLmModel
from dataclasses import dataclass
from bytez.tasks.language_modelling._models.hazyresearch_h3 import HazyresearchH3Model


@dataclass
class LanguageModellingModels:
    hazyresearch_h3 = HazyresearchH3Model().inference
    blinkdl_rwkv_lm = BlinkdlRwkvLmModel().inference