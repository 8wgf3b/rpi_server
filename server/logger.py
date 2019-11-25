import logging
import logging.handlers
from datetime import datetime
import os
import smtplib


class EmailTRFH(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, mail_params, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mail_report(self):
        try:
            msg = (f"""From:{mail_params['from']}
Subject: log reports \n
To: {mail_params['to']} \n""")
            with open(self.baseFilename, 'r') as logs:
                content = logs.read()
                if not content:
                    return None
                msg += content
            server = smtplib.SMTP_SSL(mail_params['host'], mail_params['port'])
            server.ehlo()
            server.login(mail_params['from'], mail_params['password'])
            server.sendmail(mail_params['from'], mail_params['to'], msg)
            server.quit()
        except Exception as e:
            print(e)

    def doRollover(self):
        self.mail_report()
        super().doRollover()


today = datetime.today
logger = logging.getLogger('rpi4')
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(funcName)s: %(message)s')
file_handler = logging.FileHandler(f'logs/{today().strftime("%d-%m-%Y")}.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

mail_params = dict()
mail_params['host'] = os.getenv('MAILHOST')
mail_params['port'] = int(os.getenv('MAILPORT'))
mail_params['from'] = os.getenv('FROM')
mail_params['to'] = os.getenv('TO')
mail_params['password'] = os.getenv('MAIL_PASS')

email_handler = EmailTRFH(mail_params, 'temp/temp.log', when="m", interval=30, backupCount=5)
email_handler.setFormatter(formatter)
email_handler.setLevel(logging.WARNING)

logger = logging.getLogger('rpi4')
logger.setLevel(logging.DEBUG)
logger.addHandler(email_handler)
logger.addHandler(file_handler)
#logger.addHandler(stream_handler)


if __name__ == "__main__":
    pass
