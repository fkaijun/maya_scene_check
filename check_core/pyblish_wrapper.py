import pyblish.api  # todo add compatibility so this lib is still useable when you don't have pyblish installed

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
        for mesh_name in mesh_names:
            instance = context.create_instance(mesh_name, icon="cubes", families=FAMILIES)  # parent=instance_meshes.parent)
            instance.append(mesh_name)


def plugin_factory(func, **kwargs):
    first_line_doc = func.__doc__.split('\n', 2)[1].strip().capitalize()  # first line is empty so take second line

    class ValidationPlugin(pyblish.api.Validator):
        label = first_line_doc
        hosts = ["maya"]
        families = FAMILIES
        optional = True
        _func = [func]  # we can't store func directly or it will pass self when running self.func()

        def process(self, instance, context):
            mesh_names = instance[:]
            for mesh_name in mesh_names:
                func = self._func[0]
                errors = func(mesh_name, **kwargs)
                # context.data[self.label] = errors  # save failed results for reuse later
                assert not errors, 'found:' + str(errors)

    ValidationPlugin.__name__ = 'validate_' + func.__name__

    return ValidationPlugin


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

# ValidateHasVertexPntsAttr.actions = [] # todo implement fix

# check uv overlapping
ValidateCheckUvOverlapping = plugin_factory(check_uv_overlapping.main_function)
