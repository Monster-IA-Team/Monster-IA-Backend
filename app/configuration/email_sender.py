import smtplib, os
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "mailpit")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

BASI_EMAIL = "noreply@monsteria.com"

class EmailSender:
    @staticmethod
    def send_email(to_email: str, token: str):
        msg = EmailMessage()
        msg['Subject'] = "Activate your Monster IA account"
        msg['From'] = BASI_EMAIL
        msg['To'] = to_email
        
        activation_link = token
        msg.set_content(f"""
        Hello!
        Welcome to the Monster IA app.
        
        To activate your account and log in, copy and paste this link into your browser:
        {activation_link}
        
        The link is valid for 24 hours.
        If you didn't create the account, simply ignore this message.
        """)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f5f7; padding: 20px; margin: 0;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                
                <h2 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">Welcome to Monster IA! 🐉</h2>
                
                <p style="color: #555555; font-size: 16px; line-height: 1.5;">Hello,</p>
                <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                    Thank you for registering. To activate your account and start using the app, please click the button below:
                </p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{activation_link}" style="background-color: #10b981; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; display: inline-block;">
                        Activate Account
                    </a>
                </div>
                
                <p style="color: #777777; font-size: 14px; line-height: 1.5;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{activation_link}" style="color: #3b82f6; word-break: break-all;">{activation_link}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eaeaea; margin: 30px 0;">
                
                <p style="color: #999999; font-size: 12px; text-align: center;">
                    This link is valid for 24 hours.<br>
                    If you didn't create this account, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.add_alternative(html_content, subtype='html')
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)