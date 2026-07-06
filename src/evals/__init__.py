from .jailbreakbench import JailbreakBenchEval
from .harmbench import HarmBenchEval
from .strongreject import StrongRejectEval

EVAL_REGISTRY = {
    "jailbreakbench": JailbreakBenchEval,
    "harmbench": HarmBenchEval,
    "strongreject": StrongRejectEval,
}
