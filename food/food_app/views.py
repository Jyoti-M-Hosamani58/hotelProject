from django.shortcuts import render,redirect,get_object_or_404
from django.utils.dateparse import parse_date
from food_app.models import UserLogin,UserReg,AddTable,AddItem,AddCompany,ItemOrder,Orders,Pracel,Printorders, Expenses,Salary,Purchase,Billpending,Deletedata
from django.urls import reverse

import json
from django.http import JsonResponse, HttpResponse

from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from datetime import datetime



# Create your views here.

def index(request):
    return render(request,'index.html')

def admin_nav(request):
    return render(request,'admin_nav.html')



def admin_home(request):
    tdata = AddTable.objects.all()
    saved_table_name = request.GET.get('table', None)  # Extract from URL parameter
    stored_tables = [item.table_name for item in ItemOrder.objects.all()]  # List of stored table names
    return render(request, 'admin_home.html', {'tdata': tdata, 'saved_table_name': saved_table_name, 'stored_tables': stored_tables})

def userHome(request):
    tdata = AddTable.objects.all()
    saved_table_name = request.GET.get('table', None)  # Extract from URL parameter
    stored_tables = [item.table_name for item in ItemOrder.objects.all()]  # Example: list of stored table names

    return render(request, 'userHome.html', {'tdata': tdata, 'saved_table_name': saved_table_name, 'stored_tables': stored_tables})

def register(request):
    if request.method=="POST":
        email=request.POST.get('t1')
        number= request.POST.get('t2')
        password = request.POST.get('t3')
        username = request.POST.get('t4')
        utype=request.POST.get('utype')
        ucount=UserReg.objects.filter(email=email).count()
        if ucount>=1:
            return render(request,'register.html',{'msg':'This is already exists'})
        else:
            UserReg.objects.create(email=email,number=number,password=password,usertype=utype,username=username)
            UserLogin.objects.create(utype=utype, username=email, password=password)
            return render(request,'register.html',{'msg':'Thank you for registration'})
    return render(request,'register.html')

def register_list(request):
    userdata=UserReg.objects.all()
    return render(request,'register_list.html',{'userdata':userdata})

def delete_register(request,pk):
    udata = UserReg.objects.get(id=pk)

    udata.delete()
    base_url = reverse('register_list')
    return redirect(base_url)

def login(request):
    if request.method == "POST":
        username = request.POST.get('t1')
        password = request.POST.get('t2')
        request.session['username'] = username
        ucount = UserLogin.objects.filter(username=username).count()
        if ucount >= 1:
            udata = UserLogin.objects.get(username=username)
            upass = udata.password
            utype = udata.utype
            if password == upass:
                if utype == 'staff':
                    return redirect('userHome')
                if utype == 'admin':
                    return redirect('admin_home')
            else:
                return render(request, 'login.html', {'msg': 'Invalid Password'})
        else:
            return render(request, 'login.html', {'msg': 'Invalid Username'})
    return render(request, 'login.html')


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('t1')
        password = request.POST.get('t2')
        request.session['username'] = username
        ucount = UserLogin.objects.filter(username=username).count()
        if ucount >= 1:
            udata = UserLogin.objects.get(username=username)
            upass = udata.password
            utype = udata.utype
            if password == upass:
                if utype == 'admin':
                    return redirect('admin_home')
                else:
                    return render(request, 'admin_login.html', {'msg': 'Invalid Login Type'})
            else:
                return render(request, 'admin_login.html', {'msg': 'Invalid Password'})
        else:
            return render(request, 'admin_login.html', {'msg': 'Invalid Username'})
    return render(request, 'admin_login.html')
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('t1')
        password = request.POST.get('t2')
        request.session['username'] = username
        ucount = UserLogin.objects.filter(username=username).count()
        if ucount >= 1:
            udata = UserLogin.objects.get(username=username)
            upass = udata.password
            utype = udata.utype
            if password == upass:
                if utype == 'staff':
                    return redirect('userHome')
                else:
                    return render(request, 'user_login.html', {'msg': 'Invalid Login Type'})
            else:
                return render(request, 'user_login.html', {'msg': 'Invalid Password'})
        else:
            return render(request, 'user_login.html', {'msg': 'Invalid Username'})
    return render(request, 'user_login.html')


def add_item(request):
    if request.method == "POST":
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")
        item_name = request.POST.get('t2')
        item_code = request.POST.get('t1')
        qty = request.POST.get('qty')
        item_price = request.POST.get('t4')

        # Generate a numeric unique identifier for the barcode (though not used for barcode generation anymore)

        # Create the item entry in the database without barcode information
        item = AddItem.objects.create(
            Item_name=item_name,
            qty=qty,
            Item_price=item_price,
            Item_code=item_code
        )

        # Instead of generating and saving the barcode, just return a success message
        return render(request, 'add_item.html', {'msg': 'Item added successfully!'})

    return render(request, 'add_item.html')

def view_item(request):
    # Fetch all items from AddItem
    userdata = AddItem.objects.all()
    # Fetch all purchases from Purchase
    userdata1 = Purchase.objects.all()

    grand_total = 0
    userdata_with_totals = []

    for item in userdata:
        # Filter the Purchase table to get the matching qty based on Item_code
        matching_purchase = userdata1.filter(Item_code=item.Item_code).first()  # Get the first match

        # Get the qty from the matching Purchase, or default to 0 if no match is found
        purchase_qty = matching_purchase.qty if matching_purchase else 0

        # Calculate item total
        item_total = item.qty * item.Item_price
        grand_total += item_total

        # Append details to the list
        userdata_with_totals.append({
            'id': item.id,
            'Item_code': item.Item_code,
            'Item_name': item.Item_name,
            'qty': item.qty,
            'purchase_qty': purchase_qty,  # Qty from Purchase model
            'Item_price': item.Item_price,
            'item_total': item_total  # Add item total
        })

    # Debug print the data
    print("DEBUG: userdata_with_totals:", userdata_with_totals)

    return render(request, 'view_item.html', {
        'userdata': userdata_with_totals,
        'grand_total': grand_total
    })



def delete_item(request,pk):
    udata = AddItem.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_item')
    return redirect(base_url)

def edit_item(request, pk):
    rdata = get_object_or_404(AddItem, id=pk)
    if request.method == "POST":
        item_code = request.POST.get('t1')
        item_name = request.POST.get('t2')
        qty = request.POST.get('t5')
        item_price = request.POST.get('t4')
        AddItem.objects.filter(id=pk).update(
            Item_code=item_code,
            Item_name=item_name,
            qty=qty,
            Item_price=item_price,
        )
        base_url = reverse('view_item')
        return redirect(base_url)
    return render(request, 'edit_item.html', {'rdata': rdata})



def updateStock(request, pk):
    # Fetch the existing item details
    rdata = get_object_or_404(AddItem, id=pk)

    if request.method == "POST":
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")

        # Retrieve data from the POST request
        item_code = request.POST.get('t1')
        item_name = request.POST.get('t2')
        new_qty = int(request.POST.get('t5'))  # New quantity to be added
        item_price = request.POST.get('t4')
        selling = request.POST.get('selling')

        # Add the new quantity to the existing quantity
        updated_qty = rdata.qty + new_qty

        # Update the AddItem record
        AddItem.objects.filter(id=pk).update(
            Item_code=item_code,
            Item_name=item_name,
            qty=updated_qty,
            Item_price=selling,
        )

        # Record the purchase in the Purchase table
        Purchase.objects.create(
            qty=new_qty,  # Save only the newly added quantity
            Item_name=item_name,
            Item_price=item_price,
            date=con_date,
            Item_code=item_code,
        )

        # Redirect to the view item page
        base_url = reverse('view_item')
        return redirect(base_url)

    return render(request, 'updateStock.html', {'rdata': rdata})

def purchase(request):
    if request.method == "POST":
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")
        item_name = request.POST.get('t2')
        item_code = request.POST.get('t1')
        qty = int(request.POST.get('qty'))  # Ensure qty is an integer
        item_price = request.POST.get('t4')
        selling = request.POST.get('selling')

        # Attempt to find an existing item by Item_code
        try:
            item = AddItem.objects.get(Item_code=item_code)

            # Add the new qty to the existing qty and dqty
            item.qty += qty

            # Save the updated item
            item.save()

            message = 'Item updated successfully with new quantity!'
        except AddItem.DoesNotExist:
            # If item does not exist, create a new one
            item = AddItem.objects.create(
                Item_code=item_code,
                Item_name=item_name,
                qty=qty,
                Item_price=selling
            )
            message = 'New item added successfully!'

        # Now create a purchase record (a new entry)
        purchase = Purchase.objects.create(
            qty=qty,
            Item_name=item_name,
            Item_price=item_price,
            date=con_date,
            Item_code=item_code
        )

        return render(request, 'purchase.html', {'msg': message})

    return render(request, 'purchase.html')

def purchaseList(request):
    # Fetch all items from AddItem
    userdata = Purchase.objects.all()
    # Fetch all purchases from Purchase
    userdata1 = AddItem.objects.all()

    grand_total = 0
    userdata_with_totals = []

    for item in userdata:
        # Filter the Purchase table to get the matching qty based on Item_code
        matching_item = userdata1.filter(Item_code=item.Item_code).first()  # Get the first match

        # Get the qty from the matching Purchase, or default to 0 if no match is found
        item_qty = matching_item.qty if matching_item else 0

        # Calculate item total
        item_total = item.qty * item.Item_price
        grand_total += item_total

        # Append details to the list
        userdata_with_totals.append({
            'id': item.id,
            'date': item.date,
            'Item_code': item.Item_code,
            'Item_name': item.Item_name,
            'qty': item.qty,
            'item_qty': item_qty,  # Qty from Purchase model
            'Item_price': item.Item_price,
            'item_total': item_total  # Add item total
        })

    # Debug print the data
    print("DEBUG: userdata_with_totals:", userdata_with_totals)


    return render(request, 'purchaseList.html', {
        'userdata': userdata_with_totals,
        'grand_total': grand_total,
        'userdata1':userdata1
    })

def add_table(request):
    if request.method=="POST":
        table_name=request.POST.get('t1')
        cat=request.POST.get('t2')
        AddTable.objects.create(Table_name=table_name,Category=cat)
        return render(request, 'add_table.html', {'msg': 'Added'})
    return render(request, 'add_table.html')

def view_table(request):
    udata=AddTable.objects.all()
    return render(request,'view_table.html',{'udata':udata})

def delete_table(request, pk):
    udata = AddTable.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_table')
    return redirect(base_url)

def edit_table(request, pk):
    rdata = get_object_or_404(AddTable, id=pk)
    if request.method == "POST":
        table_name = request.POST.get('t1')
        cat = request.POST.get('t2')
        AddTable.objects.filter(id=pk).update(
            Table_name=table_name,
            Category=cat
        )
        base_url = reverse('view_table')
        return redirect(base_url)
    return render(request, 'edit_table.html', {'rdata': rdata})

def add_company(request):
    if request.method=="POST":
        company_name=request.POST.get('t1')
        company_addres=request.POST.get('t2')
        company_gst=request.POST.get('t3')
        company_number=request.POST.get('t4')
        AddCompany.objects.create(Company_name=company_name,Company_address=company_addres,Company_GST=company_gst,Company_number=company_number)
        return render(request, 'add_company.html', {'msg': 'Added'})
    return render(request,'add_company.html')

def view_company(request):
    udata=AddCompany.objects.all()
    return render(request, 'view_company.html',{'udata':udata})

def edit_company(request,pk):
    udata=AddCompany.objects.get(id=pk)
    if request.method=="POST":
        company_name=request.POST.get('t1')
        company_address=request.POST.get('t2')
        company_gst=request.POST.get('t3')
        company_number=request.POST.get('t4')
        udata=AddCompany.objects.filter(id=pk).update(
            Company_name=company_name,
            Company_address=company_address,
            Company_GST=company_gst,
            Company_number=company_number
        )
        base_url = reverse('view_company')
        return redirect(base_url)
    return render(request,'edit_company.html',{'udata':udata})

def delete_company(request,pk):
    udata=AddCompany.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_company')
    return redirect(base_url)


def add_order(request):
    if request.method == 'GET':
        table_name = request.GET.get('table', '')  # Fetch the table name from the URL parameter

        # Get the last order's bill number (if exists) and generate the next one
        last_order = Orders.objects.order_by('-bill_no').first()
        if last_order:
            bill_no = int(last_order.bill_no) + 1
        else:
            bill_no = 1000

        # Render the add bill form with the table name and generated bill number
        context = {
            'Table_name': table_name,
            'Bill_no': bill_no,
        }
        return render(request, 'add_order.html', context)

    elif request.method == 'POST':
        # Handle form submission (optional: you can process form data as needed)
        return redirect('admin_home')

def add_order_user(request):
    if request.method == 'GET':
        table_name = request.GET.get('table', '')  # Fetch the table name from the URL parameter

        # Get the last order's bill number (if exists) and generate the next one
        last_order = Orders.objects.order_by('-bill_no').first()

        if last_order:
            last_bill_no = last_order.bill_no
            bill_no = str(int(last_bill_no) + 1)
        else:
            BASE_NUMBER = 1001
            bill_no = str(BASE_NUMBER)
        # Render the add bill form with the table name and generated bill number
        context = {
            'Table_name': table_name,
            'Bill_no': bill_no,
        }
        return render(request, 'add_order_user.html', context)

    elif request.method == 'POST':
        # Handle form submission (optional: you can process form data as needed)
        return redirect('userHome')

@require_http_methods(["GET"])
def fetch_item_details(request, item_code):
    try:
        # Use `iexact` for case-insensitive matching
        item = AddItem.objects.get(Item_code__iexact=item_code)
        data = {
            'item_name': item.Item_name,
            'price': item.Item_price,
        }
        return JsonResponse(data)
    except AddItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

from datetime import datetime, timedelta


@require_http_methods(["POST"])
def save_order(request):
    now = datetime.now().replace(microsecond=0)
    current_time = now.strftime("%H:%M:%S")

    # Adjust the bill date logic for the 2 AM to 2 AM cycle
    if now.hour < 2:
        # If the current time is before 2 AM, consider the bill date as the previous day
        bill_date = (now - timedelta(days=1)).date()
    else:
        # Otherwise, use the current date
        bill_date = now.date()

    data = json.loads(request.body)
    bill_details = data['billDetails']
    bill_items = data['billItems']

    table_name = bill_details['table_name']
    bill_no = bill_details['bill_no']

    for item in bill_items:
        item_code = item['item_code']
        item_name = item['item_name']
        price = float(item['price'])
        qty = int(item['qty'])
        tax_amt = float(item['tax_amt'])
        total = float(item['total'])

        # Create or update the item order, but allow duplicate entries (don't check if it exists)
        ItemOrder.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        # Create or update the corresponding record in the Orders table
        Orders.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        # Add entry to Printorders table
        Printorders.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        try:
            add_item = AddItem.objects.get(Item_code=item_code)

            # Check if the item has enough stock
            if add_item.qty >= qty:

                # Decrease qty
                add_item.qty -= qty

                # If dqty is None, initialize it to 0
                if add_item.dqty is None:
                    add_item.dqty = 0

                # Add the quantity to dqty
                add_item.dqty += qty

                # Save the updated item
                add_item.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': f"Insufficient stock for item: {item_name}"
                }, status=400)

        except AddItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f"Item with code {item_code} not found in AddItem table."
            }, status=404)

    return JsonResponse({'success': True, 'redirect_url': reverse('admin_home')})


@require_http_methods(["POST"])
def save_order_user(request):
    now = datetime.now().replace(microsecond=0)
    current_time = now.strftime("%H:%M:%S")

    # Adjust the bill date logic for the 2 AM to 2 AM cycle
    if now.hour < 2:
        # If the current time is before 2 AM, consider the bill date as the previous day
        bill_date = (now - timedelta(days=1)).date()
    else:
        # Otherwise, use the current date
        bill_date = now.date()

    data = json.loads(request.body)
    bill_details = data['billDetails']
    bill_items = data['billItems']

    table_name = bill_details['table_name']
    bill_no = bill_details['bill_no']

    for item in bill_items:
        item_code = item['item_code']
        item_name = item['item_name']
        price = float(item['price'])
        qty = int(item['qty'])
        tax_amt = float(item['tax_amt'])
        total = float(item['total'])

        # Create or update the item order, but allow duplicate entries (don't check if it exists)
        ItemOrder.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        # Create or update the corresponding record in the Orders table
        Orders.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        # Add entry to Printorders table
        Printorders.objects.create(
            table_name=table_name,
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total
        )

        try:
            add_item = AddItem.objects.get(Item_code=item_code)

            # Check if the item has enough stock
            if add_item.qty >= qty:

                # Decrease qty
                add_item.qty -= qty

                # If dqty is None, initialize it to 0
                if add_item.dqty is None:
                    add_item.dqty = 0

                # Add the quantity to dqty
                add_item.dqty += qty

                # Save the updated item
                add_item.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': f"Insufficient stock for item: {item_name}"
                }, status=400)

        except AddItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f"Item with code {item_code} not found in AddItem table."
            }, status=404)

    return JsonResponse({'success': True, 'redirect_url': reverse('userHome')})


@require_http_methods(["GET"])
def fetch_table_data(request):
    table_name = request.GET.get('table')
    if not table_name:
        return JsonResponse({'error': 'Table name is required'})

    items = ItemOrder.objects.filter(table_name=table_name).values(
        'item_code', 'item_cat', 'item_name', 'price', 'gst', 'qty', 'tax_amt', 'total_gst', 'total', 'bill_no', 'bill_date')

    if items.exists():
        bill = items.first()
        response_data = {
            'bill_no': bill['bill_no'],
            'bill_date': bill['bill_date'],
            'items': list(items)
        }
        print("Fetched data: ", response_data)  # Debug print statement
        return JsonResponse(response_data)
    else:
        print("No items found for table: ", table_name)  # Debug print statement
        return JsonResponse({'error': 'Table data not found'})

def edit_table(request, pk):
    rdata = get_object_or_404(AddTable, id=pk)
    if request.method == "POST":
        table_name = request.POST.get('t1')
        cat = request.POST.get('t2')
        AddTable.objects.filter(id=pk).update(
            Table_name=table_name,
            Category=cat
        )
        base_url = reverse('view_table')
        return redirect(base_url)
    return render(request, 'edit_table.html', {'rdata': rdata})


def exchange_tbl(request):
    table=AddTable.objects.all()
    if request.method == "POST":
        old_table = request.POST.get('oldTable')
        new_table = request.POST.get('newTable')

        # Update only the items associated with the old table
        ItemOrder.objects.filter(table_name=old_table).update(table_name=new_table)

        base_url = reverse('admin_home')
        return redirect(base_url)

    return render(request, 'exchange_tbl.html',{'table':table})

def print_table(request):
    # Get distinct table names from ItemOrder
    tableName = Printorders.objects.values('table_name').distinct()
    return render(request, 'print_table.html', {'tableName': tableName})
# views.py

def print_bill(request):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and selected_table_name:
        company = AddCompany.objects.all()

    if selected_table_name:
        # Fetch related ItemOrder objects
        item_orders = Printorders.objects.filter(table_name=selected_table_name)
        table_data = {
            'table_name': selected_table_name,
            'items': []
        }

        for item_order in item_orders:
            item_data = {
                'table_name': item_order.table_name,
                'bill_no': item_order.bill_no,
                'bill_date': item_order.bill_date,
                'bill_time': item_order.bill_time,
                'item_name': item_order.item_name,
                'qty': item_order.qty,
            }
            table_data['items'].append(item_data)

        return render(request, 'print_bill.html', {'table_data': table_data, 'company': company})
    else:
        error_message = "Please select a table name."
        return render(request, 'print_bill.html', {'error_message': error_message})

    return render(request, 'print_bill.html')

def settle_table(request):
    # Get distinct table names from ItemOrder
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'settle_table.html', {'tableName': tableName})


def settle_bill(request,table_name):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and table_name:
        company = AddCompany.objects.all()

        if table_name:
            # Fetch related ItemOrder objects
            item_orders = ItemOrder.objects.filter(table_name=table_name)
            table_data = {
                'table_name': table_name,
                'items': [],
                'taxsubtotal': 0,  # Initialize taxsubtotal
                'subtotal': 0,  # Initialize subtotal
                'total_qty': 0,  # Initialize total quantity
                'total': 0,  # Initialize total
            }

            for item_order in item_orders:

                item_data = {
                    'table_name': item_order.table_name,
                    'bill_no': item_order.bill_no,
                    'bill_date': item_order.bill_date,
                    'bill_time': item_order.bill_time,
                    'item_name': item_order.item_name,
                    'qty': item_order.qty,
                    'price': item_order.price,
                    'tax_amt': item_order.tax_amt,
                    'total_gst': item_order.total_gst,
                    'taxsubtotal': item_order.tax_amt * item_order.qty,  # Update taxsubtotal per item
                    'total': item_order.total
                }
                table_data['items'].append(item_data)

                table_data['subtotal'] += item_order.total  # Assuming total is the item total
                table_data['total_qty'] += item_order.qty
                table_data['taxsubtotal'] += item_order.tax_amt
                table_data['total'] += item_order.total


            # Delete ItemOrder objects for the selected table_name after displaying details

            return render(request, 'settle_bill.html', {'table_data': table_data, 'company': company})
        else:
            error_message = "Please select a table name."
            return render(request, 'settle_bill.html', {'error_message': error_message})

    # Handle GET request or any other cases here if needed
    return render(request, 'settle_bill.html')
def parcel(request):
    return render(request,'parcel.html')


@require_http_methods(["POST"])
def save_pracel_user(request):
    now = datetime.now().replace(microsecond=0)
    current_time = now.strftime("%H:%M:%S")

    # Adjust the bill date logic for the 2 AM to 2 AM cycle
    if now.hour < 2:
        # If the current time is before 2 AM, consider the bill date as the previous day
        bill_date = (now - timedelta(days=1)).date()
    else:
        # Otherwise, use the current date
        bill_date = now.date()

    data = json.loads(request.body)
    bill_items = data['billItems']
    parcel_charge = float(data.get('parcelCharge', 0.0))  # Note the key should match what you use in JS

    # Get the current date

    # Determine the next bill_no
    last_pracel = Pracel.objects.all().order_by('-bill_no').first()
    if last_pracel:
        bill_no = int(last_pracel.bill_no) + 1
    else:
        bill_no = 1000

    for item in bill_items:
        item_code = item['item_code']
        item_name = item['item_name']
        price = float(item['price'])
        qty = int(item['qty'])
        tax_amt = float(item['tax_amt'])
        total = float(item['total'])
        Pracel.objects.create(
            bill_no=bill_no,
            bill_date=bill_date,
            bill_time=current_time,
            item_code=item_code,
            item_name=item_name,
            price=price,
            qty=qty,
            tax_amt=tax_amt,
            total=total,
            pracel_charge=parcel_charge  # Ensure this matches your model field
        )
        try:
            add_item = AddItem.objects.get(Item_code=item_code)

            # Check if the item has enough stock
            if add_item.qty >= qty:

                # Decrease qty
                add_item.qty -= qty

                # If dqty is None, initialize it to 0
                if add_item.dqty is None:
                    add_item.dqty = 0

                # Add the quantity to dqty
                add_item.dqty += qty

                # Save the updated item
                add_item.save()
            else:
                return JsonResponse({
                    'success': False,
                    'error': f"Insufficient stock for item: {item_name}"
                }, status=400)

        except AddItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f"Item with code {item_code} not found in AddItem table."
            }, status=404)


    return JsonResponse({'success': True, 'bill_no': bill_no, 'redirect_url': reverse('userHome')})



def print_pracel(request, bill_no):
    # Fetch the pracels for the given bill_no
    pracels = Pracel.objects.filter(bill_no=bill_no)

    # Calculate totals and aggregates
    total_qty = pracels.aggregate(total_qty=Sum('qty'))['total_qty'] or 0
    subtotal = pracels.aggregate(subtotal=Sum('tax_amt'))['subtotal'] or 0


    # Calculate CGST and SGST amounts
    for pracel in pracels:
        price = pracel.price
        qty = pracel.qty
        tax_amt = pracel.tax_amt


    # Get parcel charge from the first item (assuming all items have the same parcel charge)
    parcel_charge = pracels.first().pracel_charge if pracels.exists() else 0

    # Calculate grand total
    grand_total = subtotal + parcel_charge

    # Fetch company details
    company = AddCompany.objects.all()

    context = {
        'pracels': pracels,
        'total_qty': total_qty,
        'subtotal': subtotal,
        'parcel_charge': parcel_charge,
        'grand_total': grand_total,
        'company': company
    }

    return render(request, 'print_pracel.html', context)


from collections import defaultdict

from collections import defaultdict
from django.db.models import Q
from .models import Orders, Billpending  # Adjust the import based on your project structure

def sales_report(request):

    selected_month = request.POST.get('salesmonth')
    sales_data = []
    total_amount = 0  # Initialize total amount

    if request.method == 'POST' and selected_month:
        # Extract year and month from the selected month
        year, month = selected_month.split('-')

        # Filter orders by year and month
        salesreport = Orders.objects.filter(
            Q(bill_date__year=year) & Q(bill_date__month=month)
        )

        # Create a dictionary to store the grouped data
        grouped_sales = defaultdict(lambda: {
            'bill_no': None,
            'bill_date': None,
            'items': [],
            'quantities': [],
            'total': 0,
            'status': None
        })

        # Iterate through each sale and group by bill_no
        for sales in salesreport:
            bill_no = sales.bill_no
            grouped_sales[bill_no]['bill_no'] = sales.bill_no
            grouped_sales[bill_no]['bill_date'] = sales.bill_date
            grouped_sales[bill_no]['items'].append(sales.item_name)
            grouped_sales[bill_no]['quantities'].append(str(sales.qty))
            grouped_sales[bill_no]['total'] += sales.total

            # Fetch status from Billpending if it exists
            try:
                bill_pending = Billpending.objects.get(billNo=bill_no)
                grouped_sales[bill_no]['status'] = bill_pending.satus
            except Billpending.DoesNotExist:
                grouped_sales[bill_no]['status'] = "Not Found"

        # Prepare the sales data for rendering
        for key, value in grouped_sales.items():
            # Join items and quantities with commas
            items = ', '.join(value['items'])
            quantities = ', '.join(value['quantities'])
            sales_data.append({
                'bill_no': value['bill_no'],
                'bill_date': value['bill_date'],
                'items': items,
                'quantities': quantities,
                'total': value['total'],
                'status': value['status'],  # Include the status in the sales data
            })
            total_amount += value['total']  # Add to total amount

    return render(
        request,
        'sales_report.html',
        {
            'sales_data': sales_data,
            'selected_month': selected_month,
            'total_amount': total_amount  # Pass total amount to the template
        }
    )


from django.db.models import Sum

def item_report(request):
    # Get distinct categories from AddItem
    category = AddItem.objects.values('Category').distinct()
    selectedmonth = None
    selectedcat = None
    total_amount = 0  # Initialize total amount
    orders = None  # Initialize orders

    if request.method == 'POST':
        selectedmonth = request.POST.get('salesmonth')
        selectedcat = request.POST.get('selectedcat')

        # Query the Orders table based on the selected month and category
        orders = Orders.objects.all()

        if selectedmonth:
            orders = orders.filter(bill_date__month=selectedmonth.split('-')[1])
        if selectedcat and selectedcat.strip() != "":
            orders = orders.filter(item_cat=selectedcat)  # Adjust the field based on your actual schema

        # Aggregate quantities and totals for the same item_name
        orders = orders.values('item_name').annotate(
            total_qty=Sum('qty'),
            total_amount=Sum('total')
        ).order_by('item_name')

        # Calculate the total amount for all items
        total_amount = orders.aggregate(grand_total=Sum('total_amount'))['grand_total'] or 0

    return render(request, 'item_report.html', {
        'category': category,
        'orders': orders if request.method == 'POST' else None,
        'selectedmonth': selectedmonth,
        'selectedcat': selectedcat,
        'total_amount': total_amount,  # Pass total amount to the template
    })


def daily_report(request):
    # Default to today's date in case no date is selected
    selected_date = datetime.now().date()

    if request.method == 'POST':
        selected_date_input = request.POST.get('date')
        if selected_date_input:
            # Convert the selected date to a datetime object for querying
            selected_date = datetime.strptime(selected_date_input, '%Y-%m-%d').date()
            orders = Orders.objects.filter(bill_date=selected_date)

            # Calculate the grand total by summing up the total field
            grand_total = orders.aggregate(grand_total=Sum('total'))['grand_total'] or 0
        else:
            orders = Orders.objects.none()  # No data if no date is selected
            grand_total = 0

        return render(request, 'daily_report.html', {
            'selected_date': selected_date,  # Pass the selected date to the frontend
            'orders': orders,
            'grand_total': grand_total
        })

    # If it's a GET request or no date is selected, use today's date as default
    return render(request, 'daily_report.html', {
        'selected_date': selected_date  # Pass selected_date to the template
    })

def print_bill_delete(request, bill_no):
    # Get all the Printorder records with the specified bill_no
    print_orders = Printorders.objects.filter(bill_no=bill_no)

    # Check if any records were found
    if print_orders.exists():
        # Delete all the records with the same bill_no
        print_orders.delete()
        # Optionally, provide feedback or redirect to the print bill page
        return redirect(reverse('admin_home'))
    else:
        # Handle case where no records are found (optional)
        return redirect(reverse('admin_home'))

def print_bill_delete_user(request, bill_no):
    # Get all the Printorder records with the specified bill_no
    print_orders = Printorders.objects.filter(bill_no=bill_no)

    # Check if any records were found
    if print_orders.exists():
        # Delete all the records with the same bill_no
        print_orders.delete()
        # Optionally, provide feedback or redirect to the print bill page
        return redirect(reverse('userHome'))
    else:
        # Handle case where no records are found (optional)
        return redirect(reverse('userHome'))


def settle_bill_delete(request, bill_no):
    # Get all the Printorder records with the specified bill_no
    print_orders = ItemOrder.objects.filter(bill_no=bill_no)

    # Check if any records were found
    if print_orders.exists():
        # Delete all the records with the same bill_no
        print_orders.delete()
        # Optionally, provide feedback or redirect to the print bill page
        return redirect(reverse('admin_home'))
    else:
        # Handle case where no records are found (optional)
        return redirect(reverse('admin_home'))

def settle_bill_delete_user(request, bill_no):
    # Get all the Printorder records with the specified bill_no
    print_orders = ItemOrder.objects.filter(bill_no=bill_no)

    # Check if any records were found
    if print_orders.exists():
        # Delete all the records with the same bill_no
        print_orders.delete()
        # Optionally, provide feedback or redirect to the print bill page
        return redirect(reverse('userHome'))
    else:
        # Handle case where no records are found (optional)
        return redirect(reverse('userHome'))


def exchange_tbl_user(request):
    table=AddTable.objects.all()
    if request.method == "POST":
        old_table = request.POST.get('oldTable')
        new_table = request.POST.get('newTable')

        # Update only the items associated with the old table
        ItemOrder.objects.filter(table_name=old_table).update(table_name=new_table)

        base_url = reverse('userHome')
        return redirect(base_url)

    return render(request, 'exchange_tbl_user.html',{'table':table})

def print_table_user(request):
    # Get distinct table names from ItemOrder
    tableName = Printorders.objects.values('table_name').distinct()
    return render(request, 'print_table_user.html', {'tableName': tableName})
# views.py

def print_bill_user(request):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and selected_table_name:
        company = AddCompany.objects.all()

    if selected_table_name:
        # Fetch related ItemOrder objects
        item_orders = Printorders.objects.filter(table_name=selected_table_name)
        table_data = {
            'table_name': selected_table_name,
            'items': []
        }

        for item_order in item_orders:
            item_data = {
                'table_name': item_order.table_name,
                'bill_no': item_order.bill_no,
                'bill_date': item_order.bill_date,
                'bill_time': item_order.bill_time,
                'item_name': item_order.item_name,
                'qty': item_order.qty,
            }
            table_data['items'].append(item_data)

        return render(request, 'print_bill_user.html', {'table_data': table_data, 'company': company})
    else:
        error_message = "Please select a table name."
        return render(request, 'print_bill_user.html', {'error_message': error_message})

    return render(request, 'print_bill_user.html')

def settle_table_user(request):
    # Get distinct table names from ItemOrder
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'settle_table_user.html', {'tableName': tableName})


def settle_bill_user(request,table_name):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and table_name:
        company = AddCompany.objects.all()

        if table_name:
            # Fetch related ItemOrder objects
            item_orders = ItemOrder.objects.filter(table_name=table_name)
            table_data = {
                'table_name': table_name,
                'items': [],
                'taxsubtotal': 0,  # Initialize taxsubtotal
                'subtotal': 0,  # Initialize subtotal
                'total_qty': 0,  # Initialize total quantity
                'total': 0,  # Initialize total
            }

            for item_order in item_orders:
                item_data = {
                    'table_name': item_order.table_name,
                    'bill_no': item_order.bill_no,
                    'bill_date': item_order.bill_date,
                    'bill_time': item_order.bill_time,
                    'item_name': item_order.item_name,
                    'qty': item_order.qty,
                    'price': item_order.price,
                    'tax_amt': item_order.tax_amt,
                    'total_gst': item_order.total_gst,
                    'taxsubtotal': item_order.tax_amt * item_order.qty,  # Update taxsubtotal per item
                    'total': item_order.total
                }
                table_data['items'].append(item_data)

                table_data['subtotal'] += item_order.total  # Assuming total is the item total
                table_data['total_qty'] += item_order.qty
                table_data['taxsubtotal'] += item_order.tax_amt
                table_data['total'] += item_order.total

            # Delete ItemOrder objects for the selected table_name after displaying details

            return render(request, 'settle_bill_user.html', {'table_data': table_data, 'company': company})
        else:
            error_message = "Please select a table name."
            return render(request, 'settle_bill_user.html', {'error_message': error_message})

    # Handle GET request or any other cases here if needed
    return render(request, 'settle_bill_user.html')

def checkTables(request):
    # Get distinct table names from ItemOrder
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'checkTables.html', {'tableName': tableName})


def checkItems(request):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and selected_table_name:
        company = AddCompany.objects.all()

        if selected_table_name:
            # Fetch related ItemOrder objects
            item_orders = ItemOrder.objects.filter(table_name=selected_table_name)
            table_data = {
                'table_name': selected_table_name,
                'items': [],
                'taxsubtotal': 0,  # Initialize taxsubtotal
                'subtotal': 0,  # Initialize subtotal
                'total_qty': 0,  # Initialize total quantity
                'total': 0,  # Initialize total
            }

            for item_order in item_orders:


                item_data = {
                    'id': item_order.id,
                    'item_code': item_order.item_code,
                    'table_name': item_order.table_name,
                    'bill_no': item_order.bill_no,
                    'bill_date': item_order.bill_date,
                    'bill_time': item_order.bill_time,
                    'item_name': item_order.item_name,
                    'qty': item_order.qty,
                    'price': item_order.price,
                    'tax_amt': item_order.tax_amt,
                    'total_gst': item_order.total_gst,
                    'taxsubtotal': item_order.tax_amt * item_order.qty,  # Update taxsubtotal per item
                    'total': item_order.total
                }
                table_data['items'].append(item_data)

                table_data['subtotal'] += item_order.total  # Assuming total is the item total
                table_data['total_qty'] += item_order.qty
                table_data['taxsubtotal'] += item_order.tax_amt
                table_data['total'] += item_order.total


            # Delete ItemOrder objects for the selected table_name after displaying details

            return render(request, 'checkItems.html', {'table_data': table_data, 'company': company})
        else:
            error_message = "Please select a table name."
            return render(request, 'checkItems.html', {'error_message': error_message})

    # Handle GET request or any other cases here if needed
    return render(request, 'checkItems.html')


def checkTablesUser(request):
    # Get distinct table names from ItemOrder
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'checkTablesUser.html', {'tableName': tableName})


def checkItemsUser(request):
    selected_table_name = request.GET.get('table_name')

    if request.method == 'GET' and selected_table_name:
        company = AddCompany.objects.all()

        if selected_table_name:
            # Fetch related ItemOrder objects
            item_orders = ItemOrder.objects.filter(table_name=selected_table_name)
            table_data = {
                'table_name': selected_table_name,
                'items': [],
                'taxsubtotal': 0,  # Initialize taxsubtotal
                'subtotal': 0,  # Initialize subtotal
                'total_qty': 0,  # Initialize total quantity
                'total': 0,  # Initialize total
            }

            for item_order in item_orders:

                item_data = {
                    'id': item_order.id,
                    'table_name': item_order.table_name,
                    'bill_no': item_order.bill_no,
                    'bill_date': item_order.bill_date,
                    'bill_time': item_order.bill_time,
                    'item_name': item_order.item_name,
                    'item_code': item_order.item_code,
                    'qty': item_order.qty,
                    'price': item_order.price,
                    'tax_amt': item_order.tax_amt,
                    'total_gst': item_order.total_gst,
                    'taxsubtotal': item_order.tax_amt * item_order.qty,  # Update taxsubtotal per item
                    'total': item_order.total
                }
                table_data['items'].append(item_data)

                table_data['subtotal'] += item_order.total  # Assuming total is the item total
                table_data['total_qty'] += item_order.qty
                table_data['taxsubtotal'] += item_order.tax_amt
                table_data['total'] += item_order.total

            # Delete ItemOrder objects for the selected table_name after displaying details

            return render(request, 'checkItemsUser.html', {'table_data': table_data, 'company': company})
        else:
            error_message = "Please select a table name."
            return render(request, 'checkItemsUser.html', {'error_message': error_message})

    # Handle GET request or any other cases here if needed
    return render(request, 'checkItemsUser.html')

def index1(request):
    tdata = AddTable.objects.all()
    saved_table_name = request.GET.get('table', None)  # Extract from URL parameter
    stored_tables = [item.table_name for item in ItemOrder.objects.all()]  # List of stored table names
    return render(request, 'index1.html',
                  {'tdata': tdata, 'saved_table_name': saved_table_name, 'stored_tables': stored_tables})

def addExpenses(request):
    return render(request, 'expenses.html')


def saveExpenses(request):
    if request.method == 'POST':
        # Parse and validate date
        date_str = request.POST.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format.")  # Debugging statement
            return redirect('adminExpenses')
        amount = request.POST.get('amt')
        reason = request.POST.get('reason')

        Expenses.objects.create(
            Date=date,
            Reason=reason,
            Amount=amount,
        )

    else:
        print("No username found in session.")  # Debugging statement

        return redirect('addExpenses')  # Replace with your desired success URL

    return render(request, 'expenses.html')

def viewExpenses(request):
    expenses = []
    grand_total = 0  # Initialize the grand total to 0

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')

        # Initialize the filter query
        filters = {}

        if from_date_str and to_date_str:
            try:
                # Parse the date strings into datetime objects
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

                filters['Date__range'] = (from_date, to_date)  # Date filter

            except ValueError:
                print("Invalid date format.")  # Handle invalid date formats

        # Query the Expenses model with the combined filters
        expenses = Expenses.objects.filter(**filters)

        # Calculate the grand total of Amount
        grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0  # Aggregate sum of Amount

    return render(request, 'viewExpenses.html', {'expenses': expenses, 'grand_total': grand_total})


def get_staff_name(request):
    query = request.GET.get('query', '')
    if query:
        username = UserReg.objects.filter(username__icontains=query).values_list('username', flat=True)
        print('username numbers:', list(username))  # Debugging: check the data in the terminal
        return JsonResponse(list(username), safe=False)
    return JsonResponse([], safe=False)

def salary(request):
    return render(request, 'salary.html')

def saveSalary(request):
    if request.method == 'POST':
        # Parse and validate date
        date_str = request.POST.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format.")  # Debugging statement
            return redirect('adminExpenses')
        amount = request.POST.get('amt')
        reason = request.POST.get('reason')
        salaryDetails = request.POST.get('salaryDetails')

        Salary.objects.create(
            Date=date,
            desc=reason,
            Amount=amount,
            staffname=salaryDetails,
        )

    else:
        print("No username found in session.")  # Debugging statement

        return redirect('salary')  # Replace with your desired success URL

    return render(request, 'salary.html')


def viewSalary(request):
    # Fetch all salary records initially
    expenses = Salary.objects.all()
    grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0  # Grand total for unfiltered data

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        staffname = request.POST.get('staffname')

        # Initialize the filter query
        filters = {}

        if from_date_str and to_date_str:
            try:
                # Parse the date strings into datetime objects
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

                filters['Date__range'] = (from_date, to_date)  # Date filter
            except ValueError:
                print("Invalid date format.")  # Handle invalid date formats

        if staffname:
            filters['staff_name__icontains'] = staffname  # Staff name filter

        # Apply the filters to the Salary queryset
        expenses = Salary.objects.filter(**filters)

        # Recalculate the grand total for the filtered data
        grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0

    return render(request, 'viewSalary.html', {'expenses': expenses, 'grand_total': grand_total})


from django.db.models import Sum
def profit_report(request):
    # Get the from_date and to_date from the request (if provided)
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    from_date = parse_date(from_date_str) if from_date_str else None
    to_date = parse_date(to_date_str) if to_date_str else None

    # Query all consignments and expenses
    consignments = Orders.objects.all()
    expenses = Expenses.objects.all()

    # Filter by date range if provided
    if from_date and to_date:
        consignments = consignments.filter(bill_date__range=[from_date, to_date])
        expenses = expenses.filter(Date__range=[from_date, to_date])

    # Track already processed track_ids
    processed_track_ids = set()

    # This list will store the unique consignments
    unique_consignments = []

    # Iterate over all consignments to ensure only unique track_id costs are added
    for consignment in consignments:
        track_id = consignment.bill_no
        # If track_id is not already processed, add its total_cost to the unique list
        if track_id not in processed_track_ids:
            processed_track_ids.add(track_id)
            unique_consignments.append(consignment)

    # Now group by date and branch, summing the total_cost of the unique consignments
    consignments_grouped = (
        Orders.objects.filter(id__in=[c.id for c in unique_consignments])
        .values('bill_date')
        .annotate(total=Sum('total'))
        .order_by('bill_date')
    )

    # Group expenses by Date and Reason, and calculate total Amount for each group
    expenses_grouped = expenses.values('Date', 'Reason').annotate(
        total_amount=Sum('Amount')
    ).order_by('Date', 'Reason')

    # Calculate grand totals for consignments and expenses
    grand_total_consignment = sum(item['total'] for item in consignments_grouped)
    grand_total_expenses = sum(item['total_amount'] for item in expenses_grouped)

    # Calculate combined grand total
    combined_grand_total = grand_total_consignment + grand_total_expenses

    # Calculate profit or loss
    total_balance = grand_total_consignment - grand_total_expenses

    # Set profit and loss
    profit = total_balance if total_balance > 0 else 0
    loss = abs(total_balance) if total_balance < 0 else 0

    # Pass the grouped data and totals to the template
    return render(request, 'profit_report.html', {
        'consignments': consignments_grouped,
        'expenses': expenses_grouped,
        'grand_total_consignment': grand_total_consignment,
        'grand_total_expenses': grand_total_expenses,
        'combined_grand_total': combined_grand_total,
        'profit': profit,
        'loss': loss,
        'from_date': from_date_str,
        'to_date': to_date_str,
    })



def billPending(request):
    if request.method == "POST":
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")
        # Handle form submission
        bill_no = request.POST.get('bill_no')
        name = request.POST.get('name')
        status = request.POST.get('status')
        amount = request.POST.get('amount')
        table_name = request.POST.get('tablename')

        # Save data in Billpending table
        Billpending.objects.create(
            billNo=bill_no,
            name=name,
            satus=status,
            amount=amount,
            date=con_date
        )
        return redirect('settle_bill',table_name=table_name)  # Replace with the correct name of your view

    # Fetch table names
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'settle_table.html', {'tableName': tableName})

def billPendingUser(request):
    if request.method == "POST":
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")
        # Handle form submission
        bill_no = request.POST.get('bill_no')
        name = request.POST.get('name')
        status = request.POST.get('status')
        amount = request.POST.get('amount')
        table_name = request.POST.get('tablename')

        # Save data in Billpending table
        Billpending.objects.create(
            billNo=bill_no,
            name=name,
            satus=status,
            amount=amount,
            date=con_date
        )
        return redirect('settle_bill_user',table_name=table_name)  # Replace with the correct name of your view

    # Fetch table names
    tableName = ItemOrder.objects.values('table_name').distinct()
    return render(request, 'settle_table.html', {'tableName': tableName})


def get_table_details(request):
    table_name = request.GET.get('table_name')
    item_order = ItemOrder.objects.filter(table_name=table_name).first()

    if item_order:
        data = {
            'amount': item_order.total,
            'bill_no': item_order.bill_no,
            'table_name': item_order.table_name
        }
    else:
        data = {
            'amount': 'N/A',
            'bill_no': 'N/A'
        }

    return JsonResponse(data)


def delete_item(request, item_id):
    if request.method == 'POST':
        # Fetch the item from ItemOrder using the item_id
        item = get_object_or_404(ItemOrder, id=item_id)

        # Get the remark from POST data
        remark = request.POST.get('remark', '')

        # Save the deleted item details and remark in Deletedata
        Deletedata.objects.create(
            date=item.bill_date,
            billNo=item.bill_no,
            item=item.item_name,
            item_code=item.item_code,
            qty=item.qty,
            price=item.price,
            taxAmt=item.tax_amt,
            remark=remark
        )


        # Update the quantity in AddItem table
        try:
            add_item = AddItem.objects.get(Item_code=item.item_code)
            add_item.qty += item.qty
            add_item.dqty -= item.qty
            add_item.save()
        except AddItem.DoesNotExist:
            print(f"Item with code {item.item_code} not found in AddItem table.")

        # Delete the item from ItemOrder
        item.delete()

        return redirect('admin_home')  # Redirect to the admin home view
    else:
        return HttpResponse("Method not allowed", status=405)


def delete_item_user(request, item_id):
    if request.method == 'POST':
        # Fetch the item from ItemOrder using the item_id
        item = get_object_or_404(ItemOrder, id=item_id)

        # Get the remark from POST data
        remark = request.POST.get('remark', '')

        # Save the deleted item details and remark in Deletedata
        Deletedata.objects.create(
            date=item.bill_date,
            billNo=item.bill_no,
            item=item.item_name,
            item_code=item.item_code,
            qty=item.qty,
            price=item.price,
            taxAmt=item.tax_amt,
            remark=remark
        )


        # Update the quantity in AddItem table
        try:
            add_item = AddItem.objects.get(Item_code=item.item_code)
            add_item.qty += item.qty
            add_item.dqty -= item.qty
            add_item.save()
        except AddItem.DoesNotExist:
            print(f"Item with code {item.item_code} not found in AddItem table.")

        # Delete the item from ItemOrder
        item.delete()

        return redirect('userHome')  # Redirect to the admin home view
    else:
        return HttpResponse("Method not allowed", status=405)

def editStaff(request, pk):
    rdata = get_object_or_404(UserReg, id=pk)
    original_email = rdata.email

    if request.method == "POST":
        email = request.POST.get('t1')
        number = request.POST.get('t2')
        password = request.POST.get('t3')
        username = request.POST.get('t4')
        utype = request.POST.get('utype')
        UserReg.objects.filter(id=pk).update(
            username=username,
            email=email,
            number=number,
            password=password,
            usertype=utype
        )
        # Update the Login record using the original staffPhone
        user = UserLogin.objects.filter(username=original_email).first()  # Fetch the user with the original phone number
        if user:
            user.username = email  # Update username to the new phone number
            user.password = password
            user.save()
        base_url = reverse('register_list')
        return redirect(base_url)
    return render(request, 'editStaff.html', {'rdata': rdata})

def viewSalaryHistory(request, pk):
    # Fetch all expenses for the given staff (before applying filters)
    expenses = Salary.objects.filter(staffname=pk)
    grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0  # Calculate grand total for all records initially

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        staffname = request.POST.get('staffname')

        # Initialize the filter query
        filters = {'staffname': pk}

        if from_date_str and to_date_str:
            try:
                # Parse the date strings into datetime objects
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

                filters['Date__range'] = (from_date, to_date)  # Date filter
            except ValueError:
                print("Invalid date format.")  # Handle invalid date formats

        if staffname:
            filters['staff_name__icontains'] = staffname  # Staff name filter

        # Query the Salary model with the combined filters
        expenses = Salary.objects.filter(**filters)

        # Recalculate the grand total of filtered Amount
        grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0

    return render(request, 'viewSalaryHistory.html', {'expenses': expenses, 'grand_total': grand_total})

def pendingReport(request):
    data = Billpending.objects.filter(satus='Pending')
    grand_total = 0

    if request.method == 'POST':
        # Get filter inputs from the request
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        name = request.POST.get('name')

        # Apply filters
        filters = Q(satus='Pending')  # Initial filter for pending status

        if from_date:
            # Convert string to datetime for filtering
            filters &= Q(date__gte=datetime.strptime(from_date, '%Y-%m-%d'))
        if to_date:
            # Convert string to datetime for filtering
            filters &= Q(date__lte=datetime.strptime(to_date, '%Y-%m-%d'))
        if name:
            filters &= Q(name__icontains=name)

        # Apply the filters to the query
        data = Billpending.objects.filter(filters)

    # Calculate grand total of the amount field
    grand_total = data.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(
        request,
        'pendingReport.html',
        {
            'data': data,
            'grand_total': grand_total,
            'from_date': from_date if request.method == 'POST' else '',
            'to_date': to_date if request.method == 'POST' else '',
            'name': name if request.method == 'POST' else ''
        }
    )

def get_name(request):
    query = request.GET.get('query', '')
    if query:
        username = Billpending.objects.filter(name__icontains=query).values_list('name', flat=True)
        print('username numbers:', list(username))  # Debugging: check the data in the terminal
        return JsonResponse(list(username), safe=False)
    return JsonResponse([], safe=False)

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update_bill_status(request, bill_id):
    if request.method == 'POST':
        try:
            bill = get_object_or_404(Billpending, id=bill_id)
            data = json.loads(request.body)
            entered_amount = float(data.get('entered_amount', 0))

            if entered_amount <= 0 or entered_amount > bill.amount:
                return JsonResponse({'success': False, 'error': 'Invalid amount entered'}, status=400)

            bill.amount -= entered_amount
            if bill.amount == 0:
                bill.satus = 'Paid'
            bill.save()

            return JsonResponse({'success': True, 'new_amount': bill.amount, 'status': bill.satus})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


from collections import defaultdict


def purchaseReport(request):
    # Initialize filters
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    selected_cat = request.POST.get('selectedcat')

    # Apply filters to the Purchase and AddItem queryset
    userdata = Purchase.objects.all()
    userdata1 = AddItem.objects.all()

    if from_date and to_date:
        userdata = userdata.filter(date__range=[from_date, to_date])

    if selected_cat:
        userdata = userdata.filter(Item_name=selected_cat)
        userdata1 = userdata1.filter(Item_name=selected_cat)

    grand_total = 0
    grand_item_total = 0
    grand_tax_amount = 0
    final_grand_tax_amount = 0
    userdata_with_totals = defaultdict(lambda: {
        'Item_code': None,
        'Item_name': None,
        'qty': 0,
        'item_qty': 0,
        'purchase_item_price': 0,
        'additem_item_price': 0,
        'item_total': 0,
        'tax_amount': 0
    })

    for item in userdata:
        # Fetch the Item_price from the Purchase table
        purchase_item_price = item.Item_price if item.Item_price is not None else 0

        # Filter the AddItem table to get the matching item based on Item_code
        matching_item = userdata1.filter(Item_code=item.Item_code).first()

        # Fetch the Item_price from the AddItem table, or default to 0 if no match is found
        additem_item_price = matching_item.Item_price if matching_item and matching_item.Item_price is not None else 0

        # Get the qty (dqty) from the AddItem table, or default to 0 if no match is found
        item_qty = matching_item.dqty if matching_item and matching_item.dqty is not None else 0

        # Calculate item total using qty from the Purchase table and its Item_price
        item_total = item.qty * purchase_item_price
        grand_total += item_total

        # Calculate tax amount using item_qty (from AddItem) and AddItem.Item_price
        tax_amount = item_qty * additem_item_price
        grand_tax_amount += tax_amount

        # Add to the grouped data
        group = userdata_with_totals[item.Item_code]
        group['Item_code'] = item.Item_code
        group['Item_name'] = item.Item_name
        group['qty'] += item.qty
        group['item_qty'] = item_qty
        group['purchase_item_price'] = purchase_item_price
        group['additem_item_price'] = additem_item_price
        group['item_total'] += item_total
        group['tax_amount'] += tax_amount

    # Calculate the final grand tax amount
    for group in userdata_with_totals.values():
        final_grand_tax_amount += group['tax_amount']

    # Convert grouped data to a list for rendering
    grouped_data = list(userdata_with_totals.values())

    return render(request, 'purchaseReport.html', {
        'userdata': grouped_data,
        'grand_total': grand_total,
        'grand_item_total': grand_item_total,
        'grand_tax_amount': grand_tax_amount,
        'final_grand_tax_amount': final_grand_tax_amount,
        'userdata1': userdata1
    })


def parcelReport(request):
    selected_month = request.POST.get('salesmonth')
    sales_data = []
    total_amount = 0  # Initialize total amount
    grand_total = 0  # Initialize grand total

    if request.method == 'POST' and selected_month:
        # Extract year and month from the selected month
        year, month = selected_month.split('-')

        # Filter orders by year and month
        salesreport = Pracel.objects.filter(
            Q(bill_date__year=year) & Q(bill_date__month=month)
        )

        # Create a dictionary to store the grouped data
        grouped_sales = defaultdict(lambda: {
            'bill_no': None,
            'bill_date': None,
            'pracel_charge': None,
            'items': [],
            'quantities': [],
            'total': 0,
            'status': None
        })

        # Iterate through each sale and group by bill_no
        for sales in salesreport:
            bill_no = sales.bill_no
            grouped_sales[bill_no]['bill_no'] = sales.bill_no
            grouped_sales[bill_no]['bill_date'] = sales.bill_date
            grouped_sales[bill_no]['pracel_charge'] = sales.pracel_charge  # Corrected line
            grouped_sales[bill_no]['items'].append(sales.item_name)
            grouped_sales[bill_no]['quantities'].append(str(sales.qty))
            grouped_sales[bill_no]['total'] += sales.total

            # Fetch status from Billpending if it exists
            try:
                bill_pending = Billpending.objects.get(billNo=bill_no)
                grouped_sales[bill_no]['status'] = bill_pending.satus
            except Billpending.DoesNotExist:
                grouped_sales[bill_no]['status'] = "Not Found"

        # Prepare the sales data for rendering
        for key, value in grouped_sales.items():
            # Add parcel_charge to total for grand total calculation
            total_with_charge = value['total'] + (value['pracel_charge'] or 0)
            sales_data.append({
                'bill_no': value['bill_no'],
                'pracel_charge': value['pracel_charge'],
                'bill_date': value['bill_date'],
                'items': ', '.join(value['items']),
                'quantities': ', '.join(value['quantities']),
                'total': value['total'],
                'total_with_charge': total_with_charge,  # Add this line for total with parcel_charge
                'status': value['status'],  # Include the status in the sales data
            })
            total_amount += value['total']  # Add to total amount
            grand_total += total_with_charge  # Add total with parcel_charge to grand total

    return render(
        request,
        'parcelList.html',
        {
            'sales_data': sales_data,
            'selected_month': selected_month,
            'total_amount': total_amount,  # Pass total amount to the template
            'grand_total': grand_total  # Pass grand total to the template
        }
    )

def userExpenses(request):
    return render(request, 'userExpenses.html')


def usersaveExpenses(request):
    if request.method == 'POST':
        # Parse and validate date
        date_str = request.POST.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format.")  # Debugging statement
            return redirect('adminExpenses')
        amount = request.POST.get('amt')
        reason = request.POST.get('reason')

        Expenses.objects.create(
            Date=date,
            Reason=reason,
            Amount=amount,
        )

    else:
        print("No username found in session.")  # Debugging statement

        return redirect('userExpenses')  # Replace with your desired success URL

    return render(request, 'userExpenses.html')

def userViewExpenses(request):
    expenses = []
    grand_total = 0  # Initialize the grand total to 0

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')

        # Initialize the filter query
        filters = {}

        if from_date_str and to_date_str:
            try:
                # Parse the date strings into datetime objects
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

                filters['Date__range'] = (from_date, to_date)  # Date filter

            except ValueError:
                print("Invalid date format.")  # Handle invalid date formats

        # Query the Expenses model with the combined filters
        expenses = Expenses.objects.filter(**filters)

        # Calculate the grand total of Amount
        grand_total = expenses.aggregate(total_amount=Sum('Amount'))['total_amount'] or 0  # Aggregate sum of Amount

    return render(request, 'userViewExpenses.html', {'expenses': expenses, 'grand_total': grand_total})




def deleteReport(request):
    sales_data = []
    total_amount = 0  # Initialize total amount

    if request.method == 'POST':
        # Get the from_date and to_date from the form
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        # Validate that at least one date is provided
        if from_date or to_date:
            # Filter orders by the provided date range
            filters = Q()
            if from_date:
                filters &= Q(date__gte=from_date)
            if to_date:
                filters &= Q(date__lte=to_date)

            salesreport = Deletedata.objects.filter(filters)

            # Create a dictionary to store the grouped data
            grouped_sales = defaultdict(lambda: {
                'bill_no': None,
                'bill_date': None,
                'items': [],
                'quantities': [],
                'total': 0,
                'status': None
            })

            # Iterate through each sale and group by bill_no
            for sales in salesreport:
                bill_no = sales.billNo
                grouped_sales[bill_no]['bill_no'] = sales.billNo
                grouped_sales[bill_no]['bill_date'] = sales.date
                grouped_sales[bill_no]['items'].append(sales.item)
                grouped_sales[bill_no]['quantities'].append(str(sales.qty))
                grouped_sales[bill_no]['total'] += sales.taxAmt


            # Prepare the sales data for rendering
            for key, value in grouped_sales.items():
                # Join items and quantities with commas
                items = ', '.join(value['items'])
                quantities = ', '.join(value['quantities'])
                sales_data.append({
                    'bill_no': value['bill_no'],
                    'bill_date': value['bill_date'],
                    'items': items,
                    'quantities': quantities,
                    'total': value['total'],
                    'status': value['status'],  # Include the status in the sales data
                })
                total_amount += value['total']  # Add to total amount

    return render(
        request,
        'deleteReport.html',
        {
            'sales_data': sales_data,
            'total_amount': total_amount,  # Pass total amount to the template
        }
    )

def usersalesReport(request):

    selected_month = request.POST.get('salesmonth')
    sales_data = []
    total_amount = 0  # Initialize total amount

    if request.method == 'POST' and selected_month:
        # Extract year and month from the selected month
        year, month = selected_month.split('-')

        # Filter orders by year and month
        salesreport = Orders.objects.filter(
            Q(bill_date__year=year) & Q(bill_date__month=month)
        )

        # Create a dictionary to store the grouped data
        grouped_sales = defaultdict(lambda: {
            'bill_no': None,
            'bill_date': None,
            'items': [],
            'quantities': [],
            'total': 0,
            'status': None
        })

        # Iterate through each sale and group by bill_no
        for sales in salesreport:
            bill_no = sales.bill_no
            grouped_sales[bill_no]['bill_no'] = sales.bill_no
            grouped_sales[bill_no]['bill_date'] = sales.bill_date
            grouped_sales[bill_no]['items'].append(sales.item_name)
            grouped_sales[bill_no]['quantities'].append(str(sales.qty))
            grouped_sales[bill_no]['total'] += sales.total

            # Fetch status from Billpending if it exists
            try:
                bill_pending = Billpending.objects.get(billNo=bill_no)
                grouped_sales[bill_no]['status'] = bill_pending.satus
            except Billpending.DoesNotExist:
                grouped_sales[bill_no]['status'] = "Not Found"

        # Prepare the sales data for rendering
        for key, value in grouped_sales.items():
            # Join items and quantities with commas
            items = ', '.join(value['items'])
            quantities = ', '.join(value['quantities'])
            sales_data.append({
                'bill_no': value['bill_no'],
                'bill_date': value['bill_date'],
                'items': items,
                'quantities': quantities,
                'total': value['total'],
                'status': value['status'],  # Include the status in the sales data
            })
            total_amount += value['total']  # Add to total amount

    return render(
        request,
        'usersalesReport.html',
        {
            'sales_data': sales_data,
            'selected_month': selected_month,
            'total_amount': total_amount  # Pass total amount to the template
        }
    )
