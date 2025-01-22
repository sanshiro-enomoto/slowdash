#! /usr/bin/python3


# temporary until SlowAPI becomes a package
import sys, os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))


import slowapi


class MyApp(slowapi.App):
        
    @slowapi.get('/')
    def home(self):
        return "I'm home"

    @slowapi.get('/hello/{name}')
    def hello(self, name:str="there"):
        return f"hello {name}"


app = MyApp()

key = slowapi.BasicAuthentication.generate_key('slow', 'dash')
#app.slowapi.add_middleware(slowapi.BasicAuthentication(auth_list=[key]))

app.slowapi.add_middleware(
    slowapi.FileServer('../../../web', exclude='/api', drop_exclude_prefix=True, index_file="welcome.html")
)


if __name__ == '__main__':
    print(app.slowapi('/Warning.png'))
    print(app.slowapi('/api'))
    print(app.slowapi('/api/hello/slowy'))
    app.run()
