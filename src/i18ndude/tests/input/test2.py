# bla

zero = _('Zero')
one = _('One')

out = _('Out1', domain='running')

if True:
    three = _(msgid='msgid_three',
              default='Three')

four = _(msgid='msgid_four',
        default='Four ${map}',
        mapping={'map': zero})

