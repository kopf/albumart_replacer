import os, sys, Image, re
from urllib import urlretrieve
import urllib2, MultipartPostHandler
from BeautifulSoup import BeautifulSoup

from settings import FILENAMES

def search(filepath):
    url = 'http://www.tineye.com/search'
    if 'win' in sys.platform:
        filepath = filepath.encode('cp1252')
    params = {'image': open(filepath, 'rb')}
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    urllib2.install_opener(opener)
    req = urllib2.Request(url, params)
    response = urllib2.urlopen(req)
    followed = urllib2.urlopen(response.url + u'?sort=size&order=desc')
    return followed.read().strip()

def execute():
    mp3path = sys.argv[len(sys.argv) - 1] # c:\album\01 - song.mp3
    path = os.path.dirname(mp3path) # c:\album
    orig_img_path = None # c:\album\folder.jpg
    filename = None # folder.jpg
    pixels = None # number of pixels in original image
    
    for file in FILENAMES:
        if os.path.exists(os.path.join(path, file)):
            filename = file
            orig_img_path = os.path.join(path, file)
            pixels = Image.open(orig_img_path).size
            pixels = pixels[0]*pixels[1]
            break
    
    if orig_img_path:
        print 'Searching for larger images...'
        html = search(orig_img_path)
        
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
        os.rename(orig_img_path, os.path.join(path, u'Backup of ' + filename))
        
        # fall-back mechanism:
        success = False
        i = 0
        while not success and i < len(urls):
            try:
                urlretrieve(urls[i], orig_img_path)
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
    if 'win' in sys.platform:
        from lib import win32_unicode_argv
        sys.argv = win32_unicode_argv()
    execute()