"""
    Small example of scripted animation. Bunch of shields is rotating around central sphere
    Known issues: dialog is too large, should be fitted around children TODO
"""
import maya.cmds as cmds
import random
import functools

num_of_shields = 50

# cleaning of previous run
list_objects = cmds.ls("My*")
if list_objects and len(list_objects) > 1:
    cmds.delete(list_objects)

# create pivot sphere
sphere_radius = 2
sphere = cmds.polySphere(name= "MySphere", r=sphere_radius)[0]

# shape of discular cylinder
main_cylinder = cmds.polyCylinder(name="MyCylinder#", h=0.25, r=sphere_radius * 0.25, sx=8)
# cmds.polyBevel3(res, segments=1, depth=1, fraction=0.5, autoFit=1 ) #TODO ntw wrk

instance_group = cmds.group(empty=True, name="MyInstanceGroup#") # for rotation
for i in range(0, num_of_shields):
    res = cmds.instance(main_cylinder)

    cmds.parent(res, instance_group) # add to group

    # set position randomly
    x = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    y = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    z = random.uniform(1 + sphere_radius, 10) * random.choice([1, -1])
    cmds.move(x, y, z, res)

    cmds.aimConstraint(sphere, res, aimVector=[0,1,0]) # aim disc to pivot sphere

cmds.hide(main_cylinder)
cmds.xform(instance_group, centerPivots=True) # set pivot to the center of the group

def keyRotation(instance_group, min_play, max_play, attr):
    """ Prepare key frames according to dialog """
    cmds.cutKey(instance_group, time=(min_play, max_play), attribute=attr)
    cmds.setKeyframe(instance_group, time=min_play, attribute=attr, value=0)
    cmds.setKeyframe(instance_group, time=max_play, attribute=attr, value=360)
    cmds.selectKey(instance_group, time=(min_play, max_play), attribute=attr, keyframe=True)
    cmds.keyTangent(inTangentType="linear", outTangentType="linear")


def createUI(windowTitle, applyCallback, instance_group):
    """ Creates simple UI via cmds """
    windowID = "MyWindowID"

    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)

    cmds.window(windowID, resizeToFitChildren=True, title=windowTitle, sizeable=False)

    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 75), (2,60), (3,60)], columnOffset=[(1,"right",3)])
    # 1st line
    cmds.text(label="Time range:")
    startTimeField = cmds.intField(value= cmds.playbackOptions(query=True, minTime=True))
    endTimeField = cmds.intField(value= cmds.playbackOptions(query=True, maxTime=True))
    # 2st line
    cmds.text(label="Attribute")
    targetAttributeField = cmds.textField(text="rotateY")
    cmds.separator(h=10, style='none')
    # 3rd line - empty
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    # 4th line - buttons
    cmds.separator(h=10, style='none')
    cmds.button(label="Apply", command=functools.partial(applyCallback,
                                                         instance_group,
                                                         startTimeField,
                                                         endTimeField,
                                                         targetAttributeField))

    def cancelCallback(*args):
        """ Close dialog when Cancel button pressed"""
        if cmds.window(windowID, exists=True):
            cmds.deleteUI(windowID)

    cmds.button(label="Cancel", command=cancelCallback)

    cmds.showWindow()

def applyCallback(instance_group, startTimeField, endTimeField, targetAttributeField, *args):
    """ Called after Apply button is pressed """
    startTime = cmds.intField(startTimeField, query=True, value=True)
    endTime = cmds.intField(endTimeField, query=True, value=True)
    targetAttribute = cmds.textField(targetAttributeField, query=True, text=True)

    keyRotation(instance_group, startTime, endTime, targetAttribute)

# create dialog
createUI("My Window", applyCallback, instance_group)