import bpy
import os
from io_import_scene_unreal_psa_psk_280 import *

# Specify the input directory
input_directory = r"D:\CProjects\UEModelsConverter\Input"

# Specify the output directory
output_directory = r"D:\CProjects\UEModelsConverter\Output"

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
    relative_path = os.path.relpath(psk_file_path, input_directory)
    output_file_path = os.path.join(output_directory, relative_path.replace(".psk", ".glb"))
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=output_file_path, export_format='GLB')
    print(f"File saved as {output_file_path}")

# Iterate through all .psk files in the input directory and its subdirectories
for root, dirs, files in os.walk(input_directory):
    for file in files:
        if file.endswith(".psk"):
            # Clear all objects
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()

            psk_file_path = os.path.join(root, file)
            import_psk(psk_file_path)
            
            # Check if psk_file_path is a skeleton
            if 'dskeleton' in psk_file_path.lower():
                # TODO: add animation to skeleton and export as .glb
                # or just simply dont do anything who cares
                continue

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

            # Check if psk_file_path contains '/ACC/'
            # Accessories NEED to use their own skeleton
            
            # TODO: there's cosmetics that use their own animations and skeleton
            
            if os.path.sep + 'ACC' + os.path.sep in psk_file_path:
                # Select mesh and apply smooth shading
                bpy.context.view_layer.objects.active = mesh_object
                mesh_object.select_set(True)
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()
                print("Smooth shading applied to the mesh.")

                export(psk_file_path)
            
                # Rest of the code is pointless for accessories as we keep its own skeleton
                continue

            # Clear parent relationship
            bpy.context.view_layer.objects.active = mesh_object
            bpy.ops.object.parent_clear(type='CLEAR')

            # Delete the armature object
            bpy.data.objects.remove(selected_object)
            print("Armature deleted, only the mesh remains.")

            # Select mesh and apply smooth shading
            bpy.context.view_layer.objects.active = mesh_object
            mesh_object.select_set(True)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()
            
            # Find the path that ends with '/Models/'
            models_directory = None
            current_dir = os.path.dirname(psk_file_path)
            while current_dir and not current_dir.lower().endswith(os.path.sep + 'models'):
                current_dir = os.path.dirname(current_dir)

            if current_dir.lower().endswith(os.path.sep + 'models') or current_dir.lower().endswith(os.path.sep + 'model'):
                models_directory = current_dir
                print(models_directory)
                dskeleton_file = next((f for f in os.listdir(models_directory) if 'dskeleton' in f.lower()), None)
                
                if dskeleton_file:
                    # Load .psk file for the custom armature
                    custom_armature_file_path = os.path.join(models_directory, dskeleton_file)
                    import_psk(custom_armature_file_path)

                    # Select the mesh and armature objects
                    bpy.context.view_layer.objects.active = mesh_object
                    mesh_object.select_set(True)
                    bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
                    bpy.context.selected_objects[-1].select_set(True)

                    # Parent the mesh to the armature with empty groups
                    bpy.ops.object.parent_set(type='ARMATURE')

                    print("Mesh parented to the armature with empty groups.")

                    export(psk_file_path)
                else:
                    error_message = f"DSkeleton file not found in the Models directory for {psk_file_path}."
                    raise ValueError(error_message)
            else:
                error_message = f"No '/Models/' directory found in the path for {psk_file_path}."
                raise ValueError(error_message)