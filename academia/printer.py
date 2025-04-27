import logging
import win32print
import serial
import time
import textwrap
from utils import limpar_texto
from gui import messagebox
import configparser
import os

class ImpressoraTermica:
    def __init__(self):
        self.config = self.carregar_configuracao()
        self.porta = None
        
    def carregar_configuracao(self):
        """Carrega configurações do arquivo printer.ini"""
        config = configparser.ConfigParser()
        
        # Valores padrão
        config['serial'] = {
            'porta': 'COM4',
            'baudrate': '9600',
            'bytesize': '8',
            'parity': 'N',
            'stopbits': '1',
            'timeout': '2'
        }
        
        config['codificacao'] = {
            'padrao': 'iso-8859-1',
            'fallback': 'ascii',
            'comando_tabela': '1B7401'
        }
        
        config['formato'] = {
            'largura': '32',
            'divisor': '-'*32,
            'quebra_automatica': 'sim',
            'espacamento': '1'
        }
        
        config['comandos'] = {
            'inicializacao': '1B40,1B7401,1B52,1B2100',
            'corte': '1D5601',
            'avancar_linha': '0A',
            'linhas_pre_corte': '3'
        }
        
        # Carrega configurações personalizadas se existirem
        if os.path.exists('printer.ini'):
            try:
                config.read('printer.ini', encoding='utf-8')
            except Exception as e:
                logging.error(f"Erro ao ler printer.ini: {str(e)}")
        
        return config

    def formatar_texto_impressao(self, texto):
        """Formata o texto para impressão térmica"""
        try:
            largura = int(self.config['formato']['largura'])
            divisor = self.config['formato']['divisor'][:largura]
            espacamento = int(self.config['formato']['espacamento'])
            
            linhas_formatadas = []
            for linha in texto.split('\n'):
                linha = linha.strip()
                
                # Trata linhas divisoras
                if linha.startswith('---'):
                    linhas_formatadas.append(divisor)
                    continue
                    
                # Quebra de linha inteligente
                if len(linha) > largura:
                    partes = textwrap.wrap(linha, width=largura, 
                                         break_long_words=False,
                                         replace_whitespace=False)
                    linhas_formatadas.extend(partes)
                else:
                    linhas_formatadas.append(linha)
                
                # Adiciona espaçamento
                linhas_formatadas.extend([''] * espacamento)
            
            return '\n'.join(linhas_formatadas).strip()
        
        except Exception as e:
            logging.error(f"Erro ao formatar texto: {str(e)}")
            return texto

    def detectar_porta_impressora(self):
        """Detecta automaticamente a porta da impressora"""
        try:
            # Tentar porta configurada
            porta = self.config['serial']['porta']
            try:
                with serial.Serial(port=porta, timeout=1) as ser:
                    self.porta = porta
                    logging.info(f"Usando porta configurada: {porta}")
                    return True
            except serial.SerialException:
                pass
            
            # Detecção automática
            portas_com = [f'COM{i}' for i in range(1, 11)]
            
            for porta in portas_com:
                try:
                    with serial.Serial(port=porta, timeout=1) as ser:
                        self.porta = porta
                        logging.info(f"Porta detectada: {porta}")
                        return True
                except serial.SerialException:
                    continue
            
            logging.warning("Nenhuma porta serial detectada")
            return False
            
        except Exception as e:
            logging.error(f"Erro ao detectar porta: {str(e)}")
            return False

    def imprimir_via_windows(self, texto, nome_ficha):
        """Impressão via spooler do Windows"""
        try:
            printer_name = win32print.GetDefaultPrinter()
            if not printer_name:
                raise Exception("Nenhuma impressora padrão configurada")

            logging.info(f"Imprimindo via Windows na: {printer_name}")

            texto_formatado = self.formatar_texto_impressao(texto)

            hprinter = win32print.OpenPrinter(printer_name)
            try:
                hjob = win32print.StartDocPrinter(hprinter, 1, (nome_ficha, None, "RAW"))
                try:
                    win32print.StartPagePrinter(hprinter)

                    # Codificação ajustada para compatibilidade com acentos
                    try:
                        dados = texto_formatado.encode('cp850', errors='replace')
                    except UnicodeEncodeError:
                        dados = texto_formatado.encode('utf-8', errors='replace')

                    win32print.WritePrinter(hprinter, dados)
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            logging.info("Impressão via Windows concluída")
            return True

        except Exception as e:
            logging.error(f"Falha na impressão Windows: {str(e)}", exc_info=True)
            return False


    def imprimir_serial(self, texto, nome_ficha):
        """Impressão via porta serial"""
        try:
            texto_formatado = self.formatar_texto_impressao(texto)

            with serial.Serial(
                port=self.porta,
                baudrate=int(self.config['serial']['baudrate']),
                bytesize=int(self.config['serial']['bytesize']),
                parity=self.config['serial']['parity'],
                stopbits=int(self.config['serial']['stopbits']),
                timeout=int(self.config['serial']['timeout'])
            ) as porta_serial:

                # Enviar comandos de inicialização
                for cmd in self.config['comandos']['inicializacao'].split(','):
                    porta_serial.write(bytes.fromhex(cmd))
                    time.sleep(0.1)

                # Codificação ajustada para compatibilidade com acentos
                try:
                    texto_bytes = texto_formatado.encode('cp850', errors='replace')
                except UnicodeEncodeError:
                    texto_bytes = texto_formatado.encode('utf-8', errors='replace')

                # Enviar em chunks pequenos
                chunk_size = 16
                for i in range(0, len(texto_bytes), chunk_size):
                    porta_serial.write(texto_bytes[i:i+chunk_size])
                    time.sleep(0.03)

                # Finalização
                for _ in range(int(self.config['comandos']['linhas_pre_corte'])):
                    porta_serial.write(b'\n')

                porta_serial.write(bytes.fromhex(self.config['comandos']['corte']))
                time.sleep(0.5)

            logging.info(f"Impressão concluída na porta {self.porta}")
            return True

        except Exception as e:
            logging.error(f"Falha na impressão serial: {str(e)}", exc_info=True)
            return False


# Instância global
impressora = ImpressoraTermica()

def imprimir_ficha(ficha, nome_ficha):
    return impressora.imprimir_ficha(ficha, nome_ficha)