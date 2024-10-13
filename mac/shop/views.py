from django.shortcuts import render
from django.http import HttpResponse
from .models import product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import checksum
# Create your views here.

MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

def index(request):
	products = product.objects.all()
	allprods = []
	catprods = product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prod = products.filter(category = cat)
		n = len(prod)
		nslides = n//4 + ceil((n/4)-(n//4))
		allprods.append([prod, nslides, range(1, nslides)])
	params = {"allprods": allprods}
	return render(request, "shop/index.html", params)

def searchMatch(query, item):
	if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
		return True
	else:
		return False

def search(request):
	query = request.GET.get('search')
	products = product.objects.all()
	allprods = []
	catprods = product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prod = products.filter(category = cat)
		newprod = [item for item in prod if searchMatch(query,item)]
		n = len(newprod)
		nslides = n//4 + ceil((n/4)-(n//4))
		if len(newprod) != 0:
			allprods.append([newprod, nslides, range(1, nslides)])
	
	params = {"allprods": allprods,"msg": ""}
	if len(allprods) == 0 :
		params = {"msg":"Please input valid and relevant query"}
	return render(request, "shop/search.html", params)

def about(request):
	return render(request, "shop/about.html")

def contact(request):
	if request.method=="POST":
		email = request.POST.get("email","")
		phone = request.POST.get("phone","")
		desc = request.POST.get("desc","")
		print(email, phone, desc)
		contact1 = Contact(email = email, phone = phone, desc = desc)
		contact1.save()
	return render(request, "shop/contact.html")

def tracker(request):
	if request.method=="POST":
		orderid = request.POST.get("orderid","")
		email = request.POST.get("email","")
		try:
			order = Order.objects.filter(order_id = orderid, email = email)
			if len(order)>0:
				update = OrderUpdate.objects.filter(order_id = orderid)
				updates = []
				for item in update:
					updates.append({'text':item.update_desc, 'time': item.timestamp})
					response = json.dumps({"status":"Success","updates":updates, "items_JSON":order[0].items_JSON},default = str)
				return HttpResponse(response)
			else:
				return HttpResponse('{"status":"noitems"}')
		except Exception as e:
			return HttpResponse('{"status":"error"}')
	return render(request, "shop/tracker.html")


def prodView(request, myid):
	#Fetching Product using ID
	uproduct = product.objects.filter(id = myid)
	print(uproduct)
	return render(request, "shop/productview.html",{"product":uproduct[0]})

def checkout(request):
	if request.method=="POST":
		items_JSON = request.POST.get("itemsJSON","")
		name = request.POST.get("name","")
		amount = request.POST.get("amount","")
		email = request.POST.get("email","")
		address = request.POST.get("address1","")+" "+ request.POST.get("address2","")
		city = request.POST.get("city","")
		state = request.POST.get("state","")
		phone = request.POST.get("phone","")
		zip_code = request.POST.get("zip_code","")
		thank = True
		order = Order(items_JSON = items_JSON, name = name, email = email, address = address, city = city, state = state, phone = phone, zip_code = zip_code, amount = amount)
		order.save()
		update = OrderUpdate(order_id = order.order_id, update_desc = "The Order has been placed")
		update.save()
		oid = order.order_id
		#return render(request, "shop/checkout.html",{'thank':thank, 'oid':oid})
		#Request Paytm to transfer the amount to your account after payment by user
		param_dict = {
			'MID':'WorldP64425807474247',
            'ORDER_ID':str(order.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	    	'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
		}
		param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
		return render(request,"shop/paytm.html", {"param_dict":param_dict})
	return render(request, "shop/checkout.html")

@csrf_exempt
def handlerequest(request):
	# paytm will send you post request here
	form = request.POST
	response_dict = {}
	for i in form.keys():
		response_dict[i] = form[i]
		if i == 'CHECKSUMHASH':
			checksum = form[i]

	verify = checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
	if verify:
		if response_dict['RESPCODE'] == '01':
			print("Order Successful")
		else:
			print("Order was Unsuccessful because" + response_dict['RESPMSG'])
	return render(request, 'shop/paymentstatus.html', {'response':response_dict})