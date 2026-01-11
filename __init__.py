import bpy

bl_info = {
    "name": "Mesh History Manager",
    "author": "Nuno Sponsor",
    "version": (1, 0, 0),
    "blender": (5, 0, 1),
    "description": "Save and restores mesh states",
    "category": "Object",
    "doc_url": "",
    "releases_url": ""
}

from . import addon_preferences
from . import properties
from . import operators
from . import ui

# Lista de módulos para registar
modules = [
    addon_preferences,
    properties,
    operators,
    ui,
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