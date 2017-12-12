class BidirectionalListener(object):

    def __init__(self):
        super(BidirectionalListener, self).__init__()
        # self.parent = parent

    def register_listener(self):
        return self.process_event

    def process_event(self, e):
        ## override this
        print("event: {}".format(e))

    def send_to_parent(self, e):
        self.parent.send_event(e)