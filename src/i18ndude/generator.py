# coding=utf-8
from zope.tal.talgenerator import TALGenerator
from zope.tal.talgenerator import _parseI18nAttributes
from zope.tal.taldefs import I18NError
from zope.tal.taldefs import METALError
from zope.tal.taldefs import TALError
from zope.tal.taldefs import KNOWN_TAL_ATTRIBUTES
from zope.tal.taldefs import KNOWN_METAL_ATTRIBUTES
from zope.tal.taldefs import KNOWN_I18N_ATTRIBUTES
from zope.tal.taldefs import TAL_VERSION
from zope.tal.taldefs import parseAttributeReplacements
from zope.tal.translationcontext import DEFAULT_DOMAIN
from zope.tal.translationcontext import TranslationContext

# This is needed to be used in the monkey patch
KNOWN_CHAMELEON_ATTRIBUTES = KNOWN_TAL_ATTRIBUTES.union(
    (
        'case',
        'switch',
    )
)


class DudeGenerator(TALGenerator):

    ''' Custom Generator that supports default tal attributes and chameleon
    ones
    '''

    def emitStartElement(self, name, attrlist, taldict, metaldict, i18ndict,  # noqa
                         position=(None, None), isend=0):
        if not taldict and not metaldict and not i18ndict:
            # Handle the simple, common case
            self.emitStartTag(name, attrlist, isend)
            self.todoPush({})
            if isend:
                self.emitEndElement(name, isend)
            return
        self.position = position

        # TODO: Ugly hack to work around tal:replace and i18n:translate issue.
        # I (DV) need to cleanup the code later.
        replaced = False
        if "replace" in taldict:
            if "content" in taldict:
                raise TALError(
                    "tal:content and tal:replace are mutually exclusive",
                    position)
            taldict["omit-tag"] = taldict.get("omit-tag", "")
            taldict["content"] = taldict.pop("replace")
            replaced = True

        # here we have the patch
        for key, value in taldict.items():
            if key not in KNOWN_CHAMELEON_ATTRIBUTES:
                raise TALError("bad TAL attribute: " + repr(key), position)
            if not (value or key == 'omit-tag'):
                raise TALError("missing value for TAL attribute: " +
                               repr(key), position)
        for key, value in metaldict.items():
            if key not in KNOWN_METAL_ATTRIBUTES:
                raise METALError("bad METAL attribute: " + repr(key),
                                 position)
            if not value:
                raise TALError("missing value for METAL attribute: " +
                               repr(key), position)
        for key, value in i18ndict.items():
            if key not in KNOWN_I18N_ATTRIBUTES:
                raise I18NError("bad i18n attribute: " + repr(key), position)
            if not value and key in ("attributes", "data", "id"):
                raise I18NError("missing value for i18n attribute: " +
                                repr(key), position)

        todo = {}
        defineMacro = metaldict.get("define-macro")
        extendMacro = metaldict.get("extend-macro")
        useMacro = metaldict.get("use-macro")
        defineSlot = metaldict.get("define-slot")
        fillSlot = metaldict.get("fill-slot")
        define = taldict.get("define")
        condition = taldict.get("condition")
        repeat = taldict.get("repeat")
        content = taldict.get("content")
        script = taldict.get("script")
        attrsubst = taldict.get("attributes")
        onError = taldict.get("on-error")
        omitTag = taldict.get("omit-tag")
        TALtag = taldict.get("tal tag")
        i18nattrs = i18ndict.get("attributes")
        # Preserve empty string if implicit msgids are used.  We'll generate
        # code with the msgid='' and calculate the right implicit msgid during
        # interpretation phase.
        msgid = i18ndict.get("translate")
        varname = i18ndict.get('name')
        i18ndata = i18ndict.get('data')

        if varname and not self.i18nLevel:
            raise I18NError(
                "i18n:name can only occur inside a translation unit",
                position)

        if i18ndata and not msgid:
            raise I18NError("i18n:data must be accompanied by i18n:translate",
                            position)

        if extendMacro:
            if useMacro:
                raise METALError(
                    "extend-macro cannot be used with use-macro", position)
            if not defineMacro:
                raise METALError(
                    "extend-macro must be used with define-macro", position)

        if defineMacro or extendMacro or useMacro:
            if fillSlot or defineSlot:
                raise METALError(
                    "define-slot and fill-slot cannot be used with "
                    "define-macro, extend-macro, or use-macro", position)
            if defineMacro and useMacro:
                raise METALError(
                    "define-macro may not be used with use-macro", position)

            useMacro = useMacro or extendMacro

        if content and msgid:
            raise I18NError(
                "explicit message id and tal:content can't be used together",
                position)

        repeatWhitespace = None
        if repeat:
            # Hack to include preceding whitespace in the loop program
            repeatWhitespace = self.unEmitNewlineWhitespace()
        if position != (None, None):
            # TODO: at some point we should insist on a non-trivial position
            self.emit("setPosition", position)
        if self.inMacroUse:
            if fillSlot:
                self.pushProgram()
                # generate a source annotation at the beginning of fill-slot
                if self.source_file is not None:
                    if position != (None, None):
                        self.emit("setPosition", position)
                    self.emit("setSourceFile", self.source_file)
                todo["fillSlot"] = fillSlot
                self.inMacroUse = 0
        else:
            if fillSlot:
                raise METALError("fill-slot must be within a use-macro",
                                 position)
        if not self.inMacroUse:
            if defineMacro:
                self.pushProgram()
                self.emit("version", TAL_VERSION)
                self.emit("mode", self.xml and "xml" or "html")
                # generate a source annotation at the beginning of the macro
                if self.source_file is not None:
                    if position != (None, None):
                        self.emit("setPosition", position)
                    self.emit("setSourceFile", self.source_file)
                todo["defineMacro"] = defineMacro
                self.inMacroDef = self.inMacroDef + 1
            if useMacro:
                self.pushSlots()
                self.pushProgram()
                todo["useMacro"] = useMacro
                self.inMacroUse = 1
            if defineSlot:
                if not self.inMacroDef:
                    raise METALError(
                        "define-slot must be within a define-macro",
                        position)
                self.pushProgram()
                todo["defineSlot"] = defineSlot

        if defineSlot or i18ndict:

            domain = i18ndict.get("domain") or self.i18nContext.domain
            source = i18ndict.get("source") or self.i18nContext.source
            target = i18ndict.get("target") or self.i18nContext.target
            if (domain != DEFAULT_DOMAIN
                    or source is not None
                    or target is not None):
                self.i18nContext = TranslationContext(self.i18nContext,
                                                      domain=domain,
                                                      source=source,
                                                      target=target)
                self.emit("beginI18nContext",
                          {"domain": domain, "source": source,
                           "target": target})
                todo["i18ncontext"] = 1
        if taldict or i18ndict:
            dict = {}
            for item in attrlist:
                key, value = item[:2]
                dict[key] = value
            self.emit("beginScope", dict)
            todo["scope"] = 1
        if onError:
            self.pushProgram()  # handler
            if TALtag:
                self.pushProgram()  # start
            self.emitStartTag(name, list(attrlist))  # Must copy attrlist!
            if TALtag:
                self.pushProgram()  # start
            self.pushProgram()  # block
            todo["onError"] = onError
        if define:
            self.emitDefines(define)
            todo["define"] = define
        if condition:
            self.pushProgram()
            todo["condition"] = condition
        if repeat:
            todo["repeat"] = repeat
            self.pushProgram()
            if repeatWhitespace:
                self.emitText(repeatWhitespace)
        if content:
            if varname:
                todo['i18nvar'] = varname
                todo["content"] = content
                self.pushProgram()
            else:
                todo["content"] = content
        # i18n:name w/o tal:replace uses the content as the interpolation
        # dictionary values
        elif varname:
            todo['i18nvar'] = varname
            self.pushProgram()
        if msgid is not None:
            self.i18nLevel += 1
            todo['msgid'] = msgid
        if i18ndata:
            todo['i18ndata'] = i18ndata
        optTag = omitTag is not None or TALtag
        if optTag:
            todo["optional tag"] = omitTag, TALtag
            self.pushProgram()
        if attrsubst or i18nattrs:
            if attrsubst:
                repldict = parseAttributeReplacements(attrsubst, self.xml)
            else:
                repldict = {}
            if i18nattrs:
                i18nattrs = _parseI18nAttributes(i18nattrs, self.position,
                                                 self.xml)
            else:
                i18nattrs = {}
            # Convert repldict's name-->expr mapping to a
            # name-->(compiled_expr, translate) mapping
            for key, value in sorted(repldict.items()):
                if i18nattrs.get(key, None):
                    raise I18NError(
                        "attribute [%s] cannot both be part of tal:attributes"
                        " and have a msgid in i18n:attributes" % key,
                        position)
                ce = self.compileExpression(value)
                repldict[key] = ce, key in i18nattrs, i18nattrs.get(key)
            for key in sorted(i18nattrs):
                if key not in repldict:
                    repldict[key] = None, 1, i18nattrs.get(key)
        else:
            repldict = {}
        if replaced:
            todo["repldict"] = repldict
            repldict = {}
        if script:
            todo["script"] = script
        self.emitStartTag(name, self.replaceAttrs(attrlist, repldict), isend)
        if optTag:
            self.pushProgram()
        if content and not varname:
            self.pushProgram()
        if not content and msgid is not None:
            self.pushProgram()
        if content and varname:
            self.pushProgram()
        if script:
            self.pushProgram()
        if todo and position != (None, None):
            todo["position"] = position
        self.todoPush(todo)
        if isend:
            self.emitEndElement(name, isend, position=position)
