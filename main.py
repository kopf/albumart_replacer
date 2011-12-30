import os, sys, Image, re
from urllib import urlretrieve
import urllib2, MultipartPostHandler
from BeautifulSoup import BeautifulSoup

def win32_unicode_argv():
    """Uses shell32.GetCommandLineArgvW to get sys.argv as a list of Unicode
    strings.

    Versions 2.x of Python don't support Unicode in sys.argv on
    Windows, with the underlying Windows API instead replacing multi-byte
    characters with '?'.
    """

    from ctypes import POINTER, byref, cdll, c_int, windll
    from ctypes.wintypes import LPCWSTR, LPWSTR

    GetCommandLineW = cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = LPCWSTR

    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(LPWSTR)

    cmd = GetCommandLineW()
    argc = c_int(0)
    argv = CommandLineToArgvW(cmd, byref(argc))
    if argc.value > 0:
        # Remove Python executable and commands if present
        start = argc.value - len(sys.argv)
        return [argv[i] for i in
                xrange(start, argc.value)]

def search(filepath):
    url = 'http://www.tineye.com/search'
    # FIX FOR WINDOWS, PROBABLY BREAKS ON OTHER OPERATING SYSTEMS:
    filepath = filepath.encode('cp1252')
    params = {'image': open(filepath, 'rb')}
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    urllib2.install_opener(opener)
    req = urllib2.Request(url, params)
    response = urllib2.urlopen(req)
    followed = urllib2.urlopen(response.url + u'?sort=size&order=desc')
    return followed.read().strip()

def execute():
    mp3path = sys.argv[len(sys.argv) - 1]
    path = os.path.dirname(mp3path)
    files = [u'front.jpg', u'cover.jpg', u'folder.jpg']
    fullpath = None
    filename = None
    pixels = None
    for file in files:
        if os.path.exists(os.path.join(path, file)):
            filename = file
            fullpath = os.path.join(path, file)
            pixels = Image.open(fullpath).size
            pixels = pixels[0]*pixels[1]
            break
    
    if fullpath:
        print 'Searching for larger images...'
        html = search(fullpath)
        
        print 'Processing search results...'
        soup = BeautifulSoup(html)
        div = soup.find('div', {'class':'result-match clearfix'})
        if not div:
            print '''Didn't find any matching images. Aborting.'''
            return
        pixels_span = div.find('div', {'class': 'result-match-image'}).findAll('span')[-1]
        regexp = re.search('''(\d+)x(\d+)''', str(pixels_span))
        found_pixels = int(regexp.group(0).split('x')[0]) * int(regexp.group(0).split('x')[1])
        if found_pixels <= pixels:
            print '''Only found images smaller than your current one. Aborting.'''
            return
        urls = []
        for block in div.findAll('div', {'class': 'location-match'}):
            try:
                link = urls.append(block.find('a')['href'])
                if not link in urls:
                    urls.append(link)
            except Exception, e:
                pass
        
        print 'Downloading new image...'
        os.rename(fullpath, os.path.join(path, u'Backup of ' + filename))
        
        # fall-back mechanism:
        success = False
        i = 0
        while not success and i < len(urls):
            try:
                urlretrieve(urls[i], fullpath)
                success = True
            except Exception, e:
                i += 1
        if success:
            print 'Done!'
        else:
            print 'Exhausted URL list. Download failed.'
    else:
        print 'File not found.'

if __name__ == '__main__':
    sys.argv = win32_unicode_argv()
    execute()