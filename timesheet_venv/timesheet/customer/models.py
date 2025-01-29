from django.db import models

# Create your models here.
class customer_status(models.Model):
  status_name = models.CharField( max_length=50)

  def __str__(self):
    return self.status_name

class customer(models.Model):
  name = models.CharField(max_length=100, null = True)
  city = models.CharField(max_length=100, null = True)
  state = models.CharField(max_length=100, null = True)
  zipcode = models.CharField(max_length=100, null = True)
  street1 = models.CharField(max_length=100, null = True)
  street2 = models.CharField(max_length=100, null = True)
  phone = models.CharField(max_length=100, null = True)
  contract_hr = models.IntegerField(null = True)
  create_date = models.DateField(null = True)
  status = models.ForeignKey(customer_status, on_delete= models.SET_NULL, null=True)

  def __str__(self):
    return self.name



class customer_contact(models.Model):
  customer = models.ForeignKey(customer, on_delete=models.CASCADE, null = True)
  contact_id = models.IntegerField(primary_key= True)
  name = models.CharField(max_length=100, null = True)
  phone = models.CharField(max_length=100, null = True)
  email = models.CharField(max_length=100, null = True)

  def __str__(self):
    return f"{self.customer.name}"