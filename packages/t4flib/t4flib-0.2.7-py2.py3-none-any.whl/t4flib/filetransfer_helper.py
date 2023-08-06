from .config import FT_PARAM_FILEPATH, FT_GRAVITEE_KEY, FT_GRAVITEE_URL
from .log_helper import logger
from .file_helper import get_all_file_by_filemask

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import csv
import os
import shutil
import urllib3
import logging
import datetime


class ft_flow:
    flow_name = ''
    server = ''
    ft_key = ''
    filemask = ''
    path_to_get_file = ''
    path_out = ''
    path_to_log = ''

    def __init__(self, flow_name, server, ft_key, filemask, path_to_get_file, path_out, path_to_log):
        self.flow_name = flow_name
        self.server = server
        self.ft_key = ft_key
        self.filemask = filemask
        self.path_to_get_file = path_to_get_file
        self.path_out = path_out
        self.path_to_log = path_to_log


def get_element_safely(arr, index):
    """
    Retourne l'élément d'un tableau `arr` à l'index `index` de manière sûre
    sans provoquer d'erreur si l'index est en dehors des limites du tableau.
    Si l'index est invalide, la fonction renvoie None.

    Args:
    arr (list): Le tableau dans lequel chercher l'élément
    index (int): L'index de l'élément à récupérer

    Returns:
    L'élément à l'index spécifié, ou None si l'index est invalide.
    """
    if index < 0 or index >= len(arr):
        # L'index est en dehors des limites du tableau, retourner None
        return None
    else:
        # L'index est valide, retourner l'élément correspondant
        return arr[index]


def get_flow_attributes_in_file(flow_name):

    try:

        logger('INFO', f'Vérification de l\' existance du flux {flow_name}')
        flows=[]

        if FT_PARAM_FILEPATH is not None and os.path.exists(FT_PARAM_FILEPATH):
            with open(FT_PARAM_FILEPATH, 'r+', encoding='utf-8') as ft_param_file:
                csv_reader = csv.reader(ft_param_file, delimiter=';')
                for line_flow in csv_reader:
                    if get_element_safely(line_flow, 0) == flow_name:
                        logger('INFO', f'le flux {flow_name} a été trouve')
                        flows.append(ft_flow(
                            get_element_safely(line_flow, 0),
                            get_element_safely(line_flow, 1),
                            get_element_safely(line_flow, 2),
                            get_element_safely(line_flow, 3),
                            get_element_safely(line_flow, 4),
                            get_element_safely(line_flow, 5),
                            get_element_safely(line_flow, 6),
                        ))
        
        if len(flows) == 0:
            logger('WARNING', f'Aucun flux {flow_name} existe.')
        return flows

    except Exception as e:
        logger('ERROR', f'{str(e)}')


def send_file_by_filetransfer(flow_name):
    logger('INFO', f'Envoi dans filetransfer du flux {flow_name} dans le fichier {FT_PARAM_FILEPATH}')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ft_flows_to_send = get_flow_attributes_in_file(flow_name)
    execution_timestamp=datetime.datetime.now().strftime('%Y-%m-%d')

    if len(ft_flows_to_send) > 0:

        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[401, 403, 404, 429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        headers = {
            "Content-type": "application/json",
            "X-Gravitee-api-Key": FT_GRAVITEE_KEY
        }

        for ft_flow_to_send in ft_flows_to_send:

            logging.basicConfig(filename=os.path.join(ft_flow_to_send.path_to_log, f'{flow_name}_{execution_timestamp}.log'), format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', force=True)
            log_f=logging.getLogger() 
            log_f.setLevel(logging.DEBUG) 

            logger('DEBUG', f'{ft_flow_to_send.path_to_get_file}/{ft_flow_to_send.filemask}')
            log_f.debug(f'{ft_flow_to_send.path_to_get_file}/{ft_flow_to_send.filemask}')

            files = get_all_file_by_filemask(ft_flow_to_send.path_to_get_file, ft_flow_to_send.filemask)
            if len(files) == 0:
                log_f.warning('Pas de fichier trouvé')
                continue

            for file in files:

                shutil.copy(str(file.absolute()), ft_flow_to_send.path_out)

                body_request = json.dumps({
                    "flow": ft_flow_to_send.flow_name,
                    "userId": ft_flow_to_send.server,
                    "authKey": ft_flow_to_send.ft_key,
                    "uri": str(file.absolute())
                })

                try:
                    response = requests.post(FT_GRAVITEE_URL, headers=headers, data=body_request, verify=False)
                    ret = response.status_code
                except requests.exceptions.RequestException as e:
                    logger("Error", f"{e}")
                    log_f.error(str(e))
                    ret = None

                if ret in [202, 200]:

                    logger("INFO", f"Le flux {flow_name} contenant le fichier {str(file)} est parti")
                    log_f.info(f"Le flux {flow_name} contenant le fichier {str(file)} est parti")
                else:

                    logger('ERROR', f"Un code erreur API : {ret} a eu lieu")
                    logger('ERROR', f"Erreur lors de l'appel à l'API statut => {ret}")
                    log_f.error(f"Erreur lors de l'appel à l'API statut => {ret}")
