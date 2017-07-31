# -*- coding: utf-8 -*-
from zope.tal import taldefs
from zope.tal.taldefs import I18NError
from zope.tal.taldefs import TAL_VERSION
from zope.tal.taldefs import TALError
from zope.tal.talgenerator import _parseI18nAttributes
from zope.tal.talgenerator import TALGenerator
from zope.tal.translationcontext import DEFAULT_DOMAIN
from zope.tal.translationcontext import TranslationContext

import re


class DudeGenerator(TALGenerator):

    """Custom Generator that does not raise template errors.

    We have simply removed any TALErrors and METALErrors that would be
    raised by zope.tal.  i18ndude is not a tool for checking the syntax
    of your template.  It needs to know just enough to be able to
    extract i18n information from it.

    Main use case: support default tal attributes plus
    chameleon-specific ones.
    """

    def emitStartElement(self, name, attrlist, taldict, metaldict, i18ndict,
                         position=(None, None), isend=0):
        if not taldict and not metaldict and not i18ndict:
            # Handle the simple, common case
            self.emitStartTag(name, attrlist, isend)
            self.todoPush({})
            if isend:
                self.emitEndElement(name, isend)
            return
        self.position = position

        replaced = False
        if "replace" in taldict:
            taldict["omit-tag"] = taldict.get("omit-tag", "")
            taldict["content"] = taldict.pop("replace")
            replaced = True

        for key, value in i18ndict.items():
            if key not in taldefs.KNOWN_I18N_ATTRIBUTES:
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

        if defineMacro or extendMacro or useMacro:
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
                try:
                    repldict = taldefs.parseAttributeReplacements(
                        attrsubst, self.xml)
                except TALError:
                    repldict = {}
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

    def emitRepeat(self, arg):
        try:
            super(DudeGenerator, self).emitRepeat(arg)
        except TALError:
            # Could be Chameleon syntax.
            # It might be okay to simply return, as we are not really
            # interested in compiling everything.  But we can try.
            # We look for tal:repeat="   (a,b,c) python:something"
            # in a way similar to zope.tal.
            m = re.match("(?s)\s*(\(.+\))\s+(.*)\Z", arg)
            if not m:
                raise TALError("invalid repeat syntax: " + repr(arg),
                               self.position)
            name, expr = m.group(1, 2)
            cexpr = self.compileExpression(expr)
            program = self.popProgram()
            self.emit("loop", name, cexpr, program)
