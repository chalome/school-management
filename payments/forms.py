from django import forms

from children.models import Child
from core.models import active_school_year

from .months import school_year_month_choices
from .models import MonthlyFeePayment


class PaymentForm(forms.ModelForm):
    month = forms.ChoiceField(label='Mois concerné')

    class Meta:
        model = MonthlyFeePayment
        exclude = ('receipt_number', 'school_year')
        labels = {
            'child': 'Enfant & matricule scolaire',
            'month': 'Mois concerné',
            'fee_type': 'Nature des frais',
            'amount_due': 'Montant dû (Fbu)',
            'amount_paid': 'Montant encaissé (Fbu)',
            'late_penalty': 'Pénalité de retard (Fbu)',
            'status': 'État du paiement',
            'payment_date': "Date d'encaissement",
            'payment_method': 'Mode de règlement',
            'transaction_reference': 'Référence de transaction / bordereau',
            'note': 'Commentaire ou note interne',
            'proof_of_payment': 'Preuve de paiement',
        }
        widgets = {
            'amount_due': forms.NumberInput(attrs={'min': 0, 'step': '1'}),
            'amount_paid': forms.NumberInput(attrs={'min': 0, 'step': '1'}),
            'late_penalty': forms.NumberInput(attrs={'min': 0, 'step': '1'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, school_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_year = school_year or active_school_year()
        self.fields['child'].queryset = Child.objects.filter(
            enrollments__school_year=self.school_year,
        ).distinct()
        existing_months = MonthlyFeePayment.objects.values_list(
            'month',
            flat=True,
        ).filter(school_year=self.school_year).distinct()
        if self.instance and self.instance.pk:
            existing_months = list(existing_months) + [self.instance.month]
        self.fields['month'].choices = school_year_month_choices(
            self.school_year,
            existing_months,
        )

    def clean(self):
        cleaned_data = super().clean()
        amount_due = cleaned_data.get('amount_due')
        amount_paid = cleaned_data.get('amount_paid')
        late_penalty = cleaned_data.get('late_penalty')
        if (
            amount_due is not None
            and amount_paid is not None
            and late_penalty is not None
            and amount_paid > amount_due + late_penalty
        ):
            self.add_error('amount_paid', 'Le montant payé ne peut pas dépasser le total dû.')
        return cleaned_data
