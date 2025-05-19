import xml.etree.ElementTree as ET
import os
import shutil
from copy import deepcopy

# --- Configuration ---
SECTIONS_TO_SYNC = [
    "./actorStats",
    "./spell1",
    "./spell2",
    "./spell3",
    "./spell4",
]

ACTOR_DATA_PATH = "./MonoBehaviours/ActorData"
OUTPUT_DIR = "output"

def get_element_by_xpath(root, xpath):
    """Finds an element by its XPath using ET's limited find."""
    try:
        return root.find(xpath)
    except SyntaxError:
        print(f"Warning: XPath syntax error for '{xpath}'. ET's find is limited.")
        return None

def process_character_skins(base_xml_path_orig, skin_xml_paths_input_orig, backup_in_original_loc=True):
    """
    Updates specified sections in skin XML files based on a base XML file
    and saves both base and processed skins to the flat OUTPUT_DIR.
    """
    print(f"\n--- Processing Character from Base: {base_xml_path_orig} ---")

    if not os.path.exists(base_xml_path_orig):
        print(f"  Error: Original Base XML file not found: {base_xml_path_orig}. Skipping this character.")
        return

    base_filename = os.path.basename(base_xml_path_orig)
    output_base_xml_path = os.path.join(OUTPUT_DIR, base_filename)

    try:
        shutil.copy2(base_xml_path_orig, output_base_xml_path)
        print(f"  Copied base file to: {output_base_xml_path}")
    except Exception as e:
        print(f"  Error copying base file '{base_xml_path_orig}' to '{output_base_xml_path}': {e}")
        return

    skin_xml_paths_orig = [p for p in skin_xml_paths_input_orig if p and isinstance(p, str) and p.strip()]

    if not skin_xml_paths_orig:
        print(f"  No valid skin files to process for {base_xml_path_orig}. Only base file copied to output.")
        return

    try:
        base_tree = ET.parse(base_xml_path_orig)
        base_root = base_tree.getroot()
        base_actor_data = get_element_by_xpath(base_root, ACTOR_DATA_PATH)

        if base_actor_data is None:
            print(f"  Error: <ActorData> not found in base file '{base_xml_path_orig}' at path '{ACTOR_DATA_PATH}'. Skins may not be processed correctly.")
            return

        base_sections_to_copy = {}
        for section_xpath_relative in SECTIONS_TO_SYNC:
            section_element = get_element_by_xpath(base_actor_data, section_xpath_relative)
            if section_element is not None:
                base_sections_to_copy[section_xpath_relative] = deepcopy(section_element)
            else:
                print(f"  Warning: Section '{section_xpath_relative}' not found in base file '{base_xml_path_orig}'. It will not be synced for its skins.")

    except ET.ParseError as e:
        print(f"  Error parsing base XML file '{base_xml_path_orig}': {e}. Skins for this character will not be processed with sync.")
        for skin_path_orig in skin_xml_paths_orig:
            if os.path.exists(skin_path_orig):
                skin_filename = os.path.basename(skin_path_orig)
                output_skin_path = os.path.join(OUTPUT_DIR, skin_filename)
                try:
                    shutil.copy2(skin_path_orig, output_skin_path)
                    print(f"    Copied original skin (due to base parse error): {skin_path_orig} -> {output_skin_path}")
                except Exception as copy_e:
                    print(f"    Failed to copy skin {skin_path_orig} after base parse error: {copy_e}")
            else:
                print(f"    Original skin file not found: {skin_path_orig}")
        return
    except Exception as e:
        print(f"  An unexpected error occurred while processing base file '{base_xml_path_orig}': {e}. Skins will not be processed with sync.")
        for skin_path_orig in skin_xml_paths_orig:
            if os.path.exists(skin_path_orig):
                skin_filename = os.path.basename(skin_path_orig)
                output_skin_path = os.path.join(OUTPUT_DIR, skin_filename)
                try:
                    shutil.copy2(skin_path_orig, output_skin_path)
                    print(f"    Copied original skin (due to base processing error): {skin_path_orig} -> {output_skin_path}")
                except Exception as copy_e:
                    print(f"    Failed to copy skin {skin_path_orig} after base processing error: {copy_e}")
            else:
                print(f"    Original skin file not found: {skin_path_orig}")
        return


    for skin_xml_path_orig in skin_xml_paths_orig:
        skin_filename = os.path.basename(skin_xml_path_orig)
        output_skin_xml_path = os.path.join(OUTPUT_DIR, skin_filename)
        print(f"  Processing skin file: {skin_xml_path_orig} -> {output_skin_xml_path}")

        if not os.path.exists(skin_xml_path_orig):
            print(f"    Error: Original skin XML file not found: {skin_xml_path_orig}. Skipping.")
            continue

        if backup_in_original_loc:
            backup_path_orig = skin_xml_path_orig + ".bak"
            try:
                shutil.copy2(skin_xml_path_orig, backup_path_orig)
            except Exception as e:
                print(f"    Warning: Could not backup original skin file '{skin_xml_path_orig}': {e}")

        try:
            if not base_sections_to_copy:
                shutil.copy2(skin_xml_path_orig, output_skin_xml_path)
                print(f"    Copied skin file (no sync data available from base) to: {output_skin_xml_path}")
                continue

            skin_tree = ET.parse(skin_xml_path_orig)
            skin_root = skin_tree.getroot()
            skin_actor_data = get_element_by_xpath(skin_root, ACTOR_DATA_PATH)

            if skin_actor_data is None:
                print(f"    Warning: <ActorData> not found in skin file '{skin_xml_path_orig}'. Copying as-is.")
                shutil.copy2(skin_xml_path_orig, output_skin_xml_path)
                continue

            # Perform the sync
            for section_xpath_relative, base_section_element_copy in base_sections_to_copy.items():
                old_skin_section = get_element_by_xpath(skin_actor_data, section_xpath_relative)
                if old_skin_section is not None:
                    try:
                        children_list = list(skin_actor_data)
                        idx = children_list.index(old_skin_section)
                        skin_actor_data.remove(old_skin_section)
                        skin_actor_data.insert(idx, deepcopy(base_section_element_copy))
                    except ValueError:
                        print(f"    Warning: Could not find exact position for '{section_xpath_relative}' in '{skin_xml_path_orig}'. Appending instead.")
                        skin_actor_data.append(deepcopy(base_section_element_copy))
                else:
                    print(f"    Info: Section '{section_xpath_relative}' not found in '{skin_xml_path_orig}'. Adding it from base.")
                    skin_actor_data.append(deepcopy(base_section_element_copy))

            if hasattr(ET, 'indent'):
                ET.indent(skin_tree, space="  ", level=0)

            skin_tree.write(output_skin_xml_path, encoding="utf-8", xml_declaration=True)
            print(f"    Successfully processed and saved skin to: {output_skin_xml_path}")

        except ET.ParseError as e:
            print(f"    Error parsing skin XML file '{skin_xml_path_orig}': {e}. Attempting to copy original.")
            try:
                shutil.copy2(skin_xml_path_orig, output_skin_xml_path)
            except Exception as copy_e:
                 print(f"      Failed to copy original skin file after parse error: {copy_e}")
        except Exception as e:
            print(f"    An unexpected error occurred while processing skin file '{skin_xml_path_orig}': {e}. Attempting to copy original.")
            try:
                shutil.copy2(skin_xml_path_orig, output_skin_xml_path)
            except Exception as copy_e:
                 print(f"      Failed to copy original skin file after error: {copy_e}")

# --- Character Configuration ---
CHARACTERS_CONFIG = {
    "characters/billy/billy.xml": [
        "characters/billy/billy_skin_young.xml"
    ],
    "characters/bmo/bmo.xml": [
        "characters/bmo/bmo_skin_noir.xml",
        "characters/bmo/bmo_skin_olive.xml",
        "characters/bmo/bmo_skin_puhoy.xml",
        "characters/bmo/bmo_skin_soccer.xml",
        "characters/bmo/bmo_skin_sweater.xml"
    ],
    "characters/choosegoose/choosegoose.xml": [
        ""
    ],
    "characters/cinnamonbun/cinnamonbun.xml": [
        "characters/cinnamonbun/cinnamonbun_skin_guy.xml"
    ],
    "characters/finn/finn.xml": [
        "characters/finn/finn_skin_billy.xml",
        "characters/finn/finn_skin_davey.xml",
        "characters/finn/finn_skin_guardian.xml",
        "characters/finn/finn_skin_hotbod.xml",
        "characters/finn/finn_skin_jakehat.xml",
        "characters/finn/finn_skin_lute.xml",
        "characters/finn/finn_skin_pj.xml",
        "characters/finn/finn_skin_shadow.xml",
        "characters/finn/finn_skin_wizard.xml",
        "characters/finn/bot_finn.xml"
    ],
    "characters/fionna/fionna.xml": [
        "characters/fionna/fionna_skin_ballgown.xml",
        "characters/fionna/fionna_skin_pj.xml"
    ],
    "characters/flame/flame.xml": [
        "characters/flame/flame_skin_dungeoneering.xml",
        "characters/flame/flame_skin_queen.xml"
    ],
    "characters/gunter/gunter.xml": [
        "characters/gunter/gunter_skin_evil.xml",
        "characters/gunter/gunter_skin_guntelina.xml",
        "characters/gunter/gunter_skin_jewel_thief.xml"
    ],
    "characters/hunson/hunson.xml": [
        "characters/hunson/hunson_skin_underwear.xml"
    ],
    "characters/iceking/iceking.xml": [
        "characters/iceking/iceking_skin_icequeen.xml",
        "characters/iceking/iceking_skin_young.xml",
        "characters/iceking/bot_iceking.xml"
    ],
    "characters/jake/jake.xml": [
        "characters/jake/jake_skin_cake.xml",
        "characters/jake/jake_skin_guardian.xml",
        "characters/jake/jake_skin_randy.xml",
        "characters/jake/jake_skin_wizard.xml",
        "characters/jake/jake_skin_zombie.xml",
        "characters/jake/bot_jake.xml"
    ],
    "characters/lemongrab/lemongrab.xml": [
        "characters/lemongrab/lemongrab_skin_2.xml",
        "characters/lemongrab/lemongrab_skin_fat.xml",
        "characters/lemongrab/lemongrab_skin_underwear.xml",
        "characters/lemongrab/bot_lemongrab.xml"
    ],
    "characters/lich/lich.xml": [
        "characters/lich/lich_skin_skeleton.xml"
    ],
    "characters/lsp/lsp.xml": [
        "characters/lsp/lsp_skin_gummybuns.xml",
        "characters/lsp/lsp_skin_lsprince.xml",
        "characters/lsp/lsp_skin_party.xml",
        "characters/lsp/lsp_skin_smooth.xml"
    ],
    "characters/magicman/magicman.xml": [
        "characters/magicman/magicman_skin_mystery.xml"
    ],
    "characters/marceline/marceline.xml": [
        "characters/marceline/marceline_skin_marshall.xml",
        "characters/marceline/marceline_skin_mohawk.xml",
        "characters/marceline/marceline_skin_young.xml"
    ],
    "characters/neptr/neptr.xml": [
        "characters/neptr/neptr_skin_racing.xml"
    ],
    "characters/peppermintbutler/peppermintbutler.xml": [
        "characters/peppermintbutler/peppermintbutler_skin_crowley.xml",
        "characters/peppermintbutler/peppermintbutler_skin_detective.xml",
        "characters/peppermintbutler/peppermintbutler_skin_sweater.xml",
        "characters/peppermintbutler/peppermintbutler_skin_zombie.xml"
    ],
    "characters/princessbubblegum/princessbubblegum.xml": [
        "characters/princessbubblegum/princessbubblegum_skin_hoth.xml",
        "characters/princessbubblegum/princessbubblegum_skin_prince.xml",
        "characters/princessbubblegum/princessbubblegum_skin_warrior.xml",
        "characters/princessbubblegum/princessbubblegum_skin_young.xml"
    ],
    "characters/rattleballs/rattleballs.xml": [
        "characters/rattleballs/rattleballs_skin_cloaked.xml",
        "characters/rattleballs/rattleballs_skin_spidotron.xml"
    ]
}

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
    elif os.listdir(OUTPUT_DIR): # Check if directory is not empty
        print(f"Warning: Output directory '{OUTPUT_DIR}' is not empty. Files may be overwritten.")


    if not CHARACTERS_CONFIG:
        print("No characters configured in CHARACTERS_CONFIG. Exiting.")
    else:
        processed_filenames_in_output = set() # To help warn about overwrites
        for base_file_orig_path, skin_files_list_orig_paths in CHARACTERS_CONFIG.items():
            base_fn = os.path.basename(base_file_orig_path)
            if base_fn in processed_filenames_in_output:
                print(f"  POTENTIAL OVERWRITE WARNING: Base file '{base_fn}' (from '{base_file_orig_path}') might overwrite an existing file in '{OUTPUT_DIR}'.")
            processed_filenames_in_output.add(base_fn)

            valid_skin_paths = [p for p in skin_files_list_orig_paths if p and isinstance(p, str) and p.strip()]
            for skin_path in valid_skin_paths:
                 skin_fn = os.path.basename(skin_path)
                 if skin_fn in processed_filenames_in_output:
                     print(f"  POTENTIAL OVERWRITE WARNING: Skin file '{skin_fn}' (from '{skin_path}') might overwrite an existing file in '{OUTPUT_DIR}'.")
                 processed_filenames_in_output.add(skin_fn)

            process_character_skins(base_file_orig_path, skin_files_list_orig_paths, backup_in_original_loc=True)

    print("\n--- Processing complete. ---")
    print(f"All output files are located in the '{OUTPUT_DIR}' directory (flat structure).")
    print("Remember to check the output files for correctness, especially if overwrite warnings occurred.")
    print("Backup files for original skins (if enabled) were created with a '.bak' extension in their original locations.")