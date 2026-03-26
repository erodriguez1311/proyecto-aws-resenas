import json
import boto3
import os

comprehend = boto3.client('comprehend')
sns = boto3.client('sns')
ALERTA_TOPIC_ARN = os.environ['ALERTA_TOPIC_ARN']

def lambda_handler(event, context):
    for record in event['Records']:
        # SQS envía el mensaje dentro de 'body'
        payload = json.loads(record['body'])
        # Si viene de SNS -> SQS, el texto está dentro de un campo 'Message'
        inner_message = json.loads(payload['Message'])
        text = inner_message['text']
        
        # Analizar sentimiento
        res = comprehend.detect_sentiment(Text=text, LanguageCode='es')
        sentiment = res['Sentiment']
        
        print(f"Texto: {text} | Sentimiento: {sentiment}")
        
        # Si es negativo, enviar correo al administrador
        if sentiment == 'NEGATIVE':
            sns.publish(
                TopicArn=ALERTA_TOPIC_ARN,
                Message=f"ALERTA: Se ha recibido una reseña negativa:\n\n\"{text}\"",
                Subject="Crítica Negativa Detectada"
            )
    return {'status': 'ok'}
