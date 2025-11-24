import sys, os
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
import webbrowser
import math

try:
	import requests
except ImportError:
	print('requests module not found. Installing...')
	import subprocess
	python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
	subprocess.call([python_exe, "-m", "ensurepip"])
	subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
	subprocess.call([python_exe, "-m", "pip", "install", "requests"])
	print('requests module installed successfully.')

from .utils import import_pose


ANYM_POSES = {
	'TPOSE': '0.0 0.0 0.91 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
	'STANDING': '0.0 0.0 0.915556 -2.686633 -2.507240 -3.725996 8.863924 -0.977226 1.382313 0.000000 0.113183 10.036398 2.418233 -4.287297 -4.288259 0.000000 0.000000 -0.000001 0.968358 5.593504 0.122170 0.435359 -0.016123 8.599061 -5.051244 -1.822243 -5.085787 0.000000 0.000000 -0.000001 0.807181 4.508004 -1.114769 -3.923263 -1.782650 11.946513 -2.286621 0.419885 -1.593431 5.200063 -3.178905 -5.355329 -1.712830 1.747785 16.304016 -1.668256 9.644320 4.197483 -3.659436 71.470565 5.343645 -32.365001 -8.193753 17.004270 -8.932759 7.274603 17.997885 4.799549 -14.141005 0.980003 14.342044 -67.479631 0.540239 24.710453 10.176975 12.695284 5.134529 -5.652613 22.329369\n',
	'WALKING': '0.0 0.0 0.869634 -5.156413 -1.214391 -5.410411 -1.709857 2.046793 -20.518447 -0.194409 2.821928 9.639633 22.674375 2.022817 7.065949 0.319114 -0.242817 -0.046777 -0.485952 -0.883780 21.276853 12.540215 -1.923606 17.813456 -12.848437 -5.769769 -8.659176 -0.403757 0.317752 -0.080174 4.731687 0.752432 14.091849 -1.918952 0.502233 1.095741 1.762074 0.605030 1.362915 -1.460636 4.213001 -19.982780 -0.953491 -5.442693 5.160420 5.932315 5.130612 1.747537 18.007731 72.350556 25.328865 -31.373172 -5.726233 -2.154197 2.176981 19.996316 -18.105757 1.457258 -5.002118 -1.150550 23.709883 -64.830696 -12.471515 41.735666 7.170822 -5.860969 -0.917491 -16.211826 -11.683631\n',
	'RUNNING': '0.0 0.0 0.944308 12.812485 -3.764145 -3.449099 6.162934 -2.591651 21.884037 -16.779459 5.769927 1.611377 12.924832 2.332486 2.128104 0.000000 0.000000 -0.000001 2.281804 7.332328 -16.747847 -10.971671 -0.227808 8.013506 -23.763674 -7.757531 -2.377268 0.000000 0.000000 -0.000001 -10.430504 6.608937 6.446684 -10.014379 -4.599386 6.985147 -10.106457 -0.428153 2.249650 8.424983 -2.053782 -10.427315 2.427841 1.754064 0.686918 -6.744412 -1.306699 4.014442 -37.160491 65.066568 -17.400981 -107.616498 0.533386 23.300145 -20.239555 -7.541115 -2.493251 -8.147590 2.082604 4.206349 -35.837155 -62.851323 58.385568 113.784891 1.138298 20.943669 23.422029 -4.067571 -27.872150\n',
	'CROUCHED': '0.0 0.0 0.792000 -7.587353 -3.244431 -5.244226 10.449458 -2.692427 1.237742 8.725213 8.053955 59.866197 28.034230 4.273684 -27.513477 -0.000001 -0.000000 0.000000 -12.310561 4.514536 -49.888928 -24.246104 5.546499 49.671887 -30.678573 9.327886 5.286487 0.000001 0.000000 0.000000 -8.409343 1.527181 46.302820 -4.850420 0.085146 10.987337 -3.818213 -0.937031 2.779952 15.485148 4.624125 9.982532 6.171311 -0.166689 -33.296183 -22.539460 -6.687543 -7.196572 -42.859961 27.952473 -40.464302 -95.768290 -24.000663 9.008869 -17.402181 -4.216924 19.540276 20.828827 7.671515 -3.644733 22.885188 -70.705963 -26.571569 73.503613 7.590814 9.765324 12.214401 -0.851391 0.037118\n',
	'FIGHTING': '0.0 0.0 0.929197 1.998556 0.365758 -2.714235 11.078149 -15.233524 -13.417147 15.345969 0.333671 13.138032 12.556353 10.035754 18.094387 0.000000 0.000000 -0.000001 -7.943415 11.946518 7.718570 -9.117149 -5.011846 5.266846 -16.635733 -4.257653 0.560239 0.000000 0.000000 -0.000001 0.645713 -0.742055 11.902913 3.841259 2.161500 -1.203929 0.955819 0.166722 -0.892026 12.257349 -0.606808 2.459871 15.515777 3.088477 13.207125 -10.436967 -19.768036 -9.090913 -52.863180 56.077539 -40.028783 -112.513607 -29.267658 25.987605 -6.362055 -16.723496 -3.005818 13.895320 20.171606 -7.156372 83.480282 -55.718614 -57.387083 110.505613 0.414810 22.901932 13.447608 21.708462 -25.038953\n',
}


class ANYM_OT_warning(bpy.types.Operator):
	"""Anym Plugin Message"""
	bl_idname = "anym.warning_window"
	bl_label = "Anym Plugin"
	bl_options = {'REGISTER', 'INTERNAL'}

	message: StringProperty(default="")
	details: StringProperty(default="")
	severity: EnumProperty(
		name="Severity",
		items=[
			('INFO', "Info", "", 'INFO', 0),
			('WARNING', "Warning", "", 'ERROR', 1),
			('ERROR', "Error", "", 'CANCEL', 2),
		],
		default='ERROR'
	)
	show_details: BoolProperty(default=False)

	def _icon(self):
		return {
			'INFO': 'INFO',
			'WARNING': 'ERROR',\
			'ERROR': 'CANCEL',
		}.get(self.severity, 'INFO')

	def execute(self, context):
		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = False
		layout.use_property_decorate = False

		row = layout.row(align=True)
		row.label(text=f"Anym Plugin: {self.severity.title()}", icon=self._icon())

		box = layout.box()
		for i, line in enumerate((self.message or "").split("\n")):
			box.label(text=line)

		layout.separator()
		footer = layout.row()
		footer.label(text="Press OK to continue.")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=420)


class ANYM_OT_import_armature(bpy.types.Operator):
	bl_idname = "anym.import_armature"
	bl_label = "Import Armature"
	bl_description = "Import a built-in pose as an armature"

	@classmethod
	def poll(cls, context):
		pose = context.scene.anym_selected_pose
		return pose != 'NULL_ANYM_POSE'

	def execute(self, context):
		pose = context.scene.anym_selected_pose
		import_model = context.scene.anym_import_model
		fkik_enabled = context.scene.anym_fkik_enabled

		model_path = os.path.join(os.path.dirname(__file__), "resources", "model", "AnymModel.fbx")

		pose_data = ANYM_POSES[pose]

		armature_object, name = import_pose(
			'Frames: 1\nFrame Time: 0.050000\n' + pose_data,
			name=pose.lower(),
			fkik_enabled=fkik_enabled,
			import_model=import_model,
			model_path=model_path
		)

		return {'FINISHED'}


class ANYM_OT_add_pose(bpy.types.Operator):
	bl_idname = "anym.add_pose"
	bl_label = "Add Pose"
	bl_description = "Add a new pose entry"

	@classmethod
	def poll(cls, context):
		scene = context.scene
		return scene.anym_pose_index <= 20

	def execute(self, context):
		scene = context.scene
		item = scene.anym_poses.add()
		scene.anym_pose_index = len(scene.anym_poses) - 1
		return {'FINISHED'}


class ANYM_OT_remove_pose(bpy.types.Operator):
	bl_idname = "anym.remove_pose"
	bl_label = "Remove Pose"
	bl_description = "Remove the selected pose entry"

	@classmethod
	def poll(cls, context):
		scene = context.scene
		return scene.anym_poses and scene.anym_pose_index >= 0

	def execute(self, context):
		scene = context.scene
		idx = scene.anym_pose_index
		scene.anym_poses.remove(idx)
		scene.anym_pose_index = min(max(0, idx-1), len(scene.anym_poses)-1)
		return {'FINISHED'}


class ANYM_OT_generate_animation(bpy.types.Operator):
	bl_idname = "anym.generate_animation"
	bl_label = "Generate Animation"
	bl_description = "Generate animation via API"

	@classmethod
	def poll(cls, context):
		scene = context.scene
		return len(scene.anym_poses) >= 1

	def execute(self, context):

		allow_online = bpy.app.online_access
		if allow_online == False:
			bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Blender's 'online_access' variable is set to False.")
			return {'CANCELLED'}

		scene = context.scene

		api_key = scene.anym_api_key
		url = scene.anym_url
		if len(api_key) == 0:
			bpy.ops.anym.warning_window('INVOKE_DEFAULT', message="Please fill in your Anym API key.")
			return {'CANCELLED'}

		data, request_valid, message  = self.format_request_data(context)

		if request_valid:

			status_code, output = self.api_request(data, api_key, url)

			if status_code == 200:
				anim_id = output['data']['animation_id']

				webbrowser.open(
					f'{url}preview/{anim_id}/', new=0
				)
			else:
				try:
					bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Error {status_code}: {output['error']}")
				except:
					bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Error {status_code}: {output['message']}")
				return {'CANCELLED'}

			return {'FINISHED'}
		else:
			bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=message)
			return {'CANCELLED'}

	def format_request_data(self, context):
		scene = context.scene

		total_frames = scene.anym_total_frames
		fps = scene.anym_fps
		is_looping = scene.anym_is_looping
		solve_ik = scene.anym_solve_ik

		keyframe_indices_total = list()
		rotations_total = list()
		root_pos_total = list()

		for pose_item in scene.anym_poses:
			if pose_item.armature:
				armature_object = pose_item.armature

				if pose_item.is_static:
					keyframe_indices = [pose_item.frame]

				else:
					keyframe_indices = self.find_keyframe_indices(armature_object)

				if len(keyframe_indices) > 0:

					for frame_idx in keyframe_indices:
						if frame_idx / fps >= 10:
							return None, False, f"Keyframes on armature {armature_object.name} exceed maximum duration of 10 seconds."
						if any([frame_idx - idx < 3 and frame_idx - idx > 0 for idx in keyframe_indices]):
							continue
						bpy.context.scene.frame_set(frame_idx)

						rotations = self.get_bone_rotations(armature_object)
						root_pos = self.get_root_pos(armature_object)
						rotations_total.append(rotations)
						root_pos_total.append(root_pos)

						keyframe_indices_total.append(frame_idx)
				else:
					return None, False, f"Pose {armature_object.name} does not have any keyframes set."
			else:
				return None, False, "One or more poses in the Anym Plugin do not have a pose selected."

		if len(keyframe_indices_total) != len(set(keyframe_indices_total)):
			return None, False, "Two or more armatures have keyframes set on the same frame index."

		if max(keyframe_indices_total) > total_frames:
			scene.anym_total_frames = max(keyframe_indices_total)
			total_frames = max(keyframe_indices_total)

		zipped_sorted = sorted(
			list(zip(keyframe_indices_total, rotations_total, root_pos_total)),
			key=lambda t: t[0]
		)
		indices_total, rots_total, root_pos_total = map(list, zip(*zipped_sorted))

		data = {
			"is_looping": is_looping,
			"solve_ik": solve_ik,
			"n_frames": total_frames,
			"fps": fps,
			"indices": indices_total,
			"target_rot": rots_total,
			"target_root_pos": root_pos_total,
		}

		return data, True, None

	def find_keyframe_indices(self, armature_object_main):
		keyframes = set()
		for child in armature_object_main.children:
			if 'control' in child.name:
				armature_object = child
				break

		action = armature_object.animation_data
		if not action or not action.action:
			return keyframes

		for fcurve in action.action.fcurves:
			if fcurve.data_path.startswith('pose.bones['):
				for keyframe_point in fcurve.keyframe_points:
					keyframes.add(int(keyframe_point.co[0]))
		keyframes = list(keyframes)
		keyframes.sort()

		return keyframes

	def get_bone_rotations(self, armature_object, root_name = "Hips"):

		depsgraph = bpy.context.evaluated_depsgraph_get()
		obj_eval = armature_object.evaluated_get(depsgraph)

		data = obj_eval.data
		pose = obj_eval.pose

		def preorder(b):
			out = [b]
			for c in b.children:
				out += preorder(c)
			return out

		bones_order = preorder(data.bones[root_name])

		out_vals = []

		pose_mats = {b.name: pose.bones[b.name].matrix.copy() for b in bones_order}
		rest_mats = {b.name: data.bones[b.name].matrix_local.copy() for b in bones_order}

		R_obj = obj_eval.matrix_world.to_euler()

		for i, bone in enumerate(bones_order):
			name = bone.name
			parent = bone.parent

			M_pose = pose_mats[name]
			M_rest = rest_mats[name]

			if parent:
				M_parent_pose = pose_mats[parent.name]
				M_parent_rest = rest_mats[parent.name]
				L_pose = M_parent_pose.inverted() @ M_pose
				L_rest = M_parent_rest.inverted() @ M_rest
			else:
				L_pose = M_pose.copy()
				L_rest = M_rest.copy()

			D = L_rest.inverted() @ L_pose

			R_local = D.to_3x3().to_4x4()

			M_rest = rest_mats[name]
			R_bvh = M_rest @ R_local @ M_rest.inverted()
			eul_xyz = R_bvh.to_euler('XYZ')

			if 'Hips' in name:
				eul_xyz.x += R_obj.x
				eul_xyz.y += R_obj.y
				eul_xyz.z += R_obj.z

			out_vals.append([math.degrees(eul_xyz.z) % 360,
							math.degrees(eul_xyz.y) % 360,
							math.degrees(eul_xyz.x) % 360])

		return out_vals

	def get_root_pos(self, armature_object, root_name="Hips"):
		depsgraph = bpy.context.evaluated_depsgraph_get()
		arm_eval = armature_object.evaluated_get(depsgraph)

		root_bone = arm_eval.pose.bones.get(root_name)

		world_matrix = arm_eval.matrix_world @ root_bone.matrix
		root_pos = world_matrix.translation

		root_pos = [root_pos.x, root_pos.z, -root_pos.y]

		return root_pos

	def api_request(self, data, api_key, url):
		url = f'{url}api/predict/'
		headers = {
			'X-API-KEY': f'{api_key}',
			'X-Plugin-Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbHVnaW5fdmVyc2lvbl9pZCI6IjhmZDNmZjk0LTRlYmQtNGFmOS04N2U3LThhZDdhOGEwYTRhNiJ9.f6CHpOF9Hh2Nyx71cRx2tFTebigLglNoRhQnbZVuHsE',
			'Content-Type': 'application/json'
		}
		response = requests.post(url, headers=headers, json=data)

		return response.status_code, response.json()


class ANYM_OT_fetch_animation(bpy.types.Operator):
	bl_idname = "anym.fetch_animation"
	bl_label = "Fetch Animation"
	bl_description = "Fetch exported animation from API"

	def execute(self, context):
		scene = context.scene
		url = scene.anym_url
		api_key = scene.anym_api_key

		headers = {
			'X-API-KEY': f'{api_key}',
			'X-Plugin-Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbHVnaW5fdmVyc2lvbl9pZCI6IjhmZDNmZjk0LTRlYmQtNGFmOS04N2U3LThhZDdhOGEwYTRhNiJ9.f6CHpOF9Hh2Nyx71cRx2tFTebigLglNoRhQnbZVuHsE',
			'Content-Type': 'application/json'
		}

		response = requests.get(f'{url}api/import-animation/', headers=headers)

		if response.status_code == 200:
			import_pose(
				response.json()['data']['animation'].split('MOTION')[1],
				'AnymOutput',
				False,
				False,
				'',
				scale=1.0,
				is_static=False,
				frame_indices=sorted(set(response.json()['data']['keyframe_indices']) | {0, 1}),
			)
			
		elif response.status_code == 404:
			bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Error {response.status_code}: No fetchable animation found. First click 'Generate Animation', then unlock it in the Anym previewer.")
		else:
			try:
				bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Error {response.status_code}: {response.json()['error']}")
			except:
				bpy.ops.anym.warning_window('INVOKE_DEFAULT', message=f"Error {response.status_code}: {response.json()['message']}")
			return {'CANCELLED'}

		return {'FINISHED'}
