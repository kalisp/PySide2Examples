import maya.cmds as cmds

''' Simple form to create chain of joints.
    It allows user to fill prefix of joints names, their amount, spacing
    and orientation
'''

window_name = 'joint_generator_win'
if cmds.window(window_name, exists=True):
    cmds.deleteUI(window_name, window=True)

win = cmds.window(window_name, t="Joint Window", width=100, s=False) # not resizable
cmds.columnLayout('c_layout', adj=True)
cmds.separator()

cmds.text('Define joint(s)')
cmds.separator()
cmds.textFieldGrp("jntName", l="Prefix:")
cmds.textFieldGrp("jntAmount", l="Amount of joints:")
cmds.textFieldGrp("jntSpacing", l="Spacing of joints:")
cmds.separator()

cmds.text('Choose orientation')
cmds.separator()
cmds.button('b_xyz', l='XYZ', height=30, c='xyz()', p='c_layout')
cmds.button('b_yxz', l='YXZ', height=30, c='yxz()', p='c_layout')
cmds.button('b_zxy', l='ZXY', height=30, c='zxy()', p='c_layout')

cmds.showWindow(win)

def xyz():
    ''' Create chain of joints with xyz orientation '''
    name, amount, spacing = get_values()
    cmds.select(cl=True) # clear selection

    if amount == '1':
        joint = cmds.joint(n='jointSpine_0')
        cmds.setAttr(joint + '.jointOrientX', -90)
        cmds.setAttr(joint + '.jointOrientY', 0)
        cmds.setAttr(joint + '.jointOrientZ', 90)
    else:
        create_joint_chain(name, int(amount), int(spacing), 'xyz')

def yxz():
    ''' Create chain of joints with yxz orientation '''
    name, amount, spacing = get_values()
    cmds.select(cl=True)

    if amount == '1':
        joint = cmds.joint(n='jointSpine_0')
        cmds.setAttr(joint + '.jointOrientX', 0)
        cmds.setAttr(joint + '.jointOrientY', 0)
        cmds.setAttr(joint + '.jointOrientZ', 0)
    else:
        create_joint_chain(name, int(amount), int(spacing), 'yxz')

def zxy():
    ''' Create chain of joints with zxy orientation '''
    name, amount, spacing = get_values()
    cmds.select(cl=True)

    if amount == '1':
        joint = cmds.joint(n='jointSpine_0')
        cmds.setAttr(joint + '.jointOrientX', 0)
        cmds.setAttr(joint + '.jointOrientY', 0)
        cmds.setAttr(joint + '.jointOrientZ', 90)
    else:
        create_joint_chain(name, int(amount), int(spacing), 'zxy')

def get_values():
    ''' Auxiliary function to get string values from form '''
    name = cmds.textFieldGrp("jntName", q=True, tx=True)
    amount = cmds.textFieldGrp("jntAmount", q=True, tx=True)
    spacing = cmds.textFieldGrp("jntSpacing", q=True, tx=True)

    return name, amount, spacing


#NUM_OF_JOINTS = 3

def create_joint_chain(name, amount, spacing, orient):
    ''' Create chain of 'amount' joints with 'name' prefix, 'spacing' far from each other
        with 'orient' orientation
    '''
    for i in range(amount):
        cmds.joint(n='{}_{}'.format(name, i))
        cmds.move(0, spacing*i, 0)

    cmds.joint('{}_0'.format(name), edit=True, oj=orient, children=True)
    selected_joints = cmds.ls(sl=True)
    cmds.setAttr(selected_joints[0] + '.jointOrientX', 0)
    cmds.setAttr(selected_joints[0] + '.jointOrientY', 0)
    cmds.setAttr(selected_joints[0] + '.jointOrientZ', 0)