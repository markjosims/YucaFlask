#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 14:19:50 2020

Library of helper methods to read data from various LIFT xml tags
and return in format of dictionaries

@author: mark
"""

def read_entry(elem):
    out = {}
    for tag, funct in tags.items():
        data = funct(elem)
        if data:
            out[tag] = data
    return out

# <lexical-unit> tag contains the headword datum
def read_lex_unit(elem):
    lex_unit = elem.findall('lexical-unit')
    # should only be one lexical unit per entry
    if not lex_unit:
        return
    elif len(lex_unit) > 1:
        raise TypeError(f"{len(lex_unit)} lexical-unit tags found in entry"\
                        +f"{elem.get('id')}. Make sure LIFT file is"\
                        +"formatted correctly.")
    out = read_all_forms(lex_unit[0])
    # should only have one form (for analysis language)
    if len(out) != 1:
        raise TypeError(f"{len(out)}  one form tag found under lexical-unit"\
                        +f"for entry {elem.get('id')}. Make sure LIFT"\
                        +"file is formatted correctly.")
    # only return headword datum, not language code
    headword = out.popitem()[1]
    return headword

# <trait> tag in entry contains data related to morphological inflection
def read_morph_type(elem):
    trait = elem.findall('trait')
    if len(trait) > 1:
        raise TypeError("{len(trait)} than one trait tags found in entry"\
                        +f"{elem.get('id')}. Make sure LIFT file is"\
                        +"formatted correctly.")
    trait=trait[0]
    assert trait.get('name') == 'morph-type'
    return trait.get('value')

# <citation> tag contains citation form, if specified
# separate from headword form
def read_citation(elem):
    citation = elem.findall('lexical-unit')
    # should only be one lexical unit per entry
    if len(citation) > 1:
        raise TypeError("More or less than one lexical-unit tag found in entry"\
                        +f"{elem.get('id')}. Make sure LIFT file is"\
                        +"formatted correctly.")
    elif not citation:
        return
    out = read_all_forms(citation[0])
    # should only have one form (for analysis language)
    if len(out) > 1:
        raise TypeError("More or less than one form tag found under lexical-unit"\
                        +f"for entry {elem.get('id')}. Make sure LIFT"\
                        +"file is formatted correctly.")
    # only return citation form datum, not language code
    cit_form = out.popitem()[1]
    return cit_form

# <note> tag contains an optional type attr, and a form tag
# for the note's text
# returns dict where keys are note types (or placeholder)
# and valeus are note text
def read_note(elem):
    out = {}
    notes = elem.findall('note')
    i = None
    for n in notes:
        # generate key for this note
        if 'note' in n.attrib:
            note_type = n.get('note')
        elif i:
            note_type = f'undef_{i}'
        else:
            note_type = 'undef'
            i=1
        
        out[note_type] = read_all_forms(n)
    
    return out

# <variant> tag contains a <form> tag w/ text of an allomorph
def read_var(elem):
    form = elem.findall('form')
    if len(form) > 1:
        raise TypeError("More or less than one form tag found under variant"\
                            +f"for entry {elem.get('id')}. Make sure LIFT"\
                            +"file is formatted correctly.")
    # only return text from form tag
    if len(form) == 0:
        return
    return read_form(form[0])[1]
    
# <relation> tag contains attrs type, indicating the type of variant/relation
# and ref, indicating the id of the head
# inside are any number of <trait> tags w/ name & value attrs
# returns dict of the following structure:
# { ref_id : {
#               'type': type,
#               trait.name : trait.value,
#               ...
#            },
#   ref_id : {...
# }
def read_rel(elem):
    out = {}
    rels = elem.findall('relation')
    for r in rels:
        ref = r.get('ref')
        this_rel = {'type': r.get('type')}
        for tr in r.findall('trait'):
            this_rel[tr.get('name')] = tr.get('value')
        # optional field tag, type 'summary'
        field = r.find('field')
        if field:
            assert field.get('type') == 'summary'
            this_rel['summary'] = read_all_forms(field)
        out[ref] = this_rel
    return out

# <field> tags have an attr type and contain form tags w/ text
# returns dict w/ keys as types of field and values as text
# each tag contains
def read_field(elem):
    out = {}
    fields = elem.findall('field')
    for f in fields:
        # pay respects
        out[f.get('type')] = read_all_forms(f)
    return out

# <pronunciation> tags have a form child tag containing IPA text
# and optional <field> tags reflecting features such as tone
# string if no field tags, else tuple where second element is
# type of field tag w/ value
def read_pronunc(elem):
    pronunc = elem.findall('pronunciation')
    if len(pronunc) == 0:
        return
    assert len(pronunc) == 1, pronunc
    pronunc = pronunc[0]
    
    form = pronunc.findall('form')
    assert len(form) <= 1
    if form:
        out = read_form(form[0])[1]
    else:
        out = None
    
    field_data = {}
    fields = elem.findall('fields')
    for f in fields:
        field_data[f.get('type')] = read_all_forms(f)
    
    if field_data:
        return out, field_data
    else:
        return out
    
# finds all <sense> tags for an element
# <sense> tags have a complex structure, so call respective
# helper methods to read data into dictionary
# return dictionary of senses, where keys are id attr
# for each sense tag
def read_sense(elem):
    senses = []
    for sense in elem.findall('sense'):
        sense_id = sense.get('id')
        sense_data = {'sense_id':sense_id}
        for tag, funct in sense_tags.items():
            data = funct(sense)
            if data:
                sense_data[tag] = data
        senses.append(sense_data)
    return senses

# grammatical-info tag has attr value,
# and optional trait tags
# return value attr, and dict of trait info if present
def read_pos(sense):
    gram_info = sense.findall('grammatical-info')
    if len(gram_info) == 0:
        return
    assert len(gram_info) == 1
    gram_info = gram_info[0]
    out = gram_info.get('value')
    
    trait_data = {}
    traits = gram_info.findall('trait')
    for tr in traits:
        trait_data[tr.get('name')] = tr.get('value')
    if traits:
        return out, traits
    else:
        return out

# <gloss> tag has a lang attr and a <text> child tag containing
# the gloss tag
# returns a dict of gloss tags by language
def read_gloss(sense):
    out = {}
    glosses = sense.findall('gloss')
    for gl in glosses:
        text = gl.findall('text')
        assert len(text) == 1
        out[gl.get('lang')] = get_elem_text(text[0])
    return out

# <definition> tag contains various <form> tags
# see read_all_forms for return format
def read_definition(sense):
    defs = sense.findall('definition')
    if len(defs) == 0:
        return
    assert len(defs) == 1
    return read_all_forms(defs[0])

# <example> tag has attr source
# can have <form>, <translation> and <note> tags
def read_ex(sense):
    out={}
    examples = sense.findall('example')
    for ex in examples:
        form = ex.findall('form')
        if form:
            out['text'] = read_form(form[0])[1]
        translats = ex.findall('translation')
        for tra in translats:
            # does translation tag always have a type attr?
            out[tra.get('type')] = read_all_forms(tra)
        notes = ex.findall('note')
        for n in notes:
            out[n.get('type')] = read_all_forms(n)
    return out
        
# <reversal> tag has the same structure as the <definition> tag
def read_rev(sense):
    out={}
    revs = sense.findall('reversal')
    if len(revs) == 0:
        return
    for r in revs:
        form = r.findall('forms')
        if not form:
            continue
        assert len(form) == 1, form
        out[r.get('type')] = read_form(form[0])[1]
    return out

# <trait> tag has name and value attrs
def read_trait(sense):
    out = {}
    traits = sense.findall('trait')
    for tr in traits:
        out[tr.get('name')] = tr.get('value')
    return out

# reads all <form> tags under a given element
# returns a dictionary with the language for each form
# as keys, and the text of each form as values
def read_all_forms(elem):
    out = {}
    forms = elem.findall('form')
    for f in forms:
        lang, text = read_form(f)
        # assuming one form per lang per parent element
        assert lang not in out
        out[lang] = text
    return out
    
# gets lang attr from a form tag
# and reads all text from a text child elements
def read_form(form):
    lang = form.get('lang')
    text = form.findall('text')
    text = [get_elem_text(x) for x in text]
    text = text[0] if len(text) == 1 else text
    
    return lang, text

def get_elem_text(elem):
    out = elem.text if elem.text else ''
    for span in elem.findall('span'):
        if span.text:
            out += span.text
        if span.tail:
            out += span.tail
    return out
    
tags = {
        'lexical-unit': read_lex_unit,
        'trait': read_morph_type,
        'citation': read_citation,
        'note': read_note,
        'variant': read_var,
        'relation': read_rel,
        'field': read_field,
        'pronunciation': read_pronunc,
        'sense': read_sense
        }

sense_tags = {
        'grammatical-info': read_pos,
        'gloss': read_gloss,
        'definition': read_definition,
        'example': read_ex,
        'reversal': read_rev,
        'trait': read_trait,
        'field': read_field
        }