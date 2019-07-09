import smtplib


s = smtplib.SMTP('smtp.gmail.com',587)
s.starttls()
s.login('eabcd8235@gmail.com','04023155878')
s.sendmail('eabcd8235@gmail.com','seethamraju.purvaj@iiitb.org','Hola')
s.quit()
