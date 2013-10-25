from django import forms


class AllocateForm(forms.Form):
    name = forms.CharField(max_length=100)
    type = forms.CharField(max_length=20, initial='roadm')
    ingress_endpoint = forms.CharField(max_length=20)
    ingress_label = forms.CharField(max_length=20)
    egress_endpoint = forms.CharField(max_length=20)
    egress_label = forms.CharField(max_length=20)
