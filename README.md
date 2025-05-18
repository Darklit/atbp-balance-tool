# Adventure Time: Battle Party - Balance Tool

This Python script (`stat_sync.py`) is designed to help balance character stats and abilities for Adventure Time: Battle Party. It synchronizes specific data sections (like actor stats and spell definitions) from a base character XML file to all of its corresponding skin XML files.

This tool is particularly useful when making balance changes that need to be applied consistently across a character's base version and all its cosmetic skins, without manually editing each skin file.

## Features

*   Reads base character XML files.
*   Reads associated skin XML files.
*   Copies specified data sections (e.g., `<actorStats>`, `<spell1>`, `<spell2>`, etc.) from the base file to its skins.
*   Preserves skin-specific data in the skin files.
*   Outputs all processed base and skin files into a flat directory (default: `output`).
*   Provides warnings for potential filename overwrites in the flat output directory.
*   Creates backups of original skin files (with a `.bak` extension) in their source locations.

## Prerequisites

*   **Python 3.x**: Ensure you have Python 3 installed. You can download it from [python.org](https://www.python.org/).
*   **XML Files**: Your game's character and skin data in XML format, following a structure similar to the one the script expects (with `<MonoBehaviours><ActorData>` containing the syncable sections).

## Setup and File Structure

1.  **Download the Script**: Place the `stat_sync.py` script in a root directory for your tool.
    ```
    adventure-time-battle-party-balance-tool/
    ├── stat_sync.py
    └── ... (your character XML files will go here or in subdirectories)
    ```

2.  **Organize Your Character XML Files**:
    It's recommended to organize your source XML files into subdirectories for clarity, for example:
    ```
    adventure-time-battle-party-balance-tool/
    ├── stat_sync.py
    └── characters/
        ├── finn/
        │   ├── finn.xml          (Base Finn file)
        │   ├── finn_skin_wizard.xml
        │   └── finn_skin_pj.xml
        ├── jake/
        │   ├── jake.xml          (Base Jake file)
        │   └── jake_skin_zombie.xml
        └── ... (other character subfolders)
    ```
    The script can also work if all XML files are in the same directory as the script, but subdirectories are cleaner for many files.

3.  **Configure the Script**:
    Open `stat_sync.py` in a text editor and modify the `CHARACTERS_CONFIG` dictionary. This dictionary tells the script where to find your base character files and their associated skin files.

    *   The **key** is the path to the base character's XML file (relative to where `stat_sync.py` is).
    *   The **value** is a list of paths to that character's skin XML files (also relative).

    **Example `CHARACTERS_CONFIG`:**
    ```python
    CHARACTERS_CONFIG = {
        "characters/finn/finn.xml": [
            "characters/finn/finn_skin_wizard.xml",
            "characters/finn/finn_skin_pj.xml",
        ],
        "characters/jake/jake.xml": [
            "characters/jake/jake_skin_zombie.xml",
        ],
        "characters/choosegoose/choosegoose.xml": [
            "" # For characters with no skins, an empty string or empty list is fine
        ]
        # ... add all your characters and their skins here
    }
    ```

    You can also adjust these constants at the top of the script if needed:
    *   `SECTIONS_TO_SYNC`: List of XML tags (relative to `<ActorData>`) to be copied from base to skins.
    *   `ACTOR_DATA_PATH`: XPath to the parent `<ActorData>` element.
    *   `OUTPUT_DIR`: Name of the flat output folder (default: `output_flat`).

## How to Use

1.  **Navigate to the Directory**: Open your terminal or command prompt and navigate to the directory where you placed `stat_sync.py` and your character files (or the root of their subdirectories).
    ```bash
    cd path/to/adventure-time-battle-party-balance-tool/
    ```

2.  **Run the Script**:
    Execute the Python script:
    ```bash
    python stat_sync.py
    ```

3.  **Check the Output**:
    *   A new directory named `output_flat` (or whatever you set `OUTPUT_DIR` to) will be created in the same location as the script.
    *   This directory will contain all your base character XML files and all their skin XML files (with stats/spells updated). The structure is flat, meaning all files are directly inside `output_flat/`.
    *   Original skin files in your source directories will have `.bak` backup files created next to them.

## Important Considerations

*   **Filename Uniqueness for Flat Output**: Since the `output_flat` directory has a flat structure (no subdirectories), **all base XML filenames and skin XML filenames must be unique across your entire character roster.** If you have two different characters that both have a skin file named `generic_skin.xml`, one will overwrite the other in the `output_flat` directory. The script will print warnings if it detects potential overwrites, but it will not prevent them.
*   **Backup**: The script creates `.bak` files for the original skin files it modifies in their *source* location. The `output_flat` directory contains the *newly generated* files. It's always a good idea to work with copies of your data or use version control (like Git) for your source XML files.
*   **XML Structure**: The script assumes a specific XML structure. If your game's XML differs significantly, you may need to adjust the `ACTOR_DATA_PATH` and `SECTIONS_TO_SYNC` constants in the script.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests! If you encounter issues or have suggestions, please open an issue on GitHub.

## License

(Consider adding a license if you want to specify how others can use your code, e.g., MIT License. If you don't add one, default copyright laws apply, but an explicit license is good practice for open source.)
For example:
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.