import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import os
import tempfile

class MeshHistoryPreferences(AddonPreferences):
    bl_idname = __package__

    storage_path: StringProperty (
        name="Save Directory",
        description="Path where mesh history is saved",
        default=os.path.join(tempfile.gettempdir(), "blender_mesh_history"),
        subtype='DIR_PATH'
    )

    show_vertex_count: BoolProperty(
        name="Show Vertex Count",
        description="Show the number of vertices and faces on snapshots",
        default=True
    )

    show_file_size: BoolProperty(
        name="Show File Size",
        description="Show File Size of each snapshot",
        default=True
    )
    
    confirm_restore: BoolProperty(
        name="Confirm Restore",
        description="Ask confirmation before restoring a snapshot", 
        default=True
    )
    
    confirm_delete: BoolProperty(
        name="Confirm Delete",
        description="Ask confirmation before restoring a snapshot",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Storage:", icon='FILE_FOLDER')
        box.prop(self, "storage_path")
        
        row = box.row()
        row.label(text=f"Storage Location: {self.storage_path}", icon='INFO')


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences


def register():
    bpy.utils.register_class(MeshHistoryPreferences)


def unregister():
    bpy.utils.unregister_class(MeshHistoryPreferences)