

from __future__ import absolute_import
from utils import object_form_class_name

class PipelineManager(object):

    def __init__(self, pipelines=[]):
        self.pipelines = [object_form_class_name(p) for p in pipelines]

    def process(self, doc):
        im_doc = doc
        for pp in self.pipelines:
            im_doc = pp.process(im_doc)
