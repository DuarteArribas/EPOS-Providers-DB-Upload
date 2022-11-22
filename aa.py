def emailNewFiles(newFiles):
  """Emails new files to the specified email.

  Parameters
  ----------
  newFiles : str
      the contents of the new files
  """
  server = smtplib.SMTP("smtp-mail.outlook.com",587)
  server.connect("smtp-mail.outlook.com",587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(FROM_EMAIL,keyring.get_password("system","EMAIL_TO_SEND"))
  msg = MIMEText(F"New files available! - {newFiles}")
  msg["Subject"] = "You've got new files!"
  server.sendmail(FROM_EMAIL,TO_EMAIL,msg.as_string())
  server.quit()