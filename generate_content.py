#!/usr/bin/env python

"""
This set of content scripts done a bunch of stuff, a bit confusingly, but it with a bit of love and cleanup should be super helpful to manage i18n projects.

At its core there is a yaml/ directory structure which defines the input yaml files.

parse_file does some fixing of badly formatted yaml files, but mainly it rips out all string fields and created unique keys pointing at the node in the yaml heirachy and stuffs tehm into a flattened k/v json file in intermediates/strings/.  These files are nicely handled by translation sites like Transifex.

Once transifex does its thing, it creates language specific versions of these flat strings files in intermediates/translated_strings/

Next our script grabs the generated .json file and the translated strings file and swaps in the translated values by traversing the json with the keys on the translatd strings files, something like xpath.  These translated files are created alongside the originals in assets/

In addition, some content packs have localized media.  This is accomplished by having separate locale specific media assets folders in a subdirectory in assets called {{content_pack}}-media.  prep_localized_pack creates paralele copies of the translated json files for each locale and merges in the localized media, creating top level content packs for each localization with identical json files but localized media.

then we generate indexes for the zip files

"""

import sys
import os
import yaml
import json
import glob
import click

# setup cli
@click.group()
def cli():
    pass
    
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

def parse_file(in_file_name, json_out_file_name, strings_out_file_name, json_dir, strings_dir):
    stream = open(in_file_name, 'r')
    doc = yaml.load(stream)
    strings = {}
    global cardcounts
    cardcounts = {}
    if doc.has_key('cards'): # SPLS can have no cards
        for card in doc['cards']:
            #print "card: %s" % card
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
    except: 
        pass
    
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
    except: 
        pass
        
    strings_json = json.dumps(strings, indent=2)
    strings_outfile = open(strings_out_file_name, 'w')
    strings_outfile.write(strings_json)
    strings_outfile.close()

# helper than deals with race condition in checking if dir exists
# from http://stackoverflow.com/a/14364249/41694
def mkdirs(dir):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def do_dir(yaml_dir, json_dir, strings_dir):
    for f in os.listdir(yaml_dir):
        cardcounts = {}
        file_name, file_extension = os.path.splitext(f)
        if file_extension == ".yaml":
            print "parsing %s" % f
            in_file = yaml_dir + "/" + f
            json_out_file = "%s/%s.json" % (json_dir, file_name)
            strings_out_file = "%s/%s.json" % (strings_dir, file_name)
            parse_file(in_file, json_out_file, strings_out_file, json_dir, strings_dir)

def generate_content_index_record(library_dir, package, content_pack, library, file_name, lang=None):
    rec = {}
    #id = instance.split('_library')[0]
    #id = file_name #fixme we shoulf fetch this from the id: field not infer from the filename

    # first try to use the translated file, if it doesnt exist, fallback on 'en'
    file_path = '%s/intermediates/translated_strings/%s/%s/%s/%s-%s.json' % (os.getcwd(), package, content_pack, library, file_name, lang)
    if not os.path.isfile(file_path):
        file_path = '%s/%s.json' % (library_dir, file_name)
    print "file_path: " + file_path
    f = open(file_path, 'r')
    file_json = json.load(f)
    
    rec['instanceFilePath'] = "%s/%s/%s/%s.json" % (package, content_pack, library, file_name)
    if lang is None:
        rec['language'] = 'en'
    else:
        rec['language'] = lang
    rec['title'] = next(v for k, v in file_json.items() if k.endswith('::title'))
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
    content_index = []
    content_pack_strings_dir = os.getcwd() + "/intermediates/strings/%s/%s" % (package, content_pack)
    lst = sorted(os.listdir(content_pack_strings_dir))
    for library in lst:
        library_dir = "%s/%s" % (content_pack_strings_dir, library)
        if os.path.isdir(library_dir):
            print library_dir

            for f in os.listdir(library_dir):
                file_name, file_extension = os.path.splitext(f)
                if file_extension == ".json" and "_library" in file_name:
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

package = 'org.storymaker.app'

#############################

"""
print "generating content for default library"
cardcounts = {}
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/default"
json_dir = os.getcwd() + "/assets/org.storymaker.app/default"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/default"
do_dir(yaml_dir, json_dir, strings_dir)

print "generating content for learning guide 1"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_1"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_1"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_1"
do_dir(yaml_dir, json_dir, strings_dir)

print "generating content for learning guide 2"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_2"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_2"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_2"
do_dir(yaml_dir, json_dir, strings_dir)

print "generating content for learning guide 3"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/learning_guide/learning_guide_3"
json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_3"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/learning_guide/learning_guide_3"
do_dir(yaml_dir, json_dir, strings_dir)
"""

"""
print "generating content for IJF"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/ijf15/ijf15"
json_dir = os.getcwd() + "/assets/org.storymaker.app/ijf15/ijf15"
strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/ijf15"
do_dir(yaml_dir, json_dir, strings_dir)
"""

"""
print "generating content for DressGate"
yaml_dir = os.getcwd() + "/yaml/org.storymaker.app/dressgate"
json_dir = os.getcwd() + "/assets/org.storymaker.app/dressgate"
strings_dir = os.getcwd() + "/intermediates/org.storymaker.app/dressgate"
do_dir(yaml_dir, json_dir, strings_dir)
"""

"""
print "generating content for beta paths"
pack_dir = "beta"
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/" + pack_dir
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/%s/%s" % (pack_dir, f)
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/%s/%s" % (pack_dir, f)
    do_dir(yaml_dir, json_dir, strings_dir)
generate_content_index(package, pack_dir)
generate_content_index(package, pack_dir, 'ar')
generate_content_index(package, pack_dir, 'es')
generate_content_index(package, pack_dir, 'fa')
#"""

"""
print "generating content for mobile_photo_basics"
pack_dir = "mobile_photo_basics"
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/" + pack_dir
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/%s/%s" % (pack_dir, f)
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/%s/%s" % (pack_dir, f)
    do_dir(yaml_dir, json_dir, strings_dir)
generate_content_index(package, pack_dir)
generate_content_index(package, pack_dir, 'ar')
generate_content_index(package, pack_dir, 'es')
generate_content_index(package, pack_dir, 'fa')
#"""

"""
print "generating content for citizen_journalism_pack"
pack_dir = "citizen_journalism_pack"
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/" + pack_dir
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/%s/%s" % (pack_dir, f)
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/%s/%s" % (pack_dir, f)
    do_dir(yaml_dir, json_dir, strings_dir)
generate_content_index(package, pack_dir)
generate_content_index(package, pack_dir, 'ar')
generate_content_index(package, pack_dir, 'es')
#"""

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
    do_dir(yaml_dir, json_dir, strings_dir)
#"""


"""
print "generating content for journalism_part_1"
cardcounts = {}
content_index = []
yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/journalism_part_1"
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    print yaml_dir
    json_dir = os.getcwd() + "/assets/org.storymaker.app/journalism_part_1/%s" % f
    strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/journalism_part_1/%s" % f
    do_dir(yaml_dir, json_dir, strings_dir)
#"""



#########################################

# TODO mkdir the dirs you need as they wont exist on clean checkout

def generate_translations_for_file(original_json_file_path, translated_strings_file_path, out_file_path):
    in_stream = open(original_json_file_path, 'r')
    doc = json.load(in_stream)

    strings_stream = open(translated_strings_file_path, 'r')
    strings = json.load(strings_stream)


    for k,v in strings.iteritems():
        splits = k.split('::')
        path_id = splits[0]

        # get the doc level properites (of course this will badly break if the doc has array or dict props and is hence more than 2 deep
        if len(splits) == 2:
            key_id = splits[1]
            doc[key_id] = v # in this case its a doc level prop, not a path_id
            continue

        # check we are in teh right file by checking the pathid
        if not doc['id'] == path_id:
            print "!! key in translation file '%s' doesn't match this path's id: '%s'" % (splits[0], doc['id'])
            exit(-1)

        card_id = splits[1]
        prop_key = splits[2]


        for card in doc['cards']:
            if card['id'] == card_id:
                if len(splits) == 3:
                    key_splits = prop_key.split('[')
                    if len(key_splits) == 1:
                        key = key_splits[0]
                        # of form  "event_discussion_audio_question1::evaluation_card_0::text"
                        print "at %s, replacing '%s' with '%s'" % (k, card[key], v)
                        card[key] = v
                    elif len(key_splits) == 2:
                        # of form "event_discussion_audio_question1::clip_card_5::goals[0]"
                        key = key_splits[0]
                        array_index = int(key_splits[1].split(']')[0]) # FIXME skip this step by initially splitting on [ | ] in a regex
                        print "at %s, replacing '%s' with '%s'" % (k, card[key][array_index], v)
                        card[key][array_index] = v
                        # index into an array (or dict?)
                elif len(splits) == 4:
                    key_splits = prop_key.split('[')
                    if len(key_splits) == 1:
                        key = key_splits[0]
                        # of form  "event_discussion_audio_question1::evaluation_card_0::text"
                        print "at %s, replacing '%s' with '%s'" % (k, card[key], v)
                        card[key] = v
                    elif len(key_splits) == 2:
                        # of form "default_library::tip_collection::tips[0]::text"
                        key = key_splits[0]
                        array_index = int(key_splits[1].split(']')[0]) # FIXME skip this step by initially splitting on [ | ] in a regex
                        real_prop_key = splits[3]
                        print u"at {0}".format(k)
                        print u"    replacing '{0}' with '{1}'".format(card[key][array_index][real_prop_key], v)
                        card[key][array_index][real_prop_key] = v
                        # index into an array (or dict?)
                else:
                    print "\n\n\ncard\n%s\n\n\n" % card
                    print "!! deeper nesting we need to handle in %s:\n\n\ncard\n%s\n\n\n" % (original_json_file_path, card)
                    exit(-1)
                    pass # TODO there are some deeper nestings we need to watch out for
                break

    json_string = json.dumps(doc, indent=4)
    out_file = open(out_file_path, 'w')
    out_file.write(json_string)
    out_file.close()


def gen_translations(json_dir, translations_dir):
    for translated_strings_file_name in os.listdir(translations_dir):
        file_name, file_extension = os.path.splitext(translated_strings_file_name)
        print "translations_dir: " + translations_dir
        print "translated_strings_file_name: " + translated_strings_file_name + " file_name: " + file_name
        (json_file_name, lang) = file_name.split('-')
        translated_json_file_name = "%s-%s.json" % (json_file_name, lang)
        out_file_path = "%s/%s" % (json_dir, translated_json_file_name)
        original_json_file_path = "%s/%s.json" % (json_dir, json_file_name)
        translated_strings_file_path = "%s/%s" % (translations_dir, translated_strings_file_name)

        print "inserting localized strings into %s" % out_file_path

        # strings_file_name = "%s/%s.json" % (translations_dir, file_name)
        generate_translations_for_file(original_json_file_path, translated_strings_file_path, out_file_path)

"""
print "generating content for lessons"
parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/lessons/"
for f in os.listdir(parent_dir):
    json_dir = os.getcwd() + "/assets/org.storymaker.app/lessons/%s" % f
    translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/lessons/%s" % f
    gen_translations(json_dir, translations_dir)
#"""

"""
print "generating content for beta pack"
parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/beta/"
for f in os.listdir(parent_dir):
    json_dir = os.getcwd() + "/assets/org.storymaker.app/beta/%s" % f
    translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/beta/%s" % f
    gen_translations(json_dir, translations_dir)
#"""

"""
print "generating content for mobile_photo_basics pack"
parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/mobile_photo_101/"
for f in os.listdir(parent_dir):
    json_dir = os.getcwd() + "/assets/org.storymaker.app/mobile_photo_101/%s" % f
    translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/mobile_photo_101/%s" % f
    gen_translations(json_dir, translations_dir)
#"""

"""
# FIXME make sure there's no translations present or we are going to double translate them, maybe go into a loop
json_dir = os.getcwd() + "/assets/org.storymaker.app/default"
translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/default"
gen_translations(json_dir, translations_dir)

json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_1"
translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/learning_guide/learning_guide_1"
gen_translations(json_dir, translations_dir)

json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_2"
translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/learning_guide/learning_guide_2"
gen_translations(json_dir, translations_dir)

json_dir = os.getcwd() + "/assets/org.storymaker.app/learning_guide/learning_guide_3"
translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/learning_guide/learning_guide_3"
gen_translations(json_dir, translations_dir)
#"""

"""
print "generating content for lessons"
parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/lessons/"
for f in os.listdir(parent_dir):
    json_dir = os.getcwd() + "/assets/org.storymaker.app/lessons/%s" % f
    translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/lessons/%s" % f
    gen_translations(json_dir, translations_dir)
#"""

"""
print "generating content for journalism_part_1"
parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/journalism_part_1/"
for f in os.listdir(parent_dir):
    json_dir = os.getcwd() + "/assets/org.storymaker.app/journalism_part_1/%s" % f
    translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/journalism_part_1/%s" % f
    gen_translations(json_dir, translations_dir)
#"""

def generate_translated_assets(name):
    print "generating content for {0} pack".format(name)
    parent_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/{0}/".format(name)
    for f in os.listdir(parent_dir):
        json_dir = os.getcwd() + "/assets/org.storymaker.app/{0}/{1}".format(name, f)
        translations_dir = os.getcwd() + "/intermediates/translated_strings/org.storymaker.app/{0}/{1}".format(name, f)
        gen_translations(json_dir, translations_dir)



#########################################
print "prepping lesson asset folders..."


content_packs = []

def gen_regular_pack(pack_name):
    print("generating content for {0}".format(pack_name))
    yaml_parent_dir = os.getcwd() + "/yaml/org.storymaker.app/" + pack_name
    for f in os.listdir(yaml_parent_dir):
        yaml_dir = "%s/%s" % (yaml_parent_dir, f)
        print yaml_dir
        json_dir = os.getcwd() + "/assets/org.storymaker.app/%s/%s" % (pack_name, f)
        strings_dir = os.getcwd() + "/intermediates/strings/org.storymaker.app/%s/%s" % (pack_name, f)
        do_dir(yaml_dir, json_dir, strings_dir)

    content_packs.append(pack_name)

def gen_regular_pack_and_content_indexes(pack_name):
    gen_regular_pack(pack_name)
    generate_content_indexes(pack_name)
    create_content_metadata(pack_name)

def generate_content_indexes(pack_name):
    generate_content_index(package, pack_name)
    generate_content_index(package, pack_name, 'ar')
    generate_content_index(package, pack_name, 'es')
    generate_content_index(package, pack_name, 'fa')
    generate_content_index(package, pack_name, 'fr')
    generate_content_index(package, pack_name, 'rw')
    generate_content_index(package, pack_name, 'vi')

# locale is buruni, mena or persian
# content_pack is audio, journalism_part_1, etc
# lang is the two letter lang code
#
# this method takes the input assets and copies them to each localized assets clone folder in preparation to be zipped later
def prep_localized_pack(content_pack, locale, lang=None):
    # create the json files for the base content pack before we make the localized copies
    gen_regular_pack(content_pack)

    # e.g. journalism_pack_1-burundi
    full_pack_name = "%s-%s" % (content_pack, locale)

    # TODO delete the old assets for this pack
    dir_final_assets = "%s/assets/%s/%s/" % (os.getcwd(), package, full_pack_name)
    print "purging any old generated assets for this pack: %s" % dir_final_assets
    shutil.rmtree(dir_final_assets, ignore_errors=True)

    print "copying assets for index for %s/%s" % (package, content_pack)
    dir_localized_media = "%s/assets/%s/%s-media/%s" % (os.getcwd(), package, content_pack, locale)
    print("    dir_localized_media: {0}".format(dir_localized_media))
    print("    dir_final_assets: {0}".format(dir_final_assets))
    shutil.copytree(dir_localized_media, dir_final_assets)

    # purge the old generated strings clone folder
    # intermediates/strings/org.storymaker.app/persian
    dir_localized_intermediate_strings = "%s/intermediates/strings/%s/%s" % (os.getcwd(), package, full_pack_name)
    shutil.rmtree(dir_localized_intermediate_strings, ignore_errors=True)

    # now copy the translated strings into the localized path
    dir_intermediate_strings = "%s/intermediates/strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.copytree(dir_intermediate_strings, dir_localized_intermediate_strings)

    # purge the translated_strings clone folder
    dir_localized_intermediate_translated_strings = "%s/intermediates/translated_strings/%s/%s" % (os.getcwd(), package, full_pack_name)
    shutil.rmtree(dir_localized_intermediate_translated_strings, ignore_errors=True)

    dir_localized_intermediate_strings = "%s/intermediates/translated_strings/%s/%s" % (os.getcwd(), package, content_pack)
    shutil.copytree(dir_localized_intermediate_strings, dir_localized_intermediate_translated_strings)


    # TODO copy / merge the json on top of the assets folder
    d1 = "%s/assets/%s/%s/" % (os.getcwd(), package, content_pack)
    # dir_final_assets = d2 = "%s/assets/%s/%s" % (os.getcwd(), package, full_pack_name)
    mergetree(d1, dir_final_assets)

    generate_content_indexes(full_pack_name)

    create_content_metadata(full_pack_name)

    content_packs.append(full_pack_name)

def create_content_metadata(pack_id):
    content_metadata_file = open("assets/%s/%s/content_metadata.json" % (package, pack_id), 'w')
    cover_file = "%s/%s/cover.jpg" % (package, pack_id)
    if not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.png" % (package, pack_id)
    elif not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.gif" % (package, pack_id)
    elif not os.path.isfile("assets/%s" % cover_file):
        cover_file = "%s/%s/cover.jpeg" % (package, pack_id)

    content_metadata = { "contentPackThumbnailPath": cover_file } # TODO we might want other file types
    content_metadata_file.write(json.dumps(content_metadata, indent=2))
    content_metadata_file.close()


# create available index
def create_available_index():
    for s in content_packs:
        print("adding {0} to available_index".format(s))

@cli.command()
@click.argument("name")
def generate_regular_pack(name):
    gen_regular_pack_and_content_indexes(name)

@cli.command()
@click.argument("name")
@click.argument("locale")
def generate_localized_pack(name, locale):
    prep_localized_pack(name, locale)

@cli.command()
def all_content():
    ### generate localized packs
    prep_localized_pack('audio', 'persian')
    prep_localized_pack('audio', 'mena')
    prep_localized_pack('audio', 'burundi')
    prep_localized_pack('story', 'persian')
    prep_localized_pack('story', 'mena')
    prep_localized_pack('story', 'burundi')
    #prep_localized_pack('lessons', 'persian')
    #prep_localized_pack('lessons', 'mena')
    #prep_localized_pack('lessons', 'burundi')
    prep_localized_pack('video_1', 'persian')
    prep_localized_pack('video_1', 'mena')
    prep_localized_pack('video_1', 'burundi')
    prep_localized_pack('video_2', 'persian')
    prep_localized_pack('video_2', 'mena')
    prep_localized_pack('video_2', 'burundi')
    prep_localized_pack('security', 'persian')
    prep_localized_pack('security', 'mena')
    prep_localized_pack('security', 'burundi')
    prep_localized_pack('photography_1', 'persian')
    prep_localized_pack('photography_1', 'mena')
    prep_localized_pack('photography_1', 'burundi')
    prep_localized_pack('photography_2', 'persian')
    prep_localized_pack('photography_2', 'mena')
    prep_localized_pack('photography_2', 'burundi')
    prep_localized_pack('journalism_part_1', 'persian')
    prep_localized_pack('journalism_part_1', 'mena')
    prep_localized_pack('journalism_part_1', 'burundi')
    prep_localized_pack('journalism_part_2', 'persian')
    prep_localized_pack('journalism_part_2', 'mena')
    prep_localized_pack('journalism_part_2', 'burundi')


    #### generate regular packs

    gen_regular_pack_and_content_indexes("mobile_photo_basics")
    gen_regular_pack_and_content_indexes("default")
    gen_regular_pack_and_content_indexes("learning_guide")
    gen_regular_pack_and_content_indexes("t_citizen_journalist")
    gen_regular_pack_and_content_indexes("g_odvw")
    gen_regular_pack_and_content_indexes("g_welcome")
    gen_regular_pack_and_content_indexes("t_audio")
    gen_regular_pack_and_content_indexes("t_process")
    gen_regular_pack_and_content_indexes("t_video")
    gen_regular_pack_and_content_indexes("t_photo")
    gen_regular_pack_and_content_indexes("t_news")

    generate_translated_assets("mobile_photo_basics")
    #generate_translated_assets("default")
    #generate_translated_assets("learning_guide")
    generate_translated_assets("t_citizen_journalist")
    generate_translated_assets("g_odvw")
    generate_translated_assets("g_welcome")
    generate_translated_assets("t_audio")
    generate_translated_assets("t_process")
    generate_translated_assets("t_video")
    generate_translated_assets("t_photo")
    generate_translated_assets("t_news")

    # TODO translations for localized packs
    # audio
    # story
    # lessons
    # video_1
    # video_2
    # security
    # photography_1
    # photography_2
    # journalism_part_1
    # journalism_part_2

    create_available_index()
    
cli.add_command(all_content)

if __name__ == "__main__":
    cli()
