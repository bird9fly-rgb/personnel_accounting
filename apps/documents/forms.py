# apps/documents/forms.py
from django import forms
from .models import ServicemanReport


class ServicemanReportForm(forms.ModelForm):
    """
    Форма для створення та редагування рапорту військовослужбовця.
    """

    class Meta:
        model = ServicemanReport
        fields = [
            'registration_number',
            'submission_date',
            'report_type',
            'author',
            'recipient_position',
            'summary',
            'full_text',
            'attachment',  # Додаємо нове поле
            'status',
        ]
        widgets = {
            'submission_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-input'}
            ),
            'full_text': forms.Textarea(
                attrs={'rows': 10, 'class': 'form-textarea'}
            ),
            'attachment': forms.ClearableFileInput(  # Використовуємо спеціальний віджет для файлів
                attrs={'class': 'form-input'}
            ),
        }
        labels = {
            'registration_number': "Реєстраційний номер",
            'submission_date': "Дата подання",
            'report_type': "Тип рапорту",
            'author': "Автор рапорту",
            'recipient_position': "На чиє ім'я (посада)",
            'summary': "Короткий зміст (тема)",
            'full_text': "Повний текст рапорту",
            'attachment': "Прикріпити файл",
            'status': "Статус рапорту",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('type') not in ['date', 'file']:
                base_classes = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
                field.widget.attrs.update({'class': base_classes})


class ReportResolutionForm(forms.ModelForm):
    """
    Окрема, спрощена форма для додавання резолюції.
    """

    class Meta:
        model = ServicemanReport
        fields = ['resolution', 'status']
        widgets = {
            'resolution': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Введіть ваше рішення по рапорту...'}
            ),
        }
        labels = {
            'resolution': "Резолюція / Рішення",
            'status': "Змінити статус на",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            (ServicemanReport.ReportStatus.APPROVED, 'Затверджено'),
            (ServicemanReport.ReportStatus.REJECTED, 'Відхилено'),
            (ServicemanReport.ReportStatus.UNDER_REVIEW, 'На розгляді'),
        ]
        for field_name, field in self.fields.items():
            base_classes = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            field.widget.attrs.update({'class': base_classes})