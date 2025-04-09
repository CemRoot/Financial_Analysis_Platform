import logging
from google.cloud import language_v1
from django.conf import settings
import os

logger = logging.getLogger(__name__)

class GoogleNLPSentiment:
    """
    Google Cloud Natural Language API kullanarak duygu analizi yapan servis
    """
    
    def __init__(self):
        # Doğru kimlik bilgileri yolunu ayarla
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        try:
            self.client = language_v1.LanguageServiceClient()
        except Exception as e:
            logger.error(f"Error initializing Google NLP client: {str(e)}")
            self.client = None
    
    def analyze_sentiment(self, text):
        """
        Metni analiz et ve duygu skorunu döndür
        """
        if not self.client:
            logger.error("Google NLP client is not initialized")
            return None
        
        try:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT,
                language="en"
            )
            
            response = self.client.analyze_sentiment(
                request={"document": document}
            )
            
            # Belge düzeyinde duygu bilgisini döndür
            sentiment = response.document_sentiment
            
            return {
                'score': sentiment.score,  # -1.0 (negatif) ile 1.0 (pozitif) arasında
                'magnitude': sentiment.magnitude,  # Duygu şiddeti (0.0+)
                'sentences': [{
                    'text': sentence.text.content,
                    'score': sentence.sentiment.score,
                    'magnitude': sentence.sentiment.magnitude
                } for sentence in response.sentences]
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment with Google NLP: {str(e)}")
            return None
    
    def analyze_entities(self, text):
        """
        Metindeki varlıkları (kişiler, kuruluşlar, yerler vb.) analiz et
        """
        if not self.client:
            logger.error("Google NLP client is not initialized")
            return None
            
        try:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT,
                language="en"
            )
            
            response = self.client.analyze_entities(
                request={"document": document}
            )
            
            entities = []
            for entity in response.entities:
                entity_info = {
                    'name': entity.name,
                    'type': language_v1.Entity.Type(entity.type_).name,
                    'salience': entity.salience,  # Metindeki önem (0-1)
                    'mentions': len(entity.mentions),
                    'metadata': {}
                }
                
                # Metadata alanlarını ekle
                for key, value in entity.metadata.items():
                    entity_info['metadata'][key] = value
                
                entities.append(entity_info)
            
            return entities
        
        except Exception as e:
            logger.error(f"Error analyzing entities with Google NLP: {str(e)}")
            return None