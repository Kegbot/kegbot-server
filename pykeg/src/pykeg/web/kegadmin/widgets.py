from django import forms
from django.utils.encoding import force_unicode

### Numeric ChoiceField with "Other" option.
# Based on: http://sciyoshi.com/2008/7/django-choicefield-other-choice/

class ChoiceWithOtherRenderer(forms.RadioSelect.renderer):
    """RadioFieldRenderer that renders its last choice with a placeholder."""
    def __init__(self, *args, **kwargs):
        super(ChoiceWithOtherRenderer, self).__init__(*args, **kwargs)
        self.choices, self.other = self.choices[:-1], self.choices[-1]

    def __iter__(self):
        for input in super(ChoiceWithOtherRenderer, self).__iter__():
            yield input
        id = '%s_%s' % (self.attrs['id'], self.other[0]) if 'id' in self.attrs else ''
        label_for = ' for="%s"' % id if id else ''
        checked = '' if not force_unicode(self.other[0]) == self.value else 'checked="true" '
        yield '<label%s><input type="radio" id="%s" value="%s" name="%s" %s/> %s</label> %%s' % (
            label_for, id, self.other[0], self.name, checked, self.other[1])

class ChoiceWithOtherWidget(forms.MultiWidget):
  """MultiWidget for use with ChoiceWithOtherField."""
  def __init__(self, choices):
    widgets = [
        forms.RadioSelect(choices=choices, renderer=ChoiceWithOtherRenderer),
        forms.TextInput
    ]
    super(ChoiceWithOtherWidget, self).__init__(widgets)

  def decompress(self, value):
    if not value:
        return [None, None]
    return value

  def format_output(self, rendered_widgets):
    """Format the output by substituting the "other" choice into the first widget."""
    return rendered_widgets[0] % rendered_widgets[1]

class ChoiceWithOtherField(forms.MultiValueField):
  def __init__(self, *args, **kwargs):
    fields = [
        forms.ChoiceField(widget=forms.RadioSelect(renderer=ChoiceWithOtherRenderer), *args, **kwargs),
        forms.FloatField(required=False, min_value=0.000001, max_value=1.0)
    ]
    widget = ChoiceWithOtherWidget(choices=kwargs['choices'])
    kwargs.pop('choices')
    self._was_required = kwargs.pop('required', True)
    kwargs['required'] = False
    super(ChoiceWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

  def compress(self, value):
    if self._was_required and not value or value[0] in (None, ''):
        raise forms.ValidationError(self.error_messages['required'])
    if not value:
        return [None, u'']
    return (value[0], value[1] if force_unicode(value[0]) == force_unicode(self.fields[0].choices[-1][0]) else u'')

