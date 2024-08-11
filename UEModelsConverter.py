import bpy
import os
import json
import shutil
import argparse
import sys
from io_import_scene_unreal_psa_psk_280 import pskimport

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Process paths for Blender script.')
    parser.add_argument('--root_directory', type=str, required=True, help='The root directory')
    parser.add_argument('--input_directory', type=str, required=True, help='The input directory')
    parser.add_argument('--input_mapping_directory', type=str, required=True, help='The input directory for JSON files')
    parser.add_argument('--output_directory', type=str, required=True, help='The output directory')
    return parser.parse_args(sys.argv[sys.argv.index("--")+1:])


def setup_logging(log_directory):
    """Set up logging to a file."""
    log_file_path = os.path.join(log_directory, "UEModelsConverter-Logs.log")
    with open(log_file_path, 'w') as log_file:
        log_file.write("")
    return log_file_path


def log_to_file(log_file_path, message):
    """Log messages to the specified log file."""
    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')
    print(message)


def clear_scene():
    """Clear all objects in the current Blender scene."""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def import_psk(file_path):
    """Import a PSK file into Blender."""
    try:
        pskimport(file_path, bReorientBones=False)
    except Exception as e:
        log_to_file(log_file_path, f"[ERROR] Failed to import PSK file {file_path}: {e}")


def export_as_gltf(output_file_path):
    """Export the current Blender scene as a GLTF file."""
    try:
        bpy.ops.export_scene.gltf(filepath=output_file_path, export_format='GLB')
        log_to_file(log_file_path, f"[INFO] File saved as {output_file_path}")
    except Exception as e:
        log_to_file(log_file_path, f"[ERROR] Failed to export GLTF file {output_file_path}: {e}")


def process_json_files(root_directory, input_mapping_directory, output_directory, log_file_path, input_directory):
    """Process JSON files to import PSK files and export them as GLTF."""
    for root, dirs, files in os.walk(input_mapping_directory):
        for file in files:
            if file.endswith(".json"):
                clear_scene()
                json_file_path = os.path.join(root, file)
                try:
                    with open(json_file_path, 'r') as json_file:
                        data = json.load(json_file)
                    process_json_data(data, root_directory, output_directory, log_file_path, input_directory)
                except Exception as e:
                    log_to_file(log_file_path, f"[ERROR] Failed to process JSON file {json_file_path}: {e}")


def process_json_data(data, root_directory, output_directory, log_file_path, input_directory):
    """Process data from a JSON file."""
    for key, value in data.items():
        process_model_data(value, root_directory, output_directory, log_file_path, input_directory)
        process_accessories_data(value, root_directory, output_directory, log_file_path, input_directory)


def process_model_data(model_data, root_directory, output_directory, log_file_path, input_directory):
    """Process model data from a JSON entry."""
    model_path = model_data.get("ModelPath", "")
    model_path_psk = os.path.splitext(model_path)[0] + ".psk"
    model_path_psk = model_path_psk.replace('/assets/', '')
    model_psk_file_path = os.path.join(input_directory, model_path_psk)
    
    if not os.path.exists(model_psk_file_path):
        # log_to_file(log_file_path, f"[WARN] Mesh not found: {model_psk_file_path}")
        return

    clear_scene()
    import_psk(model_psk_file_path)
    apply_smooth_shading()
    export_model(model_path_psk, output_directory)


def process_accessories_data(model_data, root_directory, output_directory, log_file_path, input_directory):
    """Process accessories data from a JSON entry."""
    accessories = model_data.get("Accessories", [])
    for accessory in accessories:
        accessory_model_path = accessory.get("ModelPath", "")
        accessory_model_path_psk = os.path.splitext(accessory_model_path)[0] + ".psk"
        accessory_model_path_psk = accessory_model_path_psk.replace('/assets/', '')
        accessory_psk_file_path = os.path.join(input_directory, accessory_model_path_psk)
        
        if not os.path.exists(accessory_psk_file_path):
            # log_to_file(log_file_path, f"[WARN] Accessory not found: {accessory_psk_file_path}")
            continue

        clear_scene()
        import_psk(accessory_psk_file_path)
        apply_smooth_shading()
        export_model(accessory_model_path_psk, output_directory)


def apply_smooth_shading():
    """Apply smooth shading to the selected mesh object."""
    selected_object = bpy.context.selected_objects[0]
    mesh_object = None
    
    if selected_object.type == 'ARMATURE' and selected_object.data:
        for child in selected_object.children:
            if child.type == 'MESH':
                mesh_object = child
                break

    if mesh_object:
        bpy.context.view_layer.objects.active = mesh_object
        mesh_object.select_set(True)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        print("Smooth shading applied to the mesh.")


def export_model(model_psk_file_path, output_directory):
    """Export the imported model as a GLTF file."""
    output_file_path = model_psk_file_path.replace(".psk", ".glb")
    output_file_path = os.path.join(output_directory, output_file_path)
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # Don't export skeletons
    if 'DSkleton' in model_psk_file_path:
        log_to_file(log_file_path, f"[WARN] PSK file path contains 'DSkleton'. Skipping export")
        return
    
    if os.path.exists(output_file_path):
        log_to_file(log_file_path, f"[INFO] File {output_file_path} already exists in output. Skipping export.")
        return
    
    export_as_gltf(output_file_path)


if __name__ == "__main__":
    args = parse_arguments()
    
    root_directory = args.root_directory
    input_directory = args.input_directory
    input_mapping_directory = args.input_mapping_directory
    output_directory = args.output_directory
    
    log_directory = os.path.join(root_directory, "Output", "Logs")
    log_file_path = setup_logging(log_directory)

    log_to_file(log_file_path, f"[INFO] UEModelsConverter script started.")
    
    process_json_files(root_directory, input_mapping_directory, output_directory, log_file_path, input_directory)
    
    log_to_file(log_file_path, f"[SUCCESS] Finished converting models.")