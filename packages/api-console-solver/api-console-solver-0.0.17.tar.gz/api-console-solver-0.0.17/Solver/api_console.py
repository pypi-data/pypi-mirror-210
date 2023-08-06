import requests, json, os, traceback
from datetime import datetime, timezone, date

class ConsoleApi:

    def __init__(self, url =''):
        self.url = 'https://consoleapi-dsv.api.zello.services'
        if url != '':
            self.url = url
        self.headers = {'Authorization': 'Bearer ','Content-Type': 'application/json'}

    def gera_token_acesso(self, constante_virtual):
        self.config = self.get_automacao_by_constante_virtual_json(constante_virtual)
        
        if 'detail' in self.config:
            return self.config['detail']

        self.nome_executor = self.config['tx_nome']
        self.config['tx_json'] = self.config['tx_json'].replace("'",'"')
        self.config = json.loads(self.config['tx_json'])
        self.set_config(tokenacesso='', url_console=self.config['url_console'])
        retorno = self.login(_user=self.config['username'], _pass=self.config['password'], client_id='executor')
        
        if 'detail' in retorno:
            return retorno['detail']
        else:
            self.tokenacesso = retorno['access_token']                
            self.set_config(tokenacesso=self.tokenacesso, url_console=self.config['url_console'])
            return [self.tokenacesso, self.config['url_console']]

    def set_config(self, tokenacesso='', url_console = ''):
        if url_console != '':
            self.url = url_console

        self.headers = {'Authorization': 'Bearer ' + tokenacesso,'Content-Type': 'application/json'}

    def login(self, _user='', _pass='', client_id='executor'):
        try:
            if _user is None or _pass is None:
                return None
            
            headers = {}

            url = str(self.url)+"/login"
            payload = {"username": f"{_user}", "password": f"{_pass}", "client_id":f"{client_id}"}

            self.headers = {'Content-Type': 'application/json'}
            self.headersFiles = {'Content-Type': 'application/octet-stream'}

            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            if 'access_token' in response:
                self.tokenacesso = response['access_token']
                self.headers = {'Authorization': 'Bearer ' + self.tokenacesso,'Content-Type': 'application/json'}
                self.headersFiles = {'Authorization': 'Bearer ' + self.tokenacesso,'Content-Type': 'application/octet-stream'}
            else:
                self.tokenacesso = response['detail']
            return response
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return error

    def pega_dados_configuracao(self, config = '/config_ex.json'):
        try:
            dir_json = os.getcwd() + config
            with open(dir_json, 'r', encoding='utf_8_sig') as f:
                arq_json = json.load(f)
            return arq_json
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return traceback.format_exc()

    def ler_arquivo(self, arquivo):
        dados = []
        if os.path.isfile(arquivo):
            with open(arquivo, 'r', encoding='utf_8_sig') as f:
                try:
                    dados = json.load(f)
                except:
                    dados = []
        return dados

    def grava_logs_local(self, conteudo):
        try:
            arquivo = "logs_" + str(date.today()).replace('-','')+'.txt'
            dir_logs = os.getcwd() + "/arquivos/logs/"+arquivo

            os.makedirs(os.getcwd() + "/arquivos/logs", exist_ok=True)

            with open(dir_logs, "a", encoding='utf_8_sig') as outfile:
                outfile.write(conteudo+chr(13))
            return True
        except Exception as error:
            print(error)

    def grava_arquivo_logs(self, json_error):
        arquivo = "logError_" + str(date.today()).replace('-','')+'.json'
        dir_logs = os.getcwd() + "/arquivos/logs/"+arquivo

        os.makedirs(os.getcwd() + "/arquivos/logs", exist_ok=True)

        #print(dir_logs)
        dados_json = self.ler_arquivo(dir_logs)
        
        conteudo = []
        if dados_json != '':
            dados_json.append(json_error)
            conteudo = dados_json
        else:
            conteudo.append(json_error)

        conteudo = str(conteudo).replace('"', '\\"')
        conteudo = str(conteudo).replace("'", '"')
        conteudo = str(conteudo).replace(': "None"', ': null')
        conteudo = str(conteudo).replace(": None", ': null')
        
        with open(dir_logs, "w", encoding='utf_8_sig') as outfile:
            outfile.write(str(conteudo))

    def start_tarefa(self,payload):
        try:        
            url = str(self.url)+"/tarefa/start/"

            payload = json.dumps(payload)

            response = self.post(url, payload)
            return response
        except Exception as erro:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return traceback.format_exc()

    def stop_automacao(self, tarefa_id, bo_status_code = 200, tx_resumo = 'Execução finalizada pela automação'):
        try:        
            url = str(self.url)+"/tarefa/stop/"

            payload = {
                "tarefa_id": tarefa_id,
                "dt_fim": str(datetime.now(timezone.utc)),
                "bo_status_code": bo_status_code,
                "tx_resumo": tx_resumo
            }
            payload = json.dumps(payload)

            if tarefa_id:
                response = self.put(url, payload)
                return response
            return {'detail':False}
        except Exception as erro:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return traceback.format_exc()

    def get_start_automacao(self, automacao_id):
        url = str(self.url)+"/tarefa/automacao/"+str(automacao_id)
        response = self.get(url)
        return response

    def get_usuario_by_executor(self, tx_ip_mac, nu_cpf):
        url = str(self.url)+"/automacao/executor/"+str(nu_cpf)+'/'+str(tx_ip_mac)
        response = self.get(url)
        return response

    def get_download_script(self, tarefa_id):
        url = str(self.url)+"/downloadScripts/"+str(tarefa_id)
        response = self.getFiles(url)
        return response

    def get_tarefa_by_automacao(self, automacao_id, tx_ip_mac):
        url = str(self.url)+"/tarefa/executor/"+str(automacao_id)+"/"+str(tx_ip_mac)
        response = self.get(url)
        return response

    def get_tarefa_by_id(self, tarefa_id):
        url = str(self.url)+"/tarefa/"+str(tarefa_id)
        response = self.get(url)
        return response

    def get_tarefa_by_constante_virtual(self, constante_virtual):
        url = str(self.url)+"/tarefa/constante_virtual/"+str(constante_virtual)
        response = self.get(url)
        return response

    def get_automacao_by_id(self, automacao_id):
        url = str(self.url)+"/automacao/"+str(automacao_id)
        response = self.get(url)
        return response

    def get_logs_by_id_historico(self, historico_tarefa_id):
        url = str(self.url)+"/logs/historico-tarefa/"+str(historico_tarefa_id)
        response = self.get(url)
        return response

    def get_automacao_by_id_json(self, automacao_id):
        url = str(self.url)+"/automacao/executor/"+str(automacao_id)
        response = self.get(url)
        return response

    def get_automacao_by_constante_virtual_json(self, constante_virtual):
        url = str(self.url)+"/automacao/executor/constante/"+str(constante_virtual)
        response = self.get(url)
        return response

    def get_cofre_senha_by_cliente(self, tx_nome, setor_id):
        url = str(self.url)+"/cofresenha/"+str(tx_nome)+"/"+str(setor_id)
        response = self.get(url)
        return response

    def gravar_logs(self, historico_tarefa_id, tx_descricao, tx_acao_auxiliar='', status='success', json_dados=''):
        url = str(self.url)+"/logs/"

        payload = {
            "historico_tarefa_id": historico_tarefa_id,
            "tx_status": f"{status}",
            "tx_acao_auxiliar": f"""{tx_acao_auxiliar}""",
            "tx_descricao": f"""{str(tx_descricao)}""",
            "tx_json": f"""{str(json_dados)}"""
        }        
        if historico_tarefa_id:
            payload = json.dumps(payload)
            response = self.post(url, payload)
            return response
        return False

    def gravar_log_execucao(self, payload):
        url = str(self.url)+"/logs/"
        
        payload = json.dumps(payload)

        response = self.post(url, payload)
        return response

    def gravar_download_executor(self, payload):
        url = str(self.url)+"/executor/"
        payload = json.dumps(payload)
        response = self.post(url, payload)
        return response

    def grava_historico_tarefa(self, payload):
        url = str(self.url)+"/historico-tarefa/"
        payload = json.dumps(payload)
        response = self.post(url, payload)
        return response

    def gravar_dados_negocial(self, payload):
        url = str(self.url)+"/dadosnegocial/"

        payload = json.dumps(payload)
        
        response = self.post(url, payload)
        return response

    def get_controle_execucao_tarefa(self, tarefa_id):
        url = str(self.url)+"/controleexecucao/"+str(tarefa_id)
        response = self.get(url)
        return response

    def gravar_controle_execucao(self, payload):
        url = str(self.url)+"/controleexecucao/"

        payload = json.dumps(payload)
        
        response = self.post(url, payload)
        return response

    def atualiza_controle_execucao(self, payload):
        url = str(self.url)+"/controleexecucao/"

        payload = json.dumps(payload)
        
        response = self.put(url, payload)
        return response

    def atualiza_situacao_tarefa(self, payload):
        url = str(self.url)+"/tarefa/situacao/"

        payload = json.dumps(payload)
        
        response = self.put(url, payload)
        return response

    def atualizar_dados_negocial(self, payload):
        url = str(self.url)+"/dadosnegocial/"

        payload = json.dumps(payload)

        response = self.put(url, payload)
        return response

    def atualizar_data_script(self, script_id, dt_download = ''):
        url = str(self.url)+"/script/dt_download?script_id="+str(script_id)+"&dt_download="+str(dt_download)
        response = self.put(url, [])
        return response

    def atualiza_executor(self, payload):
        url = str(self.url)+"/executor/arquitetura/"
        
        payload = json.dumps(payload)

        response = self.put(url, payload)
        return response

    def get(self, url):
        try:
            response = requests.request("GET", url, headers=self.headers, data="")
            if response.status_code == 200:
                return response.json()
            return {'detail':False}
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return error

    def getFiles(self, url):
        try:
            response = requests.request("GET", url, headers=self.headersFiles, stream=True)
            return response
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return error

    def put(self, url, payload):
        try:
            response = requests.request("PUT", url, headers=self.headers, data=payload)
            if response.status_code == 200:
                return response.json()
            return {'detail':False}
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return error

    def post(self, url, payload):
        try:
            response = requests.request("POST", url, headers=self.headers, data=payload)
            if response.status_code == 200:            
                if( 'detail' not in response.json() and response.json() is not None):
                    response = {'message': 'Registro inserido com sucesso!', 'id': response.json()['id']}
                else:
                    response = response.json()
                return response
            return {'detail':False}
        except Exception as error:
            self.grava_arquivo_logs(f"""{traceback.format_exc()}""")
            return error