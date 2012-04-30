import logging
from StringIO import StringIO
from urllib2 import urlopen

from django.conf import settings
from django.http import HttpResponse, Http404
from PIL import Image
import pylibmc

logger = logging.getLogger(__name__)

if settings.IS_SAE:
    mc = pylibmc.Client()
else:
    mc = pylibmc.Client(['127.0.0.1'])

DEFAULT_RESOLUTION = 400

def fetch_image(request):
    url = request.GET.get('url', None)
    url = url.encode('utf-8')
    if not url:
        raise Http404
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
    data = mc.get(url)
    if data:
        logger.info('Cache hit: {0}'.format(url))
        return HttpResponse(data, mimetype='image/%s' % ext)
    else:
        logger.info('Cache missed: {0}'.format(url))

    res = request.GET.get('res', DEFAULT_RESOLUTION)
    try:
        data = urlopen(url).read()
    except URLError as e:
        raise Http404

    if ext != 'gif':
        img = Image.open(StringIO(data))
        if img.size[0] > res:
            size = (res, int(res*1.0/img.size[0]*img.size[1]))
            img = img.resize(size, Image.ANTIALIAS)
            buf = StringIO()
            img.save(buf, ext) 
            data = buf.getvalue()
    mc.set(url, data, time=3600)
    return HttpResponse(data, mimetype='image/%s' % ext)

