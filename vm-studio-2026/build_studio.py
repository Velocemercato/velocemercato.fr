import bpy, math, os, sys, random, time
from mathutils import Vector
ROOT=os.environ.get('VM_WORKSPACE_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT=ROOT+'/vm-studio-2026/renders'
os.makedirs(OUT,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.fps=12;scene.frame_start=1;scene.frame_end=720
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.world.color=(.012,.022,.055)
sh=scene.display.shading
sh.light='STUDIO';sh.studiolight_rotate_z=.4;sh.studiolight_background_alpha=0
sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH'
sh.curvature_ridge_factor=1.4;sh.curvature_valley_factor=1.1
sh.show_specular_highlight=True;sh.show_object_outline=False
sh.background_type='WORLD'
scene.display.render_aa=os.getenv('VM_RENDER_AA','8')
scene.view_settings.view_transform='Standard'
def mat(name,c,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.metallic=metal;m.roughness=.25;return m
navy=mat('midnight lacquer',(.022,.055,.13),.7)
gold=mat('warm champagne gold',(.9,.59,.14),.75)
white=mat('porcelain',(.82,.9,.98),.25)
dark=mat('pupil',(.007,.015,.03))
green=mat('emerald',(.03,.68,.4),.3)
red=mat('coral',(.9,.12,.17))
floor=mat('navy stage',(.012,.025,.06),.2)
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def uv(name,loc,scale,material,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o
def cube(name,loc,scale,material,parent=None,bevel=.12):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material);o.parent=parent
 if bevel:
  m=o.modifiers.new('soft edges','BEVEL');m.width=bevel;m.segments=3
  o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,material,parent=None):
 a,b=Vector(a),Vector(b);v=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=v.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o
def tor(name,loc,major,minor,material,rot=(0,0,0),parent=None):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=loc,major_radius=major,minor_radius=minor,rotation=rot)
 o=bpy.context.object;o.name=name;o.data.materials.append(material);o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o
def curve(name,pts,r,material,parent=None):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3
 s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.data.materials.append(material);o.parent=parent;return o
cube('infinite stage',(0,2,-.25),(200,200,.3),floor,bevel=.01)
for i in range(4):tor('stage concentric ring',(0,0,-.07),1.3+i*.55,.025,gold)
for x in [-4.5,4.5]:
 for z in [1,2.3,3.6,4.9]:
  uv('stadium light',(x,3,z),(.17,.17,.17),gold)
  rod('light support',(x,3,-.1),(x,3,5),.035,navy)
root=empty('VM animated mascot',(-3,0,0))
body=uv('rounded navy jacket',(0,0,1.2),(.48,.32,.56),navy,root)
uv('shirt',(0,-.29,1.45),(.21,.055,.25),white,root)
for side in [-1,1]:uv('bow tie',(.095*side,-.36,1.64),(.12,.035,.075),gold,root)
uv('bow tie knot',(0,-.4,1.64),(.045,.035,.045),gold,root)
for z in [.99,1.18,1.37]:uv('jacket button',(0,-.325,z),(.035,.025,.035),gold,root)
head=empty('expressive head',(0,-.015,2.08),root)
uv('giant round head',(0,0,0),(.62,.39,.55),white,head)
uv('face screen',(0,-.35,-.01),(.51,.11,.38),navy,head)
eyes=[];brows=[]
for side in [-1,1]:
 eye=uv('bright eye',(.22*side,-.45,.065),(.135,.042,.16),white,head);eyes.append(eye)
 uv('pupil',(.22*side,-.493,.065),(.054,.019,.079),dark,head)
 uv('catchlight',(.22*side-.016,-.51,.1),(.018,.01,.022),white,head)
 brow=uv('gold eyebrow',(.22*side,-.45,.26),(.15,.035,.035),gold,head);brows.append(brow)
 uv('headphone earpad',(.62*side,0,.02),(.13,.24,.3),navy,head)
 uv('headphone gold disc',(.7*side,0,.02),(.055,.19,.22),gold,head)
curve('headband',[(-.62,0,.15),(-.48,0,.52),(0,0,.65),(.48,0,.52),(.62,0,.15)],.055,navy,head)
uv('nose',(0,-.5,-.05),(.065,.06,.075),gold,head)
curve('mischievous smile',[(-.19,-.46,-.17),(0,-.49,-.255),(.19,-.46,-.17)],.026,gold,head)
curve('microphone boom',[(.62,-.12,-.08),(.58,-.4,-.2),(.32,-.51,-.22)],.024,gold,head)
uv('microphone',(.29,-.52,-.22),(.07,.045,.055),dark,head)
arms=[];forearms=[];legs=[]
for side in [-1,1]:
 arm=empty('arm shoulder',(.45*side,0,1.48),root);arms.append(arm)
 rod('jacket sleeve',(0,0,0),(.18*side,0,-.36),.115,navy,arm)
 uv('elbow',(.18*side,0,-.36),(.12,.12,.12),gold,arm)
 fore=empty('elbow pivot',(.18*side,0,-.36),arm);forearms.append(fore)
 rod('forearm',(0,0,0),(0,-.045,-.33),.095,navy,fore)
 uv('white glove',(0,-.045,-.38),(.14,.1,.15),white,fore)
 uv('thumb',(-.08*side,-.1,-.32),(.07,.06,.095),white,fore)
 leg=empty('hip',(.22*side,0,.86),root);legs.append(leg)
 rod('trouser leg',(0,0,0),(0,0,-.58),.13,navy,leg)
 uv('sneaker',(0,-.12,-.7),(.23,.34,.14),gold,leg)
 cube('sneaker sole',(0,-.14,-.76),(.43,.59,.055),white,leg,bevel=.035)
 for j in range(3):rod('sneaker laces',(-.09,-.22+j*.065,-.59),(.09,-.22+j*.065,-.59),.012,white,leg)
# ----- Le nouveau plateau original : cinq personnages et un décor complet. -----
cream=mat('ivory tailoring',(.75,.78,.73),.3)
teal=mat('turquoise accents',(.025,.57,.64),.5)
bronze=mat('deep skin',(.31,.145,.07))
peach=mat('warm skin',(.74,.43,.28))
hair=mat('espresso hair',(.035,.016,.011))
blue=mat('electric blue',(.05,.28,.9),.5)
# L'ancienne scène est intégrée dans une rédaction circulaire.
for o in list(bpy.data.objects):
 if o.name.startswith(('stadium light','light support')): bpy.data.objects.remove(o,do_unlink=True)
for i in range(22):
 a=math.pi*i/21
 x,y=6*math.cos(a),3+1.1*math.sin(a)
 cube('architectural gold fin',(x,y,2.5),(.045,.14,5.2),gold,bevel=.01)
cube('LED backdrop',(0,3.15,3.1),(9.4,.22,4.3),navy,bevel=.18)
cube('LED inset',(0,2.99,3.1),(8.9,.035,3.84),dark,bevel=.09)
# Graphismes du mur LED, pas de logo appartenant à un tiers.
for i in range(15):
 x=-4.2+i*.6
 rod('LED fine grid',(x,2.94,1.38),(x,2.94,4.8),.008,navy)
for z in [1.5,2.1,2.7,3.3,3.9,4.5]:rod('LED fine grid',(-4.3,2.94,z),(4.3,2.94,z),.008,navy)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=bpy.data.fonts.load(fontpath) if os.path.exists(fontpath) else None
def text3(name,value,loc,size,material,align='CENTER'):
 d=bpy.data.curves.new(name,'FONT');d.body=value;d.align_x=align;d.align_y='CENTER';d.size=size;d.extrude=.003;d.bevel_depth=.001
 if font:d.font=font
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(material);return o
text3('brand wall','VÉLOCE MERCATO',(0,2.85,4.23),.39,gold)
text3('wall headline','LE JOURNAL',(0,2.83,3.55),.82,white)
text3('wall strap','SPORT  /  CULTURE  /  GAMING',(0,2.82,2.86),.23,teal)
text3('wall date','16 NOVEMBRE 2026',(0,2.81,2.45),.19,gold)
for side in [-1,1]:
 rod('wall underline',(side*.2,2.8,3.0),(side*3.8,2.8,3.0),.016,gold)
# Halo central et grandes lames architecturales.
for r in [5.1,5.3]:tor('overhead halo',(0,1,5.35),r,.035,gold)
for x in [-5.8,5.8]:
 cube('side monolith',(x,1.7,2.2),(.34,1.3,4.5),navy,.0 if False else None,bevel=.12)
 rod('cyan architectural light',(x,1.0,.25),(x,1.0,4.3),.034,teal)
# Table flottante, façade découpée et lumière en liseré.
cube('anchor desk',(0,-.86,.89),(8.9,1.15,.94),navy,bevel=.22)
cube('desk tabletop',(0,-.88,1.42),(9.25,1.42,.14),dark,bevel=.12)
cube('desk gold line',(0,-1.46,1.35),(8.7,.032,.035),gold,bevel=.014)
cube('desk cyan line',(0,-1.44,.52),(8.35,.025,.025),teal,bevel=.008)
text3('desk monogram','VM',(0,-1.47,.96),.55,gold)
text3('desk tagline','LE JOURNAL  •  LA TEAM',(0,-1.47,.64),.12,white)
# Les coéquipiers sont fictifs, créés pour le programme.
crew=[]
def human(name,x,skin,jacket,glasses=False,beard=False,curls=False):
 p=empty(name,(x,0,0)); h=empty(name+' head',(0,-.015,2.11),p)
 uv(name+' torso',(0,0,1.19),(.42,.27,.55),jacket,p)
 uv(name+' shirt',(0,-.25,1.48),(.17,.045,.25),white,p)
 for side in [-1,1]:
  uv(name+' lapel',(.17*side,-.235,1.5),(.09,.05,.23),navy,p)
  rod(name+' sleeve',(.38*side,0,1.49),(.50*side,-.19,1.17),.105,jacket,p)
  uv(name+' hand',(.5*side,-.31,1.17),(.12,.16,.09),skin,p)
 uv(name+' face',(0,0,0),(.38,.29,.43),skin,h)
 uv(name+' neck',(0,0,-.36),(.14,.13,.2),skin,h)
 uv(name+' hair',(0,.015,.245),(.4,.3,.28),hair,h)
 if curls:
  for j in range(17):
   a=2*math.pi*j/17;uv(name+' curl',(.35*math.cos(a),-.02,.24+.25*math.sin(a)),(.14,.14,.14),hair,h)
  for side in [-1,1]:uv(name+' long hair',(.33*side,.03,-.12),(.14,.22,.39),hair,h)
 else:
  uv(name+' quiff',(-.08,-.05,.37),(.31,.24,.15),hair,h)
 for side in [-1,1]:
  uv(name+' ear',(.38*side,0,-.015),(.075,.095,.12),skin,h)
  uv(name+' eye white',(.145*side,-.265,.055),(.09,.035,.10),white,h)
  uv(name+' pupil',(.145*side,-.298,.055),(.043,.014,.065),dark,h)
  brow=uv(name+' eyebrow',(.145*side,-.267,.18),(.1,.025,.023),hair,h)
  if glasses:
   tor(name+' glasses',(.145*side,-.31,.055),.112,.018,gold,(math.pi/2,0,0),h)
 if glasses:rod(name+' spectacle bridge',(-.035,-.325,.055),(.035,-.325,.055),.014,gold,h)
 uv(name+' nose',(0,-.31,-.04),(.055,.065,.074),skin,h)
 if beard:
  uv(name+' beard',(0,-.04,-.255),(.285,.255,.16),hair,h)
  uv(name+' chin skin',(0,-.23,-.19),(.195,.06,.10),skin,h)
 mouth=uv(name+' animated mouth',(0,-.286,-.19),(.095,.012,.022),dark,h)
 curve(name+' microphone',[(.37,-.08,-.1),(.37,-.33,-.18),(.19,-.34,-.22)],.012,gold,h)
 uv(name+' microphone tip',(.17,-.34,-.22),(.035,.025,.025),dark,h)
 cube(name+' tablet',(0,-.42,1.48),(.48,.31,.025),navy,p,bevel=.025)
 text3(name+' nameplate',name.upper(),(x,-1.50,1.20),.105,white)
 crew.append((p,h,mouth));return p
human('Pablo',-1.35,peach,cream,True,True)
human('Black',.30,bronze,navy,False,True)
human('Scorpion',1.95,peach,gold,False,False)
human('La créatrice',3.6,peach,teal,False,False,True)
# Objet d'ouverture qui tourne : ballon géométrique aux couleurs VM.
orb=empty('news orb',(4.5,2.2,4.1))
uv('globe',(0,0,0),(.42,.42,.42),navy,orb)
for rot in [(0,0,0),(math.pi/2,0,0),(0,math.pi/2,0)]:tor('globe meridian',(0,0,0),.44,.015,gold,rot,orb)
# Accessoires de la mascotte et sourire animé.
robotmouth=uv('animated robot mouth',(0,-.481,-.205),(.13,.015,.035),gold,head)
cam_data=bpy.data.cameras.new('VM editorial camera');cam=bpy.data.objects.new('VM editorial camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
cam.data.type='ORTHO';cam.data.lens=50
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.fps=12;scene.frame_start=1;scene.frame_end=int(os.getenv('VM_RENDER_FRAMES','48'))
scene.display.shading.studiolight_rotate_z=.25
scene.display.shading.show_cavity=True
scene.display.shading.curvature_ridge_factor=1.25
# Emphase par plan : cinq portraits et un plan d'ensemble, sans image fixe.
SHOT=os.getenv('VM_SHOT','wide')
positions={'wide':0,'vm':-3,'pablo':-1.35,'black':.30,'scorpion':1.95,'creatrice':3.6,'portrait':-2.45}
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def update(sc):
 t=(sc.frame_current-1)/12
 root.location=(-3,0,.015*math.sin(t*3));root.rotation_euler.z=.025*math.sin(t*2)
 head.rotation_euler=(.035*math.sin(t*4),.025*math.cos(t*3),.025*math.sin(t*2))
 for e in eyes:e.scale.z=.025 if (t%3)<.12 else .16
 robotmouth.scale.z=.025+.05*abs(math.sin(t*14))
 for i,side in enumerate([-1,1]):
  arms[i].rotation_euler.x=-.45+.12*math.sin(t*3+i)
  arms[i].rotation_euler.y=side*.26
  forearms[i].rotation_euler.x=-.72+.14*math.sin(t*2+i)
 for i,(p,h,m) in enumerate(crew):
  h.rotation_euler=(.025*math.sin(t*3+i),.025*math.sin(t*2+i),.018*math.sin(t*2.7+i))
  m.scale.z=.016+.038*abs(math.sin(t*(10+i)))
 orb.rotation_euler=(t*.3,t*.1,t*.25)
 if SHOT=='wide':
  cam.location=(2.1+.18*math.sin(t*.7),-13,5.4);aim(cam,(0,.65,2.24));cam.data.ortho_scale=11.9
 elif SHOT=='portrait':
  cam.location=(-2.65+.06*math.sin(t),-12,4.6);aim(cam,(-2.45,.3,2.03));cam.data.ortho_scale=6.7
 else:
  x=positions[SHOT];cam.location=(x+.45+.08*math.sin(t),-11,4.1);aim(cam,(x,.15,2.00));cam.data.ortho_scale=5.9
bpy.app.handlers.frame_change_pre.clear();bpy.app.handlers.frame_change_pre.append(update)
def save_project():
 global SHOT
 scene.frame_start=1;scene.frame_end=48;SHOT='wide'
 animated=[root,head,robotmouth,orb,cam]+eyes+arms+forearms
 for p,h,m in crew:animated.extend([p,h,m])
 for frame in range(1,49):
  scene.frame_set(frame);update(scene)
  for obj in animated:
   for path in ['location','rotation_euler','scale']:obj.keyframe_insert(data_path=path,frame=frame)
 for obj in animated:
  if obj.animation_data and obj.animation_data.action:
   for curve in obj.animation_data.action.fcurves:
    for key in curve.keyframe_points:key.interpolation='LINEAR'
    curve.modifiers.new('CYCLES')
 scene.timeline_markers.clear()
 maincam=cam
 for i,name in enumerate(['wide','vm','pablo','black','scorpion','creatrice','portrait']):
  SHOT=name;scene.frame_set(1);update(scene)
  copy=cam.copy();copy.data=cam.data.copy();copy.animation_data_clear();copy.name='VM camera - '+name;scene.collection.objects.link(copy)
  marker=scene.timeline_markers.new(name.upper(),frame=1+i*48);marker.camera=copy
 SHOT='wide';scene.frame_end=336;scene.frame_set(1);update(scene)
 scene.camera=next(o for o in scene.objects if o.name=='VM camera - wide')
 bpy.app.handlers.frame_change_pre.clear()
 scene.render.resolution_x=1280;scene.render.resolution_y=720
 code=bpy.data.texts.get('VM source studio') or bpy.data.texts.new('VM source studio')
 code.clear();code.write(open(__file__,encoding='utf-8').read())
 bpy.ops.file.pack_all()
 bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/vm-studio-2026/VM-plateau-3D.blend')
if 'project' in args:
 save_project()
elif 'preview' in args:
 for SHOT in ['wide','vm','pablo','portrait']:
  scene.render.resolution_x=540 if SHOT=='portrait' else 1280;scene.render.resolution_y=960 if SHOT=='portrait' else 720
  scene.frame_set(19);scene.render.filepath=OUT+'/'+SHOT+'-preview.png';bpy.ops.render.render(write_still=True)
else:
 for SHOT in os.getenv('VM_SHOTS','wide,vm,pablo,black,scorpion,creatrice,portrait').split(','):
  scene.render.resolution_x=540 if SHOT=='portrait' else int(os.getenv('VM_RENDER_WIDTH','1280'));scene.render.resolution_y=960 if SHOT=='portrait' else int(os.getenv('VM_RENDER_HEIGHT','720'))
  scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='HIGH';scene.render.ffmpeg.ffmpeg_preset='GOOD'
  scene.frame_set(1);scene.render.filepath=OUT+'/'+SHOT+'.mp4';bpy.ops.render.render(animation=True)
 save_project()
