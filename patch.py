#!/usr/bin/env python

import os
import click
import sys
import shutil

app_package = 'org.storymaker.app'
def build_patch(pack, old_zip, new_zip, patch_name):
    input_dir = 'assets'
    patch_dir = 'patch/%s' % pack
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
    os.system("rm patch/%s ; cd %s ; zip -n .mp4 -r %s %s ; mv %s .." 
        % (patch_name, patch_dir, patch_name, app_package, patch_name))

build_patch('burundi', 'burundi.main.2.obb', 'burundi.main.4.obb', 'burundi.patch.4.obb')
build_patch('learning_guide', 'learning_guide.main.1.obb', 'learning_guide.main.2.obb', 'learning_guide.patch.2.obb')
build_patch('default', 'main.1031.org.storymaker.app.obb', 'main.1044.org.storymaker.app.obb', 'patch.1044.org.storymaker.app.obb')
