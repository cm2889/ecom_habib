import json
import random
import requests

from sslwireless_sms import SSLWirelessSMS

from django.contrib import messages

from backend.models import (SMSConfiguration, SMSLog)
from threading import Thread


def send_sms(request, mobile_number, message_text):
    return_status = "failed"
    exist_sms_config = SMSConfiguration.objects.filter(status=True).first()

    if exist_sms_config:
        return_status = pos_send_sms(request, str(message_text), str(mobile_number))

    return return_status == "success"


def bulk_sms(request, mobile_numbers, message_text):
    return_status = "failed"

    mobile_number_list = mobile_numbers.split(",")
    for mobile_number in mobile_number_list:
        return_status = pos_send_sms(request, str(message_text), str(mobile_number))

    return return_status == "SUCCESS"


def pos_send_sms(request, sms_text, recipient_mobile):
    def pos_send_sms_thread(request, sms_text, recipient_mobile):
        return_status = "failed"

        exist_sms_config = SMSConfiguration.objects.filter(status=True).first()
        if exist_sms_config:
            try:
                if exist_sms_config.sms_configuration_type == "api_token":
                    api_url = exist_sms_config.api_url
                    api_token = exist_sms_config.api_token
                    sms_id = exist_sms_config.sms_id

                    if not api_url:
                        messages.error(request, "SMS API URL is not configured.")
                        return return_status
                    elif not api_token:
                        messages.error(request, "SMS API Token is not configured.")
                        return return_status
                    elif not sms_id:
                        messages.error(request, "SMS ID is not configured.")
                        return return_status

                    headers = {'Content-type': 'application/json'}

                    random_number = random.randrange(10**11, 10**12)
                    csms_id_random_number = f"{random_number:012d}"

                    payload = {
                        "api_token": api_token,
                        "sid": sms_id,
                        "sms": str(sms_text),
                        "msisdn": str(recipient_mobile),
                        "csms_id": str(csms_id_random_number)
                    }

                    response = requests.post(api_url, json=payload, headers=headers)

                    if response.status_code == 200:
                        return_data = response.json()
                        return_status = return_data.get('status', 'failed')
                    else:
                        return_status = 'failed'
                elif exist_sms_config.sms_configuration_type == "password":
                    username = exist_sms_config.username
                    password = exist_sms_config.password
                    sms_id = exist_sms_config.sms_id

                    if not username:
                        messages.error(request, "SMS Username is not configured.")
                        return return_status
                    elif not password:
                        messages.error(request, "SMS Password is not configured.")
                        return return_status
                    elif not sms_id:
                        messages.error(request, "SMS ID is not configured.")
                        return return_status

                    sendMobileSMS = SSLWirelessSMS(username, password, sms_id)

                    result = sendMobileSMS.send(recipient_mobile, sms_text)
                    sms_response = json.loads(result)

                    return_status = sms_response.get('status', 'failed')

                SMSLog.objects.create(mobile_number=recipient_mobile, message_text=sms_text, status=return_status, created_by_id=request.user.id, sms_configuration=exist_sms_config)
            except Exception:
                SMSLog.objects.create(mobile_number=recipient_mobile, message_text=sms_text, status="failed", created_by_id=request.user.id, sms_configuration=exist_sms_config)
        return return_status

    Thread(target=pos_send_sms_thread, args=(request, sms_text, recipient_mobile)).start()