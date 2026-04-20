from app.risk_analysis.engine import RiskAnalysisEngine
from app.honeypot.honeypot_gateway import HoneypotGateway
from app.services.payment_gateway import PaymentGateway
from config.settings import settings

class DecisionRouter:
    def __init__(self):
        self.risk_engine = RiskAnalysisEngine()
        self.honeypot_gateway = HoneypotGateway()
        self.payment_gateway = PaymentGateway()

    def _fast_check(self, transaction_data: dict) -> list:
        """
        Performs an instantaneous rule-based check on key characteristics.
        Returns a list of reasons if deemed extremely suspicious, empty list otherwise.
        """
        reasons = []
        amount = transaction_data.get("Amount", 0.0)
        try:
            if float(amount) > 50000:
                reasons.append("Failed static fast-check (e.g. unusually high amount)")
        except (ValueError, TypeError):
            pass
            
        ip_address = transaction_data.get("ip_address")
        if ip_address:
            try:
                from app.database.db import get_mongo_db
                db = get_mongo_db()
                failed_count = db['failed_payments'].count_documents({"ip_address": ip_address})
                if failed_count >= 5:
                    reasons.append(f"Multiple failed transactions detected from IP: {ip_address}")
            except Exception as e:
                print(f"Error checking IP velocity: {e}")
                
        return reasons

    def route_transaction(self, transaction_data: dict) -> dict:
        """
        Routes the transaction according to the system architecture diagram.
        Decision Layer uses fast-checks to send clear frauds to Honeypot-Integrated Gateway,
        and legitimate-looking transactions to Risk Analysis Engine for evaluation.
        """
        print(f"Decision Layer processing transaction: {transaction_data.get('transaction_id')}")

        # 1. Early decision routing
        suspicious_reasons = self._fast_check(transaction_data)

        if suspicious_reasons:
            print(f"DecisionLayer: Transaction {transaction_data.get('transaction_id')} failed fast check. Diverting to honeypot.")
            honeypot_result = self.honeypot_gateway.process_transaction(transaction_data, None)
            return {
                "status": "diverted_to_honeypot",
                "transaction_id": transaction_data.get('transaction_id'),
                "honeypot_info": honeypot_result,
                "explanations": suspicious_reasons
            }

        # 2. Deep check for transactions that passed the early filter
        risk_score, explanations, scaled_features = self.risk_engine.analyze(transaction_data)

        if risk_score > settings.RISK_THRESHOLD:
            print(f"DecisionLayer: Transaction {transaction_data.get('transaction_id')} deemed suspicious by Risk Engine. Diverting to honeypot.")
            honeypot_result = self.honeypot_gateway.process_transaction(transaction_data, scaled_features)
            return {
                "status": "diverted_to_honeypot",
                "transaction_id": transaction_data.get('transaction_id'),
                "honeypot_info": honeypot_result,
                "explanations": explanations
            }
        else:
            print(f"DecisionLayer: Transaction {transaction_data.get('transaction_id')} deemed legitimate. Proceeding to payment gateway.")
            payment_confirmation = self.payment_gateway.process_payment(transaction_data)
            return {
                "status": "processed_legitimately",
                "transaction_id": transaction_data.get('transaction_id'),
                "payment_confirmation": payment_confirmation,
                "risk_score": risk_score,
                "scaled_features": scaled_features
            }
