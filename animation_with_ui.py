import maya.cmds as cmds
import random
num_of_shields = 50

# cleaning of previous run
list_objects = cmds.ls("My*")
if list_objects and len(list_objects) > 1:
    cmds.delete(list_objects)

sphere_radius = 2
sphere = cmds.polySphere(name= "MySphere", r=sphere_radius)[0]

main_cylinder = cmds.polyCylinder(name="MyCylinder#", h=0.25, r=sphere_radius * 0.25, sx=8)
# cmds.polyBevel3(res, segments=1, depth=1, fraction=0.5, autoFit=1 )

min_play = cmds.playbackOptions(query=True, minTime=True)
max_play = cmds.playbackOptions(query=True, maxTime=True)

instance_group = cmds.group(empty=True, name="MyInstanceGroup#")

for i in range(0, num_of_shields):
    res = cmds.instance(main_cylinder)

    cmds.parent(res, instance_group)

    x = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    y = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    z = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    cmds.move(x, y, z, res)

    cmds.aimConstraint(sphere, res, aimVector=[0,1,0])

cmds.hide(main_cylinder)
cmds.xform(instance_group, centerPivots=True)

# animation
cmds.cutKey(instance_group, time=(min_play, max_play), attribute="rotateY")
cmds.setKeyframe(instance_group, time=min_play, attribute="rotateY", value=0)
cmds.setKeyframe(instance_group, time=max_play, attribute="rotateY", value=360)
cmds.selectKey(instance_group, time=(min_play, max_play), attribute="rotateY", keyframe=True)
cmds.keyTangent(inTangentType="linear", outTangentType="linear")

