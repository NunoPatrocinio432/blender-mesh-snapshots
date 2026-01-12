import bpy
from bpy.types import Panel

from . import utils
from .addon_preferences import get_preferences


class MESH_history_panel(Panel):
    bl_label = "Mesh History"
    bl_idname = "MESH_history_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mesh History'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prefs = get_preferences()
        
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("mesh.save_snapshot", icon='ADD', text="Save Snapshot")
        
        layout.separator()
        
        if len(scene.mesh_snapshots) > 0:
            box = layout.box()
            row = box.row()
            row.label(text=f"Total: {len(scene.mesh_snapshots)}", icon='FILE')
            
            if prefs.show_file_size:
                total_size = sum(s.file_size for s in scene.mesh_snapshots)
                row.label(text=utils.format_file_size(total_size))
        
        layout.separator()
        
        if len(scene.mesh_snapshots) > 0:
            box = layout.box()
            box.label(text="Saved Snapshots:", icon='DOCUMENTS')
            
            for i, snapshot in enumerate(scene.mesh_snapshots):
                snap_box = box.box()
                
                row = snap_box.row(align=True)
                row.label(text=snapshot.name, icon='MESH_DATA')
                
                col = row.column(align=True)
                col.scale_x = 0.8
                
                op = col.operator(
                    "mesh.restore_snapshot",
                    text="",
                    icon='RECOVER_LAST'
                )
                op.index = i
                
                op = col.operator(
                    "mesh.delete_snapshot",
                    text="",
                    icon='TRASH'
                )
                op.index = i
                
                info_col = snap_box.column(align=True)
                info_col.scale_y = 0.8
                
                info_col.label(
                    text=f"  Objeto: {snapshot.object_name}",
                    icon='OBJECT_DATA'
                )
                info_col.label(
                    text=f"  Data: {snapshot.timestamp}",
                    icon='TIME'
                )
                
                if prefs.show_vertex_count:
                    info_col.label(
                        text=f"  Geometry: {snapshot.vertex_count}v / {snapshot.face_count}f",
                        icon='EDITMODE_HLT'
                    )
                
                if prefs.show_file_size:
                    info_col.label(
                        text=f"  Size: {utils.format_file_size(snapshot.file_size)}",
                        icon='DISK_DRIVE'
                    )
            
            layout.separator()
            row = layout.row()
            row.operator("mesh.clear_all_snapshots", icon='TRASH', text="Clear all")
        
        else:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="No snapshot saved", icon='INFO')
            col.separator(factor=0.5)
            col.label(text="Select one mesh and click")
            col.label(text="'Save snapshot' to start")
            row.label(text=utils.format_file_size(total_size))


class MESH_history_info(Panel):
    bl_label = "Help"
    bl_idname = "MESH_history_info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mesh History'
    bl_parent_id = "MESH_history_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="How To Use:", icon='QUESTION')
        
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. Select one mesh object")
        col.label(text="2. Click in 'Save Snapshot'")
        col.label(text="3. Change the mesh as you like it")
        col.label(text="4. Use ↻ to restore to previous state")
        col.label(text="5. Use 🗑️ to delete snapshot")
        
        layout.separator()
        
        # Informações adicionais
        box = layout.box()
        box.label(text="Information:", icon='INFO')
        
        col = box.column(align=True)
        col.scale_y = 0.8
        
        storage_dir = utils.get_storage_directory()
        col.label(text="Files saved in:")
        col.label(text=f"  {storage_dir}")


classes = (
    MESH_history_panel,
    MESH_history_info,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)