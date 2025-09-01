import bpy

from .utils import is_anym_armature


class AnymPoseItem(bpy.types.PropertyGroup):
	armature: bpy.props.PointerProperty(
		name="Armature",
		type=bpy.types.Object,
		description="Select an armature object",
		poll=is_anym_armature,
	)
	is_static: bpy.props.BoolProperty(
		name="Is Static",
		description="Manually set a frame index",
		default=False,
	)
	frame: bpy.props.IntProperty(
		name="Frame",
		description="Frame index in Anym animation",
		default=1,
		min=1,
		max=999
	)
