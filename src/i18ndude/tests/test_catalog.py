from .utils import TESTDATA_DIR
from i18ndude import catalog
from i18ndude import utils

import os
import unittest
import warnings


class TestGlobal(unittest.TestCase):
    def test_isLiteralId(self):
        i = catalog.is_literal_id
        errortext = "False literal msgid recognition"
        self.assertFalse(i("label_yes"), errortext)
        self.assertFalse(i("_"), errortext)
        self.assertTrue(i(" "), errortext)
        self.assertTrue(i(" _"), errortext)
        self.assertTrue(i("text"), errortext)
        self.assertTrue(i("This is a text."), errortext)

    def test_originalComment(self):
        self.assertEqual(
            catalog.ORIGINAL_COMMENT, " Original: ", "Wrong original comment constant"
        )

    def test_defaultComment(self):
        self.assertEqual(
            catalog.DEFAULT_COMMENT, " Default: ", "Wrong default comment constant"
        )


class TestMessageEntry(unittest.TestCase):
    def setUp(self):
        self.me = catalog.MessageEntry
        self.msgid = "test msgid"
        self.msgstr = "test text"
        self.references = ["test1.pt", "test2.pt"]
        self.default_text = "test default"
        self.default_comment = f'{catalog.DEFAULT_COMMENT}"{self.default_text}"'  # noqa
        self.automatic_comments = [
            "first line",
            "second line",
            self.default_comment,
        ]  # noqa
        self.orig_text = "test original"
        self.orig_comment = f'{catalog.ORIGINAL_COMMENT}"{self.orig_text}"'  # noqa
        self.comments = ["A comment", self.orig_comment]

    def test_init(self):
        me = self.me
        me1 = me(self.msgid)
        self.assertEqual(me1.msgid, self.msgid, "msgid not set correctly")
        me1 = me(self.msgid, msgstr=self.msgstr)
        self.assertEqual(me1.msgid, self.msgid, "msgid not set correctly")
        self.assertEqual(me1.msgstr, self.msgstr, "msgstr not set correctly")

        me1 = me(self.msgid, msgstr=self.msgstr, references=self.references)
        self.assertEqual(me1.msgid, self.msgid, "msgid not set correctly")
        self.assertEqual(me1.msgstr, self.msgstr, "msgstr not set correctly")
        self.assertEqual(
            me1.references, self.references, "references not set correctly"
        )  # noqa

        me1 = me(self.msgid, msgstr=self.msgstr, comments=self.comments)
        self.assertEqual(me1.msgid, self.msgid, "msgid not set correctly")
        self.assertEqual(me1.msgstr, self.msgstr, "msgstr not set correctly")
        self.assertEqual(
            me1.comments, self.comments, "comments not set correctly"
        )  # noqa
        self.assertEqual(
            me1.getOriginalComment(),
            self.orig_comment,
            "Original comment not set correctly",
        )  # noqa
        self.assertEqual(
            me1.getOriginal(), self.orig_text, "Original text not set correctly"
        )  # noqa

        me2 = me(
            self.msgid, msgstr=self.msgstr, automatic_comments=self.automatic_comments
        )  # noqa
        self.assertEqual(me2.msgid, self.msgid, "msgid not set correctly")
        self.assertEqual(me2.msgstr, self.msgstr, "msgstr not set correctly")
        self.assertEqual(
            me2.automatic_comments,
            self.automatic_comments,
            "comments not set correctly",
        )  # noqa
        self.assertEqual(
            me2.getDefaultComment(),
            self.default_comment,
            "Default comment not set correctly",
        )  # noqa
        self.assertEqual(
            me2.getDefault(), self.default_text, "Default text not set correctly"
        )  # noqa


class TestMessageCatalogInit(unittest.TestCase):
    def setUp(self):
        self.mc = catalog.MessageCatalog
        self.me = catalog.MessageEntry
        self.file = os.path.join(TESTDATA_DIR, "input", "test-en.po")
        self.emptyfile = os.path.join(TESTDATA_DIR, "input", "empty-en.po")

        self.commentary_header = [
            " Translation of test.pot to English",
            " Hanno Schlichting <schlichting@bakb.net>, 2005",
        ]

        self.mimeheader = {
            "Language-Code": "en",
            "Domain": "testing",
            "PO-Revision-Date": "2005-08-10 21:15+0000",
            "Content-Transfer-Encoding": "8bit",
            "Language-Name": "English",
            "Plural-Forms": "nplurals=1; plural=0;",
            "Project-Id-Version": "i18ndude",
            "Preferred-Encodings": "utf-8 latin1",
            "Last-Translator": "Unicödé Guy",
            "Language-Team": "Plone i18n <plone-i18n@lists.sourceforge.net>",
            "POT-Creation-Date": "2005-08-01 12:00+0000",
            "Content-Type": "text/plain; charset=utf-8",
            "MIME-Version": "1.0",
        }

        self.msgids = {
            "msgid1": self.me(
                "msgid1",
                msgstr="msgstr1",
                references=["file1", "file2"],
                automatic_comments=[' Default: "msgstr1"'],
                comments=[" comment1"],
            ),
            "msgid2": self.me("msgid2", msgstr="msgstr2", references=["file2"]),
            "msgid3": self.me(
                "msgid3",
                msgstr="\\n\\nmsgstr\\n3",
                references=["file3"],
                comments=[" comment3"],
            ),
            "msgid4": self.me("msgid4", msgstr="msgstr4", references=["file4"]),
            "msgid5": self.me("msgid5", msgstr="msgstr5", comments=[" comment5"]),
            "msgid6": self.me("msgid6", msgstr="msgstr6"),
            "msgid7": self.me("msgid7", msgstr="msgstr7", comments=[", fuzzy"]),
            "msgid8": self.me("msgid8"),
            "msgid has spaces": self.me(
                "msgid has spaces",
                msgstr="msgstr has spaces",
                comments=["# I am a dead comment"],
            ),
            "msgid_has_underlines": self.me(
                "msgid_has_underlines", msgstr="msgstr_has_underlines"
            ),
            "msgid_has_underlines and spaces": self.me(
                "msgid_has_underlines and spaces",
                msgstr="msgstr_has_underlines and spaces",
            ),
            "msgid for standard text": self.me(
                "msgid for standard text", msgstr="msgstr \xb7\xb7\xb7"
            ),
            "msgid for text with comment": self.me(
                "msgid for text with comment",
                msgstr="msgstr \xb7\xb7\xb7",
                references=["./folder/file_unicode"],
                automatic_comments=[" Default: [···]"],
            ),
            "msgid for text with german umlaut": self.me(
                "msgid for text with german umlaut", msgstr="\xe4\xf6\xfc\xdf text"
            ),
            "msgid for text with html-entity": self.me(
                "msgid for text with html-entity",
                msgstr="&quot;this&nbsp;is&laquo;&auml;&amp;&ouml;&raquo;&quot;",
            ),  # noqa
            (
                "Its quite annoying that all translation editors wrap "
                "translations strings at 80 characters, but then when you "
                "update the po files with i18ndude they are unwrapped and "
                "kept as huge lines. Can we fix that?"
            ): self.me(
                "Its quite annoying that all translation editors wrap "
                "translations strings at 80 characters, but then when you "
                "update the po files with i18ndude they are unwrapped and "
                "kept as huge lines. Can we fix that?",
                msgstr=(
                    "Of course we can fix that. After all: i18ndude is "
                    "awesome, as I am sure you all agree."
                ),
                comments=[
                    (
                        " https://github.com/collective/i18ndude/issues/3 "
                        "complains about long lines. But long comment lines "
                        "should be left intact."
                    ),
                    (
                        " Note that the unix msgattrib command can wrap or "
                        "unwrap long lines in po files."
                    ),
                ],
            ),
            "msgid_with_long_lines_including_backslash_n.": self.me(
                "msgid_with_long_lines_including_backslash_n.",
                msgstr=(
                    "Falls aktiv wird der entsprechende \\nLinkcycle einen"
                    " Button haben, mit dem man durch ihn blaettern kann. "
                    "mit dem man durch ihn blaettern kann. mit dem man "
                    "durch ihn blaettern kann. mit dem man durch ihn "
                    "blaettern kann."
                ),
            ),  # XXX
        }

    def test_init(self):
        failing = False
        try:
            catalog.MessageCatalog()
        except AssertionError:
            failing = True
        self.assertTrue(failing, "Init without parameters should not be allowed.")

    def test_initWithDomain(self):
        domain = "testing"
        test = self.mc(domain=domain)
        mime = catalog.DEFAULT_PO_MIME
        for key, value in mime:
            if key != "Domain":
                self.assertEqual(
                    value, test.mime_header[key], "header mismatch on %s" % key
                )
            else:
                self.assertEqual(domain, test.mime_header["Domain"], "Domain mismatch")
        self.assertEqual(
            catalog.DEFAULT_PO_HEADER,
            test.commentary_header,
            "commentary header mismatch",
        )
        self.assertEqual(len(test), 0, "Non-empty catalog")

    def test_initWithEmptyFile(self):
        test = self.mc(filename=self.emptyfile)
        mime = catalog.DEFAULT_PO_MIME
        for key, value in mime:
            self.assertEqual(
                value, test.mime_header[key], "header mismatch on %s" % key
            )

    def test_initWithEmptyFileAndDomain(self):
        failing = False
        try:
            self.mc(domain="testing", filename=self.emptyfile)
        except AssertionError:
            failing = True
        self.assertTrue(
            failing, "Init with filename and domain parameters is not allowed."
        )

    def test_initWithFile(self):
        test = self.mc(filename=self.file)
        for key in test.mime_header:
            self.assertEqual(
                test.mime_header[key],
                self.mimeheader[key],
                "wrong mime header parsing:\nGot: %s !=\nExpected: %s"
                % (test.mime_header[key], self.mimeheader[key]),
            )
        for value in test.commentary_header:
            self.assertTrue(
                value in self.commentary_header, "wrong commentary header parsing"
            )
        if not test == self.msgids:
            for key in test:
                self.assertTrue(
                    test[key] == self.msgids[key],
                    "error in po parsing:\nGot:      %s !=\nExpected: %s"
                    % (test[key], self.msgids[key]),
                )


class TestMessageCatalog(unittest.TestCase):
    def setUp(self):
        self.domain = "testing"
        self.mc = catalog.MessageCatalog(domain=self.domain)
        self.msgid = "test msgid"
        self.msgstr = "test text"
        self.references = ["test1.pt", "test2.pt"]
        self.default_text = "test default"
        self.default_comment = f'{catalog.DEFAULT_COMMENT}"{self.default_text}"'  # noqa
        self.automatic_comments = [
            "first line",
            "second line",
            self.default_comment,
        ]  # noqa
        self.orig_text = "test original"
        self.orig_comment = f'{catalog.ORIGINAL_COMMENT}"{self.orig_text}"'  # noqa
        self.comments = ["A comment", self.orig_comment]

    def test_add(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        # add with msgid
        self.mc.add(msgid)
        self.assertTrue(msgid in self.mc, "msgid not found in catalog")
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, "msgid found in catalog")
        # add with msgid and msgstr
        self.mc.add(msgid, msgstr=msgstr)
        self.assertEqual(
            self.mc[msgid].msgstr, msgstr, "msgstr not found in catalog."
        )  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, "msgid found in catalog")
        # add with msgid, msgstr and filename
        self.mc.add(msgid, msgstr=msgstr, references=references)
        self.assertEqual(
            self.mc[msgid].references, references, "references not found in catalog."
        )  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, "msgid found in catalog")
        # add with msgid, msgstr, filename and excerpt
        self.mc.add(
            msgid,
            msgstr=msgstr,
            references=references,
            automatic_comments=automatic_comments,
        )  # noqa
        self.assertEqual(
            self.mc[msgid].automatic_comments,
            automatic_comments,
            "automatic_comments not found in catalog.",
        )  # noqa
        del self.mc[msgid]
        self.assertFalse(msgid in self.mc, "msgid found in catalog")

    def test_multipleAdd(self):
        msgid = self.msgid
        msgstr = self.msgstr
        references = self.references
        automatic_comments = self.automatic_comments

        self.mc.add(
            msgid,
            msgstr=msgstr,
            references=references,
            automatic_comments=automatic_comments,
        )  # noqa
        self.mc.add(
            msgid,
            msgstr=msgstr,
            references=references,
            automatic_comments=automatic_comments,
        )  # noqa
        self.assertTrue(len(self.mc) == 1, "duplicate msgid")
        self.assertTrue(
            len(self.mc[msgid].references) == 2, "references missing"
        )  # noqa

    def test_originalComment(self):
        self.mc.add(
            self.msgid,
            msgstr=self.msgstr,
            references=self.references,
            automatic_comments=self.automatic_comments,
        )  # noqa
        self.mc[self.msgid].comments.extend(self.comments)
        self.assertEqual(
            self.mc.getComments(self.msgid), self.comments, "wrong comments"
        )  # noqa
        self.assertEqual(
            self.mc.getOriginalComment(self.msgid),
            self.orig_comment,
            "wrong original comment line",
        )  # noqa
        self.assertEqual(
            self.mc.getOriginal(self.msgid),
            self.orig_text,
            "wrong original comment text",
        )  # noqa
        self.assertEqual(
            self.mc.getDefaultComment(self.msgid),
            self.default_comment,
            "wrong default comment line",
        )  # noqa
        self.assertEqual(
            self.mc.getDefault(self.msgid),
            self.default_text,
            "wrong default comment text",
        )  # noqa


class TestMessageCatalogSync(unittest.TestCase):
    def setUp(self):
        mc = catalog.MessageCatalog
        self.potfile = os.path.join(TESTDATA_DIR, "input", "synctest.pot")
        self.pofile = os.path.join(TESTDATA_DIR, "input", "synctest-de.po")
        self.pot = mc(filename=self.potfile)
        self.po = mc(filename=self.pofile)

    def test_sync(self):
        old_defaults = {}
        for id in self.po:
            old_defaults[id] = self.po[id].getDefault()
        self.po.sync(self.pot)
        self.assertTrue(
            len(self.pot) == len(self.po), "number of messages does not match"
        )  # noqa
        for msgid in self.pot:
            self.assertTrue(
                msgid in self.po, "msgid %s could not be found" % self.pot[msgid]
            )  # noqa
            self.assertTrue(
                self.po[msgid].references == self.pot[msgid].references
            )  # noqa
            defaults = self.po[msgid].getDefaults()
            if defaults is not None:
                for dc in defaults:
                    self.assertTrue(
                        dc == self.pot[msgid].getDefault() or dc == old_defaults[msgid],
                        "Either old or new default comment is missing on msgid: %s"
                        % msgid,  # noqa
                    )


class TestMessagePoWriter(unittest.TestCase):
    def setUp(self):
        mc = catalog.MessageCatalog
        self.input = os.path.join(TESTDATA_DIR, "input", "test-en.po")
        self.output = os.path.join(TESTDATA_DIR, "output", "test-en.po")
        self.input2 = os.path.join(TESTDATA_DIR, "input", "test2-en.po")
        self.expectedOutput2 = os.path.join(
            TESTDATA_DIR, "input", "test2_expected-en.po"
        )  # noqa
        self.output2 = os.path.join(TESTDATA_DIR, "output", "test2-en.po")
        self.catalog = mc(filename=self.input)
        self.catalog2 = mc(filename=self.input2)
        if os.path.exists(self.output):
            os.remove(self.output)
        if os.path.exists(self.output2):
            os.remove(self.output2)

    def test_write(self):
        # Explicitly enable wrapping here, as that is what we did in
        # the test po file.
        orig_wrap = utils.WRAP
        utils.WRAP = True
        fd = open(self.output, "w")
        pow = catalog.POWriter(fd, self.catalog)
        pow.write(sort=True)
        fd.close()
        # Restore original value.
        utils.WRAP = orig_wrap

        input_ = open(self.input)
        output = open(self.output)

        # compare line by line
        inlines = input_.readlines()
        outlines = enumerate(output.readlines())

        input_.close()
        output.close()

        for i, result in outlines:
            orig = inlines[i]
            self.assertEqual(
                orig, result, "difference in line %s, '%s' != '%s'" % (i, orig, result)
            )

    def test_writeSpecialComments(self):
        fd = open(self.output2, "w")
        pow = catalog.POWriter(fd, self.catalog2)
        pow.write(sort=True)
        fd.close()

        output = open(self.output2)
        expected = open(self.expectedOutput2)

        # compare line by line
        outlines = output.readlines()
        explines = enumerate(expected.readlines())

        output.close()
        expected.close()

        for i, result in explines:
            orig = outlines[i]
            self.assertEqual(
                orig,
                result,
                "difference in line %s, Got: '%s' != Expected: '%s'"
                % (i, orig, result),
            )

    def tearDown(self):
        if os.path.exists(self.output):
            os.remove(self.output)
        if os.path.exists(self.output2):
            os.remove(self.output2)


class TestMessagePTReader(unittest.TestCase):
    def test_read_no_line_numbers(self):
        me = catalog.MessageEntry
        input_ = os.path.join(TESTDATA_DIR, "input")
        filename = input_ + os.sep + "test1.pt"
        filename3 = input_ + os.sep + "test3.pt"
        filename5 = input_ + os.sep + "test5.pt"
        output = {
            "Buzz": me("Buzz", references=[filename]),
            "${foo} ${with-dash-and_underscore}": me(
                "${foo} ${with-dash-and_underscore}", references=[filename]
            ),  # noqa
            "dig_this": me(
                "dig_this", msgstr="Dig this", references=[filename]
            ),  # noqa
            "text_buzz": me("text_buzz", msgstr="Buzz", references=[filename]),  # noqa
            "some_alt": me(
                "some_alt", msgstr="Some alt", references=[filename, filename3]
            ),  # noqa
            "title_some_alt": me(
                "title_some_alt", msgstr="Some title", references=[filename]
            ),  # noqa
            "Job started at ${datetime} by user ${userid}.": me(
                "Job started at ${datetime} by user ${userid}.", references=[filename]
            ),  # noqa
            "spacing": me(
                "spacing",
                msgstr="Space <br /> before and after.",
                references=[filename],
            ),  # noqa
            "spacing_strong": me(
                "spacing_strong",
                msgstr="Please press your browser's <strong>Back</strong> button to try again.",
                references=[filename],
            ),  # noqa
            "<tt>domain</tt> is one of the <em>local domains</em>:": me(
                "<tt>domain</tt> is one of the <em>local domains</em>:",
                references=[filename],
            ),  # noqa
            "odd": me("odd", references=[filename]),
            "even": me("even", references=[filename]),
            "Test for issue 15, html5 attributes without value": me(
                "Test for issue 15, html5 attributes without value",
                references=[filename],
            ),  # noqa
            "rebuild-pot should not complain about Chameleon repeat syntax.": me(
                "rebuild-pot should not complain about Chameleon repeat syntax.",
                references=[filename5],
            ),  # noqa
            "rebuild-pot should not complain about Chameleon define syntax.": me(
                "rebuild-pot should not complain about Chameleon define syntax.",
                references=[filename5],
            ),  # noqa
        }

        ptr = catalog.PTReader(input_, domain="testing", include_line_numbers=False)
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter("always")
            # This call will give a warning from zope.tal.
            ptr.read()
            self.assertGreaterEqual(len(log), 1, log)
            contents = "\n".join([str(x.message) for x in log])
            # Check that a few key elements are in the
            # warning, without wanting to check the exact
            # wording, as this can easily change.
            self.assertTrue(
                "already exists with a different default" in contents,
                'missing "already exists"',
            )
            self.assertTrue(
                "bad: b'Buzzer', should be: b'Buzz'" in contents  # py36
                or "bad: Buzzer, should be: Buzz" in contents,  # py27
                f"bad Buzzer not in contents: {contents}",
            )

        out = ptr.catalogs["testing"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in pt parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out[key] == output[key],
                "Failure in pt parsing.\nGot:%s\nExpected:%s" % (out[key], output[key]),
            )
        self.assertEqual(len(out), len(output))

    def test_read_include_line_numbers(self):
        me = catalog.MessageEntry
        input_ = os.path.join(TESTDATA_DIR, "input")
        filename = input_ + os.sep + "test1.pt"
        filename3 = input_ + os.sep + "test3.pt"
        filename5 = input_ + os.sep + "test5.pt"
        output = {
            "Buzz": me("Buzz", references=[filename + ":21"]),
            "${foo} ${with-dash-and_underscore}": me(
                "${foo} ${with-dash-and_underscore}", references=[filename + ":26"]
            ),  # noqa
            "dig_this": me(
                "dig_this", msgstr="Dig this", references=[filename + ":52"]
            ),  # noqa
            "text_buzz": me(
                "text_buzz",
                msgstr="Buzz",
                references=[filename + ":29", filename + ":31"],
            ),  # noqa
            "some_alt": me(
                "some_alt",
                msgstr="Some alt",
                references=[filename + ":15", filename3 + ":15"],
            ),  # noqa
            "title_some_alt": me(
                "title_some_alt", msgstr="Some title", references=[filename + ":15"]
            ),  # noqa
            "Job started at ${datetime} by user ${userid}.": me(
                "Job started at ${datetime} by user ${userid}.",
                references=[filename + ":46"],
            ),  # noqa
            "spacing": me(
                "spacing",
                msgstr="Space <br /> before and after.",
                references=[filename + ":37"],
            ),  # noqa
            "spacing_strong": me(
                "spacing_strong",
                msgstr="Please press your browser's <strong>Back</strong> button to try again.",
                references=[filename + ":41"],
            ),  # noqa
            "<tt>domain</tt> is one of the <em>local domains</em>:": me(
                "<tt>domain</tt> is one of the <em>local domains</em>:",
                references=[filename + ":49"],
            ),  # noqa
            "odd": me("odd", references=[filename + ":58"]),
            "even": me("even", references=[filename + ":59"]),
            "Test for issue 15, html5 attributes without value": me(
                "Test for issue 15, html5 attributes without value",
                references=[filename + ":62"],
            ),  # noqa
            "rebuild-pot should not complain about Chameleon repeat syntax.": me(
                "rebuild-pot should not complain about Chameleon repeat syntax.",
                references=[filename5 + ":16"],
            ),  # noqa
            "rebuild-pot should not complain about Chameleon define syntax.": me(
                "rebuild-pot should not complain about Chameleon define syntax.",
                references=[filename5 + ":19"],
            ),  # noqa
        }

        ptr = catalog.PTReader(input_, domain="testing")
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter("always")
            # This call will give a warning from zope.tal.
            ptr.read()
            self.assertGreaterEqual(len(log), 1, log)
            contents = "\n".join([str(x.message) for x in log])
            # Check that a few key elements are in the
            # warning, without wanting to check the exact
            # wording, as this can easily change.
            self.assertTrue(
                "already exists with a different default" in contents,
                'missing "already exists"',
            )
            self.assertTrue(
                "bad: b'Buzzer', should be: b'Buzz'" in contents  # py36
                or "bad: Buzzer, should be: Buzz" in contents,  # py27
                f"bad Buzzer not in contents: {contents}",
            )

        out = ptr.catalogs["testing"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in pt parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out[key] == output[key],
                "Failure in pt parsing.\nGot:%s\nExpected:%s" % (out[key], output[key]),
            )
        self.assertEqual(len(out), len(output))


class TestMessagePYReader(unittest.TestCase):
    def test_read_py_no_line_numbers(self):
        me = catalog.MessageEntry
        dirpath = os.path.join(TESTDATA_DIR, "input")
        filepath = os.path.join(dirpath, "test2.py")
        input_ = dirpath
        output = {
            "Zero": me("Zero", references=[filepath]),
            "One": me("One", references=[filepath]),
            "msgid_three": me(
                "msgid_three", msgstr="Three", references=[filepath]
            ),  # noqa
            "msgid_four": me(
                "msgid_four", msgstr="Four ${map}", references=[filepath]
            ),  # noqa
            "msgid_five": me("msgid_five", msgstr="五番目", references=[filepath]),  # noqa
            "msgid_six": me(
                "msgid_six", msgstr="\nLine 1\nLine 2\nLine 3\n", references=[filepath]
            ),  # noqa
        }

        pyr = catalog.PYReader(input_, "testing", include_line_numbers=False)
        pyr.read()
        out = pyr.catalogs["testing"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in py parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out.get(key, False),
                "Failure in py parsing.\nMissing:%s" % output.get(key),
            )
            self.assertTrue(
                out.get(key) == output.get(key),
                "Failure in py parsing.\nGot:%s\nExpected:%s"
                % (out.get(key), output.get(key)),
            )
        self.assertEqual(len(out), len(output))

    def test_read_py_include_line_numbers(self):
        me = catalog.MessageEntry
        dirpath = os.path.join(TESTDATA_DIR, "input")
        filepath = os.path.join(dirpath, "test2.py")
        input_ = dirpath
        output = {
            "Zero": me("Zero", references=[filepath + ":6"]),
            "One": me("One", references=[filepath + ":7"]),
            "msgid_three": me(
                "msgid_three", msgstr="Three", references=[filepath + ":9"]
            ),  # noqa
            "msgid_four": me(
                "msgid_four", msgstr="Four ${map}", references=[filepath + ":11"]
            ),  # noqa
            "msgid_five": me(
                "msgid_five", msgstr="五番目", references=[filepath + ":13"]
            ),  # noqa
            "msgid_six": me(
                "msgid_six",
                msgstr="\nLine 1\nLine 2\nLine 3\n",
                references=[filepath + ":15"],
            ),  # noqa
        }

        pyr = catalog.PYReader(input_, "testing")
        pyr.read()
        out = pyr.catalogs["testing"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in py parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out.get(key, False),
                "Failure in py parsing.\nMissing:%s" % output.get(key),
            )
            self.assertTrue(
                out.get(key) == output.get(key),
                "Failure in py parsing.\nGot:%s\nExpected:%s"
                % (out.get(key), output.get(key)),
            )
        self.assertEqual(len(out), len(output))


class TestMessageGSReader(unittest.TestCase):
    def test_read_no_line_numbers(self):
        # GSReader has actually never supported line numbers.
        me = catalog.MessageEntry
        dirpath = os.path.join(TESTDATA_DIR, "input")
        filepath = os.path.join(dirpath, "test.xml")
        input_ = dirpath
        output = {
            "RSS feed": me("RSS feed", references=[filepath]),
            "Print this": me("Print this", references=[filepath]),
        }

        reader = catalog.GSReader(input_, "plone")
        reader.read()
        out = reader.catalogs["plone"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in gs parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out.get(key, False),
                "Failure in gs parsing.\nMissing:%s" % output.get(key),
            )
            self.assertTrue(
                out.get(key) == output.get(key),
                "Failure in gs parsing.\nGot:%s\nExpected:%s"
                % (out.get(key), output.get(key)),
            )
        self.assertEqual(len(out), len(output))


class TestMessageZCMLReader(unittest.TestCase):
    def test_read_no_line_numbers(self):
        me = catalog.MessageEntry
        dirpath = os.path.join(TESTDATA_DIR, "input")
        filepath = os.path.join(dirpath, "test.zcml")
        input_ = dirpath
        output = {
            "Plone Site": me("Plone Site", references=[filepath]),
            "Profile for a default Plone.": me(
                "Profile for a default Plone.", references=[filepath]
            ),
            "Mandatory dependencies for a Plone site": me(
                "Mandatory dependencies for a Plone site", references=[filepath]
            ),
            "Adds title and description fields.": me(
                "Adds title and description fields.", references=[filepath]
            ),
            "Basic metadata": me("Basic metadata", references=[filepath]),
            "Content rule names should be translated.": me(
                "Content rule names should be translated.", references=[filepath]
            ),
        }

        reader = catalog.ZCMLReader(input_, "plone", include_line_numbers=False)
        reader.read()
        out = reader.catalogs["plone"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in zcml parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out.get(key, False),
                "Failure in zcml parsing.\nMissing:%s" % output.get(key),
            )
            self.assertTrue(
                out.get(key) == output.get(key),
                "Failure in zcml parsing.\nGot:%s\nExpected:%s"
                % (out.get(key), output.get(key)),
            )
        self.assertEqual(len(out), len(output))

    def test_read_include_line_numbers(self):
        me = catalog.MessageEntry
        dirpath = os.path.join(TESTDATA_DIR, "input")
        filepath = os.path.join(dirpath, "test.zcml")
        input_ = dirpath
        output = {
            "Plone Site": me("Plone Site", references=[filepath + ":14"]),
            "Profile for a default Plone.": me(
                "Profile for a default Plone.", references=[filepath + ":14"]
            ),
            "Mandatory dependencies for a Plone site": me(
                "Mandatory dependencies for a Plone site", references=[filepath + ":22"]
            ),
            "Adds title and description fields.": me(
                "Adds title and description fields.", references=[filepath + ":42"]
            ),
            "Basic metadata": me("Basic metadata", references=[filepath + ":42"]),
            "Content rule names should be translated.": me(
                "Content rule names should be translated.",
                references=[filepath + ":53"],
            ),
        }

        reader = catalog.ZCMLReader(input_, "plone")
        reader.read()
        out = reader.catalogs["plone"]
        for key in out:
            self.assertTrue(
                key in output, "Failure in zcml parsing.\nUnexpected msgid: %s" % key
            )
        for key in output:
            self.assertTrue(
                out.get(key, False),
                "Failure in zcml parsing.\nMissing:%s" % output.get(key),
            )
            self.assertTrue(
                out.get(key) == output.get(key),
                "Failure in zcml parsing.\nGot:%s\nExpected:%s"
                % (out.get(key), output.get(key)),
            )
        self.assertEqual(len(out), len(output))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestGlobal))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageEntry))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageCatalogInit)
    )
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageCatalog))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageCatalogSync)
    )
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessagePoWriter))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessagePTReader))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessagePYReader))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageGSReader))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestMessageZCMLReader)
    )
    return suite


if __name__ == "__main__":
    unittest.main()
