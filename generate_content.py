#!/usr/bin/env python

import sys
import os
import yaml
import json
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

# TODO export directly to the real assets/ folder
# TODO warn that fields existed in card but not card

def parse_file(in_filename, json_out_filename, strings_out_filename):
    stream = open(in_filename, 'r')
    doc = yaml.load(stream)
    strings = {}
    global cardcounts
    cardcounts = {}
    if doc.has_key('cards'): # SPLS can have no cards
        for card in doc['cards']:
            #print "card: %s" % card
            if card['type'] == 'MarkDownCard':
                card['type'] = 'MarkdownCard'
                set_id("markdown_card", card)
                card['text'] = card['body']
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
    json_outfile = open(json_out_filename, 'w')
    json_outfile.write(j)
    json_outfile.close()

    # TODO save strings
    #for k,v in strings.iteritems():
    #    print "%s %s" % (k,v)
    
    # y = yaml.dump(strings)
    # strings_outfile = open(strings_out_filename, 'w')
    # strings_outfile.write(y)
    # strings_outfile.close()

    try:
        os.makedirs(strings_dir)
    except: pass
    strings_json = json.dumps(strings, indent=2)
    strings_outfile = open(strings_out_filename, 'w')
    strings_outfile.write(strings_json)
    strings_outfile.close()



def do_dir():
    for f in os.listdir(yaml_dir):
        #print name
        cardcounts = {}
        fileName, fileExtension = os.path.splitext(f)
        if fileExtension == ".yaml":
            print "parsing %s" % f
            in_file = yaml_dir + "/" + f
            json_out_file = "%s/%s.json" % (json_dir, fileName)
            strings_out_file = "%s/%s.json" % (strings_dir, fileName)
            parse_file(in_file, json_out_file, strings_out_file)

# FIXME global vars are the best!!



print "generating content for lessons"
cardcounts = {}
yaml_parent_dir = os.getcwd() + "/yaml/lessons/burundi"
for f in os.listdir(yaml_parent_dir):
    yaml_dir = "%s/%s" % (yaml_parent_dir, f)
    json_dir = os.getcwd() + "/assets/lessons/burundi/%s" % f
    strings_dir = os.getcwd() + "/intermediates/strings/lessons/burundi/%s" % f
    do_dir()

print "generating content for default library"
cardcounts = {}
yaml_dir = os.getcwd() + "/yaml/default/default_library"
json_dir = os.getcwd() + "/assets/default/default_library"
strings_dir = os.getcwd() + "/intermediates/strings/default/default_library"
do_dir()

print "generating content for learning guide 1"
yaml_dir = os.getcwd() + "/yaml/default/learning_guide_1"
json_dir = os.getcwd() + "/assets/default/learning_guide_1"
strings_dir = os.getcwd() + "/intermediates/strings/default/learning_guide_1"
do_dir()

print "generating content for learning guide 2"
yaml_dir = os.getcwd() + "/yaml/default/learning_guide_2"
json_dir = os.getcwd() + "/assets/default/learning_guide_2"
strings_dir = os.getcwd() + "/intermediates/strings/default/learning_guide_2"
do_dir()

print "generating content for learning guide 3"
yaml_dir = os.getcwd() + "/yaml/default/learning_guide_3"
json_dir = os.getcwd() + "/assets/default/learning_guide_3"
strings_dir = os.getcwd() + "/intermediates/strings/default/learning_guide_3"
do_dir()

