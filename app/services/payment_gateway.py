import datetime
import razorpay
from config.settings import settings

class PaymentGateway:
    """
    A simulated payment gateway to process legitimate transactions, integrated with Razorpay.
    """
    def __init__(self):
        # Initialize the Razorpay client
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def process_payment(self, transaction_data: dict) -> dict:
        """
        Simulates successfully processing a payment.
        In a real system, this would involve API calls to a service like Stripe or PayPal.
        """
        print(f"Connecting to external payment gateway (Razorpay) for transaction: {transaction_data.get('transaction_id')}")
        
        # Convert amount to paise (assuming original amount is in INR/USD and we need subunits for Razorpay)
        # Razorpay expects the amount in the smallest currency subunit (e.g., paise for INR)
        # Assuming transaction_data['amount'] is in a major currency unit like USD or INR
        # Note: In a real system you would enforce currency in the transaction data.
        amount_in_subunits = int(transaction_data.get('Amount', 0) * 100)
        
        if amount_in_subunits <= 0:
             print("Invalid amount for payment processing.")
             return {
                 "status": "failed",
                 "message": "Invalid transaction amount."
             }

        try:
             # Create a Razorpay Order
             order_data = {
                 "amount": amount_in_subunits,
                 "currency": "INR", # Assuming INR for simplicity
                 "receipt": f"receipt_{transaction_data.get('transaction_id')}",
                 "notes": {
                     "user_id": transaction_data.get("user_id")
                 }
             }

             order = self.client.order.create(data=order_data)
             
             # Simulate a successful payment confirmation
             # In a real frontend application, you would pass this order_id back to the client
             # so they can complete the checkout flow with the Razorpay JS SDK.
             confirmation = {
                 "status": "success",
                 "confirmation_id": order.get('id'), # This is the Razorpay Order ID
                 "processed_at": datetime.datetime.now().isoformat(),
                 "message": "Payment order successfully created by Razorpay gateway."
             }
             
             print("Payment gateway processing successful (Order Created).")
             return confirmation
             
        except Exception as e:
             # Handle any errors during API call (like invalid keys, network issues)
             print(f"Payment gateway error: {e}")
             return {
                 "status": "failed",
                 "message": f"Payment gateway error: {str(e)}"
             }
