from StringIO import StringIO
from urllib2 import urlopen

from django.http import HttpResponse, Http404
from PIL import Image

DEFAULT_RESOLUTION = 400

def fetch_image(request):
    url = request.GET.get('url', None)
    if not url:
        raise Http404
    res = request.GET.get('res', DEFAULT_RESOLUTION)

    # TODO: recursive fetch
    if not url.startswith('http://bbs.nju.edu.cn/'):
        raise Http404
    def get_ext(url):
        ext = url.rsplit('.', 1)[-1]
        ext = ext.lower()
        if ext == 'jpg':
            ext = 'jpeg'
        return ext if ext in ['jpeg', 'png', 'gif'] else None
    ext = get_ext(url)
    if not ext:
        raise Http404
    try:
        data = urlopen(url).read()
    except URLError as e:
        raise Http404
    img = Image.open(StringIO(data))
    if img.size[0] <= res:
        return Response(data, mimetype='image/%s' % ext)
    size = (res, int(res*1.0/img.size[0]*img.size[1]))
    img = img.resize(size, Image.ANTIALIAS)
    buf = StringIO()
    img.save(buf, ext) 
    return HttpResponse(buf.getvalue(), mimetype='image/%s' % ext)

