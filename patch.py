#!/usr/bin/env python

import os
import click
import sys
import shutil


def build_patch(pack, old_zip, new_zip):
    input_dir = 'assets'
    patch_dir = 'patch/%s' % pack
    #os.system('java -jar zipdiff.jar -file1 zips/%s.main.%s.obb -file2 assets/%s.main.%s.obb -outputfile diffs.html' % 
    #    (pack, old_version, pack, new_version))
    try:
        os.remove('diffs.html')
    except: 
        pass
    os.system('java -jar zipdiff.jar -file1 zips/%s -file2 zips/%s -outputfile diffs.html' % (old_zip, new_zip))

    try:
        shutil.rmtree(patch_dir)
    except:
        pass
    os.makedirs(patch_dir)

    from BeautifulSoup import BeautifulSoup
    with open('diffs.html') as f:
        soup = BeautifulSoup(f)
        
        tags = soup.findAll('td')
        
        i = iter(tags)
        for tag in i:
            #print tag
            if 'Removed (' in tag.text:
                pass # TODO we don't yet support removing files in our patches
            if 'Added (' in tag.text or 'Changed (' in tag.text:
                tag = next(i)
                tag = next(i)
                uls = tag.findAll('li')
                print uls
                for ul in uls:
                    dr = "%s/%s" % (patch_dir, os.path.dirname(ul.text))
                    print dr
                    
                    try: os.makedirs(dr) 
                    except Exception as e: print "e: %s" % e
                    shutil.copy("%s/%s" % (input_dir, ul.text), 
                                    "%s/%s" % (patch_dir, ul.text))
#    os.system("rm assets/%s.main.%s.obb ; cd liger-content/assets ; zip -n .mp4 -r main.1044.org.storymaker.app.obb org.storymaker.app/default")               

build_patch('burundi', 'burundi.main.2.obb', 'burundi.main.3.obb')
build_patch('learning_guide', 'learning_guide.main.1.obb', 'learning_guide.main.2.obb')
build_patch('default', 'main.1031.org.storymaker.app.obb', 'main.1044.org.storymaker.app.obb')
#build_patch('main', 2, 3)


#build_patch('persian')
#build_patch('assets', 'patch/mena')
