from app.core.supabase import supabase
from app.schemas.proof import DeliveryProofCreate
from app.schemas.delivery import DeliveryStatus

class ProofRepository:
    def create_proof(self, delivery_id: str, proof_in: DeliveryProofCreate):
        # 1. En un sistema real, subiríamos signature_base64 a Supabase Storage
        # Por ahora lo guardamos como referencia (simulado)
        proof_data = {
            "delivery_id": delivery_id,
            "proof_type": "signature",
            "media_url": "https://storage.example.com/signatures/dummy.png", # Simulado
            "location_lat": proof_in.latitude,
            "location_lng": proof_in.longitude,
            "receiver_name": proof_in.receiver_name
        }
        
        result = supabase.table("delivery_proofs").insert(proof_data).execute()
        
        # 2. Marcar la entrega como COMPLETADA automáticamente
        supabase.table("deliveries").update({
            "status": "delivered",
            "delivered_at": "now()"
        }).eq("id", delivery_id).execute()
        
        return result.data[0]

proof_repo = ProofRepository()
