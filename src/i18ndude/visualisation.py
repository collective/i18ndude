try:
    import gdchart
except ImportError:
    gdchart = None

def make_chart(pot, pos, out, size=None, title=None, **kwargs):
    msgids = pot.keys()
    total = len(msgids)
    names = [pot.mime_header['Language-Code']]
    values = [total]
    colors = [0x00ff00] # green

    if size is None:
        width = len(pos) * 20
        size = (width, width / 2)

    print "languages: %s, msgid's: %s" % (len(pos), len(msgids))
    for po in [p for p in pos if p.mime_header['Language-Code'] != 'en']:
        name = '%s' % po.mime_header['Language-Code']

        value = 0
        for msgid in msgids:
            if msgid in po and po[msgid].msgstr: # translated
                if not [1 for fuzzy in po[msgid].comments if 'fuzzy' in fuzzy]:
                    value += 1

        names.append(name)
        values.append(value)
        complete = int(value / (total*1.0) * 100)
        # don't ask me why or how, but this seems to work... ;-)
        colors.append(colors[0] * (101 - complete) * 3)

        print "%s: %s missing (%d%% done)" % (name, total - value, complete)

    # sort by number of translated messages
    # keeping 'en' always on first position
    z = zip(values[1:], names[1:], colors[1:])
    z.sort(lambda x, y: x[0] == y[0] and cmp((x[0], x[1]), (y[0], y[1])) or
                                         cmp((y[0], y[1]), (x[0], x[1])))
    values = values[0:1]
    names = names[0:1]
    colors = colors[0:1]
    for v,n,c in z:
        values.append(v)
        names.append(n)
        colors.append(c)

    if gdchart is not None:
        options = {'bg_color': 0xffffff,
                   'border': gdchart.GDC_BORDER_ALL,
                   'xaxis_font': gdchart.GDC_SMALL,
                   'title': title or pot.mime_header['Project-Id-Version'],
                   'ext_color' : colors,
                   }
        options.update(kwargs)
        gdchart.option(**options)

        gdchart.chart(gdchart.GDC_3DBAR,
                      size,
                      out,
                      names,
                      values)

    status = {}
    i = 0
    while i < len(names):
        status[names[i]] = values[i]
        i += 1

    return status

