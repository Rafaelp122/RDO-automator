import PyInstaller.__main__
import os
import platform
from pathlib import Path

def build():
    # Caminho base do projeto
    base_dir = Path(__file__).parent.absolute()
    
    # Define o nome do executável
    app_name = "RDO_Automator"
    
    # Configura os argumentos do PyInstaller
    args = [
        str(base_dir / 'main.py'),          # Script principal
        f'--name={app_name}',              # Nome do executável
        '--onedir',                        # Cria uma pasta (mais estável para apps com muitos recursos)
        '--noconsole',                     # Não abre o terminal preto ao iniciar (GUI mode)
        '--clean',                         # Limpa cache antes de buildar
        
        # Incluir pasta de Assets (ícones e templates)
        f'--add-data={base_dir / "assets"}{os.pathsep}assets',
        
        # Incluir arquivos de Estilo (QSS)
        f'--add-data={base_dir / "src/app/ui/styles"}{os.pathsep}src/app/ui/styles',
        
        # Ocultar bibliotecas desnecessárias para diminuir o tamanho
        '--exclude-module=tkinter',
        '--exclude-module=unittest',
    ]

    # Adicionar ícone do executável se existisse um arquivo .ico ou .icns
    # if platform.system() == "Windows":
    #     args.append('--icon=assets/icon.ico')

    print(f"Iniciando build do {app_name} para {platform.system()}...")
    PyInstaller.__main__.run(args)
    print("\nBuild concluido! Verifique a pasta 'dist/'.")

if __name__ == "__main__":
    build()
