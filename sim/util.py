"""
辅助函数.
"""

from typing import Dict
from .basic import Scenario, Entity


def set_entity_attributes(scene: Scenario, attribs: Dict):
    """ 批量设置场景中实体的属性. 
    
    :param scene: 场景.
    :param attribs: 属性值，内容为{ 'entity_name.attrib_name' : value }
    """
    for k, v in attribs.items():
        strs = k.split('.')
        if len(strs) == 2:
            name, attr = strs[0], strs[1]
            if obj := scene.find(name):
                if hasattr(obj, attr):
                    setattr(obj, attr, v)
