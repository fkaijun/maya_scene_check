import pyblish.api

from check_core.check_functions import *
import check_core.check_uv_overlapping as check_uv_overlapping
# todo would be cool to add language support to plugins


FAMILIES = ['mesh', 'cmds', 'python2']


class CollectMeshNames(pyblish.api.Collector):
    """collect long mesh names"""

    # pyblish plugin attributes
    families = ['*']
    hosts = ['maya']
    label = 'collect meshnames'
    optional = True

    def process(self, context):
        import maya.cmds as cmds
        mesh_names = cmds.ls(type='mesh', objectsOnly=True, noIntermediate=True, long=True)
        for mesh_name_long in mesh_names:
            # mesh_name_long = mesh_name_long.rsplit('|', 1)[0]  # get long name of parent transform
            mesh_name_short = mesh_name_long.rsplit('|', 1)[1]  # get short name of the node
            instance = context.create_instance(mesh_name_short, icon="cubes", families=FAMILIES)  # parent=instance_meshes.parent)
            instance.append(mesh_name_long)


class ActionSelect(pyblish.api.Action):
    label = "Select failed"
    on = "failedOrWarning"
    icon = "hand-o-up"  # Icon from Awesome Icon

    def process(self, context, plugin):
        import maya.cmds as cmds
        errors = context.data[plugin.label]  # list of strings, ex. ['pCube2.f[0]',...]
        print(errors)
        cmds.select(errors)


def plugin_factory(func, **kwargs):
    """
    create a costum class that loads the functions from check_core in pyblish as plugins.
    :param function func: function we want to wrap in a pyblish plugin
    :param dict **kwargs: additional keyword arguments we want to pass to the function when run
    :return custom class type, inherits from pyblish.api.Validator
    :rtype: Class
    """
    # extract label from the function's docstring
    first_line_doc = func.__doc__.split('\n', 2)[1]  # first line is empty so take second line
    label_extracted = first_line_doc.lower().replace('check', '').strip().capitalize()

    class ValidationPlugin(pyblish.api.Validator):
        label = label_extracted
        hosts = ["maya"]
        families = FAMILIES
        optional = True
        actions = [ActionSelect]
        _func = [func]  # we can't store func directly or it will pass self when running self.func()

        def process(self, instance, context):
            mesh_names = instance[:]
            for mesh_name in mesh_names:
                try:
                    func = self._func[0]
                    errors = func(mesh_name, **kwargs)
                except Exception as ex:
                    errors = [mesh_name]

                context.data[self.label] = errors  # save failed results for reuse later
                assert not errors, 'check failed on:' + str(errors)


    ValidationPlugin.__name__ = 'validate_' + func.__name__

    return ValidationPlugin


# we save the new plugin classes in variables so that
# pyblish.api.register_plugin_path will find the plugin classes in this module

# check functions
ValidateFindTriangleEdge = plugin_factory(find_triangle_edge)
ValidateFindManyEdge = plugin_factory(find_many_edge)
ValidateFindNonManifoldEdges = plugin_factory(find_non_manifold_edges)
ValidateFindLaminaFaces = plugin_factory(find_lamina_faces)
ValidateFindBivalentFaces = plugin_factory(find_bivalent_faces)
ValidateFindZeroAreaFaces = plugin_factory(find_zero_area_faces, max_face_area=0.0001)
ValidateFindMeshBorderEdges = plugin_factory(find_mesh_border_edges)
ValidateFindCreaseEdges = plugin_factory(find_crease_edges)
ValidateFindZeroLengthEdges = plugin_factory(find_zero_length_edges, min_edge_length=0.0001)
ValidateFindUnfrozenVertices = plugin_factory(find_unfrozen_vertices)
ValidateHasVertexPntsAttr = plugin_factory(has_vertex_pnts_attr, fix=False)
ValidateUvFaceCrossQuadrant = plugin_factory(uv_face_cross_quadrant)
ValidateMissingUvFaces = plugin_factory(missing_uv_faces)
ValidateFindDoubleFaces = plugin_factory(find_double_faces)

# check uv overlapping
ValidateCheckUvOverlapping = plugin_factory(check_uv_overlapping.main_function)


class ActionFix(pyblish.api.Action):
    label = "Fix"
    on = "failedOrWarning"
    icon = "hand-o-up"  # Icon from Awesome Icon

    def process(self, context, plugin):

        # because pyblish doesnt support getting instances from a plugin yet
        # we have to do this manually :(
        # if only we would get the plugin instances when using an action
        data = []
        for result in context.data["results"]:
            if result["error"] and result["plugin"] == plugin:
                instance = result["instance"]
                data.extend(instance)

        func = plugin._func[0]
        for mesh_name in data:
            func(mesh_name, fix=True)


# one of the functions supports a fix, implement this as an action
ValidateHasVertexPntsAttr.actions.append(ActionFix)

# TODO fix HACK: if we dont run this check after find_unfrozen_vertices it crashes maya
# see https://github.com/fkaijun/maya_scene_check/issues/4
ValidateHasVertexPntsAttr.order += .1
# for now i will remove this pyblish check since it is to dangerous to crash maya
del ValidateHasVertexPntsAttr

# this check errors out, delete for now
del ValidateFindCreaseEdges
