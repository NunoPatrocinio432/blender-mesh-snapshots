import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty
from bpy.types import PropertyGroup


class MeshSnapshot(PropertyGroup):    
    name: StringProperty(
        name="Name",
        description="Name of Snapshot",
        default="Snapshot"
    )
    
    filepath: StringProperty(
        name="Path",
        description="Path for JSON file",
        default=""
    )
    
    timestamp: StringProperty(
        name="Date/Time",
        description="Snapshot creation date and time",
        default=""
    )
    
    object_name: StringProperty(
        name="Object",
        description="Name opf the object of the original mesh",
        default=""
    )
    
    vertex_count: IntProperty(
        name="Vertex",
        description="Number of vertex",
        default=0,
        min=0
    )
    
    face_count: IntProperty(
        name="Faces",
        description="Total number of fases",
        default=0,
        min=0
    )
    
    file_size: IntProperty(
        name="Size",
        description="File Size",
        default=0,
        min=0
    )

def register():
    bpy.utils.register_class(MeshSnapshot)
    
    bpy.types.Scene.mesh_snapshots = CollectionProperty(
        type=MeshSnapshot,
        name="Mesh Snapshots",
        description="List of Saved Snapshots"
    )
    
    bpy.types.Scene.mesh_history_active_index = IntProperty(
        name="Active Index",
        default=0,
        min=0
    )

def unregister():
    del bpy.types.Scene.mesh_history_active_index
    del bpy.types.Scene.mesh_snapshots
    
    bpy.utils.unregister_class(MeshSnapshot)