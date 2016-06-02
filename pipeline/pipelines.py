

class BasePipeline(object):

    def process(self, doc):
        return doc

class SimplePipeline(BasePipeline):

    def process(self, doc):
        print doc.doc['title']
        print doc.doc['post_time']
        return doc

class EastFormatPipeline(BasePipeline):

    def process(self, doc):
        print 'east format'
        return doc

class ESPipeline(BasePipeline):

    def process(self, doc):
        print 'ES pipeline'
        return doc

class StorePipeline(BasePipeline):

    def process(self, doc):
        print 'Store pipeline'
        return doc

class KafkaPipeline(BasePipeline):

    def process(self, msg):
        pass

