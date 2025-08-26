# apps/orders/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Order, OrderAction
from .forms import OrderForm, OrderActionFormSet


class OrderListView(ListView):
    """Представлення для відображення списку наказів."""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 15


class OrderDetailView(DetailView):
    """Представлення для детального перегляду наказу."""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(CreateView):
    """Представлення для створення нового наказу."""
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    """
    Представлення для редагування наказу та пов'язаних з ним дій.
    Це найскладніше представлення, оскільки воно використовує formset.
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_update_form.html'
    success_url = reverse_lazy('orders:order-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['action_formset'] = OrderActionFormSet(self.request.POST, instance=self.object)
        else:
            data['action_formset'] = OrderActionFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        action_formset = context['action_formset']

        if action_formset.is_valid():
            self.object = form.save()
            action_formset.instance = self.object
            action_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))