class Resource:
    def __call__(self, request, *args):
        self.request = request
        self.setProperty(args)
        # Try to locate a handler method.
        try:
            callback = getattr(self, "do_%s" % request.method)
        except AttributeError:
            # This class doesn't implement this HTTP method, so return a
            # 405 (method not allowed) response with the allowed methods.
            allowed_methods = [m[3:] for m in dir(self) if m.startswith("do_")]
            return HttpResponseNotAllowed(allowed_methods)
        
        # Call the looked-up method
        return callback()
    
    def setProperty(self, *args):
        pass
