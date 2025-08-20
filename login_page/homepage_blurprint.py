from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
import re
from libs.UserDb import UserDb
# from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from login_parameter import Login,Image_upload
from loggers import Loggers
from configparser import ConfigParser
import logging
# import urllib.request
# import os
# import boto3
# from werkzeug.utils import secure_filename
# from werkzeug.exceptions import RequestEntityTooLarge
# from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
# from login_blueprint import login

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
            print(search[1])
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list.append(search_url_list2)
            return render_template("homepage.html",category=category,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("homepage.html",category=category,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
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
            url_list.append(url_list2)
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        brand=request.args.get('brand')
        price=request.args.get('price')
        motherboard=request.args.get('motherboard')
        fan=request.args.get('fan')

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
            motherboard_list.add(key)
        
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
                search_url_list.append(search_url_list2)
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.cpu_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if motherboard:
            motherboard_url_list=[]
            sort=obj3.cpu_motherboard_sort(motherboard,page)
            for i in sort[1]:
                motherboard_url_list2=[]
                motherboard_url=obj2.display_single_from_s3(i[0])
                motherboard_url_list2.append(motherboard_url)
                motherboard_url_list2.append(i[1])
                motherboard_url_list2.append(i[2])
                motherboard_url_list2.append(i[3])
                motherboard_url_list2.append(i[4])
                motherboard_url_list.append(motherboard_url_list2)
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(motherboard_url_list),url_list=motherboard_url_list,total_page=sort[2],page=page)
        if fan:
            fan_url_list=[]
            sort=obj3.cpu_fan_sort(fan,page)
            for i in sort[1]:
                fan_url_list2=[]
                fan_url=obj2.display_single_from_s3(i[0])
                fan_url_list2.append(fan_url)
                fan_url_list2.append(i[1])
                fan_url_list2.append(i[2])
                fan_url_list2.append(i[3])
                fan_url_list2.append(i[4])
                fan_url_list.append(fan_url_list2)
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,length=len(fan_url_list),url_list=fan_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("cpu_page.html",fan_list=fan_list,motherboard_list=motherboard_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
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

        brand=request.args.get('brand')
        price=request.args.get('price')
        connectivity=request.args.get('connectivity')
        noise_cancellation=request.args.get('noise_cancellation')
        microphone=request.args.get('microphone')
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
                search_url_list.append(search_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.headphone_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,connect=connect,noise_cancel=noise_cancel,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if connectivity:
            connect_url_list=[]
            sort=obj3.headphone_sorting(connectivity,page)
            for i in sort[1]:
                connect_url_list2=[]
                connect_url=obj2.display_single_from_s3(i[0])
                connect_url_list2.append(connect_url)
                connect_url_list2.append(i[1])
                connect_url_list2.append(i[2])
                connect_url_list2.append(i[3])
                connect_url_list2.append(i[4])
                connect_url_list.append(connect_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,connect=connect,product_brand=product_brand,noise_cancel=noise_cancel,name=name,length=len(connect_url_list),url_list=connect_url_list,total_page=sort[2],page=page)
        if noise_cancellation:
            noise_cancel_url_list=[]
            sort=obj3.headphone_sorting(noise_cancellation,page)
            for i in sort[1]:
                noise_cancel_url_list2=[]
                noise_cancel_url=obj2.display_single_from_s3(i[0])
                noise_cancel_url_list2.append(noise_cancel_url)
                noise_cancel_url_list2.append(i[1])
                noise_cancel_url_list2.append(i[2])
                noise_cancel_url_list2.append(i[3])
                noise_cancel_url_list2.append(i[4])
                noise_cancel_url_list.append(noise_cancel_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,connect=connect,product_brand=product_brand,noise_cancel=noise_cancel,name=name,length=len(noise_cancel_url_list),url_list=noise_cancel_url_list,total_page=sort[2],page=page)
        if microphone:
            microphone_url_list=[]
            sort=obj3.headphone_sorting(microphone,page)
            for i in sort[1]:
                microphone_url_list2=[]
                microphone_url=obj2.display_single_from_s3(i[0])
                microphone_url_list2.append(microphone_url)
                microphone_url_list2.append(i[1])
                microphone_url_list2.append(i[2])
                microphone_url_list2.append(i[3])
                microphone_url_list2.append(i[4])
                microphone_url_list.append(microphone_url_list2)
            return render_template("headphone_page.html",microphone_list=microphone_list,connect=connect,product_brand=product_brand,noise_cancel=noise_cancel,name=name,length=len(microphone_url_list),url_list=microphone_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("headphone_page.html",microphone_list=microphone_list,noise_cancel=noise_cancel,connect=connect,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)

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

        brand=request.args.get('brand')
        price=request.args.get('price')
        switch=request.args.get('switch')
        connectivity=request.args.get('connectivity')
        rollover=request.args.get('rollover')
        backlight=request.args.get('backlight')
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
                search_url_list.append(search_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.keyboard_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if switch:
            switch_url_list=[]
            sort=obj3.keyboard_sorting(switch,page)
            for i in sort[1]:
                switch_url_list2=[]
                switch_url=obj2.display_single_from_s3(i[0])
                switch_url_list2.append(switch_url)
                switch_url_list2.append(i[1])
                switch_url_list2.append(i[2])
                switch_url_list2.append(i[3])
                switch_url_list2.append(i[4])
                switch_url_list.append(switch_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(switch_url_list),url_list=switch_url_list,total_page=sort[2],page=page)
        if connectivity:
            connect_url_list=[]
            sort=obj3.keyboard_sorting(connectivity,page)
            for i in sort[1]:
                connect_url_list2=[]
                connect_url=obj2.display_single_from_s3(i[0])
                connect_url_list2.append(connect_url)
                connect_url_list2.append(i[1])
                connect_url_list2.append(i[2])
                connect_url_list2.append(i[3])
                connect_url_list2.append(i[4])
                connect_url_list.append(connect_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(connect_url_list),url_list=connect_url_list,total_page=sort[2],page=page)
        if rollover:
            rollover_url_list=[]
            sort=obj3.keyboard_sorting(rollover,page)
            for i in sort[1]:
                rollover_url_list2=[]
                rollover_url=obj2.display_single_from_s3(i[0])
                rollover_url_list2.append(rollover_url)
                rollover_url_list2.append(i[1])
                rollover_url_list2.append(i[2])
                rollover_url_list2.append(i[3])
                rollover_url_list2.append(i[4])
                rollover_url_list.append(rollover_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(rollover_url_list),url_list=rollover_url_list,total_page=sort[2],page=page)
        if backlight:
            backlight_url_list=[]
            sort=obj3.keyboard_sorting(backlight,page)
            for i in sort[1]:
                backlight_url_list2=[]
                backlight_url=obj2.display_single_from_s3(i[0])
                backlight_url_list2.append(backlight_url)
                backlight_url_list2.append(i[1])
                backlight_url_list2.append(i[2])
                backlight_url_list2.append(i[3])
                backlight_url_list2.append(i[4])
                backlight_url_list.append(backlight_url_list2)
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,length=len(backlight_url_list),url_list=backlight_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("keyboard_page.html",backlight_list=backlight_list,key_rollover=key_rollover,keyboard_connect=keyboard_connect,switch_type=switch_type,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
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
        
        brand=request.args.get('brand')
        price=request.args.get('price')
        resolution=request.args.get('resolution')
        panel=request.args.get('panel')
        refresh_rate=request.args.get('refresh_rate')
        connectivity=request.args.get('connectivity')
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
                search_url_list.append(search_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.monitor_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if resolution:
            res_url_list=[]
            sort=obj3.monitor_sorting(resolution,page)
            for i in sort[1]:
                res_url_list2=[]
                res_url=obj2.display_single_from_s3(i[0])
                res_url_list2.append(res_url)
                res_url_list2.append(i[1])
                res_url_list2.append(i[2])
                res_url_list2.append(i[3])
                res_url_list2.append(i[4])
                res_url_list.append(res_url_list2)
            return render_template("monitor_page.html",refresh_rate_list=refresh_rate_list,connectivity_list=connectivity_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(res_url_list),url_list=res_url_list,total_page=sort[2],page=page)
        if panel:
            panel_url_list=[]
            sort=obj3.monitor_sorting(panel,page)
            for i in sort[1]:
                panel_url_list2=[]
                panel_url=obj2.display_single_from_s3(i[0])
                panel_url_list2.append(panel_url)
                panel_url_list2.append(i[1])
                panel_url_list2.append(i[2])
                panel_url_list2.append(i[3])
                panel_url_list2.append(i[4])
                panel_url_list.append(panel_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(panel_url_list),url_list=panel_url_list,total_page=sort[2],page=page)
        if refresh_rate:
            rr_url_list=[]
            sort=obj3.monitor_sorting(refresh_rate,page)
            for i in sort[1]:
                rr_url_list2=[]
                rr_url=obj2.display_single_from_s3(i[0])
                rr_url_list2.append(rr_url)
                rr_url_list2.append(i[1])
                rr_url_list2.append(i[2])
                rr_url_list2.append(i[3])
                rr_url_list2.append(i[4])
                rr_url_list.append(rr_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(rr_url_list),url_list=rr_url_list,total_page=sort[2],page=page)
        if connectivity:
            connectivity_url_list=[]
            sort=obj3.monitor_sorting(connectivity,page)
            for i in sort[1]:
                connectivity_url_list2=[]
                connectivity_url=obj2.display_single_from_s3(i[0])
                connectivity_url_list2.append(connectivity_url)
                connectivity_url_list2.append(i[1])
                connectivity_url_list2.append(i[2])
                connectivity_url_list2.append(i[3])
                connectivity_url_list2.append(i[4])
                connectivity_url_list.append(connectivity_url_list2)
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,length=len(connectivity_url_list),url_list=connectivity_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("monitor_page.html",connectivity_list=connectivity_list,refresh_rate_list=refresh_rate_list,panel_list=panel_list,resolution_list=resolution_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)

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

        brand=request.args.get('brand')
        price=request.args.get('price')
        connectivity=request.args.get('connectivity')
        dpi=request.args.get('dpi')
        sensor=request.args.get('sensor')
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
                search_url_list.append(search_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.mouse_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if connectivity:
            connect_url_list=[]
            sort=obj3.mouse_sorting(connectivity,page)
            for i in sort[1]:
                connect_url_list2=[]
                connect_url=obj2.display_single_from_s3(i[0])
                connect_url_list2.append(connect_url)
                connect_url_list2.append(i[1])
                connect_url_list2.append(i[2])
                connect_url_list2.append(i[3])
                connect_url_list2.append(i[4])
                connect_url_list.append(connect_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(connect_url_list),url_list=connect_url_list,total_page=sort[2],page=page)
        if dpi:
            dpi_url_list=[]
            sort=obj3.mouse_sorting(dpi,page)
            for i in sort[1]:
                dpi_url_list2=[]
                dpi_url=obj2.display_single_from_s3(i[0])
                dpi_url_list2.append(dpi_url)
                dpi_url_list2.append(i[1])
                dpi_url_list2.append(i[2])
                dpi_url_list2.append(i[3])
                dpi_url_list2.append(i[4])
                dpi_url_list.append(dpi_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(dpi_url_list),url_list=dpi_url_list,total_page=sort[2],page=page)
        if sensor:
            sensor_url_list=[]
            sort=obj3.mouse_sorting(sensor,page)
            for i in sort[1]:
                sensor_url_list2=[]
                sensor_url=obj2.display_single_from_s3(i[0])
                sensor_url_list2.append(sensor_url)
                sensor_url_list2.append(i[1])
                sensor_url_list2.append(i[2])
                sensor_url_list2.append(i[3])
                sensor_url_list2.append(i[4])
                sensor_url_list.append(sensor_url_list2)
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(sensor_url_list),url_list=sensor_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("mouse_page.html",sensor_list=sensor_list,dpi_list=dpi_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
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

        brand=request.args.get('brand')
        price=request.args.get('price')
        connectivity=request.args.get('connectivity')
        bass=request.args.get('bass')
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
                search_url_list.append(search_url_list2)
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        if brand:
            brand_url_list=[]
            sort=obj3.speaker_brand_sort(brand,page)
            for i in sort[1]:
                brand_url_list2=[]
                brand_url=obj2.display_single_from_s3(i[0])
                brand_url_list2.append(brand_url)
                brand_url_list2.append(i[1])
                brand_url_list2.append(i[2])
                brand_url_list2.append(i[3])
                brand_url_list2.append(i[4])
                brand_url_list.append(brand_url_list2)
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(brand_url_list),url_list=brand_url_list,total_page=sort[2],page=page)
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
                price_url_list.append(price_url_list2)
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(price_url_list),url_list=price_url_list,total_page=sort[2],page=page)
        if connectivity:
            connect_url_list=[]
            sort=obj3.speaker_sorting(connectivity,page)
            for i in sort[1]:
                connect_url_list2=[]
                connect_url=obj2.display_single_from_s3(i[0])
                connect_url_list2.append(connect_url)
                connect_url_list2.append(i[1])
                connect_url_list2.append(i[2])
                connect_url_list2.append(i[3])
                connect_url_list2.append(i[4])
                connect_url_list.append(connect_url_list2)
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(connect_url_list),url_list=connect_url_list,total_page=sort[2],page=page)
        if bass:
            bass_url_list=[]
            sort=obj3.speaker_sorting(bass,page)
            for i in sort[1]:
                bass_url_list2=[]
                bass_url=obj2.display_single_from_s3(i[0])
                bass_url_list2.append(bass_url)
                bass_url_list2.append(i[1])
                bass_url_list2.append(i[2])
                bass_url_list2.append(i[3])
                bass_url_list2.append(i[4])
                bass_url_list.append(bass_url_list2)
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,length=len(bass_url_list),url_list=bass_url_list,total_page=sort[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("speaker_page.html",bass_list=bass_list,connectivity_list=connectivity_list,product_brand=product_brand,name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
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
            store=obj.fetch_product_user(product_id)
            for i in store:
                url=obj2.display_from_s3(i[5])
            return render_template("show_product_user.html",name=name,url=url,product_id=product_id,product_brand=store[0][0],product_name=store[0][1],description=store[0][2],features=store[0][3],price=store[0][4])
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
            return render_template("cart.html",prod_id=prod_id,name=name,url_list=url_list,total=total,count=count)
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
            count=obj.cart_count(name)
            cart_prod=obj.cart_product_id(name)
            for i in cart_prod:
                obj.insert_in_check_out(i[1],name)
                cart_quantity=obj.cart_quantity(i[1])
                obj.check_out_update_quantity(cart_quantity,i[1])
            return render_template("payment_method_page.html",name=name,total=total,count=count)
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
            if request.method == "POST":
                obj=UserDb()
                name=session.get('name')
                customer_name=request.form.get('customer_name')
                address=request.form.get('address')
                customer_number=request.form.get('customer_number')
                payment_method=request.form.get('payment_method')
                dateandtime=datetime.now(ZoneInfo("Asia/Kolkata"))
                date_time=dateandtime.strftime("%d-%m-%Y, %H:%M:%S")
                card_name=request.form.get('card_name')
                card_number=request.form.get('card_number')
                obj.card_details(card_name,card_number)
                obj.check_out_update(customer_name,address,customer_number,payment_method,date_time,name)
                obj.check_out_payment_update(name)
                obj.update_cart_status(name)
                check_out_details=obj.check_out_details()
                for i in check_out_details:
                    order_id=i[0]
                    customer_name=i[2]
                    user_name=i[9]
                obj.add_delivery_details(order_id,customer_name,user_name)
                return redirect(url_for('home.order_tracking'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

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
            # delivery=obj.get_delivery_details()
            # for i in delivery:
            order_product_category=obj.join_delivery_product_category(name)
            url_list=[]
            for i in order_product_category:
                rd_list=[]
                image=obj3.display_single_from_s3(i[5])
                rd_list.append(image)
                key=i[6].split(",")[0].strip()
                remaining_days=obj2.delivery_days(i[2],key)
                rd_list.append(remaining_days)
                rd_list.append(i[1])
                rd_list.append(i[3])
                rd_list.append(i[4])
                url_list.append(rd_list)
            return render_template("delivery_page.html",name=name,url_list=url_list)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

