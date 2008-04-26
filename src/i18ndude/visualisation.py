IGNORE = frozenset(('zh', 'sr-Latn', ))

GROUP1 = [
    'fr', 'it', 'de', 'es', 'nl', 'zh-cn', 'zh-tw', 'ja', 'ko', 'pt-br',
    'ru', 'pl', 'tr', 'th', 'ar',
    ]

GROUP2 = [
    'sv', 'fi', 'da', 'pt', 'ro', 'hu', 'he', 'id', 'cs', 'el', 'no', 'vi',
    'bg', 'hr', 'lt', 'sk', 'tl', 'sl', 'sr', 'ca', 'lv', 'uk', 'hi',
    ]

def make_listing(pot, pos):
    from plone.i18n.locales.languages import LanguageAvailability
    languagelist = LanguageAvailability().getLanguages(combined=True)

    msgids = pot.keys()
    total = len(msgids)
    names = [pot.mime_header['Language-Code']]
    values = {}

    print "Msgid's: %s\n" % len(msgids)
    for po in [p for p in pos if p.mime_header['Language-Code'] != 'en']:
        code = po.mime_header.get('Language-Code')
        if code in IGNORE:
            continue
        name = po.mime_header.get('Language-Name')
        language = languagelist.get(code)
        if language is not None:
            desc = "%s (%s)" % (language['name'], code)
        else:
            desc = "%s (%s)" % (name, code)

        value = 0
        for msgid in msgids:
            if msgid in po and po[msgid].msgstr: # translated
                if not [1 for fuzzy in po[msgid].comments if 'fuzzy' in fuzzy]:
                    value += 1

        percentage = int(value / (total*1.0) * 100)
        if percentage == 99:
            percentage = 100
        values[code] = dict(percentage=percentage, desc=desc)

    out = values.copy()

    def _print(percentage, desc):
        if percentage < 10:
            percentage = ' %d' % percentage
        print "%s%% - %s" % (percentage, desc)

    print 'Priority 1:\n'
    print '100% - English (en)'
    for code in GROUP1:
        if code in out:
            _print(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            print ' 0%% - %s (%s)' % (languagelist.get(code)['name'], code)

    print '\nPriority 2:\n'
    for code in GROUP2:
        if code in out:
            _print(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            print ' 0%% - %s (%s)' % (languagelist.get(code)['name'], code)

    print '\nPriority 3:\n'
    group3 = out.values()
    group3.sort()
    for value in group3:
        perc = value['percentage']
        if perc == 0:
            continue
        if perc < 10:
            perc = ' %d' % perc
        print '%s%% - %s' % (perc, value['desc'])
