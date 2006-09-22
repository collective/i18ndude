# bla

_ = context.translate

zero = context.translate('Zero')
one = context.translate('One', domain='testing')
two = _('Two')

out = context.translate('Out1', domain='running')
#out = context.translate('Out2', domain='testing')

if True:
    three = context.translate(msgid='msgid_three',
                              default='Three')

four = context.translate(msgid='msgid_four',
                         default='Four ${map}',
                         mapping={'map': zero})

