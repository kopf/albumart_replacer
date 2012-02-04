import os, sys, Image, re
from urllib import urlretrieve
import urllib2, MultipartPostHandler
from BeautifulSoup import BeautifulSoup

from settings import FILENAMES

def search(filepath):
    """ Query tineye with image.
    """
    
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
    """ Main program logic.
    """
    
    dirpath = os.path.dirname(sys.argv[-1]) # c:\album
    orig_img_fpath = None # c:\album\folder.jpg
    filename = None # folder.jpg
    pixels = None # number of pixels in original image
    
    for file in FILENAMES:
        if os.path.exists(os.path.join(dirpath, file)):
            filename = file
            orig_img_fpath = os.path.join(dirpath, file)
            pixels = Image.open(orig_img_fpath).size
            pixels = pixels[0]*pixels[1]
            break
    
    if orig_img_fpath:
        print 'Searching for larger images...'
        html = search(orig_img_fpath)
        
        print 'Processing search results...'
        soup = BeautifulSoup(html)
        results = soup.findAll('div', {'class':'result-match clearfix'})
        
        if not results:
            print '''Didn't find any matching images. Aborting.'''
            return
        
        urls = []
        for result in results:
            pixels_span = result.find('div', {'class': 'result-match-image'}).findAll('span')[-1]
            regexp = re.search('''(\d+)x(\d+)''', str(pixels_span))
            found_pixels = int(regexp.group(0).split('x')[0]) * int(regexp.group(0).split('x')[1])
            if found_pixels <= pixels:
                pass
            else:
                for block in result.findAll('div', {'class': 'location-match'}):
                    try:
                        urls.append(block.find('a')['href'])
                    except Exception, e:
                        pass
        if not urls:
            print 'No similar images found. Exiting...'
            return
        else:
            print 'Downloading new image...'
            os.rename(orig_img_fpath, os.path.join(dirpath, u'Backup of ' + filename))
            
            # fall-back mechanism:
            success = False
            i = 0
            while not success and i < len(urls):
                try:
                    urlretrieve(urls[i], orig_img_fpath)
                    success = True
                except Exception, e:
                    i += 1
            if success:
                print 'Done!'
            else:
                print 'Exhausted URL list. Download failed.'
                # revert changes to original file's name:
                os.rename(os.path.join(dirpath, u'Backup of ' + filename), orig_img_fpath)
    else:
        print 'File not found.'

if __name__ == '__main__':
    if 'win' in sys.platform:
        from lib import win32_unicode_argv
        sys.argv = win32_unicode_argv()
    execute()
    