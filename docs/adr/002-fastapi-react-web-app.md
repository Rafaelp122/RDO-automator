# ADR-002: Migração para FastAPI + React

**Status:** Aceito

**Data:** 2026-05-28

**Substitui:** ADR-001

## Contexto

Evolução para aplicação web com deploy serverless.

## Decisão

FastAPI (backend Python) + React Vite (frontend).

## Justificativa

- 100% da engine Python reaproveitada (core/infra copiados com adaptações mínimas)
- FastAPI assíncrono — concorrência nativa
- React padrão de mercado para SPAs interativas
- Deploy desacoplado: Cloud Run (escala a zero) + Vercel (CDN grátis)
- Atualizações automáticas
- Elimina TOML — UI visual substitui configuração manual

## Alternativas rejeitadas

- **Next.js fullstack:** SSR desnecessário para app de formulário
- **Tudo no Vercel:** timeout insuficiente (10-60s vs 30-60s de processamento Excel)
- **Manter PyQt:** não resolve os problemas de distribuição e portfólio

## Consequências

Trade-offs aceitos: latência de rede, limites de request size no Cloud Run, complexidade de dois deploys (mitigada por CI/CD), sem acesso offline.
