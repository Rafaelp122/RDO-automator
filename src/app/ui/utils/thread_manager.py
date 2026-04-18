from PySide6.QtCore import QThread

def run_worker_thread(worker, on_finished=None, on_error=None, on_log=None):
    """
    Abstração universal para execução de Workers em QThreads.
    Garante que os sinais sejam desconectados automaticamente ao terminar.
    """
    thread = QThread()
    worker.moveToThread(thread)
    
    # Ancoramos o worker na thread para evitar GC prematuro
    thread._worker_ref = worker 
    
    # 1. Início do Trabalho
    thread.started.connect(worker.run)
    
    # 2. Conexões de Log (Usa slot direto para evitar acúmulo)
    if on_log and hasattr(worker, 'progress_log'):
        worker.progress_log.connect(on_log)
    
    # 3. Conexões de Resultado
    if on_finished and hasattr(worker, 'finished'):
        worker.finished.connect(on_finished)
        
    if on_error and hasattr(worker, 'error'):
        worker.error.connect(on_error)

    # 4. Orquestração de Vida (Finalização Segura)
    # Todos os workers devem ter um sinal de encerramento técnico (ex: finished ou error)
    # O quit() para o loop de eventos da thread
    if hasattr(worker, 'finished'):
        worker.finished.connect(thread.quit)
    if hasattr(worker, 'error'):
        worker.error.connect(thread.quit)

    # O deleteLater garante a destruição da thread e do worker na ordem correta
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(worker.deleteLater)
    
    thread.start()
    return thread
