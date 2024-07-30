# UEModelsConverter - Blender PSK to GLTF Converter

<a href="https://www.python.org" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" align="right" alt="Python logo" width="64">
</a>

<a href="https://www.blender.org" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/0/0c/Blender_logo_no_text.svg" align="right" alt="Blender Logo" width="64">
</a>

This is a simple Python script that converts .psk file (Unreal Engine Skeletal Mesh File format) to .glb file format using Blender.

## Requirements

* Blender 2.80 or later
* io_import_scene_unreal_psa_psk_280 module
* Models data mappings generated with UEParser app (supports Dead by Daylight game only)*

*App generates models data (in JSON format) from cooked UE containers that can be later used to load models into 3D environment using library such as ThreeJS

## Usage

Run the script with Blender using the following command:
```bash
blender --background --python UEModelsConverter.py -- --root_directory /path/to/root --input_directory /path/to/input --input_mapping_directory /path/to/json --output_directory /path/to/output
