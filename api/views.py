from datetime import datetime

from django.http import HttpResponse


def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
            <a href="/write-file">Write File</a>
        </body>
    </html>
    '''
    return HttpResponse(html)

def write_file(request):
    now = datetime.now()
    f = open("demofile2.txt", "a")
    content = "The current time is " + str(now)
    f.write("Now the file has more content! \n " + content)
    f.close()
    html = f'''
    <html>
        <body>
            <h1>Write success!</h1>
            <a href="/read-file">Read File</a>
        </body>
    </html>
    '''
    return HttpResponse(html)
def read_file(request):
    f = open("demofile2.txt", "r")
    content = f.read()
    f.close()
    html = f'''
    <html>
        <body>
            <h1>Read success!</h1>
            <p>{content}</p>
            <a href="/">Back</a> 
        </body>
    </html>
    '''
    return HttpResponse(html)