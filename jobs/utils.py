from .models import OTPRequest
import random
from kavenegar import *
from django.conf import settings


try:
    import jdatetime
except ImportError:
    jdatetime = None



def clean_token(text):

    if not text:
        return "."

    s = str(text).strip()

    s = s.replace(" ", "-")
    s = s.replace("‌", "-")


    return s[:20]


def send_interview_sms(phone_number, name, job_title, interview_time, salary):

    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)


        if salary and str(salary).isdigit():
            formatted_salary = "{:,}".format(int(salary))
        else:
            formatted_salary = str(salary)

        params = {
            'receptor': phone_number,
            'template': 'interviewinvite',

            'token': clean_token(name),
            'token2': clean_token(job_title),
            'token10': clean_token(formatted_salary),
            'token3': clean_token(interview_time),

            'type': 'sms',
        }

        print(f"📤 Sending SMS params: {params}")

        response = api.verify_lookup(params)
        print("✅ SMS Sent Successfully:", response)
        return True

    except APIException as e:
        print(f"❌ Kavenegar API Error [Status {e.args[0] if e.args else '?'}]: {e}")
        return False
    except HTTPException as e:
        print(f"❌ Kavenegar Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unknown Error in SMS: {e}")
        return False
def send_otp_code(phone_number):
    # 1. تولید کد
    code = str(random.randint(1000, 9999))

    OTPRequest.objects.filter(phone=phone_number).delete()
    OTPRequest.objects.create(phone=phone_number, code=code)

    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)

        params = {
            'receptor': phone_number,
            'template': 'verify',
            'token': code,
            'type': 'sms',
        }

        response = api.verify_lookup(params)
        print(f"✅ SMS Sent! Code: {code}")
        return code

    except APIException as e:
        print(f"❌ Kavenegar API Error: {e}")
    except HTTPException as e:
        print(f"❌ Kavenegar HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Unknown Error: {e}")

    return None


