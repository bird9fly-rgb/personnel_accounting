# apps/orders/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderAction
from apps.personnel.models import Serviceman, Rank
from apps.staffing.models import Position


class OrderForm(forms.ModelForm):
    """Форма для створення та редагування наказу."""

    class Meta:
        model = Order
        fields = ['order_number', 'order_date', 'order_type', 'issuing_authority', 'order_text']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'order_text': forms.Textarea(attrs={'rows': 10, 'class': 'form-textarea'}),
            'order_number': forms.TextInput(attrs={'class': 'form-input'}),
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            base_classes = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            field.widget.attrs.update({'class': base_classes})


class OrderActionForm(forms.ModelForm):
    """
    Динамічна форма для дії в наказі.
    Показує різні поля в залежності від обраного 'action_type'.
    """
    # Поля для різних типів дій
    new_position = forms.ModelChoiceField(
        queryset=Position.objects.select_related('unit').all(),
        label="Нова посада",
        required=False,
        widget=forms.Select(attrs={'class': 'action-field-new_position'})
    )
    new_rank = forms.ModelChoiceField(
        queryset=Rank.objects.all(),
        label="Нове звання",
        required=False,
        widget=forms.Select(attrs={'class': 'action-field-new_rank'})
    )
    dismissal_reason = forms.CharField(
        label="Причина звільнення",
        required=False,
        widget=forms.TextInput(attrs={'class': 'action-field-dismissal_reason'})
    )

    class Meta:
        model = OrderAction
        fields = ['personnel', 'action_type']
        # Поле 'details' буде заповнюватися програмно, тому воно не потрібне користувачу

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо CSS класи для динамічного відображення
        self.fields['action_type'].widget.attrs.update({'class': 'action-type-select'})

    def clean(self):
        """
        Збираємо дані з динамічних полів і формуємо JSON для поля 'details'.
        """
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        details_json = {}

        if action_type in [OrderAction.ActionType.APPOINT, OrderAction.ActionType.TRANSFER]:
            new_position = cleaned_data.get('new_position')
            if not new_position:
                raise forms.ValidationError("Для призначення/переведення необхідно вказати нову посаду.")
            details_json['new_position_id'] = new_position.id

        elif action_type == OrderAction.ActionType.PROMOTE:
            new_rank = cleaned_data.get('new_rank')
            if not new_rank:
                raise forms.ValidationError("Для присвоєння звання необхідно вказати нове звання.")
            details_json['new_rank_id'] = new_rank.id

        elif action_type == OrderAction.ActionType.DISMISS:
            reason = cleaned_data.get('dismissal_reason')
            if not reason:
                raise forms.ValidationError("Необхідно вказати причину звільнення.")
            details_json['reason'] = reason

        # Записуємо зібрані дані в 'details'
        self.instance.details = details_json
        return cleaned_data


OrderActionFormSet = inlineformset_factory(
    Order,
    OrderAction,
    form=OrderActionForm,
    extra=1,
    can_delete=True,
    fk_name='order'
)