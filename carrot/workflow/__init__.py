"""workflow registry（s16 宿主 registry：注册保存好的固定编排）。"""

from . import examples

WORKFLOWS = {
    examples.META["name"]: (examples.META, examples.build_review_changes_graph),
}
