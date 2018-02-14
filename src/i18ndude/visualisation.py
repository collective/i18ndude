IGNORE = frozenset(('zh', 'sr-Latn', ))

GROUP1 = [
    'fr', 'it', 'de', 'es', 'nl', 'zh-cn', 'zh-tw', 'ja', 'ko', 'pt-br',
    'ru', 'pl', 'tr', 'th', 'ar',
]

GROUP2 = [
    'sv', 'fi', 'da', 'pt', 'ro', 'hu', 'he', 'id', 'cs', 'el', 'no', 'vi',
    'bg', 'hr', 'lt', 'sk', 'tl', 'sl', 'sr', 'ca', 'lv', 'uk', 'hi',
]

_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>i18ndude matrix</title>
</head>
<body>
%(body)s
</body>
</html>"""

_TABLE = """<table>%(table)s
</table>"""

_ROW = """
<tr>
<td><div style="padding: 2px; margin: 2px; width:%(width)spx; background-color: %(color)s">
%(percent)s%%
</div></td>
<td>%(name)s</td>
</tr>
"""  # noqa


def print_row(percentage, desc):
    width = percentage * 2
    if width == 0:
        width = 1
    color = '#0d0'  # some kind of green
    if percentage < 90:
        color = 'yellow'
    if percentage < 50:
        color = 'red'

    return _ROW % dict(
        width=width,
        color=color,
        percent=percentage,
        name=desc,
    )


def output_table(out, languagelist, total):
    body = ''
    table = ''

    body += "<h1>Messages: %s</h1>\n" % total
    body += '<h2>Tier 1:</h2>\n'

    table += print_row(100, 'English (en)')
    for code in GROUP1:
        if code in out:
            table += print_row(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            lang = languagelist.get(code)
            if lang is None:
                name = code
            else:
                name = lang['name']
            desc = '%s (%s)' % (name, code)
            table += print_row(0, desc)

    body += _TABLE % dict(table=table)
    table = ''

    body += '\n<h2>Tier 2:</h2>\n'
    for code in GROUP2:
        if code in out:
            table += print_row(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            lang = languagelist.get(code)
            if lang is None:
                name = code
            else:
                name = lang['name']
            desc = '%s (%s)' % (name, code)
            table += print_row(0, desc)

    body += _TABLE % dict(table=table)
    table = ''

    body += '\n<h2>Tier 3:</h2>\n'
    group3 = sorted(out.values())
    for value in group3:
        perc = value['percentage']
        if perc == 0:
            continue
        table += print_row(perc, value['desc'])

    body += _TABLE % dict(table=table)
    template = _TEMPLATE % dict(body=body)

    print(template)


def aligned_print(percentage, desc):
    if percentage < 10:
        percentage = '  %d' % percentage
    elif percentage < 100:
        percentage = ' %d' % percentage
    print("%s%% - %s" % (percentage, desc))


def output_list(out, languagelist, total):
    print("Messages: %s\n" % total)

    print('Tier 1:\n')
    print('100% - English (en)')
    for code in GROUP1:
        if code in out:
            aligned_print(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            lang = languagelist.get(code)
            if lang is None:
                name = code
            else:
                name = lang['name']
            desc = '%s (%s)' % (name, code)
            aligned_print(0, desc)

    print('\nTier 2:\n')
    for code in GROUP2:
        if code in out:
            aligned_print(out[code]['percentage'], out[code]['desc'])
            del out[code]
        else:
            lang = languagelist.get(code)
            if lang is None:
                name = code
            else:
                name = lang['name']
            desc = '%s (%s)' % (name, code)
            aligned_print(0, desc)

    print('\nTier 3:\n')
    group3 = sorted(out.values())
    for value in group3:
        perc = value['percentage']
        if perc == 0:
            continue
        aligned_print(perc, value['desc'])


def make_listing(pot, pos, table=False):
    try:
        from plone.i18n.locales.languages import LanguageAvailabilityXXX
        languagelist = LanguageAvailability().getLanguages(combined=True)
    except ImportError:
        languagelist = {}

    msgids = pot.keys()
    total = len(msgids)
    values = {}

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
            if msgid in po and po[msgid].msgstr:  # translated
                if not [1 for fuzzy in po[msgid].comments if 'fuzzy' in fuzzy]:
                    value += 1

        percentage = int(value / (total * 1.0) * 100)
        if percentage == 99:
            percentage = 100
        values[code] = dict(percentage=percentage, desc=desc)

    total = len(msgids)
    if table:
        output_table(values.copy(), languagelist, total)
    else:
        output_list(values.copy(), languagelist, total)
