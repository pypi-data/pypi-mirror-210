#!/usr/bin/env python3

import sys
import hdbpp
import pyqtgraph
import threading



def plot_attributes_values(attributes,begin,end,schema='',show=False):

    rd = hdbpp.get_default_reader() if not schema else hdbpp.reader(config=schema)
    _cursor = rd._cursor

    plot = pyqtgraph.plot()
    event = threading.Event()
    
    def run(attribute,begin=begin,end=end,plot=plot,event=event,rd=rd):
        event.wait(.1)
        rd._cursor = rd.db.cursor()
        values = rd.get_attribute_values(attribute,begin,end)
        x = [t[0] for t in values if t[1] is not None]
        y = [t[1] for t in values if t[1] is not None]
        plot.plot(x,y)
        rd._cursor.close()
        #print(a,'done')
        rd._cursor = _cursor

    for a in attributes:
        #th = threading.Thread(target=run,args=(a,))
        #th.start()
        run(a)

    if show:
        plot.show()

    return plot


if __name__ == '__main__':
    schema = sys.argv[1]
    begin,end = sys.argv[-2:]
    attributes = sys.argv[2:-2]
    
    plot_attributes_values(attributes,begin,end,schema,show=True)
    
