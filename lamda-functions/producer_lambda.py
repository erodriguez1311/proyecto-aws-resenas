import json
import boto3
import os

sns = boto3.client('sns')
TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    try:
        # Extraer el texto de la reseña del cuerpo de la petición (API Gateway)
        body = json.loads(event['body'])
        review_text = body.get('text', '')
        
        # Publicar en SNS
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({'text': review_text}),
            Subject='Nueva Reseña para procesar'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Reseña recibida correctamente'})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
