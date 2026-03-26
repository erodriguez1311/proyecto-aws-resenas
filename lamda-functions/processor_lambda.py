import json
import boto3
import os

# Inicializamos los clientes fuera del handler para mejorar el rendimiento
comprehend = boto3.client('comprehend')
sns = boto3.client('sns')

def lambda_handler(event, context):
    # Recuperamos el ARN del SNS de alerta desde las variables de entorno configuradas en el YAML
    ALERTA_TOPIC_ARN = os.environ['ALERTA_TOPIC_ARN']
    
    for record in event['Records']:
        try:
            # 1. SQS envía el mensaje. El cuerpo (body) contiene el mensaje original de SNS
            sqs_body = json.loads(record['body'])
            
            # 2. SNS mete nuestro JSON original en un campo llamado 'Message' como string
            inner_message = json.loads(sqs_body['Message'])
            review_text = inner_message.get('text', 'Sin texto')
            
            # 3. Llamada a Amazon Comprehend para analizar el sentimiento
            # Usamos LanguageCode='es' porque tus reseñas serán en español
            response = comprehend.detect_sentiment(Text=review_text, LanguageCode='es')
            sentiment = response['Sentiment']
            
            print(f"Procesando reseña: {review_text} | Sentimiento detectado: {sentiment}")
            
            # 4. Lógica de Negocio: Si el sentimiento es NEGATIVO, disparamos la alerta
            if sentiment == 'NEGATIVE':
                sns.publish(
                    TopicArn=ALERTA_TOPIC_ARN,
                    Message=f"ALERTA ADMINISTRADOR:\n\nSe ha recibido una reseña crítica a través de la web.\n\nContenido: \"{review_text}\"\n\nPor favor, analice el caso para mejorar el servicio.",
                    Subject="Nueva Reseña Negativa Detectada"
                )
                print("Alerta enviada al administrador.")
                
        except Exception as e:
            print(f"Error procesando registro: {str(e)}")
            continue # Continuamos con el siguiente mensaje si uno falla

    return {
        'statusCode': 200,
        'body': json.dumps('Procesamiento completado')
    }
