from django.shortcuts import render


from .models import Product


from django.views.generic import ListView, DetailView


from django.contrib.auth.mixins import LoginRequiredMixin


class Home(ListView):
    model = Product
    template_name = "home.html"


class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "product_detail.html"
