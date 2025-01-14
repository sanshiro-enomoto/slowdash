#! /usr/bin/python3


# temporary until SlowAPI becomes a package
import sys, os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))


from slowapi import SlowAPI, Response


class MyApp(SlowAPI):
        
    @SlowAPI.get('/')  # example for the simplest GET
    def home(self):
        return "I'm home"


    @SlowAPI.get('/hello/{name}')   # name from path, with default
    def hello(self, name:str="there"):
        return f"hello {name}"


    @SlowAPI.post('/message')  # example for POST
    def message(self, name:str, doc:bytes):  # name is from options, doc is from request body
        return {'message1': f"Dear {name},\n{doc.decode()}"}


    @SlowAPI.post('/message')   # multiple responses will be aggregated
    def message2(self, name:str, doc:bytes):
        return {'message2': f"I said to {name}, {doc.decode()}"}


    @SlowAPI.get('/source')  # example to return a blob
    def source(self):
        return Response(content_type='text/plain', content=open('slowapi.py', 'rb').read())


    @SlowAPI.delete('/trash')  # example for DELETE
    def delete_trash(self):
        sys.stderr.write("Trash Deleted\n")
        return Response(200)


    @SlowAPI.get('/deci')   # test to return a non-JSONable type
    def deci(self, num:float=10, den:float=3):
        import decimal
        return { "decimal": decimal.Decimal(num)/decimal.Decimal(den), "float": num/den }


    
app = MyApp()

'''
to run the app as a WSGI server, run:
$ gunicorn test_slowapi:app
'''


if __name__ == '__main__':
    ### test responses ###
    print(app.request_get('/'))
    print(app.request_get('/hello'))
    print(app.request_get('/hello/SlowDash'))
    print(app.request_post('/message?name=you', b"how are you doing?"))
    print(app.request_get('/home'))  # does not exist
    #print(app.request_get('/source'))
    print(app.request_delete('/trash'))
    print(app.request_get('/deci?den=3'))

    ### start a HTTP server at default port 8000 ###
    app.run()
