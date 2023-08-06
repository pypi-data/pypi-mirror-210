from datetime import datetime
from email.message import EmailMessage
from contextlib import contextmanager

import awswrangler as wr
import boto3
import enum
import getpass
import platform
import logging
import pytz
import smtplib
import ssl
import mysql.connector
import json
import requests
import os

# -- Criando uma sessao com a AWS -- #
awsSession = boto3.Session()

@contextmanager
def rds_conector() -> any:
    try:
        credentials = wr.secretsmanager.get_secret_json('/rpa/mysql/credentials', boto3_session=awsSession)
        conn = mysql.connector.connect(
            host=credentials['host'],
            user=credentials['username'],
            password=credentials['password'],
            port=3306
        )
        yield conn 
    except mysql.connector.Error as e:
        raise e
    finally:
        conn.close()

class Status(enum.Enum):
    ERRO = 'ERRO'
    PROCESSANDO = 'PROCESSANDO'
    FINALIZADOOK = 'FINALIZADO'
    SUCESSO="SUCESSO"

class Level(enum.Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class TbProcesso:   
    INSERT_QUERY =  'INSERT INTO logger.processo (grupo_id, processo, tipo_servico, Ativo) VALUES(%(grupo_id)s, %(processo)s, %(tipo_servico)s, %(ativo)s);'

    def __init__(self, dml:str ,**kwargs):
        self.query = "SELECT * FROM logger.processo"
        self.dml = dml
        self.kwargs = kwargs

    def filtrar(self,condition:str) -> 'TbProcesso':
        self.query += f" Where {condition}"
        return self
   
    def executar(self) -> any:
        try:
            with rds_conector() as conn:

                cursor = conn.cursor(dictionary=True)   

                if self.dml == 'insert':
                    cursor.execute(self.INSERT_QUERY, self.kwargs)
                    conn.commit()
                    result = cursor.lastrowid
                else:                
                    cursor.execute(self.query)
                    result = cursor.fetchone()['id']

        except TypeError:
            return None       
        except mysql.connector.Error as e:
            conn.rollback()
            raise e
        else:
            return result
        finally:
            cursor.close()

class TbExecucao:
    INSERT_QUERY = "INSERT INTO logger.execucao (processo_id, executado_por, dt_inicio, status) VALUES(%(processo_id)s,%(executado_por)s,%(dt_inicio)s,%(status)s);"
    UPDATE_QUERY = 'UPDATE logger.execucao SET dt_fim=%(dt_fim)s, status=%(status)s, message=%(message)s WHERE id=%(execucao_id)s;'

    def __init__(self, dml:str, **kwargs):
        self.dml = dml
        self.kwargs = kwargs
        self.value = self.executar()
    
    def executar(self) -> int:
        try:
            with rds_conector() as conn:
                cursor =conn.cursor()
                if self.dml == 'insert':
                    cursor.execute(self.INSERT_QUERY, self.kwargs)
                    conn.commit()
                    return cursor.lastrowid
                else:
                    cursor.execute(self.UPDATE_QUERY, self.kwargs)
                    conn.commit()
        except  mysql.connector.Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

class TbLog:
    INSERT_QUERY = 'INSERT INTO logger.log (execucao_id, tipo_log, descricao) VALUES(%(execucao_id)s, %(tipo_log)s, %(descricao)s);'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.executar()
    
    def executar(self) -> None:
        try:
            with rds_conector() as conn:
                cursor = conn.cursor()
                cursor.execute(self.INSERT_QUERY, self.kwargs)
                conn.commit()
        except mysql.connector.Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

class TbResponsaveis:
    def __init__(self):
        self.query = "SELECT * FROM logger.responsaveis"

    def filtrar(self, condition:str) -> 'TbResponsaveis':
        self.query += f" Where {condition}"
        return self

    def executar(self) -> dict:
        try:
            with rds_conector() as conn:
                cursor = conn.cursor(dictionary=True)                          
                cursor.execute(self.query)
                result = cursor.fetchall()
                return result
        except mysql.connector.Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

class Monitoramento:
    def __init__(self, ambiente:str, nome_processo:str, grupo_id:int):
        self.__nome_processo = nome_processo
        self.__grupo = grupo_id
        self.__environment = ambiente
        self.__tipo_servico = self.busca_nome_servico_aws()
        self.__processo_id = None
        self.__execucao_id = None
        self.__host = f'{getpass.getuser()}@{platform.node()}'

    def busca_nome_servico_aws(self):
        metadata = awsSession.client('sts').get_caller_identity()
        return metadata['Arn'].split(':')[2].upper()
    
    
    def inicia_execucao(self):
        try:
            result = TbProcesso('select').filtrar(f"processo = '{self.__nome_processo}'").executar()
        except Exception as e:
            logging.error(e)
        else:
            if result:
                self.__processo_id = result
                logging.info(f'Usando processo >> {self.__processo_id}')
            else:
                self.__processo_id = TbProcesso( dml='insert'
                                                ,grupo_id=self.__grupo 
                                                ,processo=self.__nome_processo
                                                ,tipo_servico=self.__tipo_servico
                                                ,ativo=True).executar()
                
                logging.info(f'Processo {self.__nome_processo} criado com sucesso!')
        try:
            self.__execucao_id = TbExecucao( dml='insert'
                                            ,processo_id=self.__processo_id 
                                            ,executado_por=self.__host 
                                            ,dt_inicio=datetime.now() 
                                            ,status=Status.PROCESSANDO.value )
            
            self.log(Level.INFO.value, "Inicio")
        except Exception as e:
            logging.error(e)
            raise e
        else:
            logging.info(f'Execucao >> {self.__execucao_id.value} << iniciada.')

    
    def finaliza_execucao(self, status, message=None):
        try:
            TbExecucao(dml='update', execucao_id=self.__execucao_id.value , dt_fim=datetime.now() ,status=status, message=message )
            self.log(Level.INFO.value, "Fim")
        except Exception as e:
            raise e
        else:
            logging.info(f'Execucao >> {self.__execucao_id.value} << finalizado.')

    
    def log(self, tipo_log, descricao=None):
        if not self.__execucao_id.value:
            logging.warning('Precisa iniciar um processo para gerar um log!')
        else:
            try:
                TbLog(execucao_id=self.__execucao_id.value 
                    , tipo_log=tipo_log
                    , descricao=descricao)
            except Exception as e:
                raise e

    def verifica_status(self, status:str=None, level:str=None) -> str:
        if status == 'SUCESSO':
            msg = f'<b style="color:green">{status}</b>'
        elif status == "ERRO":
            msg = f'<b style="color:red">{status}</b> <br><br> <b>Detalhes do erro:</b>'
        else:
            msg = ''
            if level == "WARNING":
                msg += '''<tr>
                            <td style="padding:20px;background:#fd5b5b;color:#fff;text-align:center;font-family:Arial,sans-serif;font-size:18px;">
                            <p> <b>Atenção: A equipe de dados já esta atuando e verificando o motivo da falha.</b> </p>
                            </td>
                        </tr>'''
        return msg
    
    def envia_alertas(self, status:str, level:str=None, exception:str=''):
        """ Metodo opcional para realizar a chama dos alertas de email e teams de uma só vez"""
        self.envia_alerta_email(status, level, exception)
        self.envia_alerta_teams(status, exception)

    
    def envia_alerta_teams(self, status:str, exception:str):
        logging.info('Enviando alerta via teams.')
        try:
            data = {
                "nome_processo": self.__nome_processo.title(),
                "tipo_servico": self.__tipo_servico,
                'data_ref': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M'),
                "status": status,
                "ambiente": self.__environment.upper(),
                "exception": exception.replace('"',"'").replace('\n','')
            }
            
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates','template_teams.json'),encoding='utf-8') as file:
                template_data = json.load(file)
            
            payload = json.dumps(template_data) % data
            headers = { 'Content-Type': 'application/json' }
            url = wr.secretsmanager.get_secret_json(f'{self.__environment}/teams/webhook', boto3_session=awsSession)['webhook_url']

            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()

        except requests.RequestException as e:
            raise e
        else:
            logging.info('Alerta via teams enviado com sucesso.')

    
    def envia_alerta_email(self, status:str, level:str=None, exception:str='') -> None:

        logging.info('Enviando email de log.')

        try:
            emailCredentials = wr.secretsmanager.get_secret_json('/rpa/email/credentials',awsSession)
            emailSender = emailCredentials['username']
            emailPass   = emailCredentials['password']
            emailSmtp   = emailCredentials['smtp']
            emailPort   = emailCredentials['port']  
            
            dtRef = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')
            
            responsaveis = TbResponsaveis().filtrar(f"ambiente LIKE '%{self.__environment}%' AND recebe_alertas = True AND ativo = True").executar()
            receivers = [email['email'] for email in responsaveis]

            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates','template_email_log.html'), encoding='utf-8') as template:

                html = template.read()
                html = html.format( status=self.verifica_status(status=status)
                                   ,alerta=self.verifica_status(level=level)
                                   ,dtRef=dtRef
                                   ,nome_processo=self.__nome_processo.title()
                                   ,tipo_servico = self.__tipo_servico
                                   ,environment=self.__environment.upper()
                                   ,exception=exception)

                message = EmailMessage()
                message['Subject'] = f'NÃO RESPONDER - ENVIO AUTOMATICO - Monitoramento {self.__nome_processo.title()} - {status}'
                message['From'] = emailSender
                message['To'] = ', '.join(receivers)
                message.set_content(html,subtype='html')

                sslContext = ssl.create_default_context()

                with smtplib.SMTP(emailSmtp, emailPort) as server:
                    server.starttls(context=sslContext)
                    server.login(emailSender, emailPass)
                    server.send_message(message)
                    server.quit()

        except Exception as e:
            logging.error(f'Erro ao enviar email de log: {e}')
            raise e
        else:
            logging.info('Email de log enviado com sucesso.')
