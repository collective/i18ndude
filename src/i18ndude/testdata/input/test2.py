# -*- coding: utf-8 -*-
# bla
_ = lambda x: x
zero = _('Zero')
one = _('One')

out = _('Out1', domain='running')

if True:
    three = _(msgid='msgid_three',
              default='Three')

four = _(msgid='msgid_four',
         default='Four ${map}',
         mapping={'map': zero})

five = _(u"msgid_five", default=u"五番目")

six = _(u"msgid_six", default=u"""
Line 1
Line 2
Line 3
""")
