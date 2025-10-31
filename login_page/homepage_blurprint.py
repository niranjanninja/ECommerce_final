from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
import re
from libs.UserDb import UserDb
from login_parameter import Login,Image_upload
from loggers import Loggers
from configparser import ConfigParser
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

app = Flask(__name__)

Loggers.loggers()
logger = logging.getLogger()

home=Blueprint("home",__name__,template_folder="templates")

@home.route('/home')
def home_page():
    try:
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        category=obj.fetch_category()
        image=obj.random_from_inventory()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            url_list.append(url_list2)
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("homepage.html",admin_check=admin_check,cart_items=cart_items,category=category,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("homepage.html",admin_check=admin_check,cart_items=cart_items,category=category,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return redirect(url_for('home.home_page'))

@home.route('/cpu_items',methods=["GET","POST"])
def cpu_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.cpu_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        price=request.args.get('price')
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte = f"({'|'.join(tuple_filter)})"

        fan_list=set()
        key_list=[]
        fans=obj.cpu_all()
        fan_pattern=r"(\d)"
        for i in fans:
            key=i[0][2].split(":")[1].strip()
            key_list.append(key)
        for j in key_list:
            a=re.search(fan_pattern,j)
            if a:
                fan_list.add(f"{a.group()} fans")

        motherboard_list=set()
        motherb=obj.cpu_all()
        for i in motherb:
            key=i[0][1].split(":")[1].strip()
            key2=key.split("/")
            for j in key2:
                motherboard_list.add(j)
        
        product_brand=set()
        brands=obj.cpu_page_items()
        for i in brands:
            product_brand.add(i[1])
        
        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.cpu_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.cpu_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.cpu_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.cpu_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("cpu_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/headphone_items',methods=["GET","POST"])
def headphone_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.headphone_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        product_brand=set()
        brands=obj.headphone_page_items()
        for i in brands:
            product_brand.add(i[1])

        connect=set()
        connect_head=set()
        connect_items=obj.headphone_all()
        for i in connect_items:
            key=i[0][1].split(":")[1].strip()
            connect_head.add(key)
        for j in connect_head:
            key2=j.split("/")
            for key3 in key2:
                connect.add(key3.strip())

        noise_cancel=set()
        noise_items=obj.headphone_all()
        for i in noise_items:
            key=i[0][2].split(":")[1].strip()
            noise_cancel.add(key)

        microphone_list=set()
        noise_items=obj.headphone_all()
        for i in noise_items:
            key=i[0][3].split(":")[1].strip()
            microphone_list.add(key)
        
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte=f"({'|'.join(tuple_filter)})"
        price=request.args.get('price')
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        
        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.headphone_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.headphone_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.headphone_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.headphone_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
                return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("headphone_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/keyboard_items',methods=["GET","POST"])
def keyboard_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.keyboard_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        
        product_brand=set()
        brands=obj.keyboard_page_items()
        for i in brands:
            product_brand.add(i[1])

        switch_type=set()
        switch_items=obj.keyboard_all()
        for i in switch_items:
            key=i[0][0].split(":")[1].strip()
            switch_type.add(key)

        keyboard_connect=set()
        connect_keyboard=set()
        key_connect=obj.keyboard_all()
        for i in key_connect:
            key=i[0][1].split(":")[1].strip()
            connect_keyboard.add(key)
        for j in connect_keyboard:
            key2=j.split("/")
            for key3 in key2:
                keyboard_connect.add(key3.strip())

        key_rollover=set()
        rollover=obj.keyboard_all()
        for i in rollover:
            key=i[0][3].split(":")[1].strip()
            key_rollover.add(key)

        backlight_list=set()
        backlight=obj.keyboard_all()
        for i in backlight:
            key=i[0][4].split(":")[1].strip()
            backlight_list.add(key)

        price=request.args.get('price')
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte = f"({'|'.join(tuple_filter)})"

        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.keyboard_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.keyboard_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.keyboard_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.keyboard_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("keyboard_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/monitor_items',methods=["GET","POST"])
def monitor_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.monitor_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        
        product_brand=set()
        brands=obj.monitor_page_items()
        for i in brands:
            product_brand.add(i[1])

        resolution_list=set()
        res_items=obj.monitor_all()
        for i in res_items:
            key=i[0][1].split(":")[1].strip()
            resolution_list.add(key)

        panel_list=set()
        panel_items=obj.monitor_all()
        for i in panel_items:
            key=i[0][2].split(":")[1].strip()
            panel_list.add(key)

        refresh_rate_list=set()
        refreshrate=obj.monitor_all()
        for i in refreshrate:
            key=i[0][3].split(":")[1].strip()
            refresh_rate_list.add(key)

        connectivity_list=set()
        connect_list=set()
        connect=obj.monitor_all()
        for i in connect:
            key=i[0][5].split(":")[1].strip()
            connect_list.add(key)
        for j in connect_list:
            key2=j.split("/")
            for key3 in key2:
                connectivity_list.add(key3.strip())
        
        price=request.args.get('price')
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte = f"({'|'.join(tuple_filter)})"
        
        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.monitor_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.monitor_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.monitor_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.monitor_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("monitor_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/mouse_items',methods=["GET","POST"])
def mouse_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.mouse_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        
        product_brand=set()
        brands=obj.mouse_page_items()
        for i in brands:
            product_brand.add(i[1])

        connectivity_list=set()
        connect_list=set()
        connect=obj.mouse_all()
        for i in connect:
            key=i[0][1].split(":")[1].strip()
            connect_list.add(key)
        for j in connect_list:
            key2=j.split("/")
            for key3 in key2:
                connectivity_list.add(key3.strip())

        dpi_list=set()
        dpi_range=obj.mouse_all()
        for i in dpi_range:
            key=i[0][2].split(":")[1].strip()
            dpi_list.add(key)

        sensor_list=set()
        sensor_item=obj.mouse_all()
        for i in sensor_item:
            key=i[0][3].split(":")[1].strip()
            sensor_list.add(key)

        price=request.args.get('price')
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte = f"({'|'.join(tuple_filter)})"

        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.mouse_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.mouse_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.mouse_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.mouse_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("mouse_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/speaker_items',methods=["GET","POST"])
def speaker_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        admin_check=obj.admin_check(name)
        cart_items=obj.cart_items_count(name)
        image=obj.speaker_page_items()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            i2=i[5].replace('/', '|')
            url_list2.append(i2)
            url_list.append(url_list2)
        
        product_brand=set()
        brands=obj.speaker_page_items()
        for i in brands:
            product_brand.add(i[1])
        
        connectivity_list=set()
        connect_list=set()
        connect=obj.speaker_all()
        for i in connect:
            key=i[0][1].split(":")[1].strip()
            connect_list.add(key)
        for j in connect_list:
            key2=j.split("/")
            for key3 in key2:
                connectivity_list.add(key3.strip())

        bass_list=set()
        bass_item=obj.speaker_all()
        for i in bass_item:
            key=i[0][3].split(":")[1].strip()
            bass_list.add(key)

        price=request.args.get('price')
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        filter_list=request.args.getlist('filter')
        tuple_filter=tuple(filter_list)
        sorte = f"({'|'.join(tuple_filter)})"

        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                search_url_list2.append(i2)
                search_url_list.append(search_url_list2)
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if price=="low_to_high" and filter_list:
            lth_url_list=[]
            sorting=obj3.speaker_low_to_high_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                lth_url_list2=[]
                lth_url=obj2.display_single_from_s3(i[0])
                lth_url_list2.append(lth_url)
                lth_url_list2.append(i[1])
                lth_url_list2.append(i[2])
                lth_url_list2.append(i[3])
                lth_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                lth_url_list2.append(i2)
                lth_url_list.append(lth_url_list2)
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(lth_url_list),url_list=lth_url_list,total_page=sorting[2],page=page)
        if price=="high_to_low" and filter_list:
            htl_url_list=[]
            sorting=obj3.speaker_high_to_low_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                htl_url_list2=[]
                htl_url=obj2.display_single_from_s3(i[0])
                htl_url_list2.append(htl_url)
                htl_url_list2.append(i[1])
                htl_url_list2.append(i[2])
                htl_url_list2.append(i[3])
                htl_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                htl_url_list2.append(i2)
                htl_url_list.append(htl_url_list2)
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(htl_url_list),url_list=htl_url_list,total_page=sorting[2],page=page)
        if price:
            price_url_list=[]
            sort=obj3.speaker_price_sort(price,page)
            for i in sort[1]:
                price_url_list2=[]
                price_url=obj2.display_single_from_s3(i[0])
                price_url_list2.append(price_url)
                price_url_list2.append(i[1])
                price_url_list2.append(i[2])
                price_url_list2.append(i[3])
                price_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                price_url_list2.append(i2)
                price_url_list.append(price_url_list2)
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if filter_list:
            filter_url_list=[]
            sorting=obj3.speaker_filter_sort(sorte,page,tuple_filter)
            for i in sorting[1]:
                filter_url_list2=[]
                filter_url=obj2.display_single_from_s3(i[0])
                filter_url_list2.append(filter_url)
                filter_url_list2.append(i[1])
                filter_url_list2.append(i[2])
                filter_url_list2.append(i[3])
                filter_url_list2.append(i[4])
                i2=i[5].replace('/', '|')
                filter_url_list2.append(i2)
                filter_url_list.append(filter_url_list2)
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(filter_url_list),url_list=filter_url_list,total_page=sorting[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("speaker_page.html",selected_filter=filter_list,selected_price=price,admin_check=admin_check,cart_items=cart_items,bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/item/<product_id>')
def show_item_user(product_id):
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            obj2=Image_upload()
            admin_check=obj.admin_check(name)
            store=obj.fetch_product_user(product_id)
            cart_items=obj.cart_items_count(name)
            for i in store:
                url=obj2.display_from_s3(i[5])
            return render_template("show_product_user.html",admin_check=admin_check,cart_items=cart_items,name=name,url=url,product_id=product_id,product_brand=store[0][0],product_name=store[0][1],description=store[0][2],features=store[0][3],price=store[0][4])
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/update_quantity/<cart_id>')
def update_quantity(cart_id):
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            quantity=request.args.get('quantity')
            obj=UserDb()
            obj.update_quantity(cart_id,quantity)
            return redirect(url_for('home.cart_items'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/add_cart/<product_id>')
def add_cart(product_id):
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            price=obj.get_price(product_id)
            brand=obj.get_brand(product_id)
            product_name=obj.get_product_name(product_id)
            cart_add=obj.add_cart(name,product_id,price,product_name,brand)
            flash("Added to Cart","success")
            return redirect(url_for('home.show_item_user',product_id=product_id))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/cart')
def cart_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            obj2=Image_upload()
            name=session.get('name')
            admin_check=obj.admin_check(name)
            cart_items=obj.cart_items_count(name)
            get_cart=obj.get_cart(name)
            total=0
            for i in get_cart:
                total+=i[3]*i[4]
            url_list=[]
            for j in get_cart:
                image_list=[]
                image=obj2.display_single_from_s3(j[0])
                image_list.append(image)
                image_list.append(j[1])
                image_list.append(j[2])
                image_list.append(j[3])
                image_list.append(j[4])
                image_list.append(j[5])
                image_list.append(j[6])
                image_list.append(j[7])
                url_list.append(image_list)
            count=obj.cart_count(name)
            prod_id=[]
            for i in url_list:
                prod_id.append(i[2])
            return render_template("cart.html",admin_check=admin_check,cart_items=cart_items,prod_id=prod_id,name=name,url_list=url_list,total=total,count=count)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/delete_cart/<cart_id>')
def delete_cart(cart_id):
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            delete_cart=obj.delete_cart(cart_id)
            return redirect(url_for('home.cart_items'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/payment_method')
def payment_method():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            total=request.args.get('total')
            name=session.get('name')
            admin_check=obj.admin_check(name)
            count=obj.cart_count(name)
            cart_prod=obj.cart_product_id(name)
            country_code_list = []
            for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
                for region in regions:
                    country_code_list.append((region, code))
                    break
            country_code_list.sort()
            for i in cart_prod:
                obj.insert_in_check_out(i[1],name)
                cart_quantity=obj.cart_quantity(i[1])
                obj.check_out_update_quantity(cart_quantity,i[1])
            stored_address=obj.address_fetch(name)
            return render_template("payment_method_page.html",stored_address=stored_address,admin_check=admin_check,name=name,total=total,count=count,country_codes=country_code_list)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"

@home.route('/payment_confirm',methods=["POST"])
def payment_confirm():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            country_code_list = []
            for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
                for region in regions:
                    country_code_list.append((region, code))
                    break
            country_code_list.sort()
            if request.method == "POST":
                obj=UserDb()
                name=session.get('name')
                customer_name=request.form.get('customer_name')
                address=request.form.get('address')
                stored_address=request.form.get('stored_address')
                landmark=request.form.get('landmark')
                country_code = request.form.get("country_code")
                customer_number=request.form.get('customer_number')
                payment_method=request.form.get('payment_method')
                instruction=request.form.get('instruction')
                dateandtime=datetime.now(ZoneInfo("Asia/Kolkata"))
                save_address=request.form.get('save_address')
                if save_address == 'home':
                    obj.save_home_address(address,name)
                if save_address == 'work':
                    obj.save_work_address(address,name)
                date_time=dateandtime.strftime("%d-%m-%Y, %H:%M")
                full_number = country_code + customer_number
                if not address and not stored_address:
                    flash("Enter or Select An Address", "error")
                    return redirect(url_for('home.payment_method'))
                else:
                    pass
                final_address= address or stored_address
                obj.check_out_update(customer_name,final_address,full_number,payment_method,date_time,name,landmark,instruction)
                if payment_method == "cod":
                    obj.check_out_payment_update(name)
                    obj.update_cart_status(name)
                    check_out_details=obj.check_out_details(name)
                    for i in check_out_details:
                        order_id=i[0]
                        customer_name=i[2]
                        user_name=i[9]
                        obj.add_delivery_details(order_id,customer_name,user_name)
                        obj.recent_update(order_id)
                    return redirect(url_for('home.order_tracking'))
                else:
                    return redirect(url_for('home.card_pay_page'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/card_pay_page')
def card_pay_page():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            name=session.get('name')
            stored_card=obj.card_fetch(name)
            return render_template("card_details.html",name=name,stored_card=stored_card)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"

@home.route('/card_payment',methods=["POST"])
def card_payment():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            if request.method == "POST":
                obj=UserDb()
                obj2=Login()
                stored_card=request.form.get('stored_card')
                name=session.get('name')
                card_number=request.form.get('card_number')
                card_name=request.form.get('card_name')
                expiry_date=request.form.get('expiry_date')
                cvv=request.form.get('cvv')
                save_address=request.form.get('save_card')
                if not stored_card and not (card_number and card_name and expiry_date and cvv): 
                    flash("Fill the details", "error")
                    return redirect(url_for('home.card_pay_page'))
                else:
                    if save_address:
                        cvv_hash=obj2.cvv_hash(cvv)
                        obj.card_details(name,card_number,card_name,expiry_date,cvv_hash)
                    obj.check_out_payment_update(name)
                    obj.update_cart_status(name)
                    check_out_details=obj.check_out_details(name)
                    for i in check_out_details:
                        order_id=i[0]
                        customer_name=i[2]
                        user_name=i[9]
                        obj.add_delivery_details(order_id,customer_name,user_name)
                        obj.recent_update(order_id)
                    return redirect(url_for('home.order_tracking'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"

@home.route('/order_tracking')
def order_tracking():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            obj2=Login()
            obj3=Image_upload()
            name=session.get('name')
            admin_check=obj.admin_check(name)
            cart_items=obj.cart_items_count(name)
            # delivery=obj.get_delivery_details()
            # for i in delivery:
            order_product_category=obj.join_delivery_product_category(name)
            url_list=[]
            for i in order_product_category:
                rd_list=[]
                image=obj3.display_single_from_s3(i[5])
                rd_list.append(image)
                key=i[6].split(",")[0].strip()
                remaining_days=obj2.delivery_days(i[2],key,i[0])
                delivery_date=obj2.delivery_date(i[2],key,i[0])
                obj.delivery_date_update(delivery_date,i[0])
                rd_list.append(remaining_days)
                rd_list.append(i[1])
                rd_list.append(i[3])
                rd_list.append(i[4])
                url_list.append(rd_list)
            return render_template("delivery_page.html",admin_check=admin_check,cart_items=cart_items,name=name,url_list=url_list)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

