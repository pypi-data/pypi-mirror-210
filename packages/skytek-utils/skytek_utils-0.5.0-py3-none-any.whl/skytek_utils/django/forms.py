from django import forms


class DateInput(forms.DateInput):
    """Django form input which render html5 date input field"""

    input_type = "date"
