from django import forms
from .models import ProductReview

# Review Add Form
class ReviewForm(forms.ModelForm):
	class Meta:
		model=ProductReview
		fields=['comment','rating']
		
		