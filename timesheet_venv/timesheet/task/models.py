from django.db import models
from django.contrib.auth.models import User
from customer.models import customer

# Create your models here.

class priority_type(models.Model):
   priority_name = models.CharField(max_length=100)
   def __str__(self):
        return f"{self.priority_name}"


class ticket_type(models.Model):
  name = models.CharField(max_length=100, null = True)

  def __str__(self):
    return f"{self.name}"

class state(models.Model):
   state_name = models.CharField(max_length=100, null = True)
   
   def __str__(self):
    return f"{self.state_name}"

class project(models.Model):
    project_id = models.CharField(max_length = 200, null = False)
    project_name = models.CharField(max_length = 200, null = False )
    date_opened = models.DateField(null=True)

    def __str__(self):
         return f"{self.project_name}"


class subproject(models.Model):
    sub_project_id = models.CharField(max_length = 200, null = False)
    sub_project_name = models.CharField(max_length = 200, null = False)
    date_opened = models.DateField(null=True)
    project_id = models.ForeignKey(project, on_delete=models.CASCADE, null=False)


    def __str__(self):
        return f"{self.sub_project_name}"

class ticket(models.Model):
    ticket_id = models.CharField(max_length = 200, null = False)
    ticket_title = models.CharField(max_length=200, null=False)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE, null=True)
    ticket_type = models.ForeignKey(ticket_type, on_delete=models.CASCADE, null=True)
    date_opened = models.DateTimeField(null=True)
    priority = models.ForeignKey(priority_type, on_delete=models.CASCADE, null = True)
    assigned_to = models.ManyToManyField(User, related_name="assigned_tickets")  # Allow multiple users
    last_updated = models.DateTimeField(null=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name="last_updated_by")
    state = models.ForeignKey(state, on_delete=models.CASCADE, null=True)
    operational_notes = models.CharField(max_length=200, null=True)
    closed_date = models.DateTimeField(null=True)
    solution = models.TextField(max_length=500 )
    project = models.ForeignKey(project, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:  # Only generate ID if it's a new ticket
            self.ticket_id = self.generate_ticket_id()  # Generate the ticket ID based on type
        super().save(*args, **kwargs)


    def generate_ticket_id(self):
        # Mapping ticket type to prefix
        ticket_type_prefix = {
            1: 'INC',  # Incident
            2: 'STA', # Standard Enhancement
            3: 'NOR',   # Normal Enhancement
            4: 'OPR',    # Operational Change
            5: 'PR'   # Project
        }


        prefix = ticket_type_prefix.get(self.ticket_type.id, 'INC')  # Default to 'INC' if type is unknown


        # Query the last ticket with the same prefix to get the last ticket number
        last_ticket = ticket.objects.filter(ticket_id__startswith=prefix).order_by('-ticket_id').first()
        if last_ticket:
            # Extract the number from the last ticket_id and increment it
            last_number = int(last_ticket.ticket_id[3:])
            new_number = last_number + 1
        else:
            # If no previous tickets exist, start from 1
            new_number = 1


        # Format and return the new ticket ID
        return f"{prefix}{new_number:03}"


    def __str__(self):
        return f"{self.ticket_title}"
    
    
# class ticket_update_history(models.Model):
#     updated_on = models.DateTimeField(null = True)
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
#     changes = models.CharField(max_length=500, null = True)

#     def __str__(self):
#         return f"{self.changes}"
    



#for comment section
class comment(models.Model):
    ticket = models.ForeignKey('ticket', on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.ticket.id}"