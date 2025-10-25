import datetime

class PaymentGateway:
    """
    A simulated payment gateway to process legitimate transactions.
    """
    def process_payment(self, transaction_data: dict) -> dict:
        """
        Simulates successfully processing a payment.
        In a real system, this would involve API calls to a service like Stripe or PayPal.
        """
        print(f"Connecting to external payment gateway for transaction: {transaction_data.get('transaction_id')}")
        
        # Simulate a successful payment confirmation
        confirmation = {
            "status": "success",
            "confirmation_id": f"gate_conf_{transaction_data.get('transaction_id')}",
            "processed_at": datetime.datetime.now().isoformat(),
            "message": "Payment processed successfully by the gateway."
        }
        
        print("Payment gateway processing successful.")
        return confirmation
