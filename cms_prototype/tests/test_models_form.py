from collections import namedtuple
from pyramid.httpexceptions import HTTPFound
from cms_prototype.tests.common import TemplateTestCase, strip_html_whitespace
from cms_prototype.models.blocks.form import Form, Input, Checkbox, MongoEngineForm, Select
from cms_prototype.models.blocks.text import HTMLBlock
from cms_prototype.models.blocks.link import Link
from pyramid import testing


## FIXME: it appears pyjade doesn't format label tags nicely. Fixing that in pyjade
# seems like the best course of action, but for the time being mangling the test html
# will suffice.

FORM_HTML = """
<form action="" method="POST" class="form-horizontal">
  <div class="control-group">
    <label for="name" class="control-label">Name</label>
    <div class="controls">
      <input type="text" name="name"/>
    </div>
  </div>
</form>
""".strip()

CBOX_HTML = """
<form action="" method="POST" class="form-horizontal">
  <div class="control-group">
    <div class="controls">
      <label for="name" class="control-label">
        <input type="checkbox" name="name"/>Name
      </label>
    </div>
  </div>
</form>
""".strip()

NO_LABEL_HTML = """
<form action="" method="POST" class="form-horizontal">
  <div class="control-group">
    <div class="controls">
      <input type="text" name="name"/>
    </div>
  </div>
</form>
""".strip()

TEXT_FROM_WITH_VALUE = """
<form action="" method="POST" class="form-horizontal">
  <div class="control-group">
    <div class="controls">
      <input type="text" name="text" value="foo"/>
    </div>
  </div>
</form>
"""

select = """
<form action="" method="POST" class="form-horizontal">
  <div class="control-group">
    <div class="controls">
      <select>
        <option value="bar">foo</option>
        <option value="bang">buz</option>
      </select>
    </div>
  </div>
</form>
"""


class FormRenderTestCase(TemplateTestCase):
    def setUp(self):
        super(FormRenderTestCase, self).setUp()
        self.request = testing.DummyRequest()
        self.request.PARAMS = {}
        self.request.cms = namedtuple('cms', ['page', 'site', 'url'])

    def test_simple_form(self):
        form_a = Form()

        field = Input(type='text', name='name', label='Name')
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)

        self.assertEqual(strip_html_whitespace(form_a.render().strip()), strip_html_whitespace(FORM_HTML))

    def test_checkbox_form(self):
        form_a = Form()

        field = Checkbox(name='name', label='Name', checked=True)
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)
        self.assertEqual(form_b.fields[0].type, 'checkbox')

        self.assertEqual(strip_html_whitespace(form_a.render().strip()), strip_html_whitespace(CBOX_HTML))

    def test_select(self):
        form_a = Form()

        field = Select(name='name', label='Name', name_field='foo', value_field='bar')
        field.options = []
        o = namedtuple('option', ['name', 'value'])
        o.name = 'foo'
        o.value = 'bar'
        field.options.append(o)
        o = namedtuple('option', ['name', 'value'])
        o.name = 'buz'
        o.value = 'bang'
        field.options.append(o)

        form_a.fields.append(field)
        form_a.save()

        form_a.to_mongo()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)
        self.assertEqual(form_b.fields[0].type, 'select')

        self.assertEqual(strip_html_whitespace(form_a.render().strip()),
                         strip_html_whitespace(select))

    def test_no_label_form(self):
        form_a = Form()

        field = Input(type='text', name='name')
        form_a.fields.append(field)
        form_a.save()

        form_b = Form.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)

        self.assertEqual(strip_html_whitespace(form_a.render().strip()), strip_html_whitespace(NO_LABEL_HTML))

    def test_value_from_population(self):
        t = HTMLBlock(text='foo')
        t.save()

        f = MongoEngineForm(mongo_object_class='cms_prototype.models.blocks.text:HTMLBlock',
                            fields=[Input(name='text')],
                            identity={'id': 'textID'})

        self.request.PARAMS = {'textID': t.id}
        f.populate(self.request)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(strip_html_whitespace(f.render()),
                         strip_html_whitespace(TEXT_FROM_WITH_VALUE))


class Post(TemplateTestCase):
    def setUp(self):
        super(Post, self).setUp()
        self.request = testing.DummyRequest()
        self.request.PARAMS = {}
        self.request.cms = namedtuple('cms', ['page', 'site', 'url'])

    def test_no_class(self):
        f = MongoEngineForm(mongo_object_class='foo:bar')
        f.save()

        req = {'POST': {}}
        with self.assertRaises(Exception):
            f.post(req)

    def test_no_id(self):
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            type='Update')
        f.save()
        req = {'POST': {}}
        with self.assertRaises(Exception):
            f.post(req)

    def test_correct_post(self):
        l = Link(href="foo", text="bar")
        l.save()

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'id': 'id'})
        f.save()

        self.request.POST = {'id': l.id, 'href': 'bar', 'text': 'foo'}
        f.post(self.request)

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "bar")
        self.assertEqual(l.text, "foo")

    def test_no_form_elements(self):
        l = Link(href="foo", text="bar")
        l.save()

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link")
        f.save()

        self.request.POST = {'id': l.id, 'href': 'bar', 'text': 'foo'}
        f.post(self.request)

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

    def test_upsert(self):
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')])
        f.save()

        self.assertEqual(Link.objects().count(), 0)

        self.request.POST['href'] = 'foo'
        self.request.POST['text'] = 'bar'
        f.post(self.request)

        self.assertEqual(Link.objects().count(), 1)
        l = Link.objects().first()
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

    def test_multivalue_id(self):
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'id': 'labelID'})
        self.request.POST = {'labelID': l.id, 'text': 'buz'}
        f.post(self.request)
        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "buz")

    def test_next_page(self):

        l = Link(href="foo", text="bar")
        l.save()

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "foo")
        self.assertEqual(l.text, "bar")

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'id': 'id'},
                            next_page='foo')
        f.save()

        self.request.POST = {'id': l.id, 'href': 'bar', 'text': 'foo'}
        with self.assertRaises(HTTPFound):
            f.post(self.request)

        l = Link.objects.get(id=l.id)
        self.assertEqual(l.href, "bar")
        self.assertEqual(l.text, "foo")


class Populate(TemplateTestCase):
    def setUp(self):
        super(Populate, self).setUp()
        self.request = testing.DummyRequest()
        self.request.cms = namedtuple('cms', ['page', 'site', 'url'])
        self.request.PARAMS = {}

    def test_get_identifier(self):
        from cms_prototype.models.blocks.block import Block

        ident = {'href': 'x', 'text': 'text'}
        self.assertDictEqual(Block.mapfield_to_dict(ident, {'x': 'foo', 'text': 'bar'}), {'href': 'foo', 'text': 'bar'})

    def test_populate(self):
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'id': 'labelID'})
        f.save()
        self.request.PARAMS = {'labelID': l.id}
        f.populate(self.request)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_populate_missing_param(self):
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'id': 'labelID'})

        f.populate(self.request)
        with self.assertRaises(AttributeError):
            a = f.fields[0].value
        with self.assertRaises(AttributeError):
            a = f.fields[1].value

    def test_populate_multivalue(self):
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'href': 'href', 'text': 'text'})
        f.save()
        self.request.PARAMS = {'href': 'foo', 'text': 'bar'}
        f.populate(self.request)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_populate_multi_missing(self):
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text')],
                            identity={'href': 'href', 'text': 'href'})
        f.save()
        self.request.PARAMS = {'href': 'foo'}
        f.populate(self.request)
        with self.assertRaises(AttributeError):
            a = f.fields[0].value
        with self.assertRaises(AttributeError):
            a = f.fields[1].value

    def test_populate_with_submit(self):
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href'),
                                    Input(type='text', name='text'),
                                    Input(type='submit', name='save')],
                            identity={'href': 'href', 'text': 'text'})
        f.save()
        self.request.PARAMS = {'href': 'foo', 'text': 'bar'}
        f.populate(self.request)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_nopost_with_defaults(self):
        from collections import namedtuple
        l = Link(href="foo", text="bar")
        l.save()

        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href', default='cms.site.name'),
                                    Input(type='text', name='text', default='foo'),
                                    Input(type='submit', name='save')],
                            identity={'href': 'href', 'text': 'href'})
        f.save()
        self.request.PARAMS = {'foo': 'bar'}
        self.request.cms = namedtuple('cms', ['page', 'site', 'url'])
        self.request.cms.site = namedtuple('site', ['name'])
        self.request.cms.site.name = 'foo'
        f.populate(self.request)

        self.assertEqual(f.fields[0].value, 'foo')
        self.assertEqual(f.fields[1].value, 'bar')

    def test_populate_with_missing_param(self):
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.blocks.link:Link",
                            fields=[Input(type='text', name='href')],
                            identity={'href': 'href', 'text': 'href'})

        f.save()
        f.populate(self.request)

        with self.assertRaises(AttributeError):
            a = f.fields[0].value

    def test_populate_with_missing_internal_param(self):
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.site:Url",
                            fields=[Input(type='text', name='site')],
                            identity={'site': 'request.cms.site.id'})
        f.save()

        self.request.cms.site = None
        f.populate(self.request)
        with self.assertRaises(AttributeError):
            a = f.fields[0].value


class Inputs(TemplateTestCase):
    def setUp(self):
        super(Inputs, self).setUp()
        self.request = testing.DummyRequest()
        self.request.cms = namedtuple('cms', ['page', 'site', 'url'])
        self.request.PARAMS = {}

    def test_populate_input_select(self):
        from cms_prototype.models.site import Page
        f = MongoEngineForm(mongo_object_class="cms_prototype.models.site:Url",
                            fields=[Select(type='select', name='page', name_field='name', value_field='id')],
                            identity={'site': 'request.cms.site.id'})
        f.save()

        f.populate(self.request)
        self.assertEqual(len(f.fields[0].options), 0)

        f = MongoEngineForm.objects(id=f.id).first()

        p = Page(name='test')
        p.save()

        f.populate(self.request)

        self.assertEqual(len(f.fields[0].options), 1)
        self.assertEqual(f.fields[0].options[0].value, p.id)
        self.assertEqual(f.fields[0].options[0].name, p.name)
