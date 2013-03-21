from cms_prototype.tests.common import TemplateTestCase


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

class FormModelsTestCase(TemplateTestCase):

    def test_simple_form(self):
        from cms_prototype.models.form import FormBlock, Input

        form_a = FormBlock()

        field = Input(type='text', name='name', label='Name')
        form_a.fields.append(field)
        form_a.save()

        form_b = FormBlock.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)

        self.assertEqual(form_a.render().strip(), FORM_HTML)

    def test_checkbox_form(self):
        from cms_prototype.models.form import FormBlock, Checkbox

        form_a = FormBlock()

        field = Checkbox(name='name', label='Name', checked=True)
        form_a.fields.append(field)
        form_a.save()

        form_b = FormBlock.objects(id=form_a.id).first()
        self.assertEqual(form_a, form_b)
        self.assertEqual(form_b.fields[0], field)
        self.assertEqual(form_b.fields[0].type, 'checkbox')

        self.assertEqual(form_a.render().strip(), CBOX_HTML)
