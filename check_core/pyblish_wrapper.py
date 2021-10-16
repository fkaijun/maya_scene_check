from check_core.check_functions import *

# create pyblish plugins
# most funcs take a meshname arg
# this can be gotten from instance collector plugin
import pyblish.api


class CollectMeshNames(pyblish.api.Collector):
    """collect meshnames"""
    # plugin attributes
    families = ['*']
    hosts = ['maya']
    label = 'collect meshnames'
    optional = True

    def process(self, context):
        import maya.cmds as cmds
        mesh_names = cmds.ls(type='mesh', objectsOnly=True, noIntermediate=True)
        for mesh_name in mesh_names:
            instance = context.create_instance(mesh_name, icon="cubes", families=['mesh', 'cmds', 'python2'])  # parent=instance_meshes.parent)
            instance.append(mesh_name)

