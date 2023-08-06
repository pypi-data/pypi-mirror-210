def text_choices_max_length(text_choices_class):
    return max(len(choice[0]) for choice in text_choices_class.choices)
