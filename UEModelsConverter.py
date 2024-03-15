import bpy
import os
import json
import shutil
from io_import_scene_unreal_psa_psk_280 import *

# Specify the root directory
root_directory = r"C:\Users\mateu\Downloads\CodeProjects\AssetsParser\UEModelsConverter"

# Specify the input directory
input_directory = r"C:\Users\mateu\Downloads\CodeProjects\AssetsParser\UEModelsConverter\Input"

# Specify the input directory for JSON files
input_mapping_directory = r"C:\Users\mateu\Downloads\CodeProjects\AssetsParser\Output\ModelsData"

# Specify the output directory
output_directory = r"C:\Users\mateu\Downloads\CodeProjects\AssetsParser\UEModelsConverter\Output"

# Specify the log directory
log_directory = os.path.join(root_directory, "Logs")

# Specify the log file path
log_file_path = os.path.join(log_directory, "log.txt")

# Path for logs check
log_check_file_path = r"D:\dbd-info-dev\assets"

# Clear the log file on script start, old log will be lost
with open(log_file_path, 'w') as log_file:
    log_file.write("")

# Function to log messages to the file
def log_to_file(message):
    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')

def log_textures_to_file(texture_paths):
    # Check if texture paths exist in the directory
    for texture_path in texture_paths:
        # Remove the initial "/assets/" part from the texture path
        texture_relative_path = texture_path.replace("/assets/", "")
        check_texture_path = os.path.join(log_check_file_path, texture_relative_path)
        if not os.path.exists(check_texture_path):
            # Log missing texture paths to a file
            message = f"[NOT FOUND TEXTURE] Texture not found: {texture_path}"
            print(message)
            log_to_file(message)

# Function to import .psk file
def import_psk(file_path):
    # Get the base name of the file without the extension
    base_name = os.path.basename(file_path)
    base_name = os.path.splitext(base_name)[0]

    # Check if an object with the same name already exists
    if base_name in bpy.data.objects:
        # If it does, delete the existing object
        bpy.data.objects[base_name].select_set(True)
        bpy.ops.object.delete()

    # Import the .psk file
    pskimport(file_path, bReorientBones=False)

# Export as .gLTF 2.0 (.glb) file
def export(psk_file_path):
    # Specify the output file path with .glb extension
    #relative_path = os.path.relpath(psk_file_path, input_directory)
    output_file_path = os.path.join(output_directory, psk_file_path.replace(".psk", ".glb").replace("Input", "Output"))
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=output_file_path, export_format='GLB')
    print(f"File saved as {output_file_path}")
    
# Function to move all .png files from Input to Output
def move_png_files(input_directory, output_directory):
    # Iterate through all files in the input directory
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".png"):
                # Construct the source and destination file paths
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_file_path, input_directory)
                destination_file_path = os.path.join(output_directory, relative_path)

                # Create the output directory if it doesn't exist
                os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

                # Move the .png file to the output directory
                shutil.move(source_file_path, destination_file_path)
                
def clear_scene():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Iterate over all objects and unlink them
    for obj in bpy.context.scene.objects:
        bpy.context.collection.objects.unlink(obj)
                
# Call the function to move .png files
move_png_files(input_directory, output_directory)

texture_paths = []
# Iterate through all .json files in the input mapping directory
for root, dirs, files in os.walk(input_mapping_directory):
    for file in files:
        if file.endswith(".json"):
            # Clear all objects
            clear_scene()

            json_file_path = os.path.join(root, file)

            # Read the JSON file
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

            # Iterate through the JSON data and process each entry
            for key, value in data.items():
                model_path = value.get("ModelPath", "")
                skeleton_path = value.get("SkeletonPath", "")

                # Iterate through Materials and grab texture paths
                materials = value.get("Materials", {})
                for material in materials.values():
                    if isinstance(material, dict):
                        textures = material.get("Textures", {})
                        texture_paths.extend(textures.values())
                
                # Iterate through Accessories and grab model path
                accessories = value.get("Accessories", [])
                for accessory in accessories:
                    # Clear all objects
                    clear_scene()

                    accessory_materials = accessory.get("Materials", {})
                    for accessory_material in accessory_materials.values():
                        if isinstance(accessory_material, dict):
                            accessory_textures = accessory_material.get("Textures", {})
                            texture_paths.extend(accessory_textures.values())
            
                    accessory_model_path = accessory.get("ModelPath", "")
                    accessory_glb_file_path = os.path.join(root_directory, "Output", accessory_model_path.replace('/assets/', ''))
                    accessory_model_path_psk = os.path.splitext(accessory_model_path)[0] + ".psk"
                    accessory_model_path_psk = accessory_model_path_psk.replace('/assets/', '')
                    accessory_psk_file_path = os.path.join(root_directory, "Input", accessory_model_path_psk)

                    accessory_logs_check_glb_file_path = accessory_model_path.replace('/assets/', '')
                    accessory_logs_check_file_path = os.path.join(log_check_file_path, accessory_logs_check_glb_file_path)
                    
                    # Skip if converted file already exists
                    if os.path.exists(accessory_glb_file_path):
                        print(f"[SKIP] File {accessory_glb_file_path} already exists. Skipping export.")
                        continue

                    # Check if the file exists
                    if not os.path.exists(accessory_psk_file_path):
                        log_message = f"[NOT FOUND ACCESSORY] File not found: {accessory_psk_file_path}."
                        if not os.path.exists(accessory_logs_check_file_path):
                            print(log_message)
                            log_to_file(log_message)
                        continue

                    # Import the accessory PSK file
                    import_psk(accessory_psk_file_path)
                    
                    # Select the imported mesh object
                    selected_object = bpy.context.selected_objects[0]
                    
                    # Check if the selected object has a mesh data type
                    mesh_object = None
                    # If the selected object is not a mesh, try to find the associated mesh
                    if selected_object.type == 'ARMATURE' and selected_object.data:
                        for child in selected_object.children:
                            if child.type == 'MESH':
                                mesh_object = child
                                print("Selected object is an armature. Found associated mesh.")
                                break
                    else:
                        print("Selected object is not a mesh or armature with an associated mesh.")
                    
                    # Select mesh and apply smooth shading
                    bpy.context.view_layer.objects.active = mesh_object
                    mesh_object.select_set(True)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.shade_smooth()
                    print("Smooth shading applied to the mesh.")

                    export(accessory_model_path_psk)

                # Replace the extension with .psk
                model_path_psk = os.path.splitext(model_path)[0] + ".psk"
                model_path_glb = os.path.splitext(model_path)[0] + ".glb"
                skeleton_path_psk = os.path.splitext(skeleton_path)[0] + ".psk"

                # Remove /assets/ from path
                model_path_psk = model_path_psk.replace('/assets/', '')
                model_path_glb = model_path_glb.replace('/assets/', '')
                skeleton_path_psk = skeleton_path_psk.replace('/assets/', '')
                
                output_model_path = model_path
                output_model_path = output_model_path.replace('/assets/', '')
                output_model_path = os.path.join(output_directory, output_model_path)
                
                # Skip if converted file already exists
                if os.path.exists(output_model_path):
                    print(f"[SKIP] File {output_model_path} already exists. Skipping export.")
                    continue

                # Construct the full path for the PSK file
                model_psk_file_path = os.path.join(root_directory, "Input", model_path_psk)
                skeleton_psk_file_path = os.path.join(root_directory, "Input", skeleton_path_psk)

                model_logs_check_file_path = os.path.join(log_check_file_path, model_path_glb)
                
                # If file doesnt exist, skip
                if not os.path.exists(model_psk_file_path):
                    log_message = f"[NOT FOUND MESH] File not found: {model_psk_file_path}"
                    if not os.path.exists(model_logs_check_file_path):
                        print(log_message)
                        log_to_file(log_message)
                    continue
                    
                # Clear all objects
                clear_scene()

                # Import the PSK file
                import_psk(model_psk_file_path)

                # Select the imported mesh object
                selected_object = bpy.context.selected_objects[0]
                # Check if the selected object has a mesh data type
                mesh_object = None
                # If the selected object is not a mesh, try to find the associated mesh
                if selected_object.type == 'ARMATURE' and selected_object.data:
                    for child in selected_object.children:
                        if child.type == 'MESH':
                            mesh_object = child
                            #print("Selected object is an armature. Found associated mesh.")
                            break

                # Select mesh and apply smooth shading
                bpy.context.view_layer.objects.active = mesh_object
                mesh_object.select_set(True)
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()

                export(model_path_psk)

log_textures_to_file(texture_paths)

print("Finished converting models.")