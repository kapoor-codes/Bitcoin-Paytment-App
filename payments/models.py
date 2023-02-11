from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class product(models.Model):
    productName = models.CharField(max_length=200)
    productDesc = models.TextField()
    productPrice = models.FloatField()
    productDisp = models.ImageField()

    def __str__(self):
        return self.productName

class invoice(models.Model):
    STATUS_CHOICES = [
        (-1,"Not Started"),
        (0,'Unconfirmed'),
        (1,"Partially Confirmed"),
        (2,"Confirmed")
    ]

    productName = models.ForeignKey(product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoiceStatus = models.IntegerField(choices=STATUS_CHOICES, default=-1)
    invoiceOrderId = models.CharField(max_length=250)
    invoiceAddress = models.CharField(max_length=250, default='')
    invoiceBtcValue = models.IntegerField(blank=True, null=True)
    invoiceReceived = models.IntegerField(blank=True, null=True)
    invoiceTxid = models.CharField(max_length=250, blank=True, null=True)
    invoiceRbf = models.IntegerField(blank=True, null=True)
    invoiceCreatedAt = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user.username) + '|' + str(self.invoiceAddress)