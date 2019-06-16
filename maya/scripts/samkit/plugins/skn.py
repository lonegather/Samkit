import pyblish.api


class SkinRootValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder
    label = 'Valid Skeleton Root'
    families = ['skn']

    def process(self, instance):
        pass
