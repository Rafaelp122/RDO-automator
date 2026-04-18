import os
import subprocess
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QFileDialog
from PySide6.QtCore import Slot

from src.app.ui.workers.processor_worker import ProcessorWorker
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.ui.components.header import Header
from src.app.ui.components.processing_panel import ProcessingPanel
from src.app.ui.utils.thread_manager import run_worker_thread
from src.app.core.logger import logger
from src.app.infra.config_manager import ConfigManager

class MainWindow(QMainWindow):
    """
    Main Window Refatorada:
    - Uso de lista para manter threads vivas (evita Garbage Collection).
    - Logs centralizados com logging.
    """
    
    def __init__(self):
        super().__init__()
        logger.info("Inicializando aplicação...")
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        self.setWindowTitle("Report Automator v1.0")
        self.setMinimumSize(800, 800)
        self._load_styles()
        
        # Lista de threads para evitar que o Python as delete prematuramente
        self._threads = []
        self._is_running = False
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header = Header("Report Automator")
        self.main_layout.addWidget(self.header)

        self.processing_panel = ProcessingPanel()
        self.processing_panel.start_requested.connect(self.iniciar_processamento)
        self.processing_panel.revalidate_requested.connect(self.executar_validacao)
        self.processing_panel.config_save_requested.connect(self.salvar_configuracao)
        self.processing_panel.import_config_requested.connect(self.importar_configuracao)
        self.processing_panel.export_config_requested.connect(self.exportar_configuracao)
        
        # Inicializa campos com config atual
        self.processing_panel.set_config_values(
            self.config['arquivos'].get('dados_origem', ''),
            self.config['arquivos'].get('user_template', ''),
            self.config.get('mapeamento', {})
        )

        panel_container = QWidget()
        panel_layout = QVBoxLayout(panel_container)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.addWidget(self.processing_panel)
        self.main_layout.addWidget(panel_container)
        
        self._setup_footer()
        logger.info("Interface pronta.")
        self.executar_validacao()

    def salvar_configuracao(self, novos_dados):
        try:
            self.config['arquivos'].update(novos_dados['arquivos'])
            self.config['mapeamento'] = novos_dados.get('mapeamento', {})
            self.config_manager.save_config(self.config)
            logger.info("Configuração persistida com sucesso.")
            QMessageBox.information(self, "Sucesso", "Configuração salva localmente!")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Falha ao salvar config: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao salvar configuração: {e}")

    def importar_configuracao(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Configuração TOML", "", "Config Files (*.toml)"
        )
        if not file_path:
            return

        try:
            import tomllib
            with open(file_path, "rb") as f:
                nova_config = tomllib.load(f)
            
            # Validação básica
            if 'arquivos' not in nova_config or 'mapeamento' not in nova_config:
                raise ValueError("Arquivo TOML inválido: chaves obrigatórias ausentes.")

            self.config = nova_config
            self.config_manager.save_config(self.config) # Sobrescreve o config.toml local
            
            # Atualiza UI
            self.processing_panel.set_config_values(
                self.config['arquivos'].get('dados_origem', ''),
                self.config['arquivos'].get('user_template', ''),
                self.config.get('mapeamento', {})
            )
            
            logger.info(f"Configuração importada de {file_path}")
            QMessageBox.information(self, "Sucesso", "Configuração importada com sucesso!")
            self.executar_validacao()
        except Exception as e:
            logger.error(f"Erro ao importar config: {e}")
            QMessageBox.critical(self, "Erro na Importação", f"Não foi possível carregar o arquivo: {e}")

    def exportar_configuracao(self, dados_ui):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Configuração TOML", "config_export.toml", "Config Files (*.toml)"
        )
        if not file_path:
            return

        try:
            import tomli_w
            # Usamos os dados atuais da UI para garantir que exportamos o que o usuário vê
            config_para_exportar = {
                "arquivos": dados_ui['arquivos'],
                "mapeamento": dados_ui['mapeamento']
            }
            
            with open(file_path, "wb") as f:
                tomli_w.dump(config_para_exportar, f)
            
            logger.info(f"Configuração exportada para {file_path}")
            QMessageBox.information(self, "Sucesso", "Configuração exportada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao exportar config: {e}")
            QMessageBox.critical(self, "Erro na Exportação", f"Não foi possível salvar o arquivo: {e}")

    def _load_styles(self):
        try:
            with open("src/app/ui/styles/main.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"Falha ao carregar estilos: {e}")

    def _setup_footer(self):
        footer_container = QWidget()
        footer_layout = QHBoxLayout(footer_container)
        self.footer_label = QLabel("v1.0.0 | Licença MIT")
        self.footer_label.setObjectName("FooterLabel")
        footer_layout.addStretch()
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        self.main_layout.addWidget(footer_container)

    def executar_validacao(self):
        if self._is_running:
            return

        logger.info("Validando mapeamento...")
        self._is_running = True
        self.processing_panel.clear_log()
        self.processing_panel.set_busy(True, "Validando arquivos...")
        
        worker = ValidationWorker()
        worker.validation_finished.connect(self.processar_resultado_validacao)
        
        # Adicionamos a thread à lista para mantê-la viva
        thread = run_worker_thread(worker, on_log=self._update_ui_log)
        self._threads.append(thread)
        # Limpa a referência da lista quando a thread terminar
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

    def _cleanup_thread(self, thread):
        """Remove a thread da lista de persistência após o término"""
        if thread in self._threads:
            self._threads.remove(thread)
            logger.debug(f"Thread encerrada e removida. Ativas: {len(self._threads)}")

    def _update_ui_log(self, message):
        """Apenas atualiza o painel visual, sem duplicar log no arquivo/console"""
        self.processing_panel.log(message)

    @Slot(bool, list)
    def processar_resultado_validacao(self, sucesso, erros):
        self._is_running = False
        if sucesso:
            self.processing_panel.set_validation_state(True, "Pronto para operação.")
        else:
            self.processing_panel.set_validation_state(False)
            for erro in erros:
                logger.error(f"Erro de validação: {erro}")
                self._update_ui_log(f"ERRO: {erro}")
            QMessageBox.critical(self, "Erro de Mapeamento", "Verifique os problemas listados.")

    def iniciar_processamento(self):
        if self._is_running:
            return

        logger.info("Iniciando geração de relatório...")
        self._is_running = True
        self.processing_panel.clear_log()
        self.processing_panel.set_busy(True, "Gerando relatório...")

        worker = ProcessorWorker()
        worker.progress_update.connect(self.processing_panel.update_progress)
        
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
        self.processing_panel.set_busy(False)
        self.processing_panel.set_progress_success()
        
        btn_open = QMessageBox.question(
            self, "Sucesso", 
            f"Relatório gerado!\n{arquivo}\n\nDeseja abrir a pasta de saída?",
            QMessageBox.Yes | QMessageBox.No
        )
        if btn_open == QMessageBox.Yes:
            self._abrir_pasta_saida()

    def _abrir_pasta_saida(self):
        caminho = os.path.abspath("data/output")
        if os.name == 'nt': # Windows
            os.startfile(caminho)
        else: # macOS/Linux
            try:
                subprocess.run(['xdg-open', caminho])
            except Exception as e:
                logger.warning(f"Não foi possível abrir a pasta automaticamente: {e}")

    @Slot(str)
    def finalizar_erro(self, msg):
        self._is_running = False
        self.processing_panel.set_validation_state(True)
        QMessageBox.critical(self, "Erro no Processamento", msg)
