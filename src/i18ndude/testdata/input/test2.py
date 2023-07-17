# bla
def _(x):
    return x


zero = _("Zero")
one = _("One")
if True:
    three = _(msgid="msgid_three", default="Three")

four = _(msgid="msgid_four", default="Four ${map}", mapping={"map": zero})

five = _("msgid_five", default="五番目")

six = _(
    "msgid_six",
    default="""
Line 1
Line 2
Line 3
""",
)
