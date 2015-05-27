#!/usr/bin/env python

import sys
import os
import yaml
import json
import glob
#stream = open("test.yaml", 'r')
#stream = open("lesson_test.yaml", 'r')

#infile = ""

#if len(sys.argv) <= 1:
#    sys.exit("you need to tell me what file to parse...")
#infile = sys.argv[1]
#stream = open(infile, 'r')

cardcounts = {}

def get_count(key):
    if not cardcounts.has_key(key):
        cardcounts[key] = 0
    ret = cardcounts[key]
    cardcounts[key] = cardcounts[key] + 1
    return ret

def set_id(key, card):
    if not card.has_key('id'):
        card['id'] = "%s_%s" % (key, get_count(key))

# TODO export directly to the real assets/org.storymaker.app/ folder
# TODO warn that fields existed in card but not card

def parse_file(in_file_name, json_out_file_name, strings_out_file_name):
    stream = open(in_file_name, 'r')
    doc = yaml.load(stream)
    strings = {}
    global cardcounts
    cardcounts = {}
    if doc.has_key('cards'): # SPLS can have no cards
        for card in doc['cards']:
            print "card: %s" % card
            if card['type'] == 'MarkDownCard': # FIXME this should deal with MarkdownCard capitalization too
                card['type'] = 'MarkdownCard'
                set_id("markdown_card", card)
                if card.has_key('body'):
                    card['text'] = card['body'] # FIXME this should also take a 'text' prop
                    del card['body']
                
                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

            elif card['type'] == 'IntroCard':
                set_id("intro_card", card)

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::headline" % card_fqid] = card['headline']
                strings["%s::level" % card_fqid] = card['level']
                
            elif card['type'] == 'QuizCard':
                set_id("quiz_card", card)
                
                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::question" % card_fqid] = card['question']

                for choice in card['choices']:
                    choice_key = "%s::choices" % card_fqid
                    strings["%s[%s]::text" % (choice_key, get_count(choice_key))] = choice['text']

            elif card['type'] == 'ClipCard':
                set_id("clip_card", card)
                
                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                for choice in card['goals']:
                    choice_key = "%s::goals" % card_fqid
                    strings["%s[%s]" % (choice_key, get_count(choice_key))] = choice

            elif card['type'] == 'ReviewCard':
                set_id("review_card", card)
                
                #no translatable strings

            elif card['type'] == 'EvaluationCard':
                card['type'] = 'BasicTextCard' # FIXME 
                set_id("evaluation_card", card)

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

            elif card['type'] == 'SelfEvalCard':
                set_id("selfeval_card", card)
                card['text'] = card['header'] # FIXME
                del card['header']

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

            elif card['type'] == 'HowToCard':
                set_id("howto_card", card)

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

            elif card['type'] == 'MilestoneCard':
                card['type'] = 'ButtonCard' # FIXME proably closer to EvaluationCard?
                set_id("milestone_card", card)
                #card['header'] = card['header']
                #card['icon'] = card['icon']

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']
                strings["%s::header" % card_fqid] = card['header']
                
            elif card['type'] == 'PublishCard':
                card['type'] = 'PublishButtonCard'
                card['id'] = 'publish_card_1'
                card['medium'] = card['medium']
                
                #no translatable strings

            elif card['type'] == 'NextUpCard':
                doc['cards'].remove(card)
                #card['type'] = 'MilestoneCard' # FIXME wtf is this?  it has no text or links
                #medium == audio 
                #card['text'] = "Next Up" # FIXME
                #set_id("nextup_card", card)
                #card['medium'] = card['medium']
                
                #no translatable strings

            elif card['type'] == 'TipCard':
                set_id("tip_card", card)
                
                #no translatable strings

            elif card['type'] == 'LinkCard':
                set_id("link_card", card)
                
                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

            elif card['type'] == 'TipCollectionHeadlessCard':
                set_id("tip_collection_card", card)
                
                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])

                for tip in card['tips']:
                    tip_key = "%s::tips" % card_fqid
                    strings["%s[%s]::text" % (tip_key, get_count(tip_key))] = tip['text']

            ### the below cards have all been renamed

            elif card['type'] == 'PreviewCard' or card['type'] == 'ExampleCard':
                set_id("preview_card", card)
                card['type'] = 'ExampleCard'
                card['header'] = card['title'] # FIXME
                del card['title']
                card['clipType'] = 'character'   # FIXME not needed at all? remove from our code
                card['exampleMediaPath'] = card['media'][0]['media'] # for now we only grab the first media
                
                if "medium" not in card:
                    print "PreviewCard missing medium: %s" % card
                    sys.exit()

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::header" % card_fqid] = card['header']

            elif card['type'] == 'TextCard' or card['type'] == 'BasicTextCard':
                set_id("text_card", card)
                card['type'] = 'BasicTextCard'

                #strings
                card_fqid = "%s::%s" % (doc['id'], card['id'])
                strings["%s::text" % card_fqid] = card['text']

    doc['classPackage'] = 'scal.io.liger.model'
    strings['%s::title' % doc['id']] = doc['title']

    try:
        os.makedirs(json_dir)
    except: pass
    
    j = json.dumps(doc, indent=4)
    json_outfile = open(json_out_file_name, 'w')
    json_outfile.write(j)
    json_outfile.close()

    # TODO save strings
    #for k,v in strings.iteritems():
    #    print "%s %s" % (k,v)
    
    # y = yaml.dump(strings)
    # strings_outfile = open(strings_out_file_name, 'w')
    # strings_outfile.write(y)
    # strings_outfile.close()

    try:
        os.makedirs(strings_dir)
    except: pass
    strings_json = json.dumps(strings, indent=2)
    strings_outfile = open(strings_out_file_name, 'w')
    strings_outfile.write(strings_json)
    strings_outfile.close()



def do_dir():
    for f in os.listdir(yaml_dir):
        #print name
        cardcounts = {}
        file_name, file_extension = os.path.splitext(f)
        if file_extension == ".yaml":
            print "parsing %s" % f
            in_file = yaml_dir + "/" + f
            json_out_file = "%s/%s.json" % (json_dir, file_name)
            strings_out_file = "%s/%s.json" % (strings_dir, file_name)
            parse_file(in_file, json_out_file, strings_out_file)

# FIXME global vars are the best!!

def generate_content_index_record(library_dir, package, content_pack, library, instance, lang=None):
    rec = {}
    instance_id = instance.split('_library')[0]

    # first try to use the translated file, if it doesnt exist, fallback on 'en'
    file_path = '%s/intermediates/translated_strings/%s/%s/%s/%s-%s.json' % (os.getcwd(), package, content_pack, library, instance, lang)
    if not os.path.isfile(file_path):
        file_path = '%s/%s.json' % (library_dir, instance)
    print "file_path: " + file_path
    f = open(file_path, 'r')
    file_json = json.load(f)
    
    rec['instanceFilePath'] = "%s/%s/%s/%s.json" % (package, content_pack, library, instance)
    if lang is None:
        rec['language'] = 'en'
    else:
        rec['language'] = lang
    rec['title'] = file_json['%s::title' % (instance_id)]
    covers = glob.glob("assets/%s/%s/%s/cover.*" % (package, content_pack, library))
    print covers
    if len(covers) > 0:
        print "library has it's own cover: %s" % covers[0]
        rec['thumbnailPath'] = covers[0].split("assets/")[1]
    else:    
        covers = glob.glob("assets/%s/%s/cover.*" % (package, content_pack))
        print "using content pack cover for library: %s" % covers[0]
        rec['thumbnailPath'] = covers[0].split("assets/")[1]
    return rec

    
def generate_content_index(package, content_pack, lang=None):
    print "prepping content index"
    lang_postfix = ""
    if lang is not None:
        lang_postfix = "-%s" % lang
    cardcounts = {}
    content_index = []
    content_pack_strings_dir = os.getcwd() + "/intermediates/strings/%s/%s" % (package, content_pack)
    lst = sorted(os.listdir(content_pack_strings_dir))
    for library in lst:
        library_dir = "%s/%s" % (content_pack_strings_dir, library)
        if os.path.isdir(library_dir):
            print library_dir
            #json_dir = os.getcwd() + "/assets/%s/%s/%s" % (package, content_pack, library)
            #strings_dir = os.getcwd() + "/intermediates/strings/%s/%s/%s" % (package, content_pack, library)
            
            for f in os.listdir(library_dir):
                #print "    %s" % f
                cardcounts = {}
                file_name, file_extension = os.path.splitext(f)
                if file_extension == ".json" and "_library" in file_name:
                    #print "      ...is library"
                    rec = generate_content_index_record(library_dir, package, content_pack, library, file_name, lang)
                    print rec
                    content_index.append(rec)

    content_index_file = open("assets/%s/%s/content_index%s.json" % (package, content_pack, lang_postfix), 'w')
    content_index_file.write(json.dumps(content_index, indent=2))
    content_index_file.close()

import os
import shutil
import stat
def mergetree(src, dst, symlinks = False, ignore = None):
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            mergetree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


#############################3
"""
print "generating content for lessons"
cardcounts = {}
content_index = []
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/lessons"
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/lessons/%s" % f
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/lessons/%s" % f
    do_dir()

print "generating content for default library"
cardcounts = {}
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/default"
json_dir = os.getcwd() + "/assets/org.storymaker.app/default"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/default"
do_dir()

print "generating content for learning guide 1"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_1"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_1"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_1"
do_dir()

print "generating content for learning guide 2"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_2"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_2"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_2"
do_dir()

print "generating content for learning guide 3"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_3"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_3"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_3"
do_dir()
"""

"""
print "generating content for IJF"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/ijf15/ijf15"
json_dir = os.getcwd() + "/assets/org.storymaker.app/ijf15/ijf15"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/ijf15"
do_dir()
"""

"""
print "generating content for DressGate"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/dressgate"
json_dir = os.getcwd() + "/assets/org.storymaker.app/dressgate"
strings_dir = os.getcwd() + "/intermediates/org.storymaker.app/dressgate"
do_dir()
"""

print "generating content for beta paths"
pack_dir = "beta_paths"
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/" + pack_dir
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/%s/%s" % (pack_dir, f)
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/%s/%s" % (pack_dir, f)
    do_dir()



#########################################
print "prepping lesson asset folder..."

package = 'org.storymaker.app'

def prep_lesson_pack(content_pack, lang=None):
    # TODO delete the old assets for this pack
    dir1 = "%s/assets/%s/%s/" % (os.getcwd(), package, content_pack)
    shutil.rmtree(dir1, ignore_errors=True)
    print "copying assets for index for %s/%s" % (package, content_pack)
    dir2 = "%s/assets/%s/lessons-media/%s" % (os.getcwd(), package, content_pack)
    dir3 = "%s/assets/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.copytree(dir2, dir3)
    # intermediates/strings/org.storymaker.app/persian
    dir4 = "%s/intermediates/strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.rmtree(dir4, ignore_errors=True)
    dir5 = "%s/intermediates/strings/%s/lessons" % (os.getcwd(), package)
    dir6 = "%s/intermediates/strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.copytree(dir5, dir6)
    dir7 = "%s/intermediates/translated_strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.rmtree(dir7, ignore_errors=True)
    dir8 = "%s/intermediates/translated_strings/%s/lessons" % (os.getcwd(), package)
    dir9 = "%s/intermediates/translated_strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.copytree(dir8, dir9)

    # TODO copy / merge the json on top of the assets folder
    mergetree("%s/assets/%s/lessons/" % (os.getcwd(), package),
                    "%s/assets/%s/%s" % (os.getcwd(), package, content_pack))
    # TODO copy / merge the json on top of the assets folder
    print "generating content index for %s/%s" % (package, content_pack)
    generate_content_index(package, content_pack)
    generate_content_index(package, content_pack, 'ar')
    generate_content_index(package, content_pack, 'fa')
    generate_content_index(package, content_pack, 'fr')
    generate_content_index(package, content_pack, 'rw')
    generate_content_index(package, content_pack, 'vi')
    
    content_metadata_file = open("assets/%s/%s/content_metadata.json" % (package, content_pack), 'w')
    cover_file = "%s/%s/cover.jpg" % (package, content_pack)
    if not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.png" % (package, content_pack)
    elif not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.gif" % (package, content_pack)
    elif not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.jpeg" % (package, content_pack)
            
    content_metadata = { "contentPackThumbnailPath": cover_file } # TODO we might want other file types
    content_metadata_file.write(json.dumps(content_metadata, indent=2))
    content_metadata_file.close()

#prep_lesson_pack('persian')
##prep_lesson_pack('mena')
#prep_lesson_pack('burundi')
