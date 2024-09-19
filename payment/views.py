from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse

from order.models import Order, Cart

from django.contrib import messages

from django.contrib.auth.decorators import login_required


from sslcommerz_lib import SSLCOMMERZ

from decimal import Decimal
import random
import string


from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator

from django.contrib.auth.models import User



def unique_transaction_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@login_required
def checkout(request):
    

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_total = order_qs[0].get_totals()
    context = {
        'order_items': order_items,
        'order_total': order_total,
    }
    return render(request, 'checkout.html', context)




@login_required
def payment(request):
    


    store_id = 'democ66334da1b3c90'

    store_pass = 'democ66334da1b3c90@ssl'
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    order_total = order_qs[0].get_totals()
    print(order_total)
    # status_url = request.build_absolute_uri(reverse('payment:complete'))
    
    
    settings = {'store_id': store_id,
                'store_pass': store_pass, 'issandbox': True}
    
    
    sslcommez = SSLCOMMERZ(settings)
    print(sslcommez)
    post_body = {}
    post_body['total_amount'] = order_total
    post_body['currency'] = "BDT"
    post_body['tran_id'] = unique_transaction_id_generator()
    post_body['success_url'] = f'http://127.0.0.1:8000/payment/purchase/{post_body['tran_id']}/{request.user.id}/'
    post_body['fail_url'] = f'http://127.0.0.1:8000/order/cart/{request.user.id}/0/'
    post_body['cancel_url'] = f'http://127.0.0.1:8000/order/cart/{request.user.id}/0/'
    post_body['emi_option'] = 0
    post_body['cus_email'] = request.user.email
    post_body['cus_phone'] = '0178888889' 
    post_body['cus_add1'] = 'Dhaka' 
    post_body['cus_city'] = 'Mohammadpur'
    post_body['cus_country'] = 'Bangladesh'
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"

    # OPTIONAL PARAMETERS
    # post_body['value_a'] = id
    # post_body['value_b'] = request.user.id
    # post_body['value_c'] = 'email'

    response = sslcommez.createSession(post_body)
    print(response)




    return redirect(response['GatewayPageURL'])


@csrf_exempt
def complete(request):
    

    
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']

        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Your Payment Completed Successfully!")
            return HttpResponseRedirect(reverse('payment:purchase', kwargs={'val_id': val_id, 'tran_id': tran_id}))
        elif status == 'FAILED':
            messages.warning(request, "Your Payment Failed Please try again!")

    context = {

    }
    return render(request, 'complete.html', context)


@csrf_exempt
def purchase(request, tran_id,user_id):
    
    
    user=User.objects.get(id=user_id)
    
    print(request.user)
    
    order_qs = Order.objects.filter(user=user, ordered=False)
    print(order_qs)
    order = order_qs[0]
    order.ordered = True
    order.orderId = tran_id
    order.paymentId = tran_id
    order.save()
    cart_items = Cart.objects.filter(user=user, purchased=False)
    print(cart_items)
    for item in cart_items:
        item.purchased = True
        item.save()
    return HttpResponseRedirect(reverse('payment:orders'))




@csrf_exempt
def order_view(request):
    
    
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {
            'orders': orders
        }

    except:
        messages.warning(request, "You don't have an active order!")
        return redirect('shop:home')

    return render(request, 'order.html', context)











