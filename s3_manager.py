import json
import mimetypes
from datetime import datetime, UTC
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from config import AWS_REGION, BUCKET_NAME


class S3Manager:
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=AWS_REGION)

    def enviar_json_dinamico(self, nome, email, mensagem, prefixo="envios"):
        dados = {
            "id": str(uuid4()),
            "nome": nome,
            "email": email,
            "mensagem": mensagem,
            "data_envio": datetime.now(UTC).isoformat()
        }

        chave = f"{prefixo}/{dados['id']}.json"
        conteudo_json = json.dumps(dados, ensure_ascii=False, indent=2)

        try:
            resposta = self.s3.put_object(
                Bucket=BUCKET_NAME,
                Key=chave,
                Body=conteudo_json.encode("utf-8"),
                ContentType="application/json"
            )
            return True, {
                "mensagem": "JSON enviado com sucesso.",
                "chave": chave,
                "etag": resposta.get("ETag")
            }
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao enviar JSON: {erro}"

    def enviar_arquivo_local(self, caminho_local, chave_s3=None):
        if not chave_s3:
            chave_s3 = caminho_local.split("/")[-1]

        content_type, _ = mimetypes.guess_type(caminho_local)
        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self.s3.upload_file(
                Filename=caminho_local,
                Bucket=BUCKET_NAME,
                Key=chave_s3,
                ExtraArgs=extra_args if extra_args else None
            )
            return True, f"Arquivo enviado com sucesso para: {chave_s3}"
        except FileNotFoundError:
            return False, "Arquivo local não encontrado."
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao enviar arquivo: {erro}"

    def listar_arquivos(self, prefixo=""):
        try:
            resposta = self.s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefixo)
            arquivos = resposta.get("Contents", [])

            if not arquivos:
                return True, []

            lista = []
            for item in arquivos:
                lista.append({
                    "chave": item["Key"],
                    "tamanho_bytes": item["Size"],
                    "ultima_modificacao": item["LastModified"].isoformat()
                })

            return True, lista
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao listar arquivos: {erro}"

    def ler_json_da_nuvem(self, chave_s3):
        try:
            resposta = self.s3.get_object(Bucket=BUCKET_NAME, Key=chave_s3)
            conteudo = resposta["Body"].read().decode("utf-8")
            dados = json.loads(conteudo)
            return True, dados
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao ler arquivo da nuvem: {erro}"
        except json.JSONDecodeError:
            return False, "O arquivo existe, mas não é um JSON válido."

    def baixar_arquivo(self, chave_s3, caminho_local):
        try:
            self.s3.download_file(BUCKET_NAME, chave_s3, caminho_local)
            return True, f"Arquivo baixado com sucesso em: {caminho_local}"
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao baixar arquivo: {erro}"

    def deletar_arquivo(self, chave_s3):
        try:
            self.s3.delete_object(Bucket=BUCKET_NAME, Key=chave_s3)
            return True, f"Arquivo deletado com sucesso: {chave_s3}"
        except NoCredentialsError:
            return False, "Credenciais AWS não encontradas. Rode 'aws configure'."
        except ClientError as erro:
            return False, f"Erro ao deletar arquivo: {erro}"
        