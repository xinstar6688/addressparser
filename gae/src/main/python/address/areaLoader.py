import bulkload
from address.models import AreaCache

class AreaLoader(bulkload.Loader):
    def __init__(self):
        # Our 'Person' entity contains a name string and an email
        bulkload.Loader.__init__(self, 'Area',
                             [('code', str),
                              ('name', str),
                              ('parentArea', str),
                              ('middle', str),
                              ('unit', str),
                              ('hasChild', bool),
                              ])

    def HandleEntity(self, entity):
        AreaCache.put(entity)
        return entity

if __name__ == '__main__':
    bulkload.main(AreaLoader())