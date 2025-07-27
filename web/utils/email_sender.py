import smtplib
from email.mime.text import MIMEText

def enviar_confirmacao_email(destinatario, assunto, corpo):
    msg = MIMEText(corpo, 'html')
    msg['Subject'] = assunto
    msg['From'] = "seuemail@gmail.com"
    msg['To'] = destinatario

    servidor = smtplib.SMTP('smtp.gmail.com', 587)
    servidor.starttls()
    servidor.login("seuemail@gmail.com", "sua_senha")
    servidor.sendmail("seuemail@gmail.com", destinatario, msg.as_string())
    servidor.quit()