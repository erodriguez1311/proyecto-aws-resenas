import boto3
import json

def lambda_handler(event, context):
    comprehend = boto3.client('comprehend')
    sns = boto3.client('sns')
    
    for record in event['Records']:
        # 1. Leer el mensaje de SQS
        body = json.loads(record['body'])
        review_text = body['text']
        
        # 2. Analizar sentimiento con IA
        response = comprehend.detect_sentiment(Text=review_text, LanguageCode='es')
        sentiment = response['Sentiment']
        
        # 3. Lógica de negocio: Si es negativo, avisar
        if sentiment == 'NEGATIVE':
            sns.publish(
                TopicArn='TU_ARN_DE_SNS_ALERTA',
                Message=f"Alerta: Reseña negativa recibida: {review_text}",
                Subject="Nueva Reseña Negativa Detectada"
            )
            
    return {'statusCode': 200}
