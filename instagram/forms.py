# instagram/forms.py
from django import forms

class InstagramUserForm(forms.Form):
    username_file = forms.FileField()
    num_posts_to_scrape = forms.IntegerField(min_value=1, max_value=100, initial=10)
