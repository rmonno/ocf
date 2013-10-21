from django import forms


# you can use form and formset_factory utility (with 'initial' values)
# & use {{ form.as_table }} in your template


class RoadmResource(forms.Form):
    name = forms.CharField(max_length=100)
