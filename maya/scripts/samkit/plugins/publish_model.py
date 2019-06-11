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
    label = 'Export FBX File'
    families = ['mdl']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)
