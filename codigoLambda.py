variavel de ambiente: TABELA_CLIENTES - ClientesTurismo


import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
tabela = dynamodb.Table(os.environ["TABELA_CLIENTES"])


def lambda_handler(event, context):
    parametros = event.get("Details", {}).get("Parameters", {})
    acao = parametros.get("acao", "").strip().lower()

    try:
        if acao == "consultar":
            numero = parametros.get("numero", "").strip()

            if not numero.isdigit() or int(numero) < 1:
                return {"status": "numero_invalido"}

            resposta = tabela.get_item(
                Key={"clienteId": int(numero)},
                ConsistentRead=True
            )

            cliente = resposta.get("Item")

            if not cliente:
                return {"status": "nao_encontrado"}

            return {
                "status": "encontrado",
                "numero": str(cliente["clienteId"]),
                "nome": cliente.get("nome", ""),
                "email": cliente.get("email", "")
            }

        if acao == "cadastrar":
            nome = parametros.get("nome", "").strip()
            email = parametros.get("email", "").strip()

            if not nome or not email:
                return {"status": "dados_incompletos"}

            contador = tabela.update_item(
                Key={"clienteId": 0},
                UpdateExpression="ADD sequencia :incremento",
                ExpressionAttributeValues={":incremento": 1},
                ReturnValues="UPDATED_NEW"
            )

            numero = int(contador["Attributes"]["sequencia"])

            tabela.put_item(
                Item={
                    "clienteId": numero,
                    "nome": nome,
                    "email": email
                },
                ConditionExpression="attribute_not_exists(clienteId)"
            )

            return {
                "status": "cadastrado",
                "numero": str(numero),
                "nome": nome,
                "email": email
            }

        return {"status": "acao_invalida"}

    except ClientError:
        return {"status": "erro_banco"}