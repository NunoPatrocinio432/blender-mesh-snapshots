bl_info = {
    "name": "Mesh History Manager",
    "author": "Nuno Sponsor",
    "version": (1, 0, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > Mesh History",
    "description": "Save and restores mesh states",
    "category": "Object",
    "doc_url": "",
    "releases_url": ""
}

import bpy

from . import addon_preferences
from . import properties
from . import operators
from . import panels


modules = [
    addon_preferences,
    properties,
    operators,
    panels,
]

def register():
    for module in modules:
        module.register()
    
    print("Mesh History: Addon sucessfully registered")

def unregister():
    for module in reversed(modules):
        module.unregister()
    
    print("Mesh History: Addon sucessfully unregistered")

if __name__ == "__main__":
    register()