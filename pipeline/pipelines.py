

class BasePipeline(object):

    def process(self, doc):
        return doc

class SimplePipeline(BasePipeline):

    def process(self, doc):
        if isinstance(doc, dict):
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
        if isinstance(doc, list):
            for item in doc:
                print item[0]
        return doc

class KafkaPipeline(BasePipeline):

    def process(self, msg):
        pass

class SaveToDictPipeline(BasePipeline):

    def process(self, doc):
        if isinstance(doc, list):
            import codecs
            fp = codecs.open('reference.txt', 'w', encoding='utf-8')
            for item in doc:
                fp.write("%s\n" % (item[1]))
            fp.close()
        return doc

