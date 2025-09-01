import math
import bpy
from mathutils import Vector, Euler, Matrix
import json


HEADER = """
HIERARCHY
ROOT Hips
{
	OFFSET 0.000000 0.000000 0.000000
	CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
	JOINT LeftHip
	{
		OFFSET 0.080781 0.005359 -0.054022
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT LeftKnee
		{
			OFFSET 0.000000 -0.010000 -0.417793
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT LeftFoot
			{
				OFFSET 0.000000 0.000000 -0.401472
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT LeftToe
				{
					OFFSET 0.011334 -0.104165 -0.041164
					CHANNELS 3 Zrotation Yrotation Xrotation
					End Site
					{
						OFFSET 0.000000 -0.150000 0.000000
					}
				}
			}
		}
	}
	JOINT RightHip
	{
		OFFSET -0.080781 0.005359 -0.054025
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT RightKnee
		{
			OFFSET 0.000000 -0.010000 -0.417793
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT RightFoot
			{
				OFFSET 0.000000 0.000000 -0.401472
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT RightToe
				{
					OFFSET  -0.011334 -0.104165 -0.041168
					CHANNELS 3 Zrotation Yrotation Xrotation
					End Site
					{
						OFFSET 0.000000 -0.150000 0.000000
					}
				}
			}
		}
	}
	JOINT Spine
	{
		OFFSET 0.000000 0.011802 0.097172
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT Spine1
		{
			OFFSET 0.000000 0.013769 0.113368
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT Spine2
			{
				OFFSET 0.000000 0.015737 0.129563
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT Neck
				{
					OFFSET 0.000000 0.017704 0.145760
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT Head
					{
						OFFSET  0.000000 -0.019722 0.067202
						CHANNELS 3 Zrotation Yrotation Xrotation
						End Site
						{
							OFFSET 0.000000 0.000000 0.200000
						}
					}
				}
				JOINT LeftShoulder
				{
					OFFSET 0.061401 0.017995 0.098779
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT LeftArm
					{
						OFFSET 0.115589 0.000581 0.000000
						CHANNELS 3 Zrotation Yrotation Xrotation
						JOINT LeftForearm
						{
							OFFSET 0.255608 0.010000 0.000000
							CHANNELS 3 Zrotation Yrotation Xrotation
							JOINT LeftHand
							{
								OFFSET 0.234041 -0.010000 0.00000
								CHANNELS 3 Zrotation Yrotation Xrotation
								End Site
								{
									OFFSET 0.200000 0.000000 0.000000
								}
							}
						}
					}
				}
				JOINT RightShoulder
				{
					OFFSET -0.061401 0.017414 0.098778
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT RightArm
					{
						OFFSET -0.115589 -0.000581 0.000000
						CHANNELS 3 Zrotation Yrotation Xrotation
						JOINT RightForearm
						{
							OFFSET -0.255711 0.010000 0.000000
							CHANNELS 3 Zrotation Yrotation Xrotation
							JOINT RightHand
							{
								OFFSET -0.234017 -0.010000 0.000000
								CHANNELS 3 Zrotation Yrotation Xrotation
								End Site
								{
									OFFSET -0.200000 0.000000 0.000000
								}
							}
						}
					}
				}
			}
		}
	}
}
MOTION
Frames: 1
Frame Time: 0.050000
"""


def is_anym_armature(self, object):
	if object.type != 'ARMATURE':
		return False
	if len(object.pose.bones) != 22:
		return False
	return True


class BVHJointData:
	def __init__(self, name, parent_data=None, is_end_site=False):
		self.name = name
		self.parent = parent_data
		self.offset = Vector((0, 0, 0))
		self.channels = []
		self.children = []
		self.is_end_site = is_end_site

		self.rot_order = [None, None, None]
		self.rot_order_str = 'XYZ'


def parse_bvh_data(lines, scale=100):
	_eul_order_lookup = {
		(None, None, None): 'XYZ',
		(0, 1, 2): 'XYZ',
		(0, 2, 1): 'XZY',
		(1, 0, 2): 'YXZ',
		(1, 2, 0): 'YZX',
		(2, 0, 1): 'ZXY',
		(2, 1, 0): 'ZYX',
	}

	hierarchy_start_idx = -1
	for i, line in enumerate(lines):
		if line.strip() == "HIERARCHY":
			hierarchy_start_idx = i
			break

	all_bvh_joints = {}
	root_bvh_joint = None
	current_parent_stack = []
	ordered_channels_for_motion = []

	line_idx = hierarchy_start_idx + 1
	while line_idx < len(lines):
		line = lines[line_idx].strip()
		line_idx += 1

		if not line: continue
		if line == "MOTION": break

		parts = line.split()
		if not parts: continue

		if parts[0] == "ROOT" or parts[0] == "JOINT":
			joint_name = " ".join(parts[1:])
			parent_joint_data = current_parent_stack[-1] if current_parent_stack else None
			joint_data = BVHJointData(joint_name, parent_joint_data)
			all_bvh_joints[joint_name] = joint_data

			if parent_joint_data:
				parent_joint_data.children.append(joint_data)
			if parts[0] == "ROOT":
				root_bvh_joint = joint_data

			line_idx += 1
			current_parent_stack.append(joint_data)

		elif parts[0] == "OFFSET":
			current_joint_data = current_parent_stack[-1]
			current_joint_data.offset = Vector([
				float(parts[1]) * scale,
				float(parts[2]) * scale,
				float(parts[3]) * scale,
			])

		elif parts[0] == "CHANNELS":
			current_joint_data = current_parent_stack[-1]
			num_channels = int(parts[1])
			current_joint_data.channels = parts[2:2+num_channels]

			rot_count = 0
			for channel in current_joint_data.channels:
				channel_lower = channel.lower()
				if channel_lower == 'xrotation':
					current_joint_data.rot_order[rot_count] = 0
					rot_count += 1
				elif channel_lower == 'yrotation':
					current_joint_data.rot_order[rot_count] = 1
					rot_count += 1
				elif channel_lower == 'zrotation':
					current_joint_data.rot_order[rot_count] = 2
					rot_count += 1

			current_joint_data.rot_order_str = _eul_order_lookup[tuple(current_joint_data.rot_order)]

			for channel_type in current_joint_data.channels:
				ordered_channels_for_motion.append((current_joint_data.name, channel_type))

		elif parts[0] == "End" and parts[1] == "Site":
			end_site_name = current_parent_stack[-1].name + "_EndSite"
			parent_joint_data = current_parent_stack[-1]
			end_site_data = BVHJointData(end_site_name, parent_joint_data, is_end_site=True)
			all_bvh_joints[end_site_name] = end_site_data
			parent_joint_data.children.append(end_site_data)
			line_idx += 1

			offset_parts = lines[line_idx].strip().split()
			line_idx += 1

			end_site_data.offset = Vector([
				float(offset_parts[1]) * scale,
				float(offset_parts[2]) * scale,
				float(offset_parts[3]) * scale
			])
			line_idx += 1

		elif parts[0] == "}":
			if current_parent_stack:
				current_parent_stack.pop()
			else:
				if line_idx < len(lines) and lines[line_idx].strip() == "MOTION":
					break

	motion_start_idx = -1
	for i in range(line_idx - 1, len(lines)):
		if lines[i].strip() == "MOTION":
			motion_start_idx = i
			break

	frame_values = []

	for i in range(motion_start_idx + 1, len(lines)):
		line = lines[i].strip()
		if line.startswith("Frames: 1"):
			motion_data_line = lines[i+2].strip()
			frame_values = [float(x) for x in motion_data_line.split()]

	return root_bvh_joint, all_bvh_joints, ordered_channels_for_motion, frame_values

def build_blender_hierarchy_recursive(bvh_joint_data, edit_bones, parent_blender_bone=None):
	if bvh_joint_data.is_end_site:
		return

	edit_bone = edit_bones.new(bvh_joint_data.name)

	if parent_blender_bone:
		edit_bone.parent = parent_blender_bone
		edit_bone.head = parent_blender_bone.head + bvh_joint_data.offset
		edit_bone.tail = edit_bone.head + bvh_joint_data.children[0].offset
	else:
		edit_bone.head = Vector((0, 0, 0))
		edit_bone.tail = Vector((0, 0, 0.03))

	for child_bvh_joint_data in bvh_joint_data.children:
		if child_bvh_joint_data.is_end_site:
			edit_bone.tail = edit_bone.head + child_bvh_joint_data.offset
			continue

		build_blender_hierarchy_recursive(child_bvh_joint_data, edit_bones, parent_blender_bone=edit_bone)

def apply_transform_safe(obj):
	vl = bpy.context.view_layer
	prev_active = vl.objects.active
	prev_selected = list(bpy.context.selected_objects)
	prev_mode = bpy.context.mode

	if prev_mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	for o in prev_selected:
		o.select_set(False)
	obj.select_set(True)
	vl.objects.active = obj

	bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

	obj.select_set(False)
	for o in prev_selected:
		o.select_set(True)
	vl.objects.active = prev_active

	if prev_active and prev_mode != 'OBJECT':
		try:
			bpy.ops.object.mode_set(mode=prev_mode)
		except RuntimeError:
			pass

def setup_fkik(armature_object, import_model=False):
	if bpy.context.view_layer.objects.active != armature_object:
		bpy.context.view_layer.objects.active = armature_object
	bpy.ops.object.mode_set(mode='OBJECT')

	armature_data = armature_object.data

	control_armature = bpy.data.objects.get(f"{armature_data.name}_controls")
	if control_armature:
		bpy.data.objects.remove(control_armature, do_unlink=True)

	control_armature_data = bpy.data.armatures.new(f"{armature_data.name}_controls")
	control_armature = bpy.data.objects.new(control_armature_data.name, control_armature_data)

	bpy.context.collection.objects.link(control_armature)
	bpy.ops.object.mode_set(mode='EDIT')

	control_armature.parent = armature_object
	bpy.context.view_layer.objects.active = control_armature

	deform_bones = armature_object.data.edit_bones

	control_bone_data = {
		'master_ctrl': (Vector((0, 0, 0)), Vector((0, 0.5, 0)), None, None),
		'Hips_ctrl': (deform_bones['Hips'].head, deform_bones['Hips'].tail, 'master_ctrl', 'Hips'),
		'Spine_fk_ctrl': (deform_bones['Spine'].head, deform_bones['Spine'].tail, 'Hips_ctrl', 'Spine'),
		'Spine1_fk_ctrl': (deform_bones['Spine1'].head, deform_bones['Spine1'].tail, 'Spine_fk_ctrl', 'Spine1'),
		'Spine2_fk_ctrl': (deform_bones['Spine2'].head, deform_bones['Spine2'].tail, 'Spine1_fk_ctrl', 'Spine2'),
		'Neck_fk_ctrl': (deform_bones['Neck'].head, deform_bones['Neck'].tail, 'Spine2_fk_ctrl', 'Neck'),
		'Head_fk_ctrl': (deform_bones['Head'].head, deform_bones['Head'].tail, 'Neck_fk_ctrl', 'Head'),

		'L_Shoulder_fk_ctrl': (deform_bones['LeftShoulder'].head, deform_bones['LeftShoulder'].tail, 'Spine2_fk_ctrl', 'LeftShoulder'),
		'L_Arm_fk_ctrl': (deform_bones['LeftArm'].head, deform_bones['LeftArm'].tail, 'L_Shoulder_fk_ctrl', 'LeftArm'),
		'L_Forearm_fk_ctrl': (deform_bones['LeftForearm'].head, deform_bones['LeftForearm'].tail, 'L_Arm_fk_ctrl', 'LeftForearm'),
		'L_Hand_fk_ctrl': (deform_bones['LeftHand'].head, deform_bones['LeftHand'].tail, 'L_Forearm_fk_ctrl', 'LeftHand'),

		'L_Hand_ik_ctrl': (deform_bones['LeftHand'].tail, deform_bones['LeftHand'].tail + Vector((0, -0.5, 0)), 'master_ctrl', 'LeftHand'),
		'L_Elbow_pole_ctrl': (deform_bones['LeftForearm'].head + Vector((0, .5, 0)), deform_bones['LeftForearm'].head, 'master_ctrl', 'LeftForearm'),

		'R_Shoulder_fk_ctrl': (deform_bones['RightShoulder'].head, deform_bones['RightShoulder'].tail, 'Spine2_fk_ctrl', 'RightShoulder'),
		'R_Arm_fk_ctrl': (deform_bones['RightArm'].head, deform_bones['RightArm'].tail, 'R_Shoulder_fk_ctrl', 'RightArm'),
		'R_Forearm_fk_ctrl': (deform_bones['RightForearm'].head, deform_bones['RightForearm'].tail, 'R_Arm_fk_ctrl', 'RightForearm'),
		'R_Hand_fk_ctrl': (deform_bones['RightHand'].head, deform_bones['RightHand'].tail, 'R_Forearm_fk_ctrl', 'RightHand'),

		'R_Hand_ik_ctrl': (deform_bones['RightHand'].tail, deform_bones['RightHand'].tail + Vector((0, -0.5, 0)), 'master_ctrl', 'RightHand'),
		'R_Elbow_pole_ctrl': (deform_bones['RightForearm'].head + Vector((0, .5, 0)), deform_bones['RightForearm'].head, 'master_ctrl', 'RightForearm'),

		'L_Hip_fk_ctrl': (deform_bones['LeftHip'].head, deform_bones['LeftHip'].tail, 'Hips_ctrl', 'LeftHip'),
		'L_Knee_fk_ctrl': (deform_bones['LeftKnee'].head, deform_bones['LeftKnee'].tail, 'L_Hip_fk_ctrl', 'LeftKnee'),
		'L_Foot_fk_ctrl': (deform_bones['LeftFoot'].head, deform_bones['LeftFoot'].tail, 'L_Knee_fk_ctrl', 'LeftFoot'),
		'L_Toe_fk_ctrl': (deform_bones['LeftToe'].head, deform_bones['LeftToe'].tail, 'L_Foot_fk_ctrl', 'LeftToe'),

		'L_Foot_ik_ctrl': (deform_bones['LeftFoot'].tail, deform_bones['LeftFoot'].tail + Vector((0, 0.5, 0)), 'master_ctrl', 'LeftFoot'),
		'L_Knee_pole_ctrl': (deform_bones['LeftKnee'].head + Vector((0, -.5, 0)), deform_bones['LeftKnee'].head, 'master_ctrl', 'LeftKnee'),

		'R_Hip_fk_ctrl': (deform_bones['RightHip'].head, deform_bones['RightHip'].tail, 'Hips_ctrl', 'RightHip'),
		'R_Knee_fk_ctrl': (deform_bones['RightKnee'].head, deform_bones['RightKnee'].tail, 'R_Hip_fk_ctrl', 'RightKnee'),
		'R_Foot_fk_ctrl': (deform_bones['RightFoot'].head, deform_bones['RightFoot'].tail, 'R_Knee_fk_ctrl', 'RightFoot'),
		'R_Toe_fk_ctrl': (deform_bones['RightToe'].head, deform_bones['RightToe'].tail, 'R_Foot_fk_ctrl', 'RightToe'),

		'R_Foot_ik_ctrl': (deform_bones['RightFoot'].tail, deform_bones['RightFoot'].tail + Vector((0, 0.5, 0)), 'master_ctrl', 'RightFoot'),
		'R_Knee_pole_ctrl': (deform_bones['RightKnee'].head + Vector((0, -.5, 0)), deform_bones['RightKnee'].head, 'master_ctrl', 'RightKnee'),
	}

	pole_sequences = {
		'L_Elbow_pole_ctrl': (deform_bones['LeftArm'], deform_bones['LeftForearm'], deform_bones['LeftHand']),
		'R_Elbow_pole_ctrl': (deform_bones['RightArm'], deform_bones['RightForearm'], deform_bones['RightHand']),
		'L_Knee_pole_ctrl': (deform_bones['LeftHip'], deform_bones['LeftKnee'], deform_bones['LeftToe']),
		'R_Knee_pole_ctrl': (deform_bones['RightHip'], deform_bones['RightKnee'], deform_bones['RightToe']),
	}

	bpy.ops.object.mode_set(mode='EDIT')
	edit_bones = control_armature.data.edit_bones
	pose_bones = armature_object.pose.bones
	for bone_name, (head, tail, parent_name, base_armature_bone_name) in control_bone_data.items():
		new_bone = edit_bones.new(bone_name)
		if 'ik' in bone_name or 'pole' in bone_name:
			new_bone.color.palette = 'THEME01'
		elif bone_name in [
				'Hips_ctrl',
				'Neck_fk_ctrl',
				'Head_fk_ctrl',
				'L_Shoulder_fk_ctrl',
				'R_Shoulder_fk_ctrl',
			]:
			new_bone.color.palette = 'THEME09'
		elif 'fk' in bone_name:
			new_bone.color.palette = 'THEME04'
		elif 'master' in bone_name:
			new_bone.color.palette = 'THEME11'

		new_bone.head = head
		new_bone.tail = tail
		if parent_name:
			new_bone.parent = edit_bones.get(parent_name)
		if base_armature_bone_name:
			base_bone = pose_bones.get(base_armature_bone_name)
			base_mat = armature_object.matrix_world @ base_bone.matrix

			if bone_name == 'Head_fk_ctrl':
				world_offset = Matrix.Translation((0.0, 0.2, 0.05))
			elif bone_name == 'Neck_fk_ctrl':
				world_offset = Matrix.Translation((0.0, 0.05, 0.))
			elif bone_name == 'L_Shoulder_fk_ctrl':
				world_offset = Matrix.Translation((0.05, 0.05, 0.))
			elif bone_name == 'R_Shoulder_fk_ctrl':
				world_offset = Matrix.Translation((-0.05, 0.05, 0.))
			elif bone_name == 'Spine_ctrl':
				world_offset = Matrix.Rotation(math.radians(-83.0), 4, 'X')
			else:
				world_offset = Matrix.Translation((0., 0., 0.))
			new_bone.matrix = base_mat @ world_offset

		if 'pole' in bone_name:
			base_bone = pose_bones.get(base_armature_bone_name)

			start_bone, mid_bone, end_bone = pole_sequences.get(bone_name)
			start_ws = (armature_object.matrix_world @ start_bone.head)
			mid_ws = (armature_object.matrix_world @ mid_bone.head)
			end_ws = (armature_object.matrix_world @ end_bone.head)

			mp = ((end_ws - start_ws) / 2.) + start_ws
			if 'Elbow' in bone_name:
				offs = Matrix.Translation((mid_ws - mp).normalized() * .3)
			else:
				offs = Matrix.Translation(-(mid_ws - mp).normalized() * .3)

			base_mat = Matrix.Translation(armature_object.matrix_world @ base_bone.head)
			new_bone.matrix = base_mat @ offs

	bpy.ops.object.mode_set(mode='OBJECT')

	bpy.context.view_layer.objects.active = control_armature
	bpy.ops.object.mode_set(mode='POSE')

	def apply_fk_constraints(deform_bone_name, ctrl_bone_name, ik_switch_bone_name):
		bone = armature_object.pose.bones.get(deform_bone_name)
		if bone:
			fk_con = bone.constraints.new('COPY_ROTATION')
			fk_con.target = control_armature
			fk_con.subtarget = ctrl_bone_name
			fk_con.mix_mode = 'REPLACE'
			fk_con.owner_space = 'WORLD'
			fk_con.target_space = 'WORLD'

			fcurve = fk_con.driver_add('influence')
			driver_data = fcurve.driver
			driver_data.type = 'SCRIPTED'
			driver_data.expression = '1 - x'
			while driver_data.variables:
				driver_data.variables.remove(driver_data.variables[0])
			var = driver_data.variables.new()
			var.name = 'x'
			var.targets[0].id = control_armature
			var.targets[0].data_path = f'pose.bones["{ik_switch_bone_name}"]["FK/IK Switch Value"]'

	def apply_rot_constraints(deform_bone_name, ctrl_bone_name, constrain_loc=False, add=False):
		if not 'ctrl' in deform_bone_name:
			bone = armature_object.pose.bones.get(deform_bone_name)
		else:
			bone = control_armature.pose.bones.get(deform_bone_name)
		if bone:
			fk_con = bone.constraints.new('COPY_ROTATION')
			fk_con.target = control_armature
			fk_con.subtarget = ctrl_bone_name
			fk_con.mix_mode = 'ADD' if add else 'REPLACE'
			fk_con.owner_space = 'WORLD'
			fk_con.target_space = 'WORLD'
		if constrain_loc:
			con_loc = bone.constraints.new('COPY_LOCATION')
			con_loc.target = control_armature
			con_loc.subtarget = ctrl_bone_name
			con_loc.target_space = 'WORLD'
			con_loc.owner_space = 'WORLD'

	def apply_ik_constraints(deform_bone_name, ik_ctrl_name, pole_ctrl_name):
		bone = armature_object.pose.bones.get(deform_bone_name)
		if bone:
			ik_con = bone.constraints.new('IK')
			ik_con.target = control_armature
			ik_con.subtarget = ik_ctrl_name
			ik_con.pole_target = control_armature
			ik_con.pole_subtarget = pole_ctrl_name
			ik_con.chain_count = 2
			ik_con.use_tail = False
			ik_con.use_rotation = False
			if 'LeftHand' in deform_bone_name:
				ik_con.pole_angle = -math.pi
			elif 'RightHand' in deform_bone_name:
				ik_con.pole_angle = 0.0
			elif 'Foot' in deform_bone_name:
				ik_con.pole_angle = -math.pi/2

			end_rot_con = bone.constraints.new('COPY_ROTATION')
			end_rot_con.target = control_armature
			end_rot_con.subtarget = ik_ctrl_name
			end_rot_con.mix_mode = 'REPLACE'
			end_rot_con.target_space = 'WORLD'
			end_rot_con.owner_space = 'WORLD'

			fcurve = ik_con.driver_add('influence')
			driver_data = fcurve.driver
			driver_data.type = 'SCRIPTED'
			driver_data.expression = 'x'
			while driver_data.variables:
				driver_data.variables.remove(driver_data.variables[0])
			var = driver_data.variables.new()
			var.name = 'x'
			var.targets[0].id = control_armature
			var.targets[0].data_path = f'pose.bones["{ik_ctrl_name}"]["FK/IK Switch Value"]'

			fcurve = end_rot_con.driver_add('influence')
			driver_data = fcurve.driver
			driver_data.type = 'SCRIPTED'
			driver_data.expression = 'x'
			while driver_data.variables:
				driver_data.variables.remove(driver_data.variables[0])
			var = driver_data.variables.new()
			var.name = 'x'
			var.targets[0].id = control_armature
			var.targets[0].data_path = f'pose.bones["{ik_ctrl_name}"]["FK/IK Switch Value"]'

	control_armature.pose.bones['L_Hand_ik_ctrl']['FK/IK Switch Value'] = 1.0
	control_armature.pose.bones['R_Hand_ik_ctrl']['FK/IK Switch Value'] = 1.0
	control_armature.pose.bones['L_Foot_ik_ctrl']['FK/IK Switch Value'] = 1.0
	control_armature.pose.bones['R_Foot_ik_ctrl']['FK/IK Switch Value'] = 1.0

	apply_rot_constraints('Hips', 'Hips_ctrl', constrain_loc=True)
	apply_rot_constraints('Spine', 'Spine_fk_ctrl')
	apply_rot_constraints('Spine1', 'Spine1_fk_ctrl')
	apply_rot_constraints('Spine2', 'Spine2_fk_ctrl')
	apply_rot_constraints('LeftShoulder', 'L_Shoulder_fk_ctrl')
	apply_rot_constraints('RightShoulder', 'R_Shoulder_fk_ctrl')
	apply_rot_constraints('Neck', 'Neck_fk_ctrl')
	apply_rot_constraints('Head', 'Head_fk_ctrl')

	apply_fk_constraints('LeftArm', 'L_Arm_fk_ctrl', 'L_Hand_ik_ctrl')
	apply_fk_constraints('LeftForearm', 'L_Forearm_fk_ctrl', 'L_Hand_ik_ctrl')
	apply_fk_constraints('LeftHand', 'L_Hand_fk_ctrl', 'L_Hand_ik_ctrl')
	apply_ik_constraints('LeftHand', 'L_Hand_ik_ctrl', 'L_Elbow_pole_ctrl')

	apply_fk_constraints('RightArm', 'R_Arm_fk_ctrl', 'R_Hand_ik_ctrl')
	apply_fk_constraints('RightForearm', 'R_Forearm_fk_ctrl', 'R_Hand_ik_ctrl')
	apply_fk_constraints('RightHand', 'R_Hand_fk_ctrl', 'R_Hand_ik_ctrl')
	apply_ik_constraints('RightHand', 'R_Hand_ik_ctrl', 'R_Elbow_pole_ctrl')

	apply_fk_constraints('LeftHip', 'L_Hip_fk_ctrl', 'L_Foot_ik_ctrl')
	apply_fk_constraints('LeftKnee', 'L_Knee_fk_ctrl', 'L_Foot_ik_ctrl')
	apply_fk_constraints('LeftFoot', 'L_Foot_fk_ctrl', 'L_Foot_ik_ctrl')
	apply_ik_constraints('LeftFoot', 'L_Foot_ik_ctrl', 'L_Knee_pole_ctrl')

	apply_fk_constraints('RightHip', 'R_Hip_fk_ctrl', 'R_Foot_ik_ctrl')
	apply_fk_constraints('RightKnee', 'R_Knee_fk_ctrl', 'R_Foot_ik_ctrl')
	apply_fk_constraints('RightFoot', 'R_Foot_fk_ctrl', 'R_Foot_ik_ctrl')
	apply_ik_constraints('RightFoot', 'R_Foot_ik_ctrl', 'R_Knee_pole_ctrl')

	radii = {
		'Hip_fk_ctrl': .12,
		'Knee_fk_ctrl': .10,
		'Foot_fk_ctrl': .28,
		'Toe_fk_ctrl': .18,
		'Spine_fk_ctrl': .60,
		'Spine1_fk_ctrl': .65,
		'Spine2_fk_ctrl': .75,
		'Neck_fk_ctrl': .55,
		'Head_fk_ctrl': .20,
		'Shoulder_fk_ctrl': .45,
		'Arm_fk_ctrl': .15,
		'Forearm_fk_ctrl': .15,
		'master_ctrl': .5,
		'Spine_ctrl': .5,
	}

	def create_and_link_shape(bone_name, parent_obj):
		if ('_fk' in bone_name and 'Shoulder' not in bone_name) or 'pole' in bone_name:
			radius = radii.get(bone_name[2:], .1) * 2 if bone_name[0] == 'L' or bone_name[0] == 'R' else radii.get(bone_name) * 2
			if not import_model:
				radius *= .8
			shape_mesh = bpy.data.objects.new(f"ControlShape_{bone_name}", None)
			shape_mesh.empty_display_type = 'SPHERE' if 'pole' in bone_name else 'CIRCLE'
			shape_mesh.empty_display_size = .1 if 'pole' in bone_name else radius

			bpy.context.collection.objects.link(shape_mesh)

		elif '_ik' in bone_name or 'Hips' in bone_name or 'Shoulder' in bone_name or 'master' in bone_name or 'Spine_ctrl' in bone_name:
			if 'Foot' in bone_name:
				box_scale = .1
				points = [
					Vector((-box_scale, -4*box_scale, -box_scale)),
					Vector((-box_scale, box_scale, -box_scale)),
					Vector((-box_scale, box_scale, 1.5*box_scale)),
					Vector((-box_scale, -box_scale, 1.5*box_scale)),
					Vector((-box_scale, -4*box_scale, -box_scale)),
					Vector((box_scale, -4*box_scale, -box_scale)),
					Vector((box_scale, box_scale, -box_scale)),
					Vector((-box_scale, box_scale, -box_scale)),
					Vector((box_scale, box_scale, -box_scale)),
					Vector((box_scale, box_scale, 1.5*box_scale)),
					Vector((-box_scale, box_scale, 1.5*box_scale)),
					Vector((box_scale, box_scale, 1.5*box_scale)),
					Vector((box_scale, -box_scale, 1.5*box_scale)),
					Vector((-box_scale, -box_scale, 1.5*box_scale)),
					Vector((box_scale, -box_scale, 1.5*box_scale)),
					Vector((box_scale, -4*box_scale, -box_scale)),
				]
			elif 'Hand' in bone_name:
				box_scale = .15
				frac = .5
				points = [
					Vector((-box_scale, -box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, -frac*box_scale)),
					Vector((box_scale, -frac*box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, frac*box_scale)),
					Vector((-box_scale, box_scale, frac*box_scale)),
					Vector((box_scale, frac*box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, -frac*box_scale)),
				]
			elif 'Hips' in bone_name:
				box_scale = 1.6 if import_model else 3.
				frac = 1.
				points = [
					Vector((-box_scale, -box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, -frac*box_scale)),
					Vector((box_scale, -frac*box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, -frac*box_scale)),
					Vector((-box_scale, box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, -frac*box_scale)),
					Vector((box_scale, frac*box_scale, frac*box_scale)),
					Vector((-box_scale, box_scale, frac*box_scale)),
					Vector((box_scale, frac*box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, frac*box_scale)),
					Vector((-box_scale, -box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, frac*box_scale)),
					Vector((box_scale, -frac*box_scale, -frac*box_scale)),
				]

			elif 'master' in bone_name:
				box_scale = 1.
				points = [
					Vector(( box_scale,  0.4142*box_scale, 0.0)),
					Vector(( 0.4142*box_scale,  box_scale, 0.0)),
					Vector((-0.4142*box_scale,  box_scale, 0.0)),
					Vector((-box_scale,  0.4142*box_scale, 0.0)),
					Vector((-box_scale, -0.4142*box_scale, 0.0)),
					Vector((-0.4142*box_scale, -box_scale, 0.0)),
					Vector(( 0.4142*box_scale, -box_scale, 0.0)),
					Vector(( box_scale, -0.4142*box_scale, 0.0)),
				]

			elif 'Spine_ctrl' in bone_name or 'Shoulder' in bone_name:
				box_scale = 1.1 if 'Spine' in bone_name else .4
				frac = 1.2 if 'Spine' in bone_name else .7
				points = [
					Vector((-2*box_scale, -box_scale, 0)),
					Vector((0, box_scale, -frac*box_scale)),
					Vector(( 2*box_scale, -box_scale, 0)),
					Vector((0, box_scale,  frac*box_scale)),
				]

			curve_data = bpy.data.curves.new(name=f'Curve_{bone_name}', type='CURVE')
			curve_data.dimensions = '3D'

			if 'Spine_ctrl' in bone_name or 'Shoulder' in bone_name:
				spline = curve_data.splines.new('BEZIER')
				spline.bezier_points.add(len(points) - 1)
				spline.use_cyclic_u = True

				handle_factor = 1.
				for i, p in enumerate(points):
					bp = spline.bezier_points[i]
					bp.co = p

					if i == 0:
						prev_p = points[-1]
						next_p = points[1]
					elif i == len(points) - 1:
						prev_p = points[i-1]
						next_p = points[0]
					else:
						prev_p = points[i-1]
						next_p = points[i+1]

					bp.handle_left_type = 'ALIGNED'
					bp.handle_right_type = 'ALIGNED'

					tangent_vector = next_p - prev_p
					tangent_direction = tangent_vector.normalized()
					handle_length = handle_factor * tangent_vector.length / 2
					bp.handle_left = p - tangent_direction * handle_length
					bp.handle_right = p + tangent_direction * handle_length

			else:
				spline = curve_data.splines.new('POLY')
				spline.use_cyclic_u = True
				spline.order_u = 4
				spline.use_smooth = True
				spline.points.add(len(points) - 1)

				for i, p in enumerate(points):
					x, y, z = p.x, p.y, p.z
					spline.points[i].co = (x, y, z, 1.0)

			shape_mesh = bpy.data.objects.new(f"ControlShape_{bone_name}", curve_data)
			bpy.context.collection.objects.link(shape_mesh)

		bpy.context.view_layer.objects.active = shape_mesh
		bpy.ops.object.mode_set(mode='OBJECT')

		if 'L_Foot_ik_ctrl' in bone_name:
			shape_mesh.rotation_euler = Vector((2.707914113998413, -0.5152463912963867, 0.11595991253852844))
			shape_mesh.location.y = -.05
		elif 'R_Foot_ik_ctrl' in bone_name:
			shape_mesh.rotation_euler = Vector((2.707888603210449, 0.5151955485343933, -0.11595503985881805))
			shape_mesh.location.y = -.05
		elif 'L_Hand_ik_ctrl' in bone_name:
			shape_mesh.rotation_euler.z = math.radians(90)
			shape_mesh.location.y = .125
		elif 'R_Hand_ik_ctrl' in bone_name:
			shape_mesh.rotation_euler.z = math.radians(90)
			shape_mesh.location.y = .125
		elif 'Hips_ctrl' in bone_name:
			if import_model:
				shape_mesh.rotation_euler = Vector((0.4498751759529114, -4.1911317083531685e-08, -1.4428644590225304e-07))
		elif 'Spine_ctrl' in bone_name:
			shape_mesh.rotation_euler.x = math.radians(90)
			apply_transform_safe(shape_mesh)
			shape_mesh.rotation_euler.z = math.radians(90)
			shape_mesh.location.z = 2.8
		elif 'Shoulder' in bone_name:
			shape_mesh.rotation_euler.x = math.radians(90)
			apply_transform_safe(shape_mesh)
			shape_mesh.location.z = .5

		apply_transform_safe(shape_mesh)

		shape_mesh.parent = parent_obj

		shape_mesh.hide_set(True)
		shape_mesh.hide_render = True

		bone = control_armature.pose.bones.get(bone_name)
		if bone:
			bone.custom_shape = shape_mesh

	control_curves_grp = bpy.data.objects.new(f'{armature_object.name}_CtrlCurves', None)
	control_curves_grp.empty_display_size = .0001
	bpy.context.collection.objects.link(control_curves_grp)
	control_curves_grp.parent = armature_object
	for ctrl_name in control_bone_data.keys():
		create_and_link_shape(ctrl_name, control_curves_grp)

	if import_model:
		for bone in armature_object.data.bones:
			bone.hide = True

	bpy.context.view_layer.objects.active = armature_object

	bpy.context.view_layer.update()

	bpy.ops.object.mode_set(mode='OBJECT')

	return control_armature


def import_pose(motion_string, name, fkik_enabled, import_model, model_path, scale=1.0):
	base_name = f'{name}'
	i = 0
	while bpy.data.objects.get(name) != None:
		name = base_name + f'.{i:03d}'
		if i > 100:
			break

	bvh_content_string = HEADER + motion_string
	lines = bvh_content_string.splitlines()
	root_bvh_joint, all_bvh_joints, ordered_channels_for_motion, frame_values = parse_bvh_data(lines, scale=scale)

	if import_model:
		bpy.ops.import_scene.fbx(filepath=model_path, use_anim=False, ignore_leaf_bones=True)

		armature_object = bpy.data.objects.get("AnymArmature")
		armature_object.name = name
		armature_data = armature_object.data

		armature_object.location.y = -.4
		armature_object.location.z = .09
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

		model = bpy.data.objects.get('AnymModel')
		model.lock_location = (True, True, True)
		model.lock_rotation = (True, True, True)
		model.lock_scale = (True, True, True)
		model.name += f'_{name}'
	else:
		armature_data = bpy.data.armatures.new("AnymArmature")
		armature_object = bpy.data.objects.new(name, armature_data)

		bpy.context.collection.objects.link(armature_object)
		bpy.context.view_layer.objects.active = armature_object

		bpy.ops.object.mode_set(mode='EDIT')
		edit_bones = armature_data.edit_bones

		build_blender_hierarchy_recursive(root_bvh_joint, edit_bones=edit_bones)

	bpy.ops.object.mode_set(mode='OBJECT')

	bpy.context.view_layer.objects.active = armature_object
	bpy.ops.object.mode_set(mode='POSE')
	pose_bones = armature_object.pose.bones

	joint_motion_data = {}
	for joint_name in all_bvh_joints.keys():
		joint_motion_data[joint_name] = {
			'pos': Vector((0, 0, 0)),
			'rot_x': 0.0, 'rot_y': 0.0, 'rot_z': 0.0
		}

	current_value_idx = 0
	for joint_name, channel_type in ordered_channels_for_motion:
		if current_value_idx >= len(frame_values):
			break

		value = frame_values[current_value_idx]
		if 'position' in channel_type:
			if import_model:
				if channel_type == "Xposition": joint_motion_data[joint_name]['pos'].x = value * scale
				elif channel_type == "Yposition": joint_motion_data[joint_name]['pos'].y = value * scale
				elif channel_type == "Zposition": joint_motion_data[joint_name]['pos'].z = value * scale
			else:
				if channel_type == "Xposition": joint_motion_data[joint_name]['pos'].z = value * scale
				elif channel_type == "Yposition": joint_motion_data[joint_name]['pos'].x = value * scale
				elif channel_type == "Zposition": joint_motion_data[joint_name]['pos'].y = value * scale
		elif channel_type == "Xrotation": joint_motion_data[joint_name]['rot_x'] = value
		elif channel_type == "Yrotation": joint_motion_data[joint_name]['rot_y'] = value
		elif channel_type == "Zrotation": joint_motion_data[joint_name]['rot_z'] = value

		current_value_idx += 1

	for bvh_joint_name, bvh_joint_data in all_bvh_joints.items():
		if bvh_joint_data.is_end_site:
			continue
		blender_bone = pose_bones.get(bvh_joint_data.name)
		if blender_bone:
			blender_bone.rotation_mode = bvh_joint_data.rot_order_str

	for bvh_joint_name, data in joint_motion_data.items():
		if bvh_joint_name not in all_bvh_joints:
			continue

		bvh_joint_data = all_bvh_joints[bvh_joint_name]

		if bvh_joint_data.is_end_site:
			continue

		blender_bone = pose_bones.get(bvh_joint_data.name)
		if not blender_bone:
			continue

		if bvh_joint_name == root_bvh_joint.name:
			blender_bone.location = data['pos']

		if data['rot_x'] != 0.0 or data['rot_y'] != 0.0 or data['rot_z'] != 0.0:
			rest_bone = armature_data.bones[bvh_joint_data.name]
			bone_rest_matrix = rest_bone.matrix_local.to_3x3()
			bone_rest_matrix_inv = Matrix(bone_rest_matrix)
			bone_rest_matrix_inv.invert()

			bone_rest_matrix_inv.resize_4x4()
			bone_rest_matrix.resize_4x4()

			rot_x = math.radians(data['rot_x'])
			rot_y = math.radians(data['rot_y'])
			rot_z = math.radians(data['rot_z'])

			bvh_rot = (rot_x, rot_y, rot_z)
			euler = Euler(bvh_rot, bvh_joint_data.rot_order_str[::-1])

			bone_rotation_matrix = euler.to_matrix().to_4x4()

			bone_rotation_matrix = (
				bone_rest_matrix_inv @
				bone_rotation_matrix @
				bone_rest_matrix
			)

			blender_bone.rotation_mode = 'QUATERNION'
			blender_bone.rotation_quaternion = bone_rotation_matrix.to_quaternion()

	bpy.ops.object.mode_set(mode='OBJECT')

	if fkik_enabled:
		control_armature = setup_fkik(armature_object, import_model=import_model)

		bpy.ops.ed.undo_push()
		bpy.context.view_layer.update()

		bpy.context.view_layer.objects.active = control_armature
		bpy.ops.object.mode_set(mode='POSE')

		hand_bone = control_armature.pose.bones.get('L_Hand_fk_ctrl')
		hand_bone.matrix.invert()
		bpy.context.view_layer.update()

		bpy.ops.ed.undo_push()
		bpy.ops.ed.undo()

	return armature_object, name

def get_pose_items(self, context):
	return [
		('NULL_ANYM_POSE', '--select pose--', ''),
		('TPOSE', 'T-Pose', ''),
		('STANDING', 'Standing', ''),
		('WALKING', 'Walking', ''),
		('RUNNING', 'Running', ''),
		('CROUCHED', 'Crouched', ''),
		('FIGHTING', 'Fighting', ''),
	]
