import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty
import os
import tempfile

class MeshHistoryPreferences(AddonPreferences):
    bl_idname = __package__

    storage_path: StringProperty (
        name="Save DirectoryW",
        description="Path where mesh history is saved",
        default=os.path.join(tempfile.gettempdir(), "blender_mesh_history"),
        subtype='DIR_PATH'
    )



def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences


def register():
    bpy.utils.register_class(MeshHistoryPreferences)


def unregister():
    bpy.utils.unregister_class(MeshHistoryPreferences)