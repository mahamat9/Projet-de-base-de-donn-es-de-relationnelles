from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length = 20, unique = True)

class Employee(models.Model):
    last_name = models.CharField(max_length = 20)
    first_name = models.CharField(max_length = 20)
    mailbox = models.CharField(max_length = 20)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)

class Content_Type(models.Model):
    ct_name = models.CharField(max_length = 20, unique = True)

class Charset(models.Model):
    charset_name = models.CharField(max_length=20, unique = True)

class Content(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(Content_Type, on_delete = models.CASCADE)
    charset = models.ForeignKey(Charset, on_delete = models.CASCADE)

class Subject(models.Model):
    subject_name = models.CharField(max_length = 100, unique = True)

class Email_address(models.Model):
    email_address_name = models.CharField(max_length = 115, unique = True)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True)
    interne = models.BooleanField()

class Message(models.Model):
    send_date = models.DateTimeField(max_length = 30)
    content = models.ForeignKey(Content, on_delete = models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE)
    sender_email = models.ForeignKey(Email_address, on_delete = models.CASCADE)

class Reciever(models.Model):
    message = models.ForeignKey(Message, on_delete = models.CASCADE)
    email_address = models.ForeignKey(Email_address, on_delete = models.CASCADE)
