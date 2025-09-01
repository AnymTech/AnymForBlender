bl_info = {
	"name": "Anym Blender UI Dummy",
	"author": "Anym Tech",
	"version": (0, 1),
	"blender": (4, 5, 0),
	"location": "View3D > Sidebar > Anym",
	"description": "Anym inbetweening tool for Blender",
	"category": "Animation",
}

import sys, os
import bpy
import bpy.utils.previews

from .operators import (ANYM_OT_warning, ANYM_OT_import_armature, ANYM_OT_add_pose,
						ANYM_OT_remove_pose, ANYM_OT_generate_animation,
						ANYM_OT_fetch_animation)
from .properties import AnymPoseItem
from .utils import get_pose_items


class ANYM_UL_pose_list(bpy.types.UIList):
	def draw_item(
		self, context, layout, data, item, icon, active_data, active_propname, index
	):
		row = layout.row(align=False)

		row.prop(item, "armature", text="")
		split = row.split(factor=0.3, align=True)
		split.prop(item, "is_static", text="", icon='PINNED' if item.is_static else 'UNPINNED')

		if item.is_static:
			split.prop(item, "frame", text="")
		else:
			split.label(text="")

		row.operator("anym.remove_pose", text="", icon="X", emboss=False)

class ANYM_PT_main_panel(bpy.types.Panel):
	bl_label = "Anym Animation Tool"
	bl_idname = "ANYM_PT_main_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Anym'

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		pcoll = anym_icons["main"]
		logo = pcoll['logo']

		box_header = layout.box()
		box_header.label(text="ANYM", icon_value=logo.icon_id)

		box_poses = layout.box()
		box_poses.label(text="Rig Import", icon='ARMATURE_DATA')

		row_pose_select = box_poses.row()
		row_pose_select.prop(scene, "anym_selected_pose", text="Available Pose")

		row_options = box_poses.row()
		row_options.prop(scene, "anym_fkik_enabled", text="Create Rig", icon="CONSTRAINT_BONE")
		row_options.prop(scene, "anym_import_model", text="Add Model", icon='OUTLINER_OB_ARMATURE')

		box_poses.operator("anym.import_armature", icon='IMPORT')

		box_pose_list = layout.box()
		box_pose_list.label(text="Selected Armatures", icon='MOD_ARRAY')

		row_pose_list_control = box_pose_list.row()
		row_pose_list_control.template_list(
			"ANYM_UL_pose_list", "pose_list_id",
			scene, "anym_poses", scene, "anym_pose_index",
			rows=4
		)

		col_buttons = box_pose_list.row(align=True)
		col_buttons.operator("anym.remove_pose", text="Remove Pose", icon='REMOVE')
		col_buttons.operator("anym.add_pose", text="Add Pose", icon='ADD')

		box_context = layout.box()
		box_context.label(text="Context", icon='SETTINGS')

		row_frame_settings = box_context.row(align=False)
		row_frame_settings.prop(scene, "anym_total_frames", text="Total Frames")
		row_frame_settings.prop(scene, "anym_fps", text="FPS")

		row_looping = box_context.row(align=True)
		row_looping.prop(scene, "anym_is_looping", text="Is Looping")
		row_looping.prop(scene, "anym_solve_ik", text="Apply IK Solver")

		box_actions = layout.box()
		row_api = box_actions.row()
		row_api.label(text="API Key", icon="INTERNET")
		row_api.prop(scene, "anym_api_key", text='')

		row_generate = box_actions.row()
		row_generate.scale_y = 1.5
		row_generate.operator("anym.generate_animation", icon_value=logo.icon_id)
		box_actions.operator("anym.fetch_animation", icon='FILE_REFRESH')


anym_icons = {}
classes = [
	AnymPoseItem,
	ANYM_OT_warning,
	ANYM_OT_import_armature,
	ANYM_OT_add_pose,
	ANYM_OT_remove_pose,
	ANYM_OT_generate_animation,
	ANYM_OT_fetch_animation,
	ANYM_UL_pose_list,
	ANYM_PT_main_panel,
]


def register():
	image_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "ANYM_logo.png")

	pcoll = bpy.utils.previews.new()
	pcoll.load("logo", image_path, 'IMAGE')

	global anym_icons
	anym_icons["main"] = pcoll

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.anym_selected_pose = bpy.props.EnumProperty(
		name="Pose",
		items=get_pose_items
	)
	bpy.types.Scene.anym_fkik_enabled = bpy.props.BoolProperty(
		name="Create FK/IK",
		default=True
	)
	bpy.types.Scene.anym_import_model = bpy.props.BoolProperty(
		name="Import Model",
		default=True
	)
	bpy.types.Scene.anym_poses = bpy.props.CollectionProperty(type=AnymPoseItem)
	bpy.types.Scene.anym_pose_index = bpy.props.IntProperty(default=0)
	bpy.types.Scene.anym_total_frames = bpy.props.IntProperty(
		name="Total Frames", default=40, min=1
	)
	bpy.types.Scene.anym_fps = bpy.props.IntProperty(
		name="FPS", default=30, min=1
	)
	bpy.types.Scene.anym_is_looping = bpy.props.BoolProperty(
		name="Is Looping", default=False
	)
	bpy.types.Scene.anym_solve_ik = bpy.props.BoolProperty(
		name="Solve IK", default=True
	)
	bpy.types.Scene.anym_api_key = bpy.props.StringProperty(
		name="API Key", default=""
	)
	bpy.types.Scene.anym_url = bpy.props.StringProperty(
		name="URL", default="https://app.anym.tech/"
	)


def unregister():
	global anym_icons
	for pcoll in anym_icons.values():
		bpy.utils.previews.remove(pcoll)
	anym_icons.clear()

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.anym_selected_pose
	del bpy.types.Scene.anym_fkik_enabled
	del bpy.types.Scene.anym_import_model
	del bpy.types.Scene.anym_poses
	del bpy.types.Scene.anym_pose_index
	del bpy.types.Scene.anym_total_frames
	del bpy.types.Scene.anym_fps
	del bpy.types.Scene.anym_is_looping
	del bpy.types.Scene.anym_solve_ik
	del bpy.types.Scene.anym_api_key
	del bpy.types.Scene.anym_url
