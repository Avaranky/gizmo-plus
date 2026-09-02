# Gizmo Plus

Gizmo Plus is a small Blender Extension that combines transform gizmos with Blender's standard modal workflow.

Gizmo Plus does not replace Blender's transform system or introduce its own. It allows gizmos and keyboard shortcuts to work as parts of the same workflow.

In standard Blender, `G`, `R`, and `S` immediately start a modal transform. Gizmo Plus changes the first step of this behavior: pressing `G`, `R`, or `S` activates the corresponding Move, Rotate, or Scale tool and keeps its gizmo visible.

Blender's standard modal workflow remains available. After pressing `G`, `R`, or `S`, moving the mouse starts the corresponding native modal transform, while axis and plane constraints continue to work as expected.

After the transform is finished, the selected tool and its gizmo remain active.

## Controls

- `G` — activates the Move tool and its gizmo.
- `R` — activates the Rotate tool and its gizmo.
- `S` — activates the Scale tool and its gizmo.
- `G` / `R` / `S` + mouse movement — starts the corresponding native modal transform.
- `G` / `R` / `S` → `X` / `Y` / `Z` — starts the transform constrained to the selected axis.
- `Shift` + `X` / `Y` / `Z` — constrains the transform to the corresponding plane.
- `G` `G` in Mesh Edit Mode — starts Vertex Slide.
- `R` `R` in the 3D View — starts Trackball Rotate.

## Settings

Gizmo Plus can be configured from its Add-on Preferences and from the Gizmo Plus panel in the 3D View sidebar.

- **Enabled** — enables or disables Gizmo Plus without disabling the Extension itself.
- **Input Timeout** — sets how long Gizmo Plus waits for additional input after pressing `G`, `R`, or `S`.
- **Show N-Panel** — shows or hides the Gizmo Plus panel in the 3D View sidebar.
- **Gizmo Plus Shortcuts** — shows the shortcuts used by Gizmo Plus and allows them to be edited.

If you prefer to keep the N-panel uncluttered, the Gizmo Plus panel can be hidden using the Show N-Panel option in the Add-on Preferences.

## Installation

Download the Gizmo Plus `.zip` package and install it using either method:

- Drag and drop the `.zip` file into Blender.
- In Blender Preferences → Extensions, choose **Install from Disk** and select the `.zip` file.

## Compatibility

- Blender 5.2+

## Issues

If you encounter a bug or unexpected behavior, please report it through [GitHub Issues](https://github.com/Avaranky/gizmo-plus/issues).

## License

Gizmo Plus is licensed under the [GNU General Public License v3.0 or later](LICENSE).