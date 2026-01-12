import bpy
import bmesh
import os
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty
from datetime import datetime

from . import utils
from .addon_preferences import get_preferences


class MESH_OT_save_snapshot(Operator):
    bl_idname = "mesh.save_snapshot"
    bl_label = "Save Snapshot"
    bl_description = "Create a snapshot of the mesh state"
    bl_options = {'REGISTER', 'UNDO'}
    
    snapshot_name: StringProperty(
        name="Snapshot Name",
        description="Snapshot Name",
        default="Snapshot"
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
    
    def execute(self, context):
        obj = context.active_object
        prefs = get_preferences()
        
        try:
            mesh_data = utils.capture_mesh_data(obj)
            
            storage_dir = prefs.storage_path
            os.makedirs(storage_dir, exist_ok=True)
            
            timestamp = datetime.now()
            filename = utils.generate_filename(obj.name, timestamp)
            filepath = os.path.join(storage_dir, filename)
            
            file_size = utils.save_mesh_to_json(mesh_data, filepath)
            
            snapshot = context.scene.mesh_snapshots.add()
            snapshot.name = self.snapshot_name if self.snapshot_name else f"Snapshot {len(context.scene.mesh_snapshots)}"
            snapshot.filepath = filepath
            snapshot.timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            snapshot.object_name = obj.name
            snapshot.vertex_count = mesh_data['vertex_count']
            snapshot.face_count = mesh_data['face_count']
            snapshot.file_size = file_size
            
            self.report({'INFO'}, f"Snapshot '{snapshot.name}' saved")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error on save: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        obj = context.active_object
        if obj:
            count = len(context.scene.mesh_snapshots) + 1
            self.snapshot_name = f"{obj.name}_v{count}"
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "snapshot_name", text="Name")

class MESH_OT_restore_snapshot(Operator):
    bl_idname = "mesh.restore_snapshot"
    bl_label = "Restore Snapshot"
    bl_description = "Restore a mesh for this snapshot state"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(default=-1)
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.mesh_snapshots) > 0
    
    def execute(self, context):
        snapshots = context.scene.mesh_snapshots
        
        if self.index < 0 or self.index >= len(snapshots):
            self.report({'ERROR'}, "Invalid snapshot")
            return {'CANCELLED'}
        
        snapshot = snapshots[self.index]
        
        try:
            mesh_data = utils.load_mesh_from_json(snapshot.filepath)
            
            obj = context.active_object
            
            if obj is None or obj.type != 'MESH':
                mesh = bpy.data.meshes.new(mesh_data['object_name'])
                obj = bpy.data.objects.new(mesh_data['object_name'], mesh)
                context.collection.objects.link(obj)
                context.view_layer.objects.active = obj
                obj.select_set(True)
            
            utils.apply_mesh_data(obj, mesh_data)
            
            self.report({'INFO'}, f"Snapshot '{snapshot.name}' restored")
            return {'FINISHED'}
            
        except FileNotFoundError:
            self.report({'ERROR'}, "File not Found")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error on restore: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        from .addon_preferences import get_preferences
        prefs = get_preferences()
        snapshots = context.scene.mesh_snapshots
        
        if self.index >= 0 and self.index < len(snapshots):
            snapshot = snapshots[self.index]
            
            if prefs.confirm_restore:
                return context.window_manager.invoke_confirm(
                    self,
                    event,
                    message=f"Restore '{snapshot.name}'?\nMesh will be replaced."
                )
        
        return self.execute(context)

class MESH_OT_delete_snapshot(Operator):
    bl_idname = "mesh.delete_snapshot"
    bl_label = "Delete Snapshot"
    bl_description = "Delete this snapshot forever"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(default=-1)
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.mesh_snapshots) > 0
    
    def execute(self, context):
        snapshots = context.scene.mesh_snapshots
        
        if self.index < 0 or self.index >= len(snapshots):
            return {'CANCELLED'}
        
        snapshot = snapshots[self.index]
        
        try:
            if os.path.exists(snapshot.filepath):
                os.remove(snapshot.filepath)
            
            snapshots.remove(self.index)
            
            self.report({'INFO'}, "Snapshot deleted")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error on delete: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        from .addon_preferences import get_preferences
        prefs = get_preferences()
        
        if prefs.confirm_delete:
            snapshots = context.scene.mesh_snapshots
            if self.index >= 0 and self.index < len(snapshots):
                snapshot = snapshots[self.index]
                return context.window_manager.invoke_confirm(
                    self,
                    event,
                    message=f"Delete '{snapshot.name}'?"
                )
        
        return self.execute(context)
    
class MESH_OT_clear_all_snapshots(Operator):
    bl_idname = "mesh.clear_all_snapshots"
    bl_label = "Remove All"
    bl_description = "Remove all saved snapshots"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.mesh_snapshots) > 0
    
    def execute(self, context):
        snapshots = context.scene.mesh_snapshots
        count = len(snapshots)
        
        try:
            for snapshot in snapshots:
                if os.path.exists(snapshot.filepath):
                    os.remove(snapshot.filepath)
            
            snapshots.clear()
            
            self.report({'INFO'}, f"{count} snapshots deleted ")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        count = len(context.scene.mesh_snapshots)
        return context.window_manager.invoke_confirm(
            self,
            event,
            message=f"Delete all {count} snapshots?\nThis action can't be reverted"
        )

classes = (
    MESH_OT_save_snapshot,
    MESH_OT_restore_snapshot,
    MESH_OT_delete_snapshot,
    MESH_OT_clear_all_snapshots,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)