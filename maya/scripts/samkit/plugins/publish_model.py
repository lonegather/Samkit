import pyblish.api


class ModelHistoryValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder
    label = 'Validate Model History'
    families = ['mdl']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)


class ModelScaleValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder
    label = 'Validate Model Scale'
    families = ['mdl']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)


class ModelExtractor(pyblish.api.InstancePlugin):

    order = pyblish.api.ExtractorOrder
    label = 'Export FBX Data'
    families = ['mdl']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)


class ModelIntegrator(pyblish.api.InstancePlugin):

    order = pyblish.api.IntegratorOrder
    label = 'Submit'
    families = ['mdl']

    def process(self, instance):
        import shutil
        import samkit
        from maya import cmds

        current_path = cmds.file(q=True, sn=True)
        shutil.copyfile(current_path, instance.data['pathSrc'])

        samkit.checkin()
