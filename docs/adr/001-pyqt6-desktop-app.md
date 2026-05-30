# ADR-001: Escolha original de PyQt6

**Status:** Substituído pelo ADR-002

**Data:** 2026-04 (original)

## Contexto

Ferramenta de uso pessoal/equipe pequena para automatização de Diários de Obra.

## Decisão

PyQt6 (PySide6) como framework de UI desktop.

## Justificativa

- Engine de processamento (openpyxl + pandas) é Python nativa
- Mesma linguagem front e back — zero overhead
- Acesso direto ao filesystem
- Empacotamento único via PyInstaller
- Iteração rápida: 1 pessoa, 1 linguagem

## Consequências

Trade-offs aceitos: usuário precisa baixar .exe, atualizações manuais, sem acesso remoto, sem portfólio.
