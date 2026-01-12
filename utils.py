import json
import os
import tempfile
import bmesh
from datetime import datetime


DEFAULT_STORAGE_DIR = os.path.join(tempfile.gettempdir(), "blender_mesh_history")


def get_storage_directory():
    os.makedirs(DEFAULT_STORAGE_DIR, exist_ok=True)
    return DEFAULT_STORAGE_DIR


def generate_filename(object_name, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
    
    time_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    safe_name = "".join(c for c in object_name if c.isalnum() or c in "._- ")
    safe_name = safe_name[:50]
    
    return f"{safe_name}_{time_str}.json"


def format_file_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def capture_mesh_data(obj):
    if obj.type != 'MESH':
        raise ValueError("Object is not a mesh")
    
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    vertex = [[v.co.x, v.co.y, v.co.z] for v in bm.verts]
    edges = [[e.verts[0].index, e.verts[1].index] for e in bm.edges]
    faces = [[v.index for v in f.verts] for f in bm.faces]
    
    bm.free()
    
    return {
        "object_name": obj.name,
        "timestamp": datetime.now().isoformat(),
        "vertex": vertex,
        "edges": edges,
        "faces": faces,
        "vertex_count": len(vertex),
        "face_count": len(faces),
    }


def save_mesh_to_json(mesh_data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mesh_data, f, indent=2, ensure_ascii=False)
    
    return os.path.getsize(filepath)


def load_mesh_from_json(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not Found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def apply_mesh_data(obj, mesh_data):
    mesh = obj.data
    
    mesh.clear_geometry()
    
    bm = bmesh.new()
    
    for v_co in mesh_data["vertex"]:
        bm.verts.new(v_co)
    
    bm.verts.ensure_lookup_table()
    
    # Adicionar faces
    for f_indices in mesh_data["faces"]:
        try:
            verts = [bm.verts[i] for i in f_indices]
            bm.faces.new(verts)
        except (ValueError, IndexError):
            # Invalide Face or exists
            pass
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename