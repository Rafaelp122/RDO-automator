import os
import shutil
import subprocess
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import QObject, Slot

from src.app.ui.workers.processor_worker import ProcessorWorker
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.ui.utils.thread_manager import run_worker_thread
from src.app.core.logger import logger

class AppController(QObject):
    """
    Controlador da aplicação que gerencia a lógica da interface,
    orquestra workers e manipula a configuração.
    """
    
    def __init__(self, main_window, config_manager):
        super().__init__()
        self.view = main_window
        self.config_manager = config_manager
        self.config = self.config_manager.load_config()
        
        self._threads = []
        self._is_running = False
        
        self._setup_connections()
        self._initialize_view()

    def _setup_connections(self):
        panel = self.view.processing_panel
        panel.start_requested.connect(self.iniciar_processamento)
        panel.revalidate_requested.connect(self.executar_validacao)
        panel.config_save_requested.connect(self.salvar_configuracao)
        panel.import_config_requested.connect(self.importar_configuracao)
        panel.export_config_requested.connect(self.exportar_configuracao)
        panel.origin_selected.connect(self.atualizar_origem_automatica)
        panel.template_selected.connect(self.atualizar_template_automatico)

    def _initialize_view(self):
        self.view.processing_panel.set_config_values(
            self.config['arquivos'].get('dados_origem', ''),
            self.config['arquivos'].get('user_template', ''),
            self.config.get('mapeamento', {})
        )

    def start(self):
        """Inicia a validação inicial da aplicação"""
        self.executar_validacao()

    def salvar_configuracao(self, novos_dados):
        try:
            self.config['arquivos'].update(novos_dados['arquivos'])
            self.config['mapeamento'] = novos_dados.get('mapeamento', {})
            self.config_manager.save_config(self.config)
            logger.info("Configuração persistida com sucesso.")
            QMessageBox.information(self.view, "Sucesso", "Configuração salva localmente!")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Falha ao salvar config: {e}")
            QMessageBox.critical(self.view, "Erro", f"Falha ao salvar configuração: {e}")

    def atualizar_origem_automatica(self, file_path):
        try:
            new_path = self._importar_arquivo(file_path)
            self.config['arquivos']['dados_origem'] = new_path
            self.config_manager.save_config(self.config)
            self.view.processing_panel.input_origin.setText(new_path)
            logger.info(f"Origem importada e atualizada para: {new_path}")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Falha ao importar origem automaticamente: {e}")
            QMessageBox.warning(self.view, "Aviso", f"Não foi possível importar o arquivo: {e}")

    def atualizar_template_automatico(self, file_path):
        try:
            new_path = self._importar_arquivo(file_path)
            self.config['arquivos']['user_template'] = new_path
            self.config_manager.save_config(self.config)
            self.view.processing_panel.input_template.setText(new_path)
            logger.info(f"Template importado e atualizado para: {new_path}")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Falha ao importar template automaticamente: {e}")
            QMessageBox.warning(self.view, "Aviso", f"Não foi possível importar o arquivo: {e}")

    def _importar_arquivo(self, source_path):
        """Copia o arquivo selecionado para a pasta data/input e retorna o novo caminho."""
        if not source_path:
            return ""

        target_dir = os.path.join("data", "input")
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename)

        # Se o arquivo já estiver lá e for o mesmo, não faz nada
        if os.path.exists(target_path) and os.path.abspath(source_path) == os.path.abspath(target_path):
            return target_path

        shutil.copy2(source_path, target_path)
        return target_path

    def importar_configuracao(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Importar Configuração TOML", "", "Config Files (*.toml)"
        )
        if not file_path:
            return

        try:
            nova_config = self.config_manager.import_config(file_path)
            
            if 'arquivos' not in nova_config or 'mapeamento' not in nova_config:
                raise ValueError("Arquivo TOML inválido: chaves obrigatórias ausentes.")

            self.config = nova_config
            self.config_manager.save_config(self.config)
            
            self.view.processing_panel.set_config_values(
                self.config['arquivos'].get('dados_origem', ''),
                self.config['arquivos'].get('user_template', ''),
                self.config.get('mapeamento', {})
            )
            
            logger.info(f"Configuração importada de {file_path}")
            QMessageBox.information(self.view, "Sucesso", "Configuração importada com sucesso!")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Erro ao importar config: {e}")
            QMessageBox.critical(self.view, "Erro na Importação", f"Não foi possível carregar o arquivo: {e}")

    def exportar_configuracao(self, dados_ui):
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Exportar Configuração TOML", "config_export.toml", "Config Files (*.toml)"
        )
        if not file_path:
            return

        try:
            config_para_exportar = {
                "arquivos": dados_ui['arquivos'],
                "mapeamento": dados_ui['mapeamento']
            }
            self.config_manager.export_config(file_path, config_para_exportar)
            logger.info(f"Configuração exportada para {file_path}")
            QMessageBox.information(self.view, "Sucesso", "Configuração exportada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao exportar config: {e}")
            QMessageBox.critical(self.view, "Erro na Exportação", f"Não foi possível salvar o arquivo: {e}")

    def executar_validacao(self):
        if self._is_running:
            return

        logger.info("Validando mapeamento...")
        self._is_running = True
        self.view.processing_panel.clear_log()
        self.view.processing_panel.set_busy(True, "Validando arquivos...")
        
        worker = ValidationWorker()
        worker.validation_finished.connect(self.processar_resultado_validacao)
        
        thread = run_worker_thread(worker, on_log=self._update_ui_log)
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

    def _cleanup_thread(self, thread):
        if thread in self._threads:
            self._threads.remove(thread)
            logger.debug(f"Thread encerrada e removida. Ativas: {len(self._threads)}")

    def _update_ui_log(self, message):
        self.view.processing_panel.log(message)

    @Slot(bool, list)
    def processar_resultado_validacao(self, sucesso, erros):
        self._is_running = False
        if sucesso:
            self.view.processing_panel.set_validation_state(True, "Pronto para operação.")
        else:
            self.view.processing_panel.set_validation_state(False)
            QMessageBox.critical(self.view, "Erro de Mapeamento", "Verifique os problemas listados.")

    def iniciar_processamento(self):
        if self._is_running:
            return

        logger.info("Iniciando geração de relatório...")
        self._is_running = True
        self.view.processing_panel.clear_log()
        self.view.processing_panel.set_busy(True, "Gerando relatório...")

        worker = ProcessorWorker()
        worker.progress_update.connect(self.view.processing_panel.update_progress)
        
        thread = run_worker_thread(
            worker,
            on_finished=self.finalizar_sucesso,
            on_error=self.finalizar_erro,
            on_log=self._update_ui_log
        )
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

    @Slot(str)
    def finalizar_sucesso(self, arquivo):
        self._is_running = False
        self.view.processing_panel.set_busy(False)
        self.view.processing_panel.set_progress_success()
        
        btn_open = QMessageBox.question(
            self.view, "Sucesso", 
            f"Relatório gerado!\n{arquivo}\n\nDeseja abrir a pasta de saída?",
            QMessageBox.Yes | QMessageBox.No
        )
        if btn_open == QMessageBox.Yes:
            self._abrir_pasta_saida()

    def _abrir_pasta_saida(self):
        caminho = os.path.abspath("data/output")
        if os.name == 'nt':
            os.startfile(caminho)
        else:
            try:
                subprocess.run(['xdg-open', caminho])
            except Exception as e:
                logger.warning(f"Não foi possível abrir a pasta automaticamente: {e}")

    @Slot(str)
    def finalizar_erro(self, msg):
        self._is_running = False
        self.view.processing_panel.set_validation_state(True)
        QMessageBox.critical(self.view, "Erro no Processamento", msg)
