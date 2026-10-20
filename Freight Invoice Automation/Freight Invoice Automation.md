#Freight Invoice Automation

##Problem

Shipment PDFs from carriers, customs brokers, and warehouses arrive in
different layouts, and staff manually re-enter the information into
finance systems.

##What to Build
A workflow where users upload PDFs and agents: - Extract the invoice
data. - Reconcile it against a booking record. - Draft the invoice. -
Flag low-confidence invoices for human approval.
Include a review queue and a dashboard showing turnaround time, error
rate, and status.
Preparation Phase
According to our project documentation, the preparation phase includes:
Collect sample invoice PDFs from different senders.
Prepare matching booking records.
Identify the correct fields in each invoice and prepare the expected
answers.
Finalize the required fields and validation rules.

##Workflow
``` text
        Invoice PDF
             |
             v
 Extract actual billed details
             |
             v
       Booking Record
             |
             v
 Retrieve expected shipment details
             |
             v
       Reconciliation
             |
             v
 Match shipment IDs and compare charges/details
             |
             v
           Result
             |
       +-----+------+
       |            |
     Match       Mismatch
       |            |
   Continue     Flag for review
```
##Key Principles

Real functionality first: The UI should look polished, but its
buttons and workflows must actually work.
Different layouts: Do not train or test the system using only
one invoice template.
Reliable results: Combine AI-based extraction with code-based
validation, booking comparison, and human approval.
Proper testing: Measure extraction accuracy, errors, mismatches,
and review outcomes.
No unnecessary features: Do not spend time on features that do
not add value to the requirements provided by the project
supervisor.
