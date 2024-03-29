import io
import re
import xml.sax


IGNORE_UNTRANSLATED = "i18n:ignore"
IGNORE_UNTRANSLATED_ATTRIBUTES = "i18n:ignore-attributes"
CHAMELEON_SUBST = re.compile(r"^\${.*}$")
NOT_ALLOWED_IN_NAME = re.compile(r"[^\w-]")


def _translatable(data):
    """Returns 1 for strings that contain alphanumeric characters."""

    for ch in data:
        if ch.isalpha():
            return 1
    return 0


def _severity(tag, attrs):
    """Returns empty string if the case may be ignored.
    Returns textual representation of severity otherwise."""

    keys = attrs.keys()
    # Check for namespaces in the tag and attributes.
    # Catch all of these use cases:
    # <span tal:condition...
    # <tal condition...
    # <tal:block tal:condition...
    # All of those should result in tal:condition as attribute key.
    # And since the lxml html parser strips off the tal namespace from tags, we
    # should also support:
    # <block condition...

    # So lets simplify the keys.
    keys = {key[key.find(":") + 1 :] for key in keys}

    if "use-macro" in keys:
        # metal
        return ""

    # comments
    if "condition" in keys:
        cond_val = attrs.get("tal:condition", attrs.get("condition", None))
        if cond_val == "nothing":
            return ""
        return "ERROR"

    elif "replace" in keys or "content" in keys:
        return "WARNING"

    return "ERROR"


def _tal_replaced_content(tag, attrs):
    """Will the data get replaced by tal?

    So: is there a tal:content or tal:replace?  Or is it '<tal:block
    content=.".."'?  Problem with that last one is that the lxml html
    parser strips off the 'tal:' namespace, unlike the standard lxml
    parser that is tried first.
    """
    if "tal:content" in attrs or "content" in attrs:
        return True
    if "tal:replace" in attrs or "replace" in attrs:
        return True
    return False


def _tal_replaced_attr(attrs, attr):
    # Is the attribute replaced by tal?
    if "tal:attributes" not in attrs and "attributes" not in attrs:
        # Not replaced by tal, but could be chameleon syntax.
        value = attrs.get(attr, "")
        if CHAMELEON_SUBST.match(value):
            return True
        return False
    talattrs = [
        talattr.strip().split()[0]
        for talattr in attrs["tal:attributes"].split(";")
        if talattr
    ]
    if attr in talattrs:
        return True
    return False


def _valid_i18ned_attr(attr, attrs):
    """This returns 1 for attributes attr that are part of attrs and are
    translated using i18n:attributes. It also returns 1 for any attr that does
    not exist at all in attrs.

    When the attr gets replaced by tal, all is fine so we return 1 as well.
    """

    if attr in attrs and _translatable(attrs[attr]):
        if IGNORE_UNTRANSLATED_ATTRIBUTES in attrs:
            if attr in attrs[IGNORE_UNTRANSLATED_ATTRIBUTES].split(";"):
                return 1
        if "i18n:attributes" in attrs:
            # First check old syntax, or the simple case of one single
            # i18n:attribute.
            if attrs["i18n:attributes"].find(";") == -1:
                i18nattrs = [
                    i18nattr.strip() for i18nattr in attrs["i18n:attributes"].split()
                ]
            else:  # new syntax
                i18nattrs = [
                    i18nattr.strip().split()[0]
                    for i18nattr in attrs["i18n:attributes"].split(";")
                    if i18nattr
                ]
            if attr in i18nattrs:
                return 1
            if _tal_replaced_attr(attrs, attr):
                return 1
            return 0
        else:
            if _tal_replaced_attr(attrs, attr):
                return 1
            return 0

    return 1


def attr_validator(tag, attrs, logfct):
    """Given a tag and it's attributes' dictionary, this function figures out
    if
       1) Each tag that has a title attribute has it i18ned.
       2) Each image tag has its alt attribute i18ned.
       3) Each tag that is a <input type="submit *or* button"> has its value
          i18ned.
    """

    if not _valid_i18ned_attr("title", attrs):
        logfct("title attribute of <%s> lacks i18n:attributes" % tag, "ERROR")

    if not _valid_i18ned_attr("aria-label", attrs):
        logfct("aria-label attribute of <%s> lacks i18n:attributes" % tag, "ERROR")

    if tag == "img":
        if not _valid_i18ned_attr("alt", attrs):
            logfct("alt attribute of <img> lacks i18n:attributes", "ERROR")

    if (
        tag == "input"
        and "type" in attrs.keys()
        and attrs["type"] in ("submit", "button")
    ):
        if not _valid_i18ned_attr("value", attrs):
            logfct(
                "value attribute of <... submit/button> lacks " "i18n:attributes",
                "ERROR",
            )

    if tag == "input" and "placeholder" in attrs.keys():
        if not _valid_i18ned_attr("placeholder", attrs):
            logfct("placeholder attribute of <%s> lacks i18n:attributes" % tag, "ERROR")

    name = attrs.get("i18n:name")
    if name and NOT_ALLOWED_IN_NAME.search(name):
        logfct(
            "invalid non-word characters (space, punctuation) "
            'in i18n:name="{}"'.format(name),
            "ERROR",
        )


class Handler(xml.sax.ContentHandler):
    def __init__(self, parser, out=None):
        self._parser = parser
        if out is None:
            self._out = io.StringIO()
        else:
            self._out = out
        self._filename = "Undefined"

    def show_output(self):
        value = self._out.getvalue().strip()
        if value:
            if not isinstance(value, str):
                value = value.decode("utf-8")
            # Note: if value contains non-ascii and we redirect stdout
            # or pipe the output through 'grep', we get a UnicodeEncodeError.
            # Solution: export PYTHONIOENCODING=utf-8
            # See https://stackoverflow.com/questions/492483
            print(value + "\n")

    def clear_output(self):
        self._out = io.StringIO()

    def log(self, msg, severity):
        """Severity may be one out of 'WARNING', 'ERROR' or 'FATAL'."""
        assert severity in self._stats.keys()
        self._stats[severity] += 1

    def has_errors(self):
        return self._stats["ERROR"] or self._stats["FATAL"]

    def set_filename(self, filename):
        self._filename = filename

    def startDocument(self):
        # history contains 3-tuples in the form
        # (tag, attrs, characterdata)
        self._history = []
        # 0 means not inside i18n:translate area
        self._i18nlevel = 0
        # When you add i18n:ignore on a tag, then all untranslated messages on this
        # or enclosed tags are ignored.
        self._ignore_untranslated = False
        self._stats = {"WARNING": 0, "ERROR": 0, "FATAL": 0}

    def endDocument(self):
        pass

    def startElement(self, tag, attrs):
        self._history.append([tag, attrs, ""])

        if "i18n:translate" in attrs.keys():
            self._i18nlevel += 1
        elif self._i18nlevel != 0:
            self._i18nlevel += 1
        if IGNORE_UNTRANSLATED in attrs:
            self._ignore_untranslated = True
        if not self._ignore_untranslated:
            attr_validator(tag, attrs, self.log)

    def endElement(self, tag):
        tag, attrs, data = self._history.pop()
        data = data.strip()

        if (
            not self._ignore_untranslated
            and _translatable(data)
            and not _tal_replaced_content(tag, attrs)
            and (self._i18nlevel == 0)
            and tag not in ["script", "style", "html"]
        ):
            severity = _severity(tag, attrs) or ""
            if severity and not CHAMELEON_SUBST.match(data):
                self.log(
                    "i18n:translate missing for this:\n" '"""\n%s\n"""' % (data,),
                    severity,
                )

        if self._i18nlevel != 0:
            self._i18nlevel -= 1
        if IGNORE_UNTRANSLATED in attrs:
            # reset
            self._ignore_untranslated = False

    def characters(self, data):
        self._history[-1][2] += data


class SilentHandler(Handler):
    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        if severity == "FATAL":
            self._out.write("Fatal error in document %s" % self._filename)
            self._out.write("\n")

    def endDocument(self):
        if not (self._stats["WARNING"] or self._stats["ERROR"]):
            return

        self._out.write(
            "%s: %s warnings, %s errors"
            % (self._filename, self._stats["WARNING"], self._stats["ERROR"])
        )


class VerboseHandler(Handler):
    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        self._out.write(
            str(
                "{}:{}:{}:\n-{}- - {}\n".format(
                    self._filename,
                    self._parser.getLineNumber(),
                    self._parser.getColumnNumber(),
                    severity,
                    msg,
                )
            )
        )

        if severity == "FATAL":
            char = "="
        else:
            char = "-"
        self._out.write(str(char * 79) + "\n")

    def endDocument(self):
        self._out.write(
            str(
                "Processing of %s finished. (%s warnings, %s errors)\n"
                % (self._filename, self._stats["WARNING"], self._stats["ERROR"])
            )
        )
        self._out.write(str("=" * 79) + "\n")


class NoSummaryVerboseHandler(Handler):
    def log(self, msg, severity):
        Handler.log(self, msg, severity)

        self._out.write(
            str(
                "{}:{}:{}:\n-{}- - {}".format(
                    self._filename,
                    self._parser.getLineNumber(),
                    self._parser.getColumnNumber(),
                    severity,
                    msg,
                )
            )
        )
        self._out.write("\n")

    def endDocument(self):
        pass
