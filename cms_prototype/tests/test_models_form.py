from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace


## FIXME: it appears pyjade doesn't format label tags nicely. Fixing that in pyjade
# seems like the best course of action, but for the time being mangling the test html
# will suffice.

FORM_HTML = """
<form action="" method="POST">
  <label for="name">Name</label>
  <input type="text" id="name" name="name"/>
</form>
""".strip()

CBOX_HTML = """
<form action="" method="POST">
  <label for="name">
    <input type="checkbox" id="name" name="name"/>Name

  </label>
</form>
""".strip()

NO_LABEL_HTML = """
<form action="" method="POST">
  <input type="text" id="name" name="name"/>
</form>
""".strip()

TEXT_FROM_WITH_VALUE = """
<form action="" method="POST">
  <input type="text" id="text" name="text" value="foo"/>
</form>
"""


class FormRenderTestCase(TemplateTestCase):
    def test_simple_form(self):
        from cms_prototype.models.blocks.form import Form, Input

        form_a = Form()

        field = Input(type='text', name='name', label='Name')
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)

        self.assertEqual(form_a.render().strip(), FORM_HTML)

    def test_checkbox_form(self):
        from cms_prototype.models.blocks.form import Form, Checkbox

        form_a = Form()

        field = Checkbox(name='name', label='Name', checked=True)
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)
        self.assertEqual(form_b.fields[0].type, 'checkbox')

        self.assertEqual(form_a.render().strip(), CBOX_HTML)

    def test_no_label_form(self):
        from cms_prototype.models.blocks.form import Form, Input

        form_a = Form()

        field = Input(type='text', name='name')
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)

        self.assertEqual(form_a.render().strip(), NO_LABEL_HTML)

    def test_value_from_population(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.text import HTMLBlock

        t = HTMLBlock(text='foo')
        t.save()

        f = MongoEngineForm(mongo_object_class='cms_prototype.models.blocks.text:HTMLBlock',
                            fields=[Input(name='text')],
                            identity=['textID'])
        f.populate({'textID': t.id})

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(strip_html_whitespace(f.render()),
                         strip_html_whitespace(TEXT_FROM_WITH_VALUE))


class FormPostTestCase(TemplateTestCase):
    def test_no_class(self):
        from cms_prototype.models.blocks.form import MongoEngineForm
        f = MongoEngineForm(mongo_object_class='foo:bar')
        f.save()

        post = {}
        with self.assertRaises(Exception):
            f.process(post)

    def test_no_id(self):
        from cms_prototype.models.blocks.form import MongoEngineForm

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            type='Update')
        f.save()
        post = {}
        with self.assertRaises(Exception):
            f.process(post)

    def test_correct_post(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['id'])
        f.save()

        post = {}
        post['id'] = l.id
        post['href'] = 'bar'
        post['text'] = 'foo'
        f.process(post)

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "bar")
        self.assertEqual(l.text, "foo")

    def test_no_form_elements(self):
        from cms_prototype.models.blocks.form import MongoEngineForm
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link")
        f.save()

        post = {}
        post['id'] = l.id
        post['href'] = 'bar'
        post['text'] = 'foo'
        f.process(post)

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

    def test_upsert(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')])
        f.save()

        self.assertEqual(Link.objects().count(), 0)

        post = {}
        post['href'] = 'foo'
        post['text'] = 'bar'
        f.process(post)

        self.assertEqual(Link.objects().count(), 1)
        l = Link.objects().first()
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

    def test_multivalue_id(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['labelID'])

        f.process({'labelID': l.id, 'text': 'buz'})
        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "buz")


class FormPopulateTestCase(TemplateTestCase):
    def test_get_identifier(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['labelID'])
        self.assertDictEqual(f._get_identifier({'labelID': l.id}), {'id': l.id})

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['href', 'text'])
        self.assertDictEqual(f._get_identifier({'href': 'foo', 'text': 'bar'}), {'href': 'foo', 'text': 'bar'})

    def test_populate(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['labelID'])
        f.save()
        p = {'labelID': l.id}
        f.populate(p)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_populate_missing_param(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['labelID'])

        f.populate({})
        with self.assertRaises(AttributeError):
            a = f.fields[0].value
        with self.assertRaises(AttributeError):
            a = f.fields[1].value

    def test_populate_multivalue(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['href', 'text'])
        f.save()
        p = {'href': 'foo', 'text': 'bar'}
        f.populate(p)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_populate_multi_missing(self):
        from cms_prototype.models.blocks.form import MongoEngineForm, Input
        from cms_prototype.models.blocks.link import Link

        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity=['href', 'text'])
        f.save()
        p = {'href': 'foo'}
        f.populate(p)
        with self.assertRaises(AttributeError):
            a = f.fields[0].value
        with self.assertRaises(AttributeError):
            a = f.fields[1].value
