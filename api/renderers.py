import re
from rest_framework import renderers

import json

class UserRenderer(renderers.JSONRenderer):
    """
    When data is render throught API in form of json then by default
    JSONRenderer class is used but instead of it we are using Custom_JSONRenderer 
    so, to see if there is any Errordetail(signifies error) is mention in it and in return
    output we can show error.
    """



    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        
        response =""
        if 'ErrorDetail' in str(data):
            response = json.dumps(({'errors':data}))
        else:
            response = json.dumps(data)
        
        return response