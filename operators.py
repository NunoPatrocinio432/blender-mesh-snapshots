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
        if context.mode == 'EDIT_MESH':
            self.report({'ERROR'}, "It's not possible to save a snapshot in Edit Mode.")
            return {'CANCELLED'}

        obj = context.active_object
        if obj:
            count = sum(
                1
                for snap in context.scene.mesh_snapshots
                if snap.object_name == obj.name
            )            
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
                self.report({'ERROR'}, 
                    f"Select the object '{mesh_data['object_name']}'")
                return {'CANCELLED'}
            
            original_name = mesh_data['object_name']
            current_name = obj.name
            
            if current_name != original_name:
                self.report({'ERROR'}, 
                    f"This snapshot only works on the object '{original_name}'. "
                    f"Current object: '{current_name}'")
                return {'CANCELLED'}
            
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            utils.apply_mesh_data(obj, mesh_data)
            
            self.report({'INFO'}, 
                f"✓ Snapshot '{snapshot.name}' restored "
                f"({mesh_data['vertex_count']}v, {mesh_data['face_count']}f)")
            return {'FINISHED'}
            
        except FileNotFoundError:
            self.report({'ERROR'}, "File not Found")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error on restore: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        prefs = get_preferences()
        snapshots = context.scene.mesh_snapshots
        
        if self.index >= 0 and self.index < len(snapshots):
            snapshot = snapshots[self.index]
            
            obj = context.active_object
            if obj is None or obj.type != 'MESH':
                self.report({'WARNING'}, 
                    f"Select the object '{snapshot.object_name}' first")
                return {'CANCELLED'}
            
            original_name = snapshot.object_name
            current_name = obj.name
            
            if current_name != original_name:
                self.report({'ERROR'}, 
                    f"Incompatible snapshot! This snapshot belongs to the object. '{original_name}'. "
                    f"Current object: '{current_name}'")
                return {'CANCELLED'}
            
            if prefs.confirm_restore:
                message=f"Restore '{snapshot.name}'?\nMesh will be replaced."
                
                return context.window_manager.invoke_confirm(
                    self,
                    event,
                    message=message
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
    
class MESH_clear_object_snapshots(Operator):
    bl_idname = "mesh.clear_object_snapshots"
    bl_label = "Clear Object's Snapshots"
    bl_description = "Remove all object's snapshots"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return False
        
        current_name = obj.name
        for snapshot in context.scene.mesh_snapshots:
            if snapshot.object_name == current_name:
                return True
        return False
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}
        
        current_name = obj.name
        snapshots = context.scene.mesh_snapshots
        
        try:
            indices_to_remove = []
            for i in range(len(snapshots) - 1, -1, -1):
                snapshot = snapshots[i]
                if snapshot.object_name == current_name:
                    if os.path.exists(snapshot.filepath):
                        os.remove(snapshot.filepath)
                    indices_to_remove.append(i)
            
            for i in indices_to_remove:
                snapshots.remove(i)
            
            count = len(indices_to_remove)
            self.report({'INFO'}, f"{count} snapshots of '{current_name}' deleted")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        obj = context.active_object
        if not obj:
            return {'CANCELLED'}
        
        current_name = obj.name
        
        count = sum(1 for s in context.scene.mesh_snapshots if s.object_name == current_name)
        
        return context.window_manager.invoke_confirm(
            self,
            event,
            message=f"Delete {count} snapshot of '{current_name}'?\nThis action can't be reverted."
        )


classes = (
    MESH_OT_save_snapshot,
    MESH_OT_restore_snapshot,
    MESH_OT_delete_snapshot,
    MESH_OT_clear_all_snapshots,
    MESH_clear_object_snapshots
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)