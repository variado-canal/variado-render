# Blender 3.x / 4.x -- procedural real-geometry cinematic reel.
# Usage: blender -b --python cine3d/render.py -- job.json vertical output.mp4
import bpy, sys, json, math, random
from mathutils import Vector
from math import sin,cos,pi
argv=sys.argv[sys.argv.index('--')+1:]
job_path,ratio,out=argv
job=json.load(open(job_path,encoding='utf8'))
random.seed(42)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE' if bpy.app.version<(4,2,0) else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1080 if ratio=='vertical' else 1920
scene.render.resolution_y=1920 if ratio=='vertical' else 1080
scene.render.resolution_percentage=100
scene.render.fps=60
scene.frame_start=1
scene.frame_end=1272
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='HIGH'
scene.render.filepath=out
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
world=bpy.data.worlds.new('Deep cinematic void')
scene.world=world
world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.007,.006,.021,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.3

def mat(name,color,metal=.0,rough=.35,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
 m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:
  if 'Emission Color' in p.inputs:
   p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
  else:
   p.inputs['Emission'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
PURPLE=mat('Violeta Variado premium',(.19,.045,.46),.24,.3)
CYAN=mat('Electric cyan',(.025,.72,1),.2,.23,2)
GOLD=mat('Amber signal',(1,.51,.08),.2,.32,1.2)
WHITE=mat('Pearl',(.82,.85,1),.12,.27)
DARK=mat('Obsidian',(.013,.021,.045),.5,.25)
RED=mat('Explosion core',(1,.09,.015),.12,.3,2.4)

def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 bpy.ops.object.shade_smooth()
 return o
def ring(name,loc,major,minor,material):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=96,minor_segments=12,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(material)
 bpy.ops.object.shade_smooth()
 return o
def text_obj(s,loc,size=0.6,material=WHITE):
 cu=bpy.data.curves.new('type','FONT');cu.body=s;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.extrude=.008;cu.bevel_depth=.003
 ob=bpy.data.objects.new(s,cu);scene.collection.objects.link(ob);ob.location=loc;cu.materials.append(material)
 # 3D texts face local XY, camera travels on negative Y; rotate toward camera
 ob.rotation_euler=(pi/2,0,0)
 return ob
def area(name,loc,color,energy,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size
 ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc
 direction=Vector((0,0,1))-ob.location;ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 return ob
area('Blue rim',(0,-7,9),(.28,.59,1),2400,12)
area('Warm key',(-9,-4,5),(1,.56,.3),1700,10)

# All stations coexist in a single continuous three-dimensional world along X.
stations=[0,9,18,27,36,45]
for idx,x in enumerate(stations):
 ring('Architectural portal '+str(idx),(x,2,0),3.2,.065,PURPLE)
 ring('Portal inner '+str(idx),(x,2,0),2.75,.02,CYAN)
 for j in range(3):
  a=j*2*pi/3+idx*.6
  uv('Floating sculpture',(x+cos(a)*3.4,2.1,sin(a)*3.4),(.28,.28,.28),GOLD if j==0 else PURPLE)

# A singular luminous physical connection between all narrative stations.
curve=bpy.data.curves.new('Continuous light thread','CURVE');curve.dimensions='3D';curve.bevel_depth=.075;curve.bevel_resolution=4
spline=curve.splines.new('POLY');spline.points.add(119)
for k,p in enumerate(spline.points):
 x=45*k/119.
 p.co=(x,1.2+0.8*sin(x*.55),1.3+1.1*sin(x*.31),1)
obj=bpy.data.objects.new('One continuous path of knowledge',curve);scene.collection.objects.link(obj);obj.data.materials.append(CYAN)
curve.bevel_factor_end=0.
for frame,v in [(1,.02),(1120,1),(1272,1)]:
 curve.bevel_factor_end=v;curve.keyframe_insert(data_path='bevel_factor_end',frame=frame)
# Scene 1 - impossible silent explosion.
core=uv('Silent explosion',(0,2,0),(1.08,1.08,1.08),RED)
for k in range(36):
 a=2*pi*k/36;ball=uv('Fire debris',(cos(a)*2,2+sin(a)*.7,sin(a)*1.4),(.08,.08,.08),GOLD)
 ball.keyframe_insert(data_path='location',frame=1)
 ball.location.x*=1.8;ball.location.z*=1.5
 ball.keyframe_insert(data_path='location',frame=95)
core.keyframe_insert(data_path='scale',frame=1)
core.scale=(1.8,1.8,1.8);core.keyframe_insert(data_path='scale',frame=95)
text_obj('EN EL ESPACIO',(0,0,4),.78)
text_obj('NO HAY SONIDO',(0,0,-4),.64,CYAN)
# Scene 2 - molecules physically moving, sound wave path.
for i in range(7):
 for j in range(5):
  x=9+(i-3)*.57;z=(j-2)*.62
  p=uv('Air molecule',(x,1.5+(.2 if (i+j)%2 else 0),z),(.12,.12,.12),CYAN if i%3==0 else WHITE)
  for f in [220,285,350]:
   p.location.x=x+(.17 if f==285 else 0)*sin(i*.8+j)
   p.keyframe_insert(data_path='location',frame=f)
text_obj('EL AIRE VIBRA',(9,0,4),.70)
# Scene 3 - ear shaped concentric wave rings.
for i in range(5):
 r=ring('Acoustic pressure',(18,2,0),.65+i*.42,.035,CYAN)
 r.scale=(1,1,1)
text_obj('EL SONIDO VIAJA',(18,0,-4),.64)
# Scene 4 - vacuum destroys pulse wave.
for i in range(8):
 x=27-2.2+i*.65
 p=uv('Sparse atom',(x,1.9,1.3*sin(i)),(.1,.1,.1),WHITE)
text_obj('SIN PARTICULAS',(27,0,4),.66)
text_obj('NO HAY ONDA',(27,0,-4),.72,GOLD)
# Scene 5 - stylized moon in void.
moon=uv('Moon',(36,2,0),(2.2,2.2,2.2),WHITE)
for i in range(12):
 a=2*pi*i/12
 uv('Crater',(36+cos(a)*1.8,.13,sin(a)*1.8),(.21,.18,.21),DARK)
text_obj('LA LUNA ES SILENCIOSA',(36,0,-3.8),.58)
# Scene 6 - conclusion brand.
ring('Brand physical halo',(45,2,0),2.2,.15,GOLD)
text_obj('VARIADO',(45,0,0.6),1.12,WHITE)
text_obj('LO INCREIBLE ES REAL',(45,0,-.65),.43,CYAN)

# Camera: one object, unbroken trajectory; independent recomposition per ratio.
camdata=bpy.data.cameras.new('Perspective cine camera');cam=bpy.data.objects.new('Continuous single camera',camdata);scene.collection.objects.link(cam)
scene.camera=cam
camdata.type='PERSP';camdata.lens=32 if ratio=='vertical' else 38
camdata.dof.use_dof=False
def point_camera(ob,point):
 ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
for i,frame in enumerate([1,190,385,580,770,980,1272]):
 x=stations[min(i,5)] + (-3 if i==0 else 0)
 cam.location=(x,-11.4 if ratio=='vertical' else -14,1.2 if ratio=='vertical' else 1.7)
 cam.keyframe_insert(data_path='location',frame=frame)
 point_camera(cam,(min(max(x,0),45),1.5,0))
 cam.keyframe_insert(data_path='rotation_euler',frame=frame)
for fc in cam.animation_data.action.fcurves:
 for kp in fc.keyframe_points:kp.interpolation='BEZIER';kp.handle_left_type='AUTO_CLAMPED';kp.handle_right_type='AUTO_CLAMPED'
# Tone down volumetric complexity for reproducible open-source runners.
scene.render.film_transparent=False
scene.render.image_settings.color_mode='RGB'
bpy.ops.wm.save_as_mainfile(filepath=out.replace('.mp4','.blend'))
bpy.ops.render.render(animation=True)
