from flask import Flask, request, jsonify,render_template,send_from_directory
import hashlib
import hmac
import os
from dotenv import load_dotenv
import razorpay
from  pymongo import MongoClient
# import smtplib
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import asyncio

app = Flask(__name__)
load_dotenv()

razorpay_api_key = os.getenv('RAZORPAY_API_KEY')
razorpay_api_secret = os.getenv("RAZORPAY_APT_SECRET")
mongo_uri = os.getenv("MONGO_URI")

client = razorpay.Client(auth=(razorpay_api_key, razorpay_api_secret))
mongo_client = MongoClient(mongo_uri)
mongo_db=mongo_client["user_payment"]
collection =mongo_db['test']

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'anupamghorai73@gmail.com'
sender_password = 'nlsx pgpo emvt ofrg'
subject = 'Test Email from Python Script'


@app.route('/')
def index():
    return render_template('index.html', razorpay_api_key=razorpay_api_key)

@app.route('/create_order', methods=['POST'])
def create_order():
    # amount = int(request.form.get('amount')) * 100  # Convert to paise
    amount = 37900  # Example amount in paise
    currency = 'INR'
    payment_capture = 1

    order = client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': payment_capture
    })

    return jsonify(order)

@app.route('/payment_verification', methods=['POST'])
def payment_verification():
    data = request.get_json()
    print(data)
    razorpay_order_id = data['razorpay_order_id']
    razorpay_payment_id = data['razorpay_payment_id']
    razorpay_signature = data['razorpay_signature']
    user_name= data["user_name"]
    user_email=data['user_email']
    user_phone=data["user_phone"]

    body = razorpay_order_id + "|" + razorpay_payment_id
    expected_signature = hmac.new(
        razorpay_api_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected_signature == razorpay_signature:
        document={
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
            'user_name':user_name,
            'user_email':user_email,
            'user_phone':user_phone
        }
        collection.insert_one(document)
        print("data inserted sucessfully::",document)

        # send_confirmation_email(user_name, user_email, razorpay_payment_id)


        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
@app.route('/order_success')
def order_success():
    reference = request.args.get('reference')
    user_name = request.args.get('user_name')
    user_email = request.args.get('user_email')
    print("Reference:", reference)
    print("User Name:", user_name)
    print("User Email:", user_email)
    asyncio.run(send_confirmation_email(user_name, user_email, reference))
    return render_template('order_success.html', reference=reference, user_name=user_name, user_email=user_email)

async def send_confirmation_email(user_name, user_email, payment_id):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Payment Confirmation'
    
    body = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        td, th {
            padding: 10px;
            vertical-align: middle;
            border: 1px solid #dddddd;
            text-align: center;
        }
        .link-col {
            text-align: center;
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <p>Dear {{ user_name }},</p>
    <p>We are excited to share the following resources with you:</p>
    <table>
        <tr>
            <th>Topic</th>
            <th>Topic Link</th>
        </tr>
        <tr>
            <td>{{ topic1_name }}</td>
            <td class="link-col"><a href="{{ link1_url }}">{{ link1_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic2_name }}</td>
            <td class="link-col"><a href="{{ link2_url }}">{{ link2_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic3_name }}</td>
            <td class="link-col"><a href="{{ link3_url }}">{{ link3_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic4_name }}</td>
            <td class="link-col"><a href="{{ link4_url }}">{{ link4_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic5_name }}</td>
            <td class="link-col"><a href="{{ link5_url }}">{{ link5_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic6_name }}</td>
            <td class="link-col"><a href="{{ link6_url }}">{{ link6_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic7_name }}</td>
            <td class="link-col"><a href="{{ link7_url }}">{{ link7_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic8_name }}</td>
            <td class="link-col"><a href="{{ link8_url }}">{{ link8_url }}</a></td>
        </tr>
        <tr>
            <td>{{ topic9_name }}</td>
            <td class="link-col"><a href="{{ link9_url }}">{{ link9_url }}</a></td>
        </tr>
    </table>
    <p>Best regards,</p>
    <p>Mr. Anupam Ghorai</p>
    <p>B.A.S.L.P(WBUHS)</p>
    <p>RCI REG-A72311</p>
    <p>Phone Number:+91-7003458858<p>
</body>
</html>


    """
    template = Template(body)   
    context = {
    'user_name': user_name,
    'topic1_name': 'Topic- অটিজম Symptoms & Speech Therapy',
    'link1_url': 'https://drive.google.com/file/d/1qd6wH0T0Wrrp07fFf85ScWGz3fytcEJX/view?usp=sharing',
    'topic2_name': "Topic- (সমস্ত শিশুর জন্য) Why Don't Children Speak on time",
    'link2_url': 'https://drive.google.com/file/d/19x8YIeKGk6fqT4J9MX10ImKywZfElMK9/view?usp=sharing',
    'topic3_name': 'Topic- CP child, Home based therapy, Oro motor Exercise',
    'link3_url': 'https://drive.google.com/file/d/1vGoZIG6HThqaVbqMEHjCwi4VtD4TagJP/view?usp=sharing',
    'topic4_name': 'Topic-শুনতে কম পায় এমন শিশুর Hearing aids পর থেরাপি',
    'link4_url': 'https://drive.google.com/file/d/1IgdfBWUc10CW6YWf12yHOSAenYf6sJub/view?usp=sharing',
    'topic5_name': 'Topic- অটিজম Behavioral Management ও বাড়িতে থেরাপি Hyper Activity দূর',
    'link5_url': 'https://drive.google.com/file/d/1Nn4hkr4BQ2B4ZwXzbgiyIszRAiLMn8E3/view?usp=sharing',
    'topic6_name': 'Topic- ADHD VS Autism Diff. Diagnosis & Therapy',
    'link6_url': 'https://drive.google.com/file/d/1HB4IHGx-GgIr2D23WV42a7vG572LzNJ1/view?usp=sharing',
    'topic7_name': 'Topic- Stuttering(জড়ানো কথা)Patient Target based Speech Therapy',
    'link7_url': 'https://drive.google.com/file/d/1apd0Vun1Yp56zN1Y4VEW3FOr9UJsj7Th/view?usp=sharing',
    'topic8_name': 'Topic-Articulation-Phonological উচ্চারণের সমস্যা Therapy',
    'link8_url': 'https://drive.google.com/file/d/1BVz6hliDPCzyZnOasxkwy9SvztbmFNFI/view?usp=sharing',
    'topic9_name': 'Topic- Ear-Tinnitusকানে শব্দ-Dischargeজল পুঁজ-OM',
    'link9_url': 'https://drive.google.com/file/d/1UoUc2aGbBrKvrXHLRQbg-BbTsUkk0tK0/view?usp=sharing',
    'sender_name': "Sender Name",
    'company_name': "Company Name"
}

    rendered_html = template.render(context)
    msg.attach(MIMEText(rendered_html, 'html'))
    
    # try:
    #     server = smtplib.SMTP(smtp_server, smtp_port)
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     text = msg.as_string()
    #     server.sendmail(sender_email, user_email, text)
    #     server.quit()
    #     print(f"Email sent to {user_email}")
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
    try:
        async with aiosmtplib.SMTP(hostname=smtp_server, port=smtp_port) as server:
            await server.login(sender_email, sender_password)
            await server.send_message(msg)
            # print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')


@app.route('/terms')
def terms():
    return render_template('Terms_and_condition_page.html')
@app.route('/contact')
def contact():
    return render_template("Contact_us_page.html")
@app.route('/privacy')
def privacy():
    return render_template("Privacy_policy_page.html")
@app.route('/about_us')
def about_us():
    return render_template("About_us_page.html")
@app.route('/refund')
def refund():
    return render_template("Refund_and_Cancellation_page.html")
if __name__ == '__main__':
    app.run()
